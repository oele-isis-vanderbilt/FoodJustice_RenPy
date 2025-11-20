init python:
    import datetime
    from typing import Dict, Any, Optional
    import os
    import re
    import pygame.scrap
    from renpy import store
    _last_notebook_length_logged = None

    if not hasattr(store, "new_note_text_template"):
        store.new_note_text_template = "whats your evidence?"
    if not hasattr(store, "new_note_source_template"):
        store.new_note_source_template = "where did you learn this?"
    
    config.label_callbacks = [label_callback]
    NEW_NOTE_ID = -1

    def normalize_tags(tags_value):
        if isinstance(tags_value, str):
            return [t.strip() for t in tags_value.split(",") if t.strip()]
        try:
            iterable = list(tags_value) if tags_value is not None else []
        except TypeError:
            return []
        cleaned = []
        for tag in iterable:
            tag_text = str(tag).strip()
            if tag_text:
                cleaned.append(tag_text)
        return cleaned

    def auto_character_tags(content, existing_tags=None):
        """Derive notebook tags from character note content."""
        library = list(getattr(store, "tagLibrary", []))
        bucket_map = dict(getattr(store, "tagBuckets", {}))
        bucket_keys = set(bucket_map.keys())
        synonym_to_bucket = {}

        for bucket, keywords in bucket_map.items():
            if not isinstance(keywords, (list, tuple)):
                continue
            for keyword in keywords:
                keyword_text = str(keyword).strip()
                if not keyword_text:
                    continue
                synonym_to_bucket.setdefault(keyword_text.lower(), bucket)
            synonym_to_bucket.setdefault(str(bucket).strip().lower(), bucket)

        def add_tag(tag_list, seen_set, tag_value):
            tag_text = str(tag_value).strip()
            if not tag_text:
                return
            key = tag_text.lower()
            if key not in seen_set:
                tag_list.append(tag_text)
                seen_set.add(key)

        tags = []
        seen = set()

        existing_iterable = normalize_tags(existing_tags)
        for original_tag in existing_iterable:
            mapped_bucket = synonym_to_bucket.get(str(original_tag).strip().lower())
            if mapped_bucket:
                add_tag(tags, seen, mapped_bucket)
            else:
                add_tag(tags, seen, original_tag)

        if not isinstance(content, str):
            return tags

        text = re.sub(r"[\[\]]", " ", content)

        def matches(keyword):
            pattern = r"\b{}\b".format(re.escape(keyword))
            return re.search(pattern, text, flags=re.IGNORECASE)

        for bucket, keywords in bucket_map.items():
            if not isinstance(keywords, (list, tuple)):
                continue
            for keyword in keywords:
                keyword_text = str(keyword).strip()
                if keyword_text and matches(keyword_text):
                    add_tag(tags, seen, bucket)
                    break

        for tag_name in library:
            if tag_name in bucket_keys:
                continue
            if matches(tag_name):
                add_tag(tags, seen, tag_name)

        return tags

    def refresh_character_note_tags():
        """Ensure all character notes reflect current tag matches."""
        global notebook
        for note in notebook:
            if note.get("type") == "character-dialog":
                current_tags = normalize_tags(note.get("tags", []))
                note["tags"] = auto_character_tags(note.get("content", ""), current_tags)

    def toggle_auto_tag_user_notes():
        current = getattr(store, "auto_tag_user_notes", True)
        new_value = not current
        store.auto_tag_user_notes = new_value
        renpy.notify("Auto-tag user notes: {}".format("On" if new_value else "Off"))

    def log_notebook_length(length):
        """Only log notebook length when it actually changes."""
        global _last_notebook_length_logged
        length = int(length)
        if _last_notebook_length_logged == length:
            return
        _last_notebook_length_logged = length
        renpy.log("Notebook length: {}".format(length))

    def _tag_origin(manual, auto_added):
        if auto_added and manual:
            return "mixed"
        if auto_added:
            return "auto"
        return "player"

    def new_note(content, speaker, tag, note_type):
        global notebook, note_id_counter, edited_note_id
        requested_tags = normalize_tags(tag)
        tags_list = list(requested_tags)
        auto_added_tags = []
        if note_type == "character-dialog":
            existing = next(
                (n for n in notebook if n["type"] == "character-dialog" and n["content"] == content and n["source"] == speaker),
                None
            )
            if existing:
                renpy.notify("Note Already Saved")
                return existing["id"]
            tags_list = auto_character_tags(content, tags_list)
        elif note_type == "user-written" and getattr(store, "auto_tag_user_notes", True):
            tags_list = auto_character_tags(content, tags_list)
        auto_added_tags = [t for t in tags_list if t not in requested_tags]

        note_id = note_id_counter
        notebook.append({
            "id": note_id,
            "source": speaker,
            "content": content,
            "tags": tags_list,
            "type": note_type
        })
        # renpy.block_rollback()
        
        if note_type == "user-written":
            narrator.add_history(kind="adv", who="You wrote a note: ", what=content)
        if note_type == "character-dialog":
            narrator.add_history(kind="adv", who="You saved a note from " + speaker + ": ", what=content)
        else:
            edited_note_id = None
            narrator.add_history(kind="adv", who="A note was added: ", what=content)

        note_id_counter += 1
        renpy.notify("Note Taken!")

        if note_type == "character-dialog":
            refresh_character_note_tags()
            for n in notebook:
                if n["id"] == note_id:
                    tags_list = n.get("tags", tags_list)
                    break

        log_http(current_user, action="PlayerTookNote", view=current_label, payload={
            "note": content,
            "source": speaker,
            "tags": tags_list,
            "requested_tags": requested_tags,
            "auto_tags_added": auto_added_tags,
            "auto_tagged": bool(auto_added_tags),
            "tag_origin": _tag_origin(requested_tags, auto_added_tags),
            "note_id": note_id,
            "type": note_type
        })

        renpy.take_screenshot()
        renpy.save("1-1", save_name)

        for achievement_fn in ("achieve_notes5", "achieve_notes10"):
            fn = globals().get(achievement_fn)
            if callable(fn):
                fn()
    
    def deletenote(note_id):
        global notebook
        note = next((n for n in notebook if n["id"] == note_id), None)
        if note:
            notebook = [n for n in notebook if n["id"] != note_id]
            renpy.notify("Note Deleted")
            log_http(
                current_user,
                action="PlayerDeletedNote",
                view=current_label,
                payload={"note": note["content"], "source": note["source"], "note_id": note_id}
            )
            narrator.add_history(kind="adv", who="You erased a note: ", what=note["content"])
            renpy.take_screenshot()
            renpy.save("1-1", save_name)
            renpy.block_rollback()
    # def draft ():
    #     log_http(
    #             current_user,
    #             action="PlayerDeletedNote",
    #             view=current_label,
    #             payload={"note": note["content"], "source": note["source"], "note_id": note_id}
    #         )
    def add_tag(tag):
        # add to library if new
        new_tag = str(tag).strip()
        if new_tag and new_tag not in tagLibrary:
            tagLibrary.append(new_tag)
            refresh_character_note_tags()
        
        narrator.add_history(kind="adv", who="You created a new tag: ", what=new_tag or tag)
    
    def save_note(note_id, newnote, newsource, newtags):
        global notebook
        updated_tags = normalize_tags(newtags)
        manual_tags = list(updated_tags)
        for n in notebook:
            if n["id"] == note_id:
                previous_content = n["content"]
                previous_source = n["source"]
                previous_tags = normalize_tags(n.get("tags", []))
                n["content"] = newnote
                n["source"] = newsource
                note_type = n.get("type")
                should_auto_tag = False
                if note_type == "character-dialog":
                    should_auto_tag = True
                elif note_type == "user-written" and getattr(store, "auto_tag_user_notes", True):
                    should_auto_tag = True
                if should_auto_tag:
                    updated_tags = auto_character_tags(newnote, updated_tags)
                auto_added_tags = [t for t in updated_tags if t not in manual_tags]
                n["tags"] = updated_tags
                renpy.notify("Note Revised")
                changes = []
                if previous_content != newnote:
                    changes.append(f"content updated")
                if previous_source != newsource:
                    changes.append(f"source {previous_source} -> {newsource}")
                added = sorted(set(updated_tags) - set(previous_tags))
                removed = sorted(set(previous_tags) - set(updated_tags))
                if added:
                    changes.append(f"tags added: {', '.join(added)}")
                if removed:
                    changes.append(f"tags removed: {', '.join(removed)}")
                log_http(
                    current_user,
                    action="PlayerEditedNote",
                    view=current_label,
                    payload={
                        "note": newnote,
                        "source": newsource,
                        "tags": updated_tags,
                        "note_id": note_id,
                        "changes": changes,
                        "tags_added": added,
                        "tags_removed": removed,
                        "auto_tags_added": auto_added_tags,
                        "tag_origin": _tag_origin(manual_tags, auto_added_tags),
                    }
                )
                narrator.add_history(kind="adv", who="You edited a note:", what=newnote)
                renpy.take_screenshot()
                renpy.save("1-1", save_name)
                renpy.block_rollback()
                break

    def validate_user_note_inputs(note_text, note_source, tag_values):
        """Check minimum requirements before saving a user-written note."""
        words = [w for w in re.findall(r"[A-Za-z0-9']+", note_text or "") if w]
        note_text_trim = (note_text or "").strip()
        source_trim = (note_source or "").strip()
        tag_list = normalize_tags(tag_values)

        template_note = (getattr(store, "new_note_text_template", "") or "").strip()
        template_source = (getattr(store, "new_note_source_template", "") or "").strip()

        if len(words) < 4 or (template_note and note_text_trim.lower() == template_note.lower()):
            return False, "Can you say more in your note?"

        if not source_trim or (template_source and source_trim.lower() == template_source.lower()):
            return False, "Where did this information come from?"

        return True, None

    def commit_note(note_id, newnote, newsource, newtags):
        global edited_note_id
        tags_list = normalize_tags(newtags)

        if note_id == NEW_NOTE_ID:
            is_valid, message = validate_user_note_inputs(newnote, newsource, tags_list)
            if not is_valid:
                renpy.notify(message)
                return False
            new_note(newnote, newsource, tags_list, "user-written")
            renpy.block_rollback()
            edited_note_id = None
            return True
        else:
            note = next((n for n in notebook if n["id"] == note_id), None)
            if note and note.get("type") == "user-written":
                is_valid, message = validate_user_note_inputs(newnote, newsource, tags_list)
                if not is_valid:
                    renpy.notify(message)
                    return False
            save_note(note_id, newnote, newsource, tags_list)
            renpy.block_rollback()
            edited_note_id = None
    
    def argument_edit(newcontent):
        save_draft(newcontent, edited=True)

    def save_draft(newcontent, edited=False):
        global notebook_argument, last_notebook_argument, argument_edits, argument_history
        previous = notebook_argument
        if newcontent != notebook_argument:
            argument_history.append(notebook_argument)
            notebook_argument = newcontent
            argument_edits += 1
            last_notebook_argument = newcontent
            renpy.notify("Draft Argument Updated!" if not edited else "Draft Argument Edited!")
            log_http(current_user, action="PlayerEditedArgument" if edited else "PlayerSavedArgument", view=current_label, payload={
                "draft": newcontent,
                "previous": previous,
                "change_summary": {
                    "previous_length": len(previous or ""),
                    "new_length": len(newcontent or ""),
                    "delta_length": len(newcontent or "") - len(previous or "")
                }
            })
            narrator.add_history(kind="adv", who="You edited your draft: " if edited else "Action", what=newcontent)
            renpy.take_screenshot()
            renpy.save("1-1", save_name)
            renpy.block_rollback()
            fn = globals().get("achieve_argument")
            if callable(fn):
                fn()

