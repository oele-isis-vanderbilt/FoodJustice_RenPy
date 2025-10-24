init python:
    # ------------------------------------------------------------------
    # SyncFlow logging adapter.
    #
    # Two complementary channels:
    #   1. Scene logs: buffered during play, mirrored locally, uploaded
    #      with retries, and exportable as ZIPs.
    #   2. Immediate events: sent to the backend right away with short,
    #      exponential retries before falling back to a background queue.
    #
    # All network requests include the bearer token defined by
    # GAME_CLIENT_KEY. When connectivity is poor, data is retained in
    # Ren'Py's persistent storage until uploads succeed or a backup ZIP
    # is pushed to the dedicated endpoint.
    # ------------------------------------------------------------------
    import base64
    import csv
    import datetime
    import hashlib
    import io
    import json
    import os
    import time
    import zipfile
    from typing import Any, Dict, Optional

    # -------------------------
    # Session & configuration
    # -------------------------
    SESSION_ID = renpy.random.randint(10**8, 10**9 - 1)

    _log_base_url = os.getenv("LOG_BASE_URL", "https://foodjustice.syncflow.live")
    _scene_path = os.getenv("LOG_SCENE_PATH", "/api/logs/scene")
    _event_path = os.getenv("LOG_EVENT_PATH", "/api/logs/event")
    _backup_path = os.getenv("LOG_BACKUP_PATH", "/api/logs/backup")
    _client_token = os.getenv("GAME_CLIENT_KEY", "")

    _scene_events = []
    _scene_started_at = None
    _scene_metrics = {}

    _max_persistent_logs = 500
    _max_scene_queue = 1000
    _max_event_queue = 2000

    _scene_retry_interval = 300.0  # 5 minutes
    _scene_retry_window = 3600.0   # escalate after 1 hour
    _event_retry_interval = 60.0   # once steady-state, try once per minute

    _last_scene_flush = 0.0
    _last_event_flush = 0.0

    _logging_context = {
        "session_id": str(SESSION_ID),
        "student_id": None,
        "classroom_id": None,
    }

    # -------------------------
    # Utilities
    # -------------------------
    def _now_stamp():
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

    def _iso_now():
        return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    def _sha256(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _to_csv(events):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["timestamp", "event_type", "view", "payload"])
        writer.writeheader()
        for e in events:
            row = {
                "timestamp": e.get("timestamp"),
                "event_type": e.get("event_type"),
                "view": e.get("view"),
                "payload": json.dumps(e.get("payload") or {}, ensure_ascii=False),
            }
            writer.writerow(row)
        return buf.getvalue()

    def _trigger_web_download(filename, text, mime="text/plain"):
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

    def _current_context():
        ctx = dict(_logging_context)
        if not ctx.get("session_id"):
            ctx["session_id"] = str(SESSION_ID)
        return ctx

    # -------------------------
    # Public logging API
    # -------------------------
    def configure_logging_context(student_id=None, classroom_id=None, session_id=None):
        """
        Call once the player identity is known so every log carries it.
        """
        if student_id:
            _logging_context["student_id"] = str(student_id)
        if classroom_id:
            _logging_context["classroom_id"] = str(classroom_id)
        if session_id:
            _logging_context["session_id"] = str(session_id)

    def log_event(event_type, payload=None, view=None, metrics=None):
        """
        Use inside scenes to accumulate events for later upload/export.
        """
        global _scene_started_at
        ctx = _current_context()
        if _scene_started_at is None:
            _scene_started_at = time.time()
        event = {
            "session_id": ctx["session_id"],
            "student_id": ctx["student_id"],
            "classroom_id": ctx["classroom_id"],
            "timestamp": _iso_now(),
            "event_type": event_type,
            "view": view,
            "payload": payload or {},
        }
        _scene_events.append(event)
        _scene_metrics["events_recorded"] = _scene_metrics.get("events_recorded", 0) + 1
        if metrics:
            for key, value in metrics.items():
                _scene_metrics[key] = _scene_metrics.get(key, 0) + value

    def download_scene_log(scene_name, as_csv=False):
        """
        Call at the end of a scene to save, archive, and upload buffered events.
        """
        global _scene_started_at
        if not _scene_events:
            return

        ctx = _current_context()
        start_iso = None
        if _scene_started_at:
            start_iso = datetime.datetime.utcfromtimestamp(_scene_started_at).replace(microsecond=0).isoformat() + "Z"
        end_iso = _iso_now()
        stamp = _now_stamp()

        scene_payload = {
            "session_id": ctx["session_id"],
            "student_id": ctx["student_id"],
            "classroom_id": ctx["classroom_id"],
            "game_version": getattr(config, "version", "unknown"),
            "scene_name": scene_name,
            "start_time": start_iso,
            "end_time": end_iso,
            "events": list(_scene_events),
            "metrics": dict(_scene_metrics),
        }

        content = json.dumps(scene_payload, ensure_ascii=False, indent=2)
        fname_json = f"log_{scene_name}_{stamp}_sid{ctx['session_id']}.json"

        # 2) Mirror into persistent rolling archive
        _save_copy_for_export(scene_name, stamp, content, "json")

        # 3) Enqueue reliable remote upload
        _queue_scene_for_upload(scene_name, stamp, content)

        # 4) Provide local copy for teachers (optional CSV mirror)
        if as_csv:
            csv_content = _to_csv(_scene_events)
            fname_csv = fname_json.replace(".json", ".csv")
            if not _trigger_web_download(fname_csv, csv_content, mime="text/csv"):
                _write_native(fname_csv, csv_content)
        else:
            if not _trigger_web_download(fname_json, content, mime="application/json"):
                _write_native(fname_json, content)

        _scene_events[:] = []
        _scene_metrics.clear()
        _scene_started_at = None

    # -------------------------
    # Persistent archive (ZIP export)
    # -------------------------
    def _ensure_persistent_list(name):
        data = getattr(persistent, name, None)
        if not isinstance(data, list):
            data = []
            setattr(persistent, name, data)
        return data

    def _save_copy_for_export(scene, stamp, content, ext):
        logs = _ensure_persistent_list("logs")
        if len(logs) >= _max_persistent_logs:
            logs[:] = logs[-(_max_persistent_logs - 1):]
        entry = {
            "scene": scene,
            "when": stamp,
            "session": _current_context()["session_id"],
            "ext": ext,
            "hash": _sha256(content),
            "content": content,
        }
        logs.append(entry)
        renpy.save_persistent()

    def export_all_logs_zip():
        """
        Manual backup: write every stored log to a ZIP for download.
        """
        if not hasattr(persistent, "logs") or not persistent.logs:
            renpy.notify("No logs to export.")
            return

        stamp = _now_stamp()
        zip_name = f"all_logs_{stamp}_sid{_current_context()['session_id']}.zip"
        tmp_path = os.path.join(renpy.config.savedir, zip_name)

        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
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
                    "hash": e["hash"],
                })
            z.writestr("manifest.json", json.dumps(manifest, indent=2))

        with open(tmp_path, "rb") as f:
            data = f.read()

        if renpy.emscripten:
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
    # Scene upload queue
    # -------------------------
    def _queue_scene_for_upload(scene, stamp, content):
        scene_queue = _ensure_persistent_list("unsent")
        if len(scene_queue) >= _max_scene_queue:
            scene_queue[:] = scene_queue[-(_max_scene_queue - 1):]
        scene_queue.append({
            "scene": scene,
            "when": stamp,
            "session": _current_context()["session_id"],
            "hash": _sha256(content),
            "payload": content,
            "attempts": 0,
            "last_error": None,
            "first_failure": None,
            "next_attempt": 0.0,
        })
        renpy.save_persistent()

    def flush_scene_queue(force=False):
        scene_queue = _ensure_persistent_list("unsent")
        if not scene_queue:
            return 0

        remaining = []
        sent = 0
        now = time.time()
        for item in scene_queue:
            if not force and now < (item.get("next_attempt") or 0.0):
                remaining.append(item)
                continue

            if _post_scene_item(item):
                sent += 1
            else:
                item["attempts"] = (item.get("attempts") or 0) + 1
                if not item.get("first_failure"):
                    item["first_failure"] = now
                item["next_attempt"] = now + _scene_retry_interval
                remaining.append(item)
        scene_queue[:] = remaining
        renpy.save_persistent()
        return sent

    def _post_scene_item(item):
        try:
            url = f"{_log_base_url}{_scene_path}"
            headers = [("Content-Type", "application/json")]
            if _client_token:
                headers.append(("Authorization", f"Bearer {_client_token}"))
            response = renpy.fetch(
                url,
                method="POST",
                data=item["payload"].encode("utf-8"),
                headers=headers,
                timeout=20.0,
            )
            success = 200 <= response.status < 300
            if not success:
                item["last_error"] = f"HTTP {response.status}"
            return success
        except Exception as e:
            item["last_error"] = repr(e)
            return False
        finally:
            _check_scene_for_backup(item)

    def _check_scene_for_backup(item):
        first_failure = item.get("first_failure")
        if not first_failure:
            return
        if time.time() - first_failure >= _scene_retry_window:
            try:
                if _upload_backup_zip("scene_retry_timeout"):
                    item["next_attempt"] = time.time() + _scene_retry_interval
            except Exception:
                pass

    # -------------------------
    # Event upload queue
    # -------------------------
    def _queue_event_for_retry(event_payload, initial_delay=1.0):
        event_queue = _ensure_persistent_list("event_unsent")
        if len(event_queue) >= _max_event_queue:
            event_queue[:] = event_queue[-(_max_event_queue - 1):]
        event_queue.append({
            "payload": event_payload,
            "attempts": 1,
            "backoff": 2.0,
            "next_attempt": time.time() + initial_delay,
            "last_error": None,
            "queued_at": time.time(),
        })
        renpy.save_persistent()

    def flush_event_queue(force=False):
        event_queue = _ensure_persistent_list("event_unsent")
        if not event_queue:
            return 0

        remaining = []
        sent = 0
        now = time.time()
        for item in event_queue:
            if not force and now < (item.get("next_attempt") or 0.0):
                remaining.append(item)
                continue

            if _post_event_payload(item["payload"]):
                sent += 1
            else:
                item["attempts"] = (item.get("attempts") or 0) + 1
                if item["attempts"] < 3:
                    delay = item.get("backoff", 2.0)
                    item["next_attempt"] = now + delay
                    item["backoff"] = min(delay * 2, 4.0)
                else:
                    item["next_attempt"] = now + _event_retry_interval
                    item["backoff"] = _event_retry_interval
                remaining.append(item)
        event_queue[:] = remaining
        renpy.save_persistent()
        return sent

    def _post_event_payload(payload):
        try:
            url = f"{_log_base_url}{_event_path}"
            headers = [("Content-Type", "application/json")]
            if _client_token:
                headers.append(("Authorization", f"Bearer {_client_token}"))
            response = renpy.fetch(
                url,
                method="POST",
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers=headers,
                timeout=10.0,
            )
            return 200 <= response.status < 300
        except Exception:
            return False

    # -------------------------
    # Backup ZIP uploader
    # -------------------------
    def _upload_backup_zip(reason="manual"):
        ctx = _current_context()
        scene_items = list(_ensure_persistent_list("unsent"))
        event_items = list(_ensure_persistent_list("event_unsent"))
        if not scene_items and not event_items:
            return False

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            manifest = {
                "reason": reason,
                "session_id": ctx["session_id"],
                "student_id": ctx["student_id"],
                "classroom_id": ctx["classroom_id"],
                "generated_at": _iso_now(),
                "scene_count": len(scene_items),
                "event_count": len(event_items),
            }
            z.writestr("manifest.json", json.dumps(manifest, indent=2))
            for idx, item in enumerate(scene_items, start=1):
                fname = f"scene_{idx:04d}_{item.get('scene','unknown')}.json"
                z.writestr(fname, item["payload"])
            if event_items:
                z.writestr("events.json", json.dumps([e["payload"] for e in event_items], indent=2))

        data = buf.getvalue()

        try:
            url = f"{_log_base_url}{_backup_path}"
            headers = [("Content-Type", "application/zip")]
            if _client_token:
                headers.append(("Authorization", f"Bearer {_client_token}"))
            response = renpy.fetch(
                url,
                method="POST",
                data=data,
                headers=headers,
                timeout=30.0,
            )
            return 200 <= response.status < 300
        except Exception:
            return False

    # -------------------------
    # Background flushing
    # -------------------------
    def background_flush_uploads():
        try:
            now = time.time()
            global _last_scene_flush, _last_event_flush
            if now - _last_scene_flush >= _scene_retry_interval:
                flush_scene_queue()
                _last_scene_flush = now
            if now - _last_event_flush >= _event_retry_interval:
                flush_event_queue()
                _last_event_flush = now
        except Exception:
            pass

    def sync_logs_now():
        scene_sent = flush_scene_queue(force=True)
        event_sent = flush_event_queue(force=True)
        if scene_sent or event_sent:
            renpy.notify("SyncFlow logs queued for upload.")
        else:
            if _upload_backup_zip("manual_sync"):
                renpy.notify("Backup ZIP uploaded to SyncFlow.")
            else:
                renpy.notify("No pending logs or upload still pending.")

    config.start_callbacks.append(lambda: background_flush_uploads())
    if not hasattr(config, "periodic_callbacks"):
        config.periodic_callbacks = []
    config.periodic_callbacks.append(lambda: background_flush_uploads())


init python:
    def log(action):
        timestamp = datetime.datetime.now()
        renpy.log(timestamp)
        renpy.log(action + "\n")

    def log_http(user: str, payload: Optional[Dict[str, Any]], action: str, view: str = None):
        """
        Immediate SyncFlow event logger. Tries once right now, then queues for retry.
        """
        ctx = _current_context()
        event_payload = {
            "session_id": ctx["session_id"],
            "student_id": ctx["student_id"] or (user if user else None),
            "classroom_id": ctx["classroom_id"],
            "timestamp": _iso_now(),
            "event_type": action,
            "view": view,
            "payload": payload or {},
        }

        if _post_event_payload(event_payload):
            flush_event_queue()
            return True

        _queue_event_for_retry(event_payload)
        renpy.log(f"[log_http buffered] {event_payload['timestamp']} | {action}")
        return False

    def label_callback(label, interaction):
        if not label.startswith("_"):
            log_http(current_user, action=f"PlayerJumpedLabel({label}|{interaction})", view=label, payload=None)
            global current_label
            current_label = label

    def retaindata():
        renpy.retain_after_load()
