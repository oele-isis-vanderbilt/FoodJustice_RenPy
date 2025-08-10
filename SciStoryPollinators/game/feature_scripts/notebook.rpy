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

    def copy(text):
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
        copied_argment = text

    def retaindata():
        renpy.retain_after_load()

    def new_note(content, speaker, tag, note_type="character-saved"):
        global notebook, note_id_counter, edited_note_id
        note_id = note_id_counter
        notebook.append({
            "id": note_id,
            "source": speaker,
            "content": content,
            "tags": [tag] if isinstance(tag, str) else tag,
            "type": note_type
        })
        note_id_counter += 1
        edited_note_id = note_id
        renpy.notify("Note Taken!")
        log_http(current_user, action="PlayerTookNote", view=current_label, payload={
            "note": content,
            "source": speaker,
            "tags": tag,
            "note_id": note_id,
            "type": note_type
        })
        narrator.add_history(kind="adv", who="You wrote a note:", what=content)
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
            narrator.add_history(kind="adv", who="You erased a note:", what=note["content"])
            renpy.take_screenshot()
            renpy.save("1-1", save_name)

    ### replaces the value of note w/ new values
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

    def draft(argument):
        global notebook_argument, last_notebook_argument, argument_edits, argument_history
        if argument != notebook_argument:
            argument_history.append(notebook_argument)
            notebook_argument = argument
            if argument != last_notebook_argument:
                argument_edits += 1
                last_notebook_argument = argument
            renpy.notify("Draft Argument Updated!")
            log_http(current_user, action="PlayerSavedArgument", view=current_label, payload={
                "draft": argument,
            })
            narrator.add_history(kind="adv",who="Action",what="(You wrote this argument in your notebook.)")
            renpy.take_screenshot()
            renpy.save("1-1", save_name)

    def editdraft(newargument):
        global notebook_argument, last_notebook_argument, argument_edits, argument_history
        if newargument != notebook_argument:
            argument_history.append(notebook_argument)
            notebook_argument = newargument
            if newargument != last_notebook_argument:
                argument_edits += 1
                last_notebook_argument = newargument
            renpy.notify("Draft Argument Edited!")
            log_http(current_user, action="PlayerEditedArgument", view=current_label, payload={
                "draft": newargument,
            })
            narrator.add_history(kind="adv",who="You edited your draft:",what=newargument)
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


#### Notebook ######

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
        tooltip "Close Notebook"
        idle Transform("icons/button_exit.png", xysize=(75, 75))
        hover Transform(im.MatrixColor("icons/button_exit.png", im.matrix.tint(0.75, 0.75, 0.75)), xysize=(70, 70))
        action Hide("notebook")
        anchor (0.5, 0.5)
        pos (0.792, 0.17)

    ## left side of notebook for notes                
    viewport:
        anchor (0.5, 0.5)
        pos (0.325, 0.52)
        xsize 0.26
        ysize 0.6
        scrollbars "vertical"
        mousewheel True
        vscrollbar_unscrollable "hide"
        has vbox style "note_text"

        button:
            background Solid("#dddddd80")
            hover_background Solid("#cccccc")   # visible change when hovered
            padding (12, 10)
            xfill True
            xmargin 10
            ymargin 10
            ysize 95

            action Function(new_note, "...", "...", ["..."])  

            vbox:
                yalign 0.5
                hbox:
                    yalign 0.5
                    spacing 20

                    # Icon box (no nested button!)
                    fixed:
                        xysize (75, 75)
                        # padding (10, 10)
                        add Transform(
                            "icons/button_add.png",
                            xysize=(40, 40),
                            xalign=0.5, yalign=0.5
                        )

                    text "Add a Note":
                        size 20
                        color "#333333"
                        yalign 0.5
                        italic True

        $ note_count = len(notebook)
        for i, note in enumerate(notebook):
            $ s = note["source"] or ""
            $ t = ", ".join(note["tags"]) if note["tags"] else ""
            $ n = note["content"]
            $ note_id = note["id"]

            if edited_note_id == note_id: ### EDIT NOTE MODE
                frame style "editing_note_frame":
                    vbox:
                        spacing 20
                        xfill True
                        hbox:
                            spacing 20
                            text "Note:" style "note_label" xalign 1.0 xsize 150
                            frame style "edit_frame":
                                button:
                                    action ScreenVariableInputValue("edit_note_text").Toggle()
                                    input value ScreenVariableInputValue("edit_note_text") style "edit_input" multiline True

                        hbox:
                            spacing 20
                            text "Source:" style "note_label" xalign 1.0 xsize 150
                            frame style "edit_frame":
                                button:
                                    action ScreenVariableInputValue("edit_note_source").Toggle()
                                    input value ScreenVariableInputValue("edit_note_source") style "edit_input"

                        hbox:
                            spacing 20
                            text "Tags:" style "note_label" xalign 1.0 xsize 150
                            frame style "edit_frame":
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

                        hbox:
                            spacing 10
                            xalign 1.0
                            textbutton "Save Note":
                                style "standard_button"
                                action [
                                    Function(save_note, note_id, edit_note_text, edit_note_source, edit_note_tags),
                                    SetScreenVariable("edited_note_id", None)
                                ]
                            textbutton "Cancel":
                                style "standard_button"
                                action SetScreenVariable("edited_note_id", None)
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
                                        SetScreenVariable("edit_note_text", n),
                                        SetScreenVariable("edit_note_source", s),
                                        SetScreenVariable("edit_note_tags", t),
                                        SetScreenVariable("edited_note_id", note_id)
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

# Input field style
style argument_input:
    background "#ffffff"
    font "DejaVuSans.ttf"
    size 20
    color "#000000"

# Button style
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

style imagebutton_note:
    size 50

style note_text:
    anchor (0.0,0.0)
    pos (0.325,0.12)

style notebook_title:
    anchor (0.5,0.0)
    pos (0.5,0.05)


# Style for the notebook edit labels
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

# style edit_button:
#     background "#aaaaaa"
#     hover_background "#888888"
#     padding (12, 8)
#     xminimum 160
#     yminimum 45
#     font "DejaVuSans.ttf"
#     color "#ffffff"
#     size 10

style note_box:
    background "#dddddd80"  # grey with ~50% opacity
    padding (12, 10)
    xfill True
    xmargin 10
    ymargin 10
    xalign 0.5

style edit_frame:
    background "#ffffff"
    padding (10, 10)
    xfill True  # this makes the frame take all horizontal space
    xalign 1.0

style editing_note_frame:
    background "#cccccc40"  # Slightly darker translucent gray
    padding (20, 20)
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

style tag_button_text:
    font "DejaVuSans.ttf"
    size 12
    color "#000000"
    xalign 0.5
    yalign 0.5

style selected_tag_button:
    background "#8076ae"

style tag_button:
    background "#d1c7ff"