#### Notebook ###### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
screen notebook():
    default editing_argument = False
    default argument_edit_text = notebook_argument
    default edit_note_text = ""
    default edit_note_source = ""
    default edit_note_tags = ""
    default filter_tag = None
    # default voice_request_active = False

    modal True
    zorder 92
    on "show" action Function(lock_dialogue_advancement, "notebook")
    on "hide" action Function(unlock_dialogue_advancement, "notebook")

    # on "hide" action If(
    #     voice_request_active,
    #     true=[Function(release_voice_input), SetScreenVariable("voice_request_active", False)],
    #     false=SetScreenVariable("voice_request_active", False)
    # )

    # $ has_note_input = editing_argument or (edited_note_id is not None)
    # if has_note_input:
    #     if not voice_request_active:
    #         $ request_voice_input()
    #         $ voice_request_active = True
    #     use voice_recording_toggle
    # elif voice_request_active:
    #     $ release_voice_input()
    #     $ voice_request_active = False

    use my_button_screen


    add "images/notebook_open.png" xpos 0.5 ypos 0.5 anchor (0.5, 0.5) zoom .8

    $ iw, ih = renpy.image_size("images/imagebutton_close.png")
    $ exit_btn = Transform("images/imagebutton_close.png", zoom=50.0 / ih)

    imagebutton:
        tooltip "Close"
        idle exit_btn
        hover darken_hover(exit_btn, 0.40)

        action Hide("notebook")
        anchor (0.5, 0.5)
        pos (0.792, 0.17)

    fixed:
        # ---- geometry (relative units) ----
        $ vp_center_x, vp_center_y = 0.325, 0.52
        $ vp_w, vp_h = 0.26, 0.6

        # convert pixel heights to relative (so math matches your % sizes)
        $ scr_h = float(config.screen_height)
        $ btn_h_px = 95
        $ btn_h = btn_h_px / scr_h

        $ top_y = vp_center_y - vp_h/2.0

        # ===== STICKY ADD BUTTON (non-scrolling, on top) =====
        $ log_notebook_length(len(notebook))
        $ all_tags = sorted({tag for note in notebook for tag in note.get("tags", []) if tag})
        if filter_tag and filter_tag not in all_tags:
            $ filter_tag = None
        
        ## LEFT NOTE SIDE
        frame:
            anchor (0.5, 0.0)
            pos (vp_center_x, top_y)
            xsize vp_w
            ysize vp_h
            background None
            padding (0, 0)
            has vbox
            spacing 12

            ##FILTER FRAME
            if all_tags:
                frame style "filter_frame":
                    has hbox
                    spacing 6
                    box_wrap True
                    box_wrap_spacing 8

                    text "Filter tags:" style "filter_label"

                    $ all_selected = filter_tag is None
                    textbutton "All":
                        style all_selected and "selected_tag_button" or "tag_button"
                        action SetScreenVariable("filter_tag", None)

                    for tag_name in all_tags:
                        $ selected = filter_tag == tag_name
                        textbutton tag_name:
                            style selected and "selected_tag_button" or "tag_button"
                            action SetScreenVariable("filter_tag", None if selected else tag_name)
            
            ##ADD NEW NOTE
            button:
                xfill True
                ysize btn_h
                background Solid("#d9b9f66c")
                hover_background Solid("#b48ed787")
                padding (12, 20)

                action [
                    SetVariable("edited_note_id", NEW_NOTE_ID),
                    SetScreenVariable("edit_note_text", new_note_text_template),
                    SetScreenVariable("edit_note_source", new_note_source_template),
                    SetScreenVariable("edit_note_tags", ""),
                ]
                
                vbox:
                    yalign 0.5
                    hbox:
                        yalign 0.5
                        spacing 20
                        fixed:
                            xysize (75, 75)
                            add Transform("icons/button_add.png", xysize=(40, 40), xalign=0.5, yalign=0.5)
                        text "Add a Note":
                            style "add_note_text"
            
            ##LIST OF ALL NOTES
            viewport:
                xfill True
                yfill True
                scrollbars "vertical"
                mousewheel True
                vscrollbar_unscrollable "hide"
                draggable True
                pagekeys True
                has vbox style "note_text"
                spacing 12

                $ notes_to_display = list(reversed(notebook))
                
                if edited_note_id == NEW_NOTE_ID:
                    $ notes_to_display.insert(0, {"id": NEW_NOTE_ID, "source": edit_note_source, "content": edit_note_text, "tags": normalize_tags(edit_note_tags), "type": "user-written"})
                
                if filter_tag:
                    $ matched_notes = [note for note in notes_to_display if filter_tag in note.get("tags", [])]
                    $ unmatched_notes = [note for note in notes_to_display if filter_tag not in note.get("tags", [])]
                    $ notes_to_display = matched_notes + unmatched_notes

                for note in notes_to_display:
                    $ s = note["source"] or ""
                    $ note_tags = [tag for tag in note.get("tags", []) if tag]
                    $ t = ", ".join(note_tags) if note_tags else ""
                    $ n = note["content"]
                    $ note_id = note["id"]
                    $ matches_filter = (not filter_tag) or (filter_tag in note_tags)
                    
                    ## EDITABLE NOTE
                    if edited_note_id == note_id:
                        $ note_input_max_height = int(config.screen_height * 0.05)
                        $ source_input_max_height = int(config.screen_height * 0.05)
                        frame style "editing_note_frame":
                            vbox:
                                spacing 20
                                xfill True
                                hbox:
                                    spacing 20
                                    text "Note:" style "note_label" xalign 1.0 xsize 150
                                    $ note_input_value = ScreenVariableInputValue("edit_note_text")
                                    $ note_field_color = "#f1edff" if active_input_field == "note" else "#ffffff"
                                    button:
                                        style "edit_input_container"
                                        background note_field_color
                                        hover_background note_field_color
                                        action [
                                            SetScreenVariable("active_input_field", "note"),
                                            note_input_value.Toggle()
                                        ]
                                        input value note_input_value style "edit_input" multiline True
                                        

                                hbox:
                                    spacing 20
                                    text "Source:" style "note_label" xalign 1.0 xsize 150
                                    $ source_input_value = ScreenVariableInputValue("edit_note_source")
                                    $ source_field_color = "#f1edff" if active_input_field == "source" else "#ffffff"
                                    button:
                                        style "edit_input_container"
                                        background source_field_color
                                        hover_background source_field_color
                                        action [
                                            SetScreenVariable("active_input_field", "source"),
                                            source_input_value.Toggle()
                                        ]
                                        input value source_input_value style "edit_input"

                                hbox:
                                    spacing 20
                                    text "Tags:" style "note_label" xalign 1.0 xsize 150
                                    $ tags_field_color = "#f1edff" if active_input_field == "tags" else "#ffffff"
                                    frame style "edit_frame":
                                        background tags_field_color
                                        hbox:
                                            spacing 4
                                            xfill True
                                            box_wrap True
                                            box_wrap_spacing 6

                                            for tag in tagLibrary:
                                                $ selected = tag in [t.strip() for t in edit_note_tags.split(",") if t.strip()]
                                                textbutton tag:
                                                    style selected and "selected_tag_button" or "tag_button"
                                                    selected selected
                                                    action If(
                                                        selected,
                                                        SetScreenVariable(
                                                            "edit_note_tags",
                                                            ", ".join([t for t in [tt.strip() for tt in edit_note_tags.split(",") if tt.strip()] if t != tag])
                                                        ),
                                                        SetScreenVariable(
                                                            "edit_note_tags",
                                                            ", ".join([t for t in [tt.strip() for tt in edit_note_tags.split(",") if tt.strip()] if t] + [tag])
                                                        )
                                                    )

                                            default creating_tag = False
                                            default new_tag_name = "YOUR TAG"

                                            if creating_tag:
                                                hbox:
                                                    spacing 6
                                                    frame:
                                                        style "create_tag_box_active"
                                                        has hbox
                                                        button:
                                                            action ScreenVariableInputValue("new_tag_name").Toggle()
                                                            input value ScreenVariableInputValue("new_tag_name") style "edit_tag_input"

                                                    textbutton "Save":
                                                        style "edit_tag_support"
                                                        action [
                                                            Function(add_tag, new_tag_name),
                                                            SetScreenVariable("creating_tag", False)
                                                        ]

                                                    textbutton "Cancel":
                                                        style "edit_tag_support"
                                                        action SetScreenVariable("creating_tag", False)
                                            else:
                                                textbutton "Create Tag":
                                                    style "create_tag_box"
                                                    action SetScreenVariable("creating_tag", True)

                                hbox:
                                    spacing 10
                                    xalign 1.0
                                    textbutton "Save Note":
                                        style "standard_button"
                                        action Function(commit_note, note_id, edit_note_text, edit_note_source, edit_note_tags)
                                    textbutton "Cancel":
                                        style "standard_button"
                                        action SetVariable("edited_note_id", None)
                    ## NON-EDITABLE NOTE
                    else:
                        $ note_style = matches_filter and "note_box" or "note_box_dimmed"
                        frame:
                            style note_style
                            vbox:
                                spacing 8
                                hbox:
                                    xfill True
                                    spacing 4
                                    hbox:
                                        spacing 4
                                        xmaximum 350
                                        box_wrap True
                                        box_wrap_spacing 6
                                        for tag_item in note_tags:
                                            textbutton tag_item style "tag_button":
                                                text_style "tag_button_text"
                                    hbox:
                                        spacing 4
                                        xalign 1.0

                                        $ iw, ih = renpy.image_size("images/imagebutton_trashcan.png")
                                        $ delete_btn = Transform("images/imagebutton_trashcan.png", zoom=50.0 / ih)

                                        $ iw, ih = renpy.image_size("images/imagebutton_pencil.png")
                                        $ edit_btn = Transform("images/imagebutton_pencil.png", zoom=50.0 / ih)

                                        imagebutton:
                                            tooltip "Delete note"
                                            idle delete_btn
                                            hover darken_hover(delete_btn)
                                            action Confirm("Are you sure you want to delete this note?", yes=Function(deletenote, note_id))
                                        imagebutton:
                                            tooltip "Edit note"
                                            idle edit_btn
                                            hover darken_hover(edit_btn)
                                            action [
                                                SetScreenVariable("edit_note_text", n),
                                                SetScreenVariable("edit_note_source", s),
                                                SetScreenVariable("edit_note_tags", t),
                                                SetVariable("edited_note_id", note_id)
                                            ]
                                            xalign 1.0
                                text "{b}Note:{/b} " + n:
                                    size 22
                                text "{b}Source:{/b} " + s:
                                    size 14

        ## RIGHT SIDE OF NOTEBOOK                 
        frame:
            anchor (0.5, 0.5)
            pos (0.675, 0.52)
            xsize 0.26
            ysize 0.6
            background None
            has vbox
            spacing 12

            $ argument_column_width = int(config.screen_width * 0.26)
            $ argument_box_width = max(argument_column_width - 40, 250)
            $ argument_box_max_height = int(config.screen_height * 0.3)
        
            ## CURRENT ARGUMENT  FRAME                
            frame:
                style "editing_note_frame"
                background (Solid("#d9dcff80") if editing_argument else Solid("#cccccc40"))
                vbox:
                    spacing 10

                    hbox:
                        xfill True
                        spacing 8

                        text "Current Argument" style "argument_header"

                        $ iw, ih = renpy.image_size("images/imagebutton_pencil.png")
                        $ edit_argument_idle = Transform("images/imagebutton_pencil.png", zoom=50.0 / ih)
                        $ edit_argument_active = Transform("images/imagebutton_pencil.png", zoom=50.0 / ih, alpha=0.65)

                        if not editing_argument:
                            imagebutton:
                                tooltip "Edit draft argument"
                                idle edit_argument_idle
                                hover darken_hover(edit_argument_idle, 0.40)
                                action [
                                    SetScreenVariable("argument_edit_text", notebook_argument),
                                    SetScreenVariable("editing_argument", True)
                                ]
                                xalign 1.0
                                yalign 0.5

                    if editing_argument:
                        frame style "current_argument_edit_frame":
                            viewport:
                                xfill True
                                ymaximum argument_box_max_height
                                scrollbars "vertical"
                                mousewheel True
                                draggable False
                                has vbox
                                input value ScreenVariableInputValue("argument_edit_text") style "argument_input" multiline True xmaximum argument_box_width
                        null height 10
                        hbox:
                            spacing 10
                            xalign 1.0
                            textbutton "Save":
                                style "standard_button"
                                action [
                                    Function(argument_edit, argument_edit_text),
                                    SetScreenVariable("editing_argument", False),
                                    SetScreenVariable("argument_edit_text", notebook_argument)
                                ]
                            textbutton "Cancel":
                                style "standard_button"
                                action [
                                    SetScreenVariable("editing_argument", False),
                                    SetScreenVariable("argument_edit_text", notebook_argument)
                                ]
                    else:
                        frame style "current_argument_view_frame":
                            viewport:
                                xfill True
                                ymaximum argument_box_max_height
                                scrollbars "vertical"
                                mousewheel True
                                draggable False
                                text notebook_argument style "current_argument_text" xmaximum argument_box_width
            ## ARGUMENT HISTORY                
            viewport:
                xfill True
                yfill True
                scrollbars "vertical"
                mousewheel True
                vscrollbar_unscrollable "hide"
                has vbox
                spacing 8

                if len(argument_history) > 0:
                    null height 12
                    text "Previous Drafts:" style "argument_history_header"
                    $ history_max_width = int(config.screen_width * 0.26) - 40
                    for prev_arg in reversed(argument_history):
                        frame:
                            style "argument_history_frame"
                            xmaximum history_max_width
                            text prev_arg:
                                style "argument_history_text"
                                xmaximum history_max_width
                                xfill True
                                xalign 0.0
                                text_align 0.0
                        add Solid("#00000033", xsize=history_max_width, ysize=2)

