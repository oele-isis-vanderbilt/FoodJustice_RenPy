#### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####

# GLOBAL NOTEBOOK Variables 
default notebook = []
default argument_history = []
default note_id_counter = 0
default notebook_argument = "Draft your argument here."
default last_notebook_argument = "Draft your argument here."
default argument_edits = 0
default customnotecount = 0
default copied_argument = ""
default user_argument = ""
default tagLibrary = ["bees", "pollination", "food", "garden", "lab", "family", "kids", "money", "shopping", "cars", "parking lot", "community"]
default editing_argument = False
default edited_note_id = None
default new_note_text_template = "whats your evidence?"
default new_note_source_template = "where did you learn this?"

init python:
    import datetime
    from typing import Dict, Any, Optional
    import os
    import pygame.scrap
    
    def label_callback(label, interaction):
        if not label.startswith("_"):
            log_http(current_user, action=f"PlayerJumpedLabel({label}|{interaction})", view=label, payload=None)
            global current_label
            current_label = label

    config.label_callbacks = [label_callback]

    def retaindata():
        renpy.retain_after_load()

    def new_note(content, speaker, tag, note_type="character-saved"):
        global notebook, note_id_counter, edited_note_id
        note_id = note_id_counter
        edited_note_id = note_id  # Always set to the newest note
        notebook.append({
            "id": note_id,
            "source": speaker,
            "content": content,
            "tags": [tag] if isinstance(tag, str) else tag,
            "type": note_type
        })
        note_id_counter += 1
        renpy.restart_interaction()  # Force UI refresh if needed
        renpy.notify("Note Taken!")
        log_http(current_user, action="PlayerTookNote", view=current_label, payload={
            "note": content,
            "source": speaker,
            "tags": tag,
            "note_id": note_id,
            "type": note_type
        })
        narrator.add_history(kind="adv", who="You wrote a note: ", what=content)
        renpy.take_screenshot()
        renpy.save("1-1", save_name)
    
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
    
    def add_tag(tag):
        # add to library if new
        if tag.strip() not in tagLibrary:
            tagLibrary.append(tag)
        
        narrator.add_history(kind="adv", who="You created a new tag: ", what=tag)

    def save_note(note_id, newnote, newsource, newtags):
        global notebook
        for n in notebook:
            if n["id"] == note_id:
                n["content"] = newnote
                n["source"] = newsource
                n["tags"] = [newtags] if isinstance(newtags, str) else newtags
                renpy.notify("Note Revised")
                log_http(
                    current_user,
                    action="PlayerEditedNote",
                    view=current_label,
                    payload={"note": newnote, "source": newsource, "tags": newtags, "note_id": note_id}
                )
                narrator.add_history(kind="adv", who="You edited a note:", what=newnote)
                renpy.take_screenshot()
                renpy.save("1-1", save_name)
                break

    def save_draft(argument, edited=False):
        global notebook_argument, last_notebook_argument, argument_edits, argument_history
        if argument != notebook_argument:
            argument_history.append(notebook_argument)
            notebook_argument = argument
            if argument != last_notebook_argument:
                argument_edits += 1
                last_notebook_argument = argument
            renpy.notify("Draft Argument Updated!" if not edited else "Draft Argument Edited!")
            log_http(current_user, action="PlayerEditedArgument" if edited else "PlayerSavedArgument", view=current_label, payload={
                "draft": argument,
            })
            narrator.add_history(kind="adv", who="You edited your draft: " if edited else "Action", what=argument)
            renpy.take_screenshot()
            renpy.save("1-1", save_name)

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


#### Notebook ###### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

