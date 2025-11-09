default last_spoken_character = None
default last_player_choice = None

init python:
    import json, csv, io, time, hashlib, os, zipfile, random
    from math import pow
    import datetime
    from typing import Dict, Any, Optional
    from functools import partial
    import contextlib
    import os
    import pygame.scrap

    # -------------------------
    # Session & buffers
    # -------------------------
    SESSION_ID = random.randint(10**8, 10**9 - 1)

    _scene_events = []                 # in-memory for the current scene
    _upload_endpoint = "https://example.com/ingest"  # <- change me
    _max_persistent_logs = 500         # rolling cap
    _max_queue = 1000                  # safety cap on unsent queue
    _dialogue_origin_stack = [{"source": "script", "details": None}]
    _active_choice_log = None

    def _current_dialogue_origin():
        top = _dialogue_origin_stack[-1]
        return {"source": top.get("source"), "details": top.get("details")}

    def start_generated_dialogue(kind="eca", metadata=None):
        """Mark subsequent dialogue lines as being generated (e.g., ECA)."""
        payload = {"source": kind or "generated", "details": metadata or {}}
        _dialogue_origin_stack.append(payload)

    def finish_generated_dialogue():
        """Pop the last generated dialogue marker."""
        if len(_dialogue_origin_stack) > 1:
            _dialogue_origin_stack.pop()

    @contextlib.contextmanager
    def dialogue_origin(kind="script", metadata=None):
        start_generated_dialogue(kind, metadata)
        try:
            yield
        finally:
            finish_generated_dialogue()

    def remember_menu_choice(caption):
        """Called from the choice screen when a button is clicked."""
        global _active_choice_log
        _active_choice_log = {
            "text": caption,
            "timestamp": time.time(),
            "delivery": "menu",
            "is_question": False,
            "question_target": None,
            "auto_generated": False,
        }

    def _choice_payload(extra=None):
        if not _active_choice_log:
            return None
        payload = dict(_active_choice_log)
        payload["origin"] = _current_dialogue_origin()
        if extra:
            payload.update(extra)
        return payload

    def log_player_choice(extra=None):
        """Send the buffered choice info to the logging endpoint."""
        global last_player_choice
        payload = _choice_payload(extra=extra)
        if not payload:
            return
        log_http(
            current_user,
            action="PlayerDialogueChoice",
            view=current_label,
            payload=payload,
        )
        last_player_choice = payload
        clear_pending_choice()

    def clear_pending_choice():
        global _active_choice_log
        _active_choice_log = None

    def mark_choice_as_question(target):
        global _active_choice_log
        if _active_choice_log:
            _active_choice_log["is_question"] = True
            _active_choice_log["question_target"] = target

    def annotate_choice(**kwargs):
        global _active_choice_log
        if not _active_choice_log:
            return
        _active_choice_log.update({k: v for k, v in kwargs.items() if v is not None})

    def active_choice_caption(fallback=True):
        if _active_choice_log and _active_choice_log.get("text"):
            return _active_choice_log["text"]
        if fallback and last_player_choice:
            return last_player_choice.get("text")
        return None

    def log_player_input(text, prompt="", screen=None, input_type="manual", is_question=False, metadata=None):
        entry = {
            "text": text,
            "prompt": prompt,
            "screen": screen,
            "delivery": input_type,
            "is_question": bool(is_question),
            "metadata": metadata or {},
        }
        log_http(
            current_user,
            action="PlayerDialogueInput",
            view=current_label,
            payload=entry,
        )

    def log_player_script_line(text, source="scripted", metadata=None):
        payload = {
            "text": text,
            "delivery": source,
            "metadata": metadata or {},
        }
        log_http(
            current_user,
            action="PlayerDialogueLine",
            view=current_label,
            payload=payload,
        )

    def character_dialogue_callback(event, interact=True, metadata=None, **kwargs):
        if event != "show" or not metadata:
            return
        text = kwargs.get("what") or ""
        start = kwargs.get("start", 0)
        end = kwargs.get("end", len(text))
        snippet = text[start:end].strip()
        if not snippet:
            return
        origin = _current_dialogue_origin()
        payload = {
            "speaker_id": metadata.get("id"),
            "speaker_name": metadata.get("name"),
            "text": snippet,
            "role": metadata.get("role", "npc"),
            "content_source": origin.get("source"),
            "content_metadata": origin.get("details"),
            "segment_start": start,
            "segment_end": end,
        }
        action = "NPCDialogueLine" if payload["role"] != "player" else "PlayerDialogueLine"
        log_http(
            current_user,
            action=action,
            view=current_label,
            payload=payload,
        )
        global last_spoken_character
        last_spoken_character = payload["speaker_id"]

    def attach_character_callbacks():
        """Bind dialogue callbacks to every character in the directory."""
        import renpy
        directory = list(getattr(renpy.store, "character_directory", []))
        for entry in directory:
            char = entry.get("variable")
            if not char:
                continue
            metadata = {
                "id": entry.get("id") or entry.get("name"),
                "name": entry.get("name"),
                "role": entry.get("role", "npc"),
            }
            char.callback = partial(character_dialogue_callback, metadata=metadata)

    # -------------------------
    # Utilities
    # -------------------------
    def _now_stamp():
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

    def _sha256(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _to_csv(events):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["t","kind","data"])
        writer.writeheader()
        for e in events:
            row = dict(e)
            row["data"] = json.dumps(row["data"], ensure_ascii=False)
            writer.writerow(row)
        return buf.getvalue()

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

    def _write_native(filename, text):
        path = os.path.join(config.savedir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        renpy.notify(f"Saved log to {path}")

    # -------------------------
    # Public logging API
    # -------------------------
    def log_event(kind, payload=None):
        _scene_events.append({
            "t": time.time(),
            "kind": kind,
            "data": payload or {}
        })

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
        _mirror_to_persistent(scene_name, stamp, content, ext)

        # 3) Enqueue reliable remote upload
        _enqueue_for_upload(scene_name, stamp, content, ext)

        # 4) Download (web) or write to disk (desktop)
        if not _trigger_web_download(fname, content, mime=mime):
            _write_native(fname, content)

        # reset for next scene
        _scene_events[:] = []

    # -------------------------
    # Persistent archive
    # -------------------------
    def _mirror_to_persistent(scene, stamp, content, ext):
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
    def _enqueue_for_upload(scene, stamp, content, ext):
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
            ok = _try_upload(item)
            if ok:
                sent_count += 1
            else:
                # backoff: keep if attempts < 8 (~max ~2.5 min if called per second; adjust to your cadence)
                item["attempts"] = (item.get("attempts") or 0) + 1
                remaining.append(item)

        persistent.unsent = remaining
        renpy.save_persistent()
        return sent_count

    def _try_upload(item):
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


init 10 python:
    try:
        attach_character_callbacks()
    except Exception:
        pass


init python:
    def log(action):
        timestamp = datetime.datetime.now()
        renpy.log(timestamp)
        renpy.log(action + "\n")
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
        try:
            renpy.fetch(
                f"{base_url}/player-log",
                method="POST",
                json=log_entry,
            )
        except Exception as e:
            renpy.log(timestamp)
            renpy.log(f"{action}\n")
            renpy.log(f"{payload}\n")
    def label_callback(label, interaction):
        if not label.startswith("_"):
            log_http(current_user, action=f"PlayerJumpedLabel({label}|{interaction})", view=label, payload=None)
            global current_label
            current_label = label

    def retaindata():
        renpy.retain_after_load()
