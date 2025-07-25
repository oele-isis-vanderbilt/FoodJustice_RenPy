#### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####

# GLOBAL NOTEBOOK Variables 

default notebook = []
default note_id_counter = 0
default notebook_argument = "Draft your argument here."
default last_notebook_argument = "Draft your argument here."
default argument_edits = 0
default customnotecount = 0
default copied_argument = ""
default user_argument = ""

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

    def note(content, speaker, tag, note_type="character-saved"):
        global notebook, note_id_counter
        note_id = note_id_counter
        notebook.append({
            "id": note_id,
            "source": speaker,
            "content": content,
            "tags": [tag] if isinstance(tag, str) else tag,
            "type": note_type
        })
        note_id_counter += 1
        renpy.notify("Note Taken!")
        log_http(current_user, action="PlayerTookNote", view=current_label, payload={
            "note": content,
            "source": speaker,
            "tag": tag,
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

    def editnote(note_id, newnote, newsource, newtags):
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
                    payload={"note": newnote, "source": newsource, "tag": newtags, "note_id": note_id}
                )
                narrator.add_history(kind="adv", who="You edited a note:", what=newnote)
                renpy.take_screenshot()
                renpy.save("1-1", save_name)
                break

    def draft(argument):
        global notebook_argument, last_notebook_argument, argument_edits
        if argument != notebook_argument:
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
        global notebook_argument, last_notebook_argument, argument_edits
        if newargument != notebook_argument:
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


##  Notebook to collect evidence, idea board, etc.
##
#################################################################

#### Notebook ######

style note_text:
    anchor (0.0,0.0)
    pos (0.325,0.12)

style notebook_title:
    anchor (0.5,0.0)
    pos (0.5,0.05)

style close_button:
    anchor (0.5, 0.0)
    pos (0.68,0.03)

screen notebook():
    modal True
    add "images/notebook_tall.png"
    zorder 92

    imagebutton:
        idle "images/close button.png"
        hover "images/close button dark.png"
        action Hide(screen="notebook") 
        style "close_button" 
    
    text "Evidence Notebook" style "notebook_title"

    viewport:
        anchor (0.0,0.0)
        pos (0.325,0.12)
        xsize 740
        ysize 600
        scrollbars "vertical"
        mousewheel True
        vscrollbar_unscrollable "hide"
        has vbox style "note_text"

        for note in notebook:
            $ s = note["source"] or ""
            $ t = ", ".join(note["tags"]) if note["tags"] else ""
            $ n = note["content"]
            $ note_id = note["id"]
            text "Source: " + s + "   Tag: " + t:
                size 15
            text n id "note":
                size 22
            hbox:
                imagebutton:
                    tooltip "Delete note"
                    idle "images/delete note.png"
                    hover "images/delete note dark.png"
                    action Confirm("Are you sure you want to delete this note?", yes=Function(deletenote, note_id))
                imagebutton:
                    tooltip "Edit note"
                    idle "images/edit pencil.png"
                    hover "images/edit pencil dark.png"
                    action Show("note_edit", None, note_id, n, s, t)
            text "\n":
                size 8
        
        imagebutton:
            tooltip "New note"
            idle "images/takenote.png"
            hover "images/takenotedark.png"
            action Show("noteentry")
            xpos -40

    viewport:
        anchor (0.0,0.0)
        pos (0.325,0.7)
        xsize 740
        ysize 200
        scrollbars "vertical"
        mousewheel True
        vscrollbar_unscrollable "hide"
        has vbox style "note_text"
        hbox:
            text "Draft Argument for Mayor":
                size 30
            imagebutton:
                tooltip "Edit draft argument"
                idle "images/edit pencil.png"
                hover "images/edit pencil dark.png"
                action Show("argument_edit", None, notebook_argument)
            text "  ":
                size 8
            imagebutton:
                tooltip "Copy argument"
                idle "images/copy.png"
                hover "images/copy dark.png"
                action Function(copy, notebook_argument)
        text notebook_argument:
            size 22

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15

style note_input:
    size 25

##### Shows key bindings for typing in the input box ######

screen keyboard_shortcuts():
    modal False
    zorder 94
    add "images/keyboard shortcuts.png":
        pos (0.0, 0.15)

###### Custom notetaking for player to add notes to notebook #####

screen noteentry():
    modal True
    zorder 93
    add "images/notebook_wide.png"

    if customnotecount == 0:
        default customnote = "Type ideas here"
        default customsource = "What's the source?"
        default customtag = "What is this evidence about?"
        add "images/keyboard shortcuts.png":
            pos (0.0, 0.15)
    else:
        default customnote = ""
        default customsource = ""
        default customtag = ""
        imagebutton:
            pos (0.30, 0.17)
            tooltip "Show/Hide Shortcuts"
            idle "images/note clip.png"
            hover "images/note clip.png"
            action If(renpy.get_screen("keyboard_shortcuts"), true=Hide("keyboard_shortcuts"), false=Show("keyboard_shortcuts"))

    default noteinput = ScreenVariableInputValue("customnote")
    default sourceinput = ScreenVariableInputValue("customsource")
    default taginput = ScreenVariableInputValue("customtag")

    viewport:
        anchor (0.0,0.0)
        pos (0.325,0.20)
        xsize 720
        ysize 400
        scrollbars "vertical"
        vscrollbar_unscrollable "hide"
        mousewheel True
        has vbox
        text "My note: ":
            size 20
        button:
            action noteinput.Toggle()
            xsize 720
            input: 
                value noteinput
                copypaste True
                multiline True
                style "note_input"
        text "\n" + "I learned this from: ":
            size 20
        button:
            action sourceinput.Toggle()
            xsize 720
            input: 
                value sourceinput
                copypaste True
                multiline True
                style "note_input"
        text "\n" + "Tag/Label: ":
            size 20
        button:
            action taginput.Toggle()
            xsize 720
            input: 
                value taginput
                copypaste True
                multiline True
                style "note_input"
    
    textbutton "Save Note":
        pos (0.35, 0.6)
        action (Function(note, customnote, customsource, customtag), IncrementVariable("customnotecount"), Hide("noteentry"), Hide("keyboard_shortcuts"))
    textbutton "Cancel":
        pos (0.55, 0.6)
        action (Hide("noteentry"), Hide("keyboard_shortcuts"))  

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15  

##### Note editing for existing notes in the player's notebook ######

screen note_edit(note_id, n, s, t):
    default newnote = n
    default newsource = s
    default newtag = t

    modal True
    zorder 93
    add "images/notebook_wide.png"

    imagebutton:
        pos (0.30, 0.17)
        tooltip "Show/Hide Shortcuts"
        idle "images/note clip.png"
        hover "images/note clip.png"
        action If(renpy.get_screen("keyboard_shortcuts"), true=Hide("keyboard_shortcuts"), false=Show("keyboard_shortcuts"))

    default noteinput = ScreenVariableInputValue("newnote")
    default sourceinput = ScreenVariableInputValue("newsource")
    default taginput = ScreenVariableInputValue("newtag")

    viewport:
        anchor (0.0,0.0)
        pos (0.325,0.20)
        xsize 720
        ysize 400
        scrollbars "vertical"
        vscrollbar_unscrollable "hide"
        mousewheel True
        has vbox
        text "Note: ":
            size 20
        button:
            action noteinput.Toggle()
            xsize 720
            input: 
                value noteinput
                copypaste True
                multiline True
                style "note_input"
        text "\n" + "Source: ":
            size 20
        button:
            action sourceinput.Toggle()
            xsize 720
            input: 
                value sourceinput
                copypaste True
                multiline True
                style "note_input"
        text "\n" + "Tag: ":
            size 20
        button:
            action taginput.Toggle()
            xsize 720
            input: 
                value taginput
                copypaste True
                multiline True
                style "note_input"
    
    textbutton "Save Revised Note":
        pos (0.35, 0.6)
        action (Function(editnote, note_id, newnote, newsource, newtag), Hide("note_edit"), Hide("keyboard_shortcuts"))
    textbutton "Cancel":
        pos (0.55, 0.6)
        action (Hide("note_edit"), Hide("keyboard_shortcuts"))  

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15  

### Argument Revision in Notebook ###

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

#### Invisible Character Selection Screen ####

screen characterselect3(c_left, c_center, c_right):
    zorder 80

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.2, 0.25)
        action Jump(c_left + "_chatting")

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.5, 0.25)
        action Jump(c_center + "_chatting")

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.8, 0.25)
        action Jump(c_right + "_chatting")

screen characterselect2(c_left, c_right):
    zorder 80

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.2, 0.25)
        action Jump(c_left + "_chatting")

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.8, 0.25)
        action Jump(c_right + "_chatting")


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
                    action SetVariable("user_argument", notebook_argument)

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

style argument_button_text:
    bold True
    color "#fff"
    size 18
    font "DejaVuSans.ttf"  
    xalign 0.5
    yalign 0.5