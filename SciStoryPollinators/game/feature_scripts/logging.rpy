init python:
    # ------------------------------------------------------------------
    # Logging helpers used across the project.
    #
    # Two flavors live here:
    #   1. Scene logs (buffer now, save/export later) via log_event().
    #   2. Immediate HTTP pings for live tracking via log_http().
    #
    # The scene system also manages a persistent archive, an upload queue,
    # and a one-click ZIP export to help folks grab everything at once.
    # ------------------------------------------------------------------
    import json, csv, io, time, hashlib, os, zipfile
    import datetime
    from typing import Dict, Any, Optional

    # -------------------------
    # Session & buffers
    # -------------------------
    # Fresh identifier per boot so the same player can be distinguished across sessions.
    SESSION_ID = renpy.random.randint(10**8, 10**9-1)

    _scene_events = []  # in-memory scratchpad for the active scene
    _upload_endpoint = "https://example.com/ingest"  # <- change me before shipping
    _max_persistent_logs = 500  # keep the newest N archived scene logs
    _max_queue = 1000  # cap on pending uploads to avoid runaway growth

    # -------------------------
    # Utilities
    # -------------------------
    # Returns a timestamp string so saved files have unique, human-readable names.
    def _now_stamp():
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

    # Creates a hash fingerprint; used to detect duplicates on the server later.
    def _sha256(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Turns the in-memory scene notes into a CSV string for easy spreadsheet review.
    def _to_csv(events):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["t","kind","data"])
        writer.writeheader()
        for e in events:
            row = dict(e)
            row["data"] = json.dumps(row["data"], ensure_ascii=False)
            writer.writerow(row)
        return buf.getvalue()

    # Attempts to trigger a browser download when the game runs on the web; desktop builds skip this.
    def _trigger_web_download(filename, text, mime="text/plain"):
        # Works only on Web builds; on desktop, returns False and we disk-write instead.
        if renpy.emscripten:
            import emscripten
            safe_text = text.replace("`", "\\`")
            js = f"""
            (function(){{
                var data = `{safe_text}`;
                var blob = new Blob([data], {{type: "{mime}"}});
                var a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = "{filename}";
                document.body.appendChild(a);
                a.click();
                setTimeout(function() {{
                    URL.revokeObjectURL(a.href);
                    a.remove();
                }}, 0);
            }})();
            """
            emscripten.run_script(js)
            return True
        return False

    # Writes the log file to the local save folder and notifies the player.
    def _write_native(filename, text):
        path = os.path.join(config.savedir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        renpy.notify(f"Saved log to {path}")

    # -------------------------
    # Public logging API
    # -------------------------
    # Call during a scene to remember something noteworthy; data is buffered until the scene ends.
    def log_event(kind, payload=None):
        _scene_events.append({
            "t": time.time(),
            "kind": kind,
            "data": payload or {}
        })

    # Call once when the scene wraps to save, archive, and queue every buffered event.
    def download_scene_log(scene_name, as_csv=True):
        """
        Call at the end of a scene.
        1) Serializes the scene log
        2) Mirrors into persistent archive
        3) Enqueues for remote upload (store-and-forward)
        4) Triggers a user download (web) OR writes to disk (desktop)
        """
        if not _scene_events:
            return

        stamp = _now_stamp()
        ext = "csv" if as_csv else "json"
        fname = f"log_{scene_name}_{stamp}_sid{SESSION_ID}.{ext}"

        if as_csv:
            content = _to_csv(_scene_events)
            mime = "text/csv"
        else:
            content = json.dumps(_scene_events, ensure_ascii=False, indent=2)
            mime = "application/json"

        # 2) Mirror into persistent rolling archive
        _save_copy_for_export(scene_name, stamp, content, ext)

        # 3) Enqueue reliable remote upload
        _queue_for_upload(scene_name, stamp, content, ext)

        # 4) Download (web) or write to disk (desktop)
        if not _trigger_web_download(fname, content, mime=mime):
            _write_native(fname, content)

        # reset for next scene
        _scene_events[:] = []

    # -------------------------
    # Persistent archive
    # -------------------------
    # Mirrors the scene log into persistent storage so we can export everything later.
    def _save_copy_for_export(scene, stamp, content, ext):
        if not hasattr(persistent, "logs"):
            persistent.logs = []
        # rolling cap
        if len(persistent.logs) >= _max_persistent_logs:
            persistent.logs = persistent.logs[-(_max_persistent_logs-1):]
        entry = {
            "scene": scene,
            "when": stamp,
            "session": SESSION_ID,
            "ext": ext,
            "hash": _sha256(content),
            "content": content,
        }
        persistent.logs.append(entry)
        renpy.save_persistent()

    # -------------------------
    # Store-and-forward upload
    # -------------------------
    # Adds the scene log to a retry queue that will be posted to the server when possible.
    def _queue_for_upload(scene, stamp, content, ext):
        if not hasattr(persistent, "unsent"):
            persistent.unsent = []
        if len(persistent.unsent) >= _max_queue:
            # keep last N (newest first); drop oldest to avoid unbounded growth
            persistent.unsent = persistent.unsent[-(_max_queue-1):]
        persistent.unsent.append({
            "scene": scene,
            "when": stamp,
            "session": SESSION_ID,
            "ext": ext,
            "hash": _sha256(content),
            "payload": content,
            "attempts": 0,
            "last_error": None,
        })
        renpy.save_persistent()

    # Tries to send everything in the upload queue; safe to call often.
    def flush_upload_queue():
        """
        Try to POST everything in persistent.unsent to your server.
        Safe to call often (e.g., at main menu, scene start, or after a successful upload).
        """
        if not hasattr(persistent, "unsent") or not persistent.unsent:
            return 0

        # Work on a copy so we can modify the list while iterating
        remaining = []
        sent_count = 0

        for item in persistent.unsent:
            ok = _post_queue_item(item)
            if ok:
                sent_count += 1
            else:
                # backoff: keep if attempts < 8 (~max ~2.5 min if called per second; adjust to your cadence)
                item["attempts"] = (item.get("attempts") or 0) + 1
                remaining.append(item)

        persistent.unsent = remaining
        renpy.save_persistent()
        return sent_count

    # Helper that performs a single HTTP POST and notes whether it succeeded.
    def _post_queue_item(item):
        """
        POST the log to your server; expects HTTP 2xx to count as success.
        The server should de-duplicate via the 'hash' or (session, when) tuple.
        """
        try:
            # renpy.fetch is cross-platform; on Web it maps to JS fetch.
            # You can add headers like auth tokens here.
            body = json.dumps({
                "scene": item["scene"],
                "when": item["when"],
                "session": item["session"],
                "ext": item["ext"],
                "hash": item["hash"],
                "payload": item["payload"],
                "game_version": config.version,
                "platform": renpy.platform,
            }, ensure_ascii=False)

            r = renpy.fetch(_upload_endpoint, method="POST",
                            data=body.encode("utf-8"),
                            headers=[("Content-Type", "application/json")],
                            timeout=10.0)
            # r.status exists on all platforms
            if 200 <= r.status < 300:
                return True
            else:
                item["last_error"] = f"HTTP {r.status}"
                return False
        except Exception as e:
            item["last_error"] = repr(e)
            return False

    # Optional convenience: call this on common transitions
    # Fire-and-forget version of flush_upload_queue; safe to call behind the scenes.
    def background_flush_uploads():
        """
        Fire-and-forget queue flush. Cheap to call from labels or screens.
        """
        try:
            flush_upload_queue()
        except Exception:
            pass

    # -------------------------
    # Bulk export (ZIP)
    # -------------------------
    # Creates a ZIP file of every stored scene log so a player can take everything with them.
    def export_all_logs_zip():
        """
        Zips everything in persistent.logs and triggers a download (Web) or writes to disk (desktop).
        """
        if not hasattr(persistent, "logs") or not persistent.logs:
            renpy.notify("No logs to export.")
            return

        stamp = _now_stamp()
        zip_name = f"all_logs_{stamp}_sid{SESSION_ID}.zip"
        tmp_path = os.path.join(renpy.config.savedir, zip_name)

        # Write a temp zip
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            # Manifest file for easy indexing
            manifest = []
            for idx, e in enumerate(persistent.logs, start=1):
                fname = f"{idx:04d}_{e['when']}_{e['scene']}_sid{e['session']}.{e['ext']}"
                z.writestr(fname, e["content"])
                manifest.append({
                    "file": fname,
                    "scene": e["scene"],
                    "when": e["when"],
                    "session": e["session"],
                    "ext": e["ext"],
                    "hash": e["hash"]
                })
            z.writestr("manifest.json", json.dumps(manifest, indent=2))

        # Read back & trigger download (so it works on Web too)
        with open(tmp_path, "rb") as f:
            data = f.read()

        if renpy.emscripten:
            import base64
            b64 = base64.b64encode(data).decode("ascii")
            import emscripten
            js = f"""
            (function(){{
                var b64 = "{b64}";
                var bin = atob(b64);
                var len = bin.length;
                var bytes = new Uint8Array(len);
                for (var i=0; i<len; i++) bytes[i] = bin.charCodeAt(i);
                var blob = new Blob([bytes], {{type: "application/zip"}});
                var a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = "{zip_name}";
                document.body.appendChild(a);
                a.click();
                setTimeout(function() {{ URL.revokeObjectURL(a.href); a.remove(); }}, 0);
            }})();
            """
            emscripten.run_script(js)
        else:
            renpy.notify(f"Exported zip: {tmp_path}")

    # -------------------------
    # Example hooks (call where it makes sense)
    # -------------------------
    # At game start or main menu, try flushing anything pending.
    config.start_callbacks.append(lambda: background_flush_uploads())


init python:
    # Quick helper that writes a timestamp and message to Ren'Py's developer log.
    def log(action):
        timestamp = datetime.datetime.now()
        renpy.log(timestamp)
        renpy.log(action + "\n")
    # Sends an immediate status update to the /player-log endpoint; falls back to Ren'Py log on failure.
    def log_http(user: str, payload: Optional[Dict[str, Any]], action: str, view: str = None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.getenv("SERVICE_URL") is None:
            base_url = ""
        else:
            base_url = os.getenv("SERVICE_URL")
            
        log_entry = {
            "action": action,
            "timestamp": timestamp,
            "user": user,
            "view": view,
            "payload": payload
        }
        body = json.dumps(log_entry, ensure_ascii=False).encode("utf-8")
        try:
            renpy.fetch(
                f"{base_url}/player-log",
                method="POST",
                data=body,
                headers=[("Content-Type", "application/json")],
                timeout=10.0,
            )
        except Exception as e:
            renpy.log(timestamp)
            renpy.log(f"{action}\n")
            renpy.log(f"{payload}\n")
            renpy.log(repr(e))
    # Ren'Py callback that keeps track of the current label and logs story jumps.
    def label_callback(label, interaction):
        if not label.startswith("_"):
            log_http(current_user, action=f"PlayerJumpedLabel({label}|{interaction})", view=label, payload=None)
            global current_label
            current_label = label

    # Ensures certain data sticks around after loading a save; call once where needed.
    def retaindata():
        renpy.retain_after_load()