# ##### Shows key bindings for typing in the input box ######
    # screen keyboard_shortcuts():
    #     modal False
    #     zorder 94
    #     add "images/keyboard shortcuts.png":
    #         pos (0.0, 0.15)

    # ## Argument Revision in Notebook ###
    # screen argument_edit(currentargument):
    #     modal True
    #     zorder 93
    #     add "images/notebook_wide.png"

    #     default newargument = currentargument
    #     default argumentinput = ScreenVariableInputValue("newargument")
    #     $ argument_edits += 1
    #     $ achieve_argument()

    #     imagebutton:
    #         pos (0.30, 0.17)
    #         tooltip "Show/Hide Shortcuts"
    #         idle "images/note clip.png"
    #         hover "images/note clip.png"
    #         action If(renpy.get_screen("keyboard_shortcuts"), true=Hide("keyboard_shortcuts"), false=Show("keyboard_shortcuts"))

    #     viewport:
    #         anchor (0.0,0.0)
    #         pos (0.325,0.20)
    #         xsize 720
    #         ysize 400
    #         scrollbars "vertical"
    #         vscrollbar_unscrollable "hide"
    #         mousewheel True
    #         has vbox
    #         text "Draft Argument: ":
    #             size 20
    #         input value argumentinput color "#037426" xmaximum 720 copypaste True multiline True
        
    #     textbutton "Save Revised Note":
    #         pos (0.35, 0.6)
    #         # action (Function(editdraft, newargument), Hide("argument_edit"), Hide("keyboard_shortcuts"))
    #     textbutton "Cancel":
    #         pos (0.55, 0.6)
    #         # action (Hide("argument_edit"), Hide("keyboard_shortcuts"))  

    #     $ tooltip = GetTooltip()
    #     if tooltip:
    #         nearrect:
    #             focus "tooltip"

    #             frame:
    #                 xalign 0.5
    #                 text tooltip:
    #                     size 15  

