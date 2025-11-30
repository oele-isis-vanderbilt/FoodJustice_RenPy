init python:

    import renpy.store as store
    from renpy.display.core import EndInteraction

    _screen_response_cache = {}

    def cache_screen_response(screen_name, text):
        """Remember the most recent text a modal input screen tried to return."""
        if not screen_name:
            return
        _screen_response_cache[screen_name] = text or ""

    def consume_screen_response(screen_name):
        """Retrieve and clear the cached response for a screen, if any."""
        if not screen_name:
            return ""
        return _screen_response_cache.pop(screen_name, "")

    def lock_dialogue_advancement(source=None):
        """
        Increment a shared counter so the say screen knows to ignore dismiss
        clicks while a modal UI is layered on top.
        """
        current = getattr(store, "overlay_dialogue_block_count", 0)
        store.overlay_dialogue_block_count = current + 1

    def unlock_dialogue_advancement(source=None):
        """Release a previously acquired dialogue lock."""
        current = getattr(store, "overlay_dialogue_block_count", 0)
        if current <= 0:
            store.overlay_dialogue_block_count = 0
            return
        store.overlay_dialogue_block_count = current - 1

    def dialogue_advancement_locked():
        """Return True while any popup has requested a dialogue lock."""
        return getattr(store, "overlay_dialogue_block_count", 0) > 0

    def _log_approval_change(char_name, delta, new_total, message, change_type):
        payload = {
            "character": char_name,
            "delta": delta,
            "new_total": new_total,
            "change_type": change_type,
            "choice": active_choice_caption(),
            "message": message,
        }
        log_http(
            current_user,
            action="CharacterApprovalChanged",
            view=current_label,
            payload=payload,
        )

    def _voice_features_active():
        return getattr(store, "voice_features_enabled", True)

    def set_voice_features_enabled(enabled):
        enabled = bool(enabled)
        store.voice_features_enabled = enabled
        if not enabled:
            store.voice_input_contexts = 0
            store.voice_input_available = False
            store.voice_recording_active = False
        renpy.notify("Voice features {}".format("enabled" if enabled else "disabled"))

    def toggle_voice_features_enabled():
        set_voice_features_enabled(not _voice_features_active())

    # --- character stats functions ---
    def _find_character_record(char_name):
        target = (char_name or "").strip().lower()
        if not target:
            return None
        for char in character_directory:
            name = (char.get("name") or "").strip().lower()
            if not name:
                continue
            if name == target or name.startswith(target):
                return char
        return None

    def _coerce_counter(value, default=0):
        """
        Normalize stored counters into ints so downstream code never compares
        strings against numbers.
        """
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return default
            try:
                return int(float(value))
            except ValueError:
                return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _sync_counter(record, key, fallback=0):
        value = _coerce_counter(record.get(key, fallback), fallback)
        if record.get(key) != value:
            record[key] = value
        return value

    def update_char_stats(char_name):
        record = _find_character_record(char_name)
        if record:
            chats = _sync_counter(record, "chats")
            record["chats"] = chats + 1
            record["spoken"] = True

    def get_character_spoken(char_name):
        record = _find_character_record(char_name)
        return bool(record and record.get("spoken"))

    def get_character_chats(char_name):
        record = _find_character_record(char_name)
        if not record:
            return 0

        return _sync_counter(record, "chats")

    def ask_character_question(char_name):
        record = _find_character_record(char_name)
        if record:
            questions = _sync_counter(record, "questions")
            record["questions"] = questions + 1
        mark_choice_as_question(char_name)

    def character_approval(char_name, amount, message=None):
        for char in character_directory:
            if char["name"] == char_name:
                char["approval"] = char.get("approval", 0) + amount
                annotate_choice(approval_delta=amount, approval_character=char_name)
                _log_approval_change(char_name, amount, char["approval"], message, "gain")
                if message:
                    renpy.notify(message)
                break

    def character_disapproval(char_name, amount, message=None):
        for char in character_directory:
            if char["name"] == char_name:
                char["approval"] = char.get("approval", 0) - amount
                annotate_choice(approval_delta=-amount, approval_character=char_name)
                _log_approval_change(char_name, -amount, char["approval"], message, "loss")
                if message:
                    renpy.notify(message)
                break

    def get_note_by_id(note_id):
        for note in notebook: 
            if note["id"] == note_id:
                return note

    def toggle_argument_share_screen():
        if renpy.get_screen("argument_sharing"):
            renpy.hide_screen("argument_sharing")
        else:
            renpy.show_screen("argument_sharing")

    def safe_renpy_input(prompt="", screen=None, **kwargs):
        """Collect player input via Ren'Py and always return a safe string."""

        def _do_call():
            if screen:
                return renpy.call_screen(screen, prompt=prompt, **kwargs)
            return renpy.input(prompt, **kwargs)

        try:
            if screen:
                cache_screen_response(screen, "")
            response = renpy.invoke_in_new_context(_do_call)
        except EndInteraction as exc:
            response = getattr(exc, "value", "")
        if response is None:
            return ""
        if isinstance(response, bytes):
            response = response.decode("utf-8", errors="ignore")
        if not isinstance(response, str):
            fallback = consume_screen_response(screen)
            if fallback:
                response = fallback
            else:
                return ""
        text = response
        if screen:
            consume_screen_response(screen)
        if text:
            is_question = "?" in (prompt or "")
            log_player_input(
                text,
                prompt=prompt,
                screen=screen,
                input_type="manual",
                is_question=is_question,
                metadata={"source": "safe_renpy_input", "stripped": text.strip()},
            )
        return text

    def argument_sharing(prompt=""):
        """
        Backwards-compatible helper so legacy script calls to argument_sharing(...)
        still invoke the modern safe input workflow.
        """
        return safe_renpy_input(prompt, screen="argument_sharing")



    def toggle_argument_edit_screen():
        if renpy.get_screen("argument_edit"):
            renpy.hide_screen("argument_edit")
        else:
            renpy.show_screen("argument_edit")


    def toggle_map_popup():
        if renpy.get_screen("map_popup"):
            renpy.hide_screen("map_popup")
        else:
            renpy.show_screen("map_popup")

    # def toggle_question_input():
    #     if renpy.get_screen("dialog_bubble_input"):
    #         renpy.hide_screen("dialog_bubble_input")
    #     else:
    #         renpy.show_screen("dialog_bubble_input")

    def toggle_achievements_screen():
        if renpy.get_screen("achievements_screen"):
            renpy.hide_screen("achievements_screen")
        else:
            renpy.show_screen("achievements_screen")

    def toggle_notebook():
        if renpy.get_screen("notebook"):
            renpy.hide_screen("notebook")
        else:
            renpy.show_screen("notebook")

    # def toggle_voice_recording():
    #     if not _voice_features_active():
    #         renpy.notify("Voice features disabled")
    #         return
    #     global voice_recording_active
    #     voice_recording_active = not voice_recording_active
    #     status = "started" if voice_recording_active else "stopped"
    #     renpy.notify("Voice recording {}".format(status))

    # def request_voice_input():
    #     # Keep track of active contexts requesting speech-to-text.
    #     if not _voice_features_active():
    #         store.voice_input_contexts = 0
    #         store.voice_input_available = False
    #         return False
    #     store.voice_input_contexts = getattr(store, "voice_input_contexts", 0) + 1
    #     store.voice_input_available = store.voice_input_contexts > 0
    #     return True

    # def release_voice_input():
    #     # Release a context, clamping at zero so we never underflow.
    #     if not _voice_features_active():
    #         store.voice_input_contexts = 0
    #         store.voice_input_available = False
    #         return False
    #     current = getattr(store, "voice_input_contexts", 0)
    #     store.voice_input_contexts = max(0, current - 1)
    #     store.voice_input_available = store.voice_input_contexts > 0
    #     return True

    from renpy.display.transform import Transform
    from renpy.display.matrix import Matrix

    def darken_hover(d, amount=0.40):
        f = max(0.0, 1.0 - float(amount))
        mat = Matrix([f,0,0,0, 0,f,0,0, 0,0,f,0, 0,0,0,1.0])
        return Transform(d, matrixcolor=mat)

    def brighten_hover(d, amount=0.40):
        f = 1.0 + float(amount)
        mat = Matrix([f,0,0,0, 0,f,0,0, 0,0,f,0, 0,0,0,1.0])
        return Transform(d, matrixcolor=mat)

    def grow_hover(d, amount=0.20):
        return Transform(d, zoom=1.0 + float(amount))

    def shrink_hover(d, amount=0.20):
        return Transform(d, zoom=max(0.01, 1.0 - float(amount)))