screen notebook():
    default editing_argument = False
    default argument_edit_text = notebook_argument
    default edit_note_text = ""
    default edit_note_source = ""
    default edit_note_tags = ""

    modal True
    zorder 92

    add "images/notebook_open.png" xpos 0.5 ypos 0.5 anchor (0.5, 0.5) zoom .8

    imagebutton:
        idle Transform("icons/button_exit-popup.png", xysize=(36,36))
        hover Transform("icons/button_exit-popup_hover.png", xysize=(36,36))
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
        $ gap_px   = 10
        $ btn_h = btn_h_px / scr_h
        $ gap   = gap_px   / scr_h

        $ top_y = vp_center_y - vp_h/2.0

    # ===== STICKY ADD BUTTON (non-scrolling, on top) =====
        button:
            anchor (0.5, 0.0)
            pos (vp_center_x, top_y)
            xsize vp_w
            ysize btn_h
            background Solid("#dddddd80")
            hover_background Solid("#cccccc")
            padding (12, 10)

            action [
                Function(new_note, "evidence", "where did you learn this?", []),
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

        # ============ SCROLLABLE LIST ============
        viewport:
            anchor (0.5, 0.0)
            pos (vp_center_x, top_y + btn_h + gap)   # BELOW the button
            xsize vp_w
            ysize vp_h - (btn_h + gap)               # shorter by button+gap
            scrollbars "vertical"
            mousewheel True
            vscrollbar_unscrollable "hide"
            has vbox style "note_text"

            $ note_count = len(notebook)
            for i, note in enumerate(reversed(notebook)):
                $ s = note["source"] or ""
                $ t = ", ".join(note["tags"]) if note["tags"] else ""
                $ n = note["content"]
                $ note_id = note["id"]
### EDIT NOTE MODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if edited_note_id == note_id: 
                    frame style "editing_note_frame":
                        vbox:
                            spacing 20
                            xfill True
                            hbox: ### edit note content
                                spacing 20
                                text "Note:" style "note_label" xalign 1.0 xsize 150
                                frame style "edit_frame":
                                    button:
                                        action ScreenVariableInputValue("edit_note_text").Toggle()
                                        input value ScreenVariableInputValue("edit_note_text") style "edit_input" multiline True

                            hbox: ### edit source of note
                                spacing 20
                                text "Source:" style "note_label" xalign 1.0 xsize 150
                                frame style "edit_frame":
                                    button:
                                        action ScreenVariableInputValue("edit_note_source").Toggle()
                                        input value ScreenVariableInputValue("edit_note_source") style "edit_input"

                            hbox: ### select / deselect tags from tag library
                                spacing 20
                                text "Tags:" style "note_label" xalign 1.0 xsize 150
                                frame style "edit_frame":
                                    hbox:
                                        spacing 4
                                        xfill True
                                        box_wrap True
                                        box_wrap_spacing 6

                                        # existing tags
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

                                        # --- inline Create Tag editor ---
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
                                    action [
                                        Function(save_note, note_id, edit_note_text, edit_note_source, edit_note_tags),
                                        SetVariable("edited_note_id", None)
                                    ]
                                textbutton "Cancel":
                                    style "standard_button"
                                    action SetVariable("edited_note_id", None)
                                        
                else: ## DISPLAY EXISTING NOTES (not in edit mode)
                    frame:
                        style "note_box"
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
                                    for tag_item in [tag.strip() for tag in t.split(",") if tag.strip()]:
                                        textbutton tag_item style "tag_button":
                                            text_style "tag_button_text"
                                hbox:
                                    spacing 4
                                    xalign 1.0
                                    imagebutton:
                                        tooltip "Delete note"
                                        style "imagebutton_note"
                                        idle "images/delete note.png"
                                        hover "images/delete note dark.png"
                                        action Confirm("Are you sure you want to delete this note?", yes=Function(deletenote, note_id))
                                    imagebutton:
                                        tooltip "Edit note"
                                        style "imagebutton_note"
                                        idle "images/edit pencil.png"
                                        hover "images/edit pencil dark.png"
                                        action [
                                            SetVariable("edit_note_text", n),
                                            SetVariable("edit_note_source", s),
                                            SetVariable("edit_note_tags", t),
                                            SetVariable("edited_note_id", note_id)
                                        ]
                                        xalign 1.0
                            text n id "note":
                                size 22
                            text "Source: " + s:
                                size 14


        ## right side of notebook for argument drafting                 
        viewport:
            anchor (0.5, 0.5)
            pos (0.675, 0.52)
            xsize 0.26
            ysize 0.6
            scrollbars "vertical"
            mousewheel True
            vscrollbar_unscrollable "hide"
            has vbox style "note_text"

            frame style "editing_note_frame":
                vbox:
                    if editing_argument:
                        frame style "edit_frame":
                            input value ScreenVariableInputValue("argument_edit_text") style "argument_input" multiline True xmaximum 550
                        hbox:
                            spacing 10
                            xalign 1.0
                            textbutton "Save":
                                style "standard_button"
                                action [
                                    Function(editdraft, argument_edit_text),
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
                        hbox:
                            imagebutton:
                                tooltip "Edit draft argument"
                                idle "images/edit pencil.png"
                                hover "images/edit pencil dark.png"
                                action SetScreenVariable("editing_argument", True)
                        text notebook_argument size 22

            if len(argument_history) > 0:
                text "Previous Drafts:" size 16
                for prev_arg in reversed(argument_history):
                    frame:
                        style "note_box"
                        text prev_arg size 16


##### Shows key bindings for typing in the input box ######

screen keyboard_shortcuts():
    modal False
    zorder 94
    add "images/keyboard shortcuts.png":
        pos (0.0, 0.15)


## Argument Revision in Notebook ###
screen argument_edit(currentargument):
    modal True
    zorder 93
    add "images/notebook_wide.png"

    default newargument = currentargument
    default argumentinput = ScreenVariableInputValue("newargument")
    $ argument_edits += 1
    $ achieve_argument()

    imagebutton:
        pos (0.30, 0.17)
        tooltip "Show/Hide Shortcuts"
        idle "images/note clip.png"
        hover "images/note clip.png"
        action If(renpy.get_screen("keyboard_shortcuts"), true=Hide("keyboard_shortcuts"), false=Show("keyboard_shortcuts"))

    viewport:
        anchor (0.0,0.0)
        pos (0.325,0.20)
        xsize 720
        ysize 400
        scrollbars "vertical"
        vscrollbar_unscrollable "hide"
        mousewheel True
        has vbox
        text "Draft Argument: ":
            size 20
        input value argumentinput color "#037426" xmaximum 720 copypaste True multiline True
    
    textbutton "Save Revised Note":
        pos (0.35, 0.6)
        action (Function(editdraft, newargument), Hide("argument_edit"), Hide("keyboard_shortcuts"))
    textbutton "Cancel":
        pos (0.55, 0.6)
        action (Hide("argument_edit"), Hide("keyboard_shortcuts"))  

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15  

screen argument_writing(prompt):

    modal True
    zorder 100

    default user_argument = ""
    default argumentinput = ScreenVariableInputValue("user_argument")

    button:
        action NullAction()
        xysize (config.screen_width, config.screen_height)
        style "empty"

    add "notebook_wide.png" xpos 0.5 ypos 0.5 anchor (0.5, 0.5) xsize 1000 ysize 750

    frame:
        align (0.52, 0.5)
        background "#23bb7900"
        xsize 600
        ysize 720

        vbox:
            text prompt:
                size 28
            
            frame:
                xsize 600
                ysize 200
                align (0.5, 0.5)
                input:
                    value argumentinput
                    ymaximum 400
                    xmaximum 600
                    style "argument_input"
                    copypaste True
                    multiline True

            hbox:
                spacing 20
                xalign 0.0
                textbutton "Copy from Notebook":
                    style "argument_button"
                    action SetScreenVariable("user_argument", notebook_argument)

                textbutton "Submit":
                    style "argument_button"
                    action [Function(draft, user_argument), Return()]

                textbutton "Cancel":
                    style "argument_button"
                    action Return()

# ARGUMENT STYLES
style argument_input:
    background "#ffffff"
    font "DejaVuSans.ttf"
    size 20
    color "#000000"

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

style note_text:
    anchor (0.0,0.0)
    pos (0.325,0.12)

style notebook_title:
    anchor (0.5,0.0)
    pos (0.5,0.05)

style imagebutton_note:
    size 50

# EDTING NOTES STYLES

style edit_frame:
    background "#ffffff"
    padding (10, 10)
    xfill True  # this makes the frame take all horizontal space
    xalign 1.0

style editing_note_frame:
    background "#cccccc40"  # Slightly darker translucent gray
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