screen argument_sharing(prompt):
    modal True
    zorder 100

    default user_argument = ""
    default argumentinput = ScreenVariableInputValue("user_argument")
    # default voice_request_active = False

    # if not voice_request_active:
    #     $ request_voice_input()
    #     $ voice_request_active = True

    # on "hide" action If(
    #     voice_request_active,
    #     true=[Function(release_voice_input), SetScreenVariable("voice_request_active", False)],
    #     false=SetScreenVariable("voice_request_active", False)
    # )

    use my_button_screen

    frame:
        xpos 1.0
        ypos 1.0
        anchor (1.0, 1.0)
        xsize 500
        ysize 700
        background Transform("images/screen_speaking.png", fit="contain")
        padding (40, 28, 40, 80)

        vbox:
            spacing 10

            text prompt:
                size 20
                bold True
                xalign 0.0

            # Scrollable input container
            viewport:
                xmaximum 400
                ymaximum 400
                scrollbars "vertical"
                mousewheel True

                input:
                    value argumentinput
                    multiline True
                    copypaste True
                    style "argument_input"
                    xmaximum 600

            vbox:
                spacing 10
                xmaximum 400
                ymaximum 150

                hbox:
                    spacing 10
                    xsize 320
                    xalign 0.5
                    
                    frame:
                        background None
                        xsize 160
                        textbutton "Nevermind":
                            style "standard_button"
                            action Return(None)
                            tooltip "Close"
                            xfill True

                    frame:
                        background None
                        xsize 160
                        textbutton "Share":
                            style "standard_button"
                            action [
                                Function(cache_screen_response, "argument_sharing", user_argument),
                                Return(user_argument)
                            ]
                            xfill True

                hbox:
                    spacing 10
                    xsize 320
                    xalign 0.5
                    
                    frame:
                        background None
                        xsize 160
                        textbutton "Copy Argument from Notebook":
                            style "standard_button"
                            action SetScreenVariable("user_argument", notebook_argument)
                            xfill True

                    frame:
                        background None
                        xsize 160
                        textbutton "Save Argument in Notebook":
                            style "standard_button"
                            action [
                                Function(argument_edit, user_argument),
                                Function(cache_screen_response, "argument_sharing", user_argument),
                            ]
                            xfill True

