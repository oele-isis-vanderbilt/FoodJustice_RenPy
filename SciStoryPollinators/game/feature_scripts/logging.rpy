# This file keeps track of everything the player does (dialogue, clicks,
# uploads) so we can review the session later or send it to a server.
# The goal is to make the flow understandable even if you are not familiar
# with Ren'Py or networking code.

default last_spoken_character = None   # remembers who spoke last on screen
default last_player_choice = None      # remembers the most recent menu choice

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
    _last_label_event_key = None
    _default_feedback_contexts = {
        "FoodJustice_RileyEvaluation",
        "FoodJustice_MayorEvaluation",
    }

    # Return the latest dialogue origin by peeking the stack so reports know which system produced a line.
    def _current_dialogue_origin():
        top = _dialogue_origin_stack[-1]
        return {"source": top.get("source"), "details": top.get("details")}

    # Helper for other systems to detect when dialogue is AI feedback on player arguments.
    def is_argument_feedback_dialogue():
        origin = _current_dialogue_origin()
        if origin.get("source") != "eca":
            return False
        details = origin.get("details")
        context = None
        if isinstance(details, dict):
            context = details.get("context")
        configured = getattr(renpy.store, "argument_feedback_contexts", None)
        if configured is None:
            configured = _default_feedback_contexts
        try:
            contexts = set(configured)
        except TypeError:
            contexts = set(_default_feedback_contexts)
        return context in contexts

    # Push a new origin entry so upcoming lines are tagged as generated content for later analytics.
    def start_generated_dialogue(kind="eca", metadata=None):
        payload = {"source": kind or "generated", "details": metadata or {}}
        _dialogue_origin_stack.append(payload)

    # Pop the origin stack when generated dialogue ends so script lines resume normal tagging.
    def finish_generated_dialogue():
        if len(_dialogue_origin_stack) > 1:
            _dialogue_origin_stack.pop()

    # Context manager that wraps a section with start/finish logic so custom origins auto-clean when the block exits.
    @contextlib.contextmanager
    def dialogue_origin(kind="script", metadata=None):
        start_generated_dialogue(kind, metadata)
        try:
            yield
        finally:
            finish_generated_dialogue()

    # Cache the clicked menu option, storing timestamp and flags so we can ship a complete record once the choice resolves.
    def remember_menu_choice(caption):
        global _active_choice_log
        _active_choice_log = {
            "text": caption,
            "timestamp": time.time(),
            "delivery": "menu",
            "is_question": False,
            "question_target": None,
            "auto_generated": False,
        }

    # Clone the pending choice dict, merge in any overrides, and attach origin info so uploads are consistent.
    def _choice_payload(extra=None):
        if not _active_choice_log:
            return None
        payload = dict(_active_choice_log)
        payload["origin"] = _current_dialogue_origin()
        if extra:
            payload.update(extra)
        return payload

    # POST the prepared choice payload via log_http so downstream dashboards know what the player selected and when.
    def log_player_choice(extra=None):
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
        translator = getattr(renpy.store, "__", None) or getattr(renpy.store, "_", None)
        if callable(translator):
            history_who = translator("Choice:")
            history_what = translator(payload.get("text") or "")
        else:
            history_who = "Choice:"
            history_what = payload.get("text") or ""
        record_history_entry(history_who, history_what, kind="adv")
        last_player_choice = payload
        clear_pending_choice()

    # Drop the cached choice so the next click starts fresh and duplicate rows are avoided.
    def clear_pending_choice():
        global _active_choice_log
        _active_choice_log = None

    # Mark the pending choice as a question and log the addressee so transcripts can describe conversational intent.
    def mark_choice_as_question(target):
        global _active_choice_log
        if _active_choice_log:
            _active_choice_log["is_question"] = True
            _active_choice_log["question_target"] = target

    # Update the pending choice with ad-hoc metadata (tone, branch tags, etc.) so later analysis has richer context.
    def annotate_choice(**kwargs):
        global _active_choice_log
        if not _active_choice_log:
            return
        _active_choice_log.update({k: v for k, v in kwargs.items() if v is not None})

    # Return the text of the current or previous choice so UI or narration can reference what was asked and why.
    def active_choice_caption(fallback=True):
        if _active_choice_log and _active_choice_log.get("text"):
            return _active_choice_log["text"]
        if fallback and last_player_choice:
            return last_player_choice.get("text")
        return None

    # Capture what the player typed, record the prompt/screen used, and send it upstream so custom responses are auditable.
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

    # Record lines auto-delivered by the protagonist by packaging the text plus metadata and forwarding via log_http.
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

    # Helper so gameplay code can update the history log without touching narrator directly.
    def record_history_entry(who=None, what="", kind="adv"):
        narrator_character = getattr(renpy.store, "narrator", None)
        if not narrator_character or not hasattr(narrator_character, "add_history"):
            return
        try:
            narrator_character.add_history(kind=kind, who=who, what=what or "")
        except Exception:
            pass

    def log_with_history(action=None, payload=None, view=None, history_who=None, history_what=None, history_kind="adv"):
        """
        Unified entry point so callers can log remotely and update the in-game history
        with a single function call.
        """
        if history_who is not None or history_what:
            record_history_entry(history_who, history_what, kind=history_kind)
        if action:
            log_http(
                current_user,
                action=action,
                view=view if view is not None else current_label,
                payload=payload,
            )

    def notify_with_history(message, history_who="Notification", history_what=None):
        renpy.notify(message)
        record_history_entry(history_who, history_what or message, kind="adv")

    _LOCATION_DISPLAY = {
        "emptylot": "Empty Lot",
        "foodlab": "Food Lab",
        "garden": "Garden",
        "beehives": "Beehives",
        "town": "Town",
    }

    def _location_name(label):
        if not label:
            return ""
        friendly = _LOCATION_DISPLAY.get(label)
        if friendly:
            return friendly
        return str(label).replace("_", " ").title()

    def set_current_location(location, source=None, description=None):
        renpy.store.currentlocation = location
        pretty = description or _location_name(location)
        history_line = f"You traveled to {pretty}" if pretty else "You traveled."
        log_with_history(
            action="LocationChanged",
            payload={"location": location, "source": source, "description": pretty},
            history_who="Travel",
            history_what=history_line,
        )

    # Listen for Ren'Py's dialogue events, slice the shown text, and log who spoke so conversation history stays complete.
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

    # Iterate over the character directory, wiring our callback to each one so speech logging happens automatically.
    def attach_character_callbacks():
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
    # Build a sortable YYYYMMDD-HHMMSS stamp using local time so filenames are readable and chronological.
    def _now_stamp():
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

    # Hash any text via SHA-256 so uploads and archives can detect duplicates cheaply.
    def _sha256(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Write the scene event list into CSV format by iterating rows so educators can open the file in spreadsheets.
    def _to_csv(events):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["t","kind","data"])
        writer.writeheader()
        for e in events:
            row = dict(e)
            row["data"] = json.dumps(row["data"], ensure_ascii=False)
            writer.writerow(row)
        return buf.getvalue()

    # When on Web builds, inject JS that streams the data into a Blob so the browser prompts a download without server help.
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

    # Write the log file under config.savedir so desktop players can find it even without a browser download step.
    def _write_native(filename, text):
        path = os.path.join(config.savedir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        notify_with_history(f"Saved log to {path}", history_who="System", history_what=f"Saved log to {path}")

    # Export Ren'Py's configured game log file so players can download the live runtime log locally.
    def download_gamelog_file():
        log_name = "gamelog.txt"
        preferred_path = os.path.abspath(os.path.join(config.gamedir, "..", log_name))
        fallback_path = os.path.abspath(os.path.join(config.savedir, log_name))
        log_path = preferred_path if os.path.exists(preferred_path) else None

        if log_path is None and os.path.exists(fallback_path):
            log_path = fallback_path

        if not log_path:
            notify_with_history(f"Could not find {log_name}.", history_who="System")
            return

        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        first_line = ""
        if content:
            first_line = content.splitlines()[0][:80]
        notify_with_history(
            "Game log source: {} | Preview: {}".format(log_path, first_line or "<empty>"),
            history_who="System",
        )

        filename = f"{os.path.splitext(log_name)[0]}_{_now_stamp()}.txt"
        if not _trigger_web_download(filename, content, mime="text/plain"):
            _write_native(filename, content)

    # -------------------------
    # Public logging API
    # -------------------------
    # Append an event dict (type plus payload) into the scene buffer so later exports capture everything that happened.
    def log_event(kind, payload=None):
        _scene_events.append({
            "t": time.time(),
            "kind": kind,
            "data": payload or {}
        })

    # Wrap up a scene by serializing buffered events, mirroring them locally, queuing an upload,
    # and delivering a file to the player so no data is lost between story beats.
    def download_scene_log(scene_name, as_csv=True):
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
    # Store the log in persistent data (with a size cap) so future sessions or admin tools can reopen past scenes.
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
    # Push an upload job (content plus hash) into persistent.unsent so the game can retry when connectivity returns.
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

    # Iterate over the unsent queue, call _try_upload for each entry, and prune successes so the backlog stays manageable.
    def flush_upload_queue():
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

    # Perform the cross-platform HTTP POST via renpy.fetch, count 2xx responses as success,
    # and record errors so operators know why an item keeps retrying.
    def _try_upload(item):
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
    # Call flush_upload_queue() inside a blanket try/except so story transitions can trigger uploads without scaring players.
    def background_flush_uploads():
        try:
            flush_upload_queue()
        except Exception:
            pass

    # -------------------------
    # Bulk export (ZIP)
    # -------------------------
    # Bundle every persistent log into a ZIP (plus manifest) so facilitators can pull full transcripts via one download.
    def export_all_logs_zip():
        if not hasattr(persistent, "logs") or not persistent.logs:
            notify_with_history("No logs to export.", history_who="System")
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
            notify_with_history(f"Exported zip: {tmp_path}", history_who="System")

    # -------------------------
    # Example hooks (call where it makes sense)
    # -------------------------
    # At game start or main menu, try flushing anything pending.
    config.start_callbacks.append(lambda: background_flush_uploads())
    # ^ keeps the upload queue from growing if the player pauses on the title screen.


init 10 python:
    try:
        attach_character_callbacks()
    except Exception:
        pass


init python:
    def _safe_log_value(value):
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return {str(k): _safe_log_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [_safe_log_value(v) for v in value]
        return repr(value)

    def _default_user():
        return getattr(renpy.store, "current_user", "unknown")

    def _default_view():
        return getattr(renpy.store, "current_label", None)

    def _is_local_web_runtime():
        if not renpy.emscripten:
            return False
        try:
            import emscripten
            host = (emscripten.run_script_string("window.location.hostname || ''") or "").strip().lower()
            protocol = (emscripten.run_script_string("window.location.protocol || ''") or "").strip().lower()
            return protocol == "file:" or host in {"", "localhost", "127.0.0.1"}
        except Exception:
            return False

    def _normalize_timestamp(ts):
        if isinstance(ts, datetime.datetime):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
        if ts:
            return str(ts)
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _build_log_entry(action, payload=None, user=None, view=None, timestamp=None):
        return {
            "action": action,
            "user": user if user is not None else _default_user(),
            "view": view if view is not None else _default_view(),
            "timestamp": _normalize_timestamp(timestamp),
            "payload": payload,
        }

    def _sanitize_log_entry(entry):
        return {
            "action": _safe_log_value(entry.get("action")),
            "timestamp": _safe_log_value(entry.get("timestamp")),
            "user": _safe_log_value(entry.get("user")),
            "view": _safe_log_value(entry.get("view")),
            "payload": _safe_log_value(entry.get("payload")),
        }

    def _log_locally(log_entry):
        renpy.log(json.dumps(_sanitize_log_entry(log_entry), ensure_ascii=False))

    # Write a timestamped string to Ren'Py's developer log so we always mirror important actions locally.
    def log(action):
        log_entry = _build_log_entry(action, payload=None, timestamp=datetime.datetime.now())
        _log_locally(log_entry)

    # Standardized UI interaction logger for button presses and screen open/close events.
    def log_ui_event(event, screen=None, element=None, detail=None, payload=None):
        data = {"event": event}
        if screen is not None:
            data["screen"] = screen
        if element is not None:
            data["element"] = element
        if detail is not None:
            data["detail"] = detail
        if payload is not None:
            data["payload"] = payload

        log_http(
            _default_user(),
            action="UIEvent",
            view=screen if screen is not None else _default_view(),
            payload=data,
        )

    # Construct the REST payload, POST it via renpy.fetch, and still fall back to renpy.log so every action is recorded.
    def log_http(user: str, payload: Optional[Dict[str, Any]], action: str, view: str = None):
        timestamp = datetime.datetime.now()
        base_url = (os.getenv("SERVICE_URL") or "").strip()
        if base_url == "/":
            base_url = ""
        log_entry = _build_log_entry(action, payload=payload, user=user, view=view, timestamp=timestamp)
        safe_entry = _sanitize_log_entry(log_entry)

        _log_locally(safe_entry)

        if base_url:
            endpoint = f"{base_url.rstrip('/')}/player-log"
        elif renpy.emscripten:
            if _is_local_web_runtime():
                return
            endpoint = "/player-log"
        else:
            return

        if renpy.emscripten:
            try:
                import emscripten
                js_payload = json.dumps(safe_entry, ensure_ascii=False)
                emscripten.run_script(f"""
                    try {{
                        fetch('{endpoint}', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({js_payload})
                        }}).catch(function(){{}});
                    }} catch(e) {{}}
                """)
            except Exception:
                pass
            return

        try:
            renpy.fetch(
                endpoint,
                method="POST",
                json=safe_entry,
                timeout=1.0,
            )
        except Exception:
            pass


    # Send friendly notebook activity strings alongside structured logs so facilitators can follow along.
    def log_notebook_event(message, extra=None):
        payload = {"message": message}
        if extra:
            payload.update({k: v for k, v in extra.items() if v is not None})
        log_http(current_user, action="NotebookEvent", view=current_label, payload=payload)

    # Record when the player opens the notebook UI.
    def log_notebook_opened():
        log_notebook_event("Player opened the notebook")

    # Record when the player closes the notebook UI.
    def log_notebook_closed():
        log_notebook_event("Player closed the notebook")
    # Log every label jump (ignoring private _ labels) by reporting it through log_http so analysts know what screen the player is on.
    def label_callback(label, interaction):
        global current_label, _last_label_event_key
        if label.startswith("_"):
            return
        current_label = label

        key = (label, bool(interaction))
        if _last_label_event_key == key:
            return
        _last_label_event_key = key

        log_http(
            current_user,
            action=f"PlayerJumpedLabel({label}|{interaction})",
            view=label,
            payload=None,
        )

    # Call renpy.retain_after_load() so our session buffers survive save/load cycles and we don't lose pending logs.
    def retaindata():
        renpy.retain_after_load()