# ARGUMENT STYLES
style argument_input:
    background "#ffffff"
    font "DejaVuSans.ttf"
    size 20
    color "#000000"

style current_argument_view_frame:
    background "#ffffff"
    padding (14, 12)
    xfill True

style current_argument_edit_frame:
    background "#ffffff"
    padding (14, 12)
    xfill True

style current_argument_text:
    font "DejaVuSans.ttf"
    size 22
    color "#1a1a1a"

style argument_header:
    font "DejaVuSans-Bold.ttf"
    size 20
    color "#1a1a1a"
    xfill True
    yalign 0.5

style argument_history_header:
    font "DejaVuSans-Bold.ttf"
    size 16
    color "#1a1a1a"
    ymargin 8

style argument_history_frame:
    background "#f2f2f280"
    padding (10, 8)
    xfill False
    xmargin 6
    ymargin 4

style argument_history_text:
    font "DejaVuSans.ttf"
    size 16
    color "#1f1f1f"
    text_align 0.0
    xalign 0.0

style argument_button:
    background "#1558b0"
    hover_background "#021b3c"
    padding (10, 6)
    xminimum 150
    yminimum 40
    font "DejaVuSans.ttf"
    color "#ffffff"
    size 18
    bold True

# IDLE NOTE STYLES
style note_box:
    background "#dddddd80" 
    padding (12, 10)
    xfill True
    xmargin 10
    ymargin 10
    xalign 0.5

style note_box_dimmed:
    background "#cfcfcf86"
    foreground Solid("#ffffff86")
    padding (12, 10)
    xfill True
    xmargin 10
    ymargin 10
    xalign 0.5

style note_text:
    anchor (0.0,0.0)
    pos (0.325,0.12)
    font "DejaVuSans.ttf"
    size 16

style notebook_title:
    anchor (0.5,0.0)
    pos (0.5,0.05)

# EDTING NOTES STYLES

style edit_frame:
    background "#ffffff"
    padding (10, 10)
    xfill True 
    xalign 1.0

style editing_note_frame:
    background "#cccccc40" 
    padding (20, 20)
    xfill True

style note_label:
    size 12
    color "#000000"
    font "DejaVuSans.ttf"
    xalign 0.0

# Style for input fields
style edit_input:
    padding (2, 2, 2, 2)
    font "DejaVuSans.ttf"
    size 14
    color "#000000"
    xfill True

style standard_button:
    background "#d1c7ff"
    hover_background "#a79fceff"
    insensitive_background "#cccccc"
    padding (6, 4)
    xminimum 90
    yminimum 32
    xalign 1.0

style standard_button_text:
    font "DejaVuSans-Bold.ttf"  # or use bold True
    size 10
    color "#3a3a3a"
    hover_color "#000000"
    xalign 0.5
    yalign 0.5

style add_note_text:
    size 20
    color "#333333"
    yalign 0.5
    italic True

# TAG BUTTONS

style tag_button:
    background "#d1c7ff"
    padding (4, 4)

style tag_button_text:
    font "DejaVuSans.ttf"
    size 14
    color "#000000"
    xalign 0.5
    yalign 0.5

style selected_tag_button:
    background "#8076ae"

style filter_frame:
    background "#d1c7ff33"
    padding (8, 8)
    xfill True

style filter_label:
    font "DejaVuSans-Bold.ttf"
    size 14
    color "#333333"
    yalign 0.5

# EDITING TAG STYLES

style create_tag_box:
    padding (6, 4)
    background "#f5f3fe"

style create_tag_box_text:
    font "DejaVuSans.ttf"
    size 12
    color "#000000"
    xfill True

style create_tag_box_active:
    padding (6, 4)
    background "#f5f3fe"

style edit_tag_input:
    font "DejaVuSans.ttf"
    size 12
    color "#000000"
    xfill True

style edit_tag_support:
    background "#00000023"
    padding (4, 4)

style edit_tag_support_text:
    font "DejaVuSans.ttf"
    size 12
    color "#3d3d3d"
    xalign 0.5
    yalign 0.5
    italic True
