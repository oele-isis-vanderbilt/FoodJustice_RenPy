#### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####
init python:
    import datetime
    from typing import Dict, Any, Optional
    import os
    import pygame.scrap
    # Todo: Remove this later
    # if renpy.emscripten:
    # import emscripten
    # result = emscripten.run_script("window.syncFlowPublisher.startPublishing('umesh', 'umesh')")
    

    def label_callback(label, interaction):
        if not label.startswith("_"):
            log_http(current_user, action=f"PlayerJumpedLabel({label}|{interaction})", view=label, payload=None)
            global current_label
            current_label = label

    config.label_callbacks = [label_callback]

    def copy(text):
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))

    def retaindata():
        renpy.retain_after_load()

    def note(info, speaker, tag):
        note_list.append(info)
        source_list.append(speaker)
        tag_list.append(tag)
        renpy.notify("Note Taken!")
        noteindex = note_list.index(info)
        notenumber = str(noteindex)
        # log("Took note #" + notenumber + ": " + info + " (Source: " + speaker + ")")
        log_http(current_user, action="PlayerTookNote", view=current_label, payload={
            "note": info,
            "source": speaker,
            "tag": tag,
            "note_id": noteindex
        })
        narrator.add_history(kind="adv",who="You wrote a note:",what=info)
        renpy.take_screenshot()
        renpy.save("1-1", save_name)

    def deletenote(notetext):
        noteindex = note_list.index(notetext)
        notetext = note_list[noteindex]
        note_source = source_list[noteindex]
        del note_list[noteindex]
        del source_list[noteindex]
        del tag_list[noteindex]
        renpy.notify("Note Deleted")
        # log("Player deleted note: " + notetext)
        log_http(
            current_user,
            action="PlayerDeletedNote",
            view=current_label,
            payload={"note": notetext, "source": note_source, "note_id": noteindex}
        )
        narrator.add_history(kind="adv",who="You erased a note:",what=notetext)
        renpy.take_screenshot()
        renpy.save("1-1", save_name)
    
    def editnote(oldtext, newnote, newsource, newtag):
        noteindex = note_list.index(oldtext)
        note_list[noteindex] = newnote
        source_list[noteindex] = newsource
        tag_list[noteindex] = newtag
        renpy.notify("Note Revised")
        notenumber = str(noteindex)
        # log("Player edited note #" + notenumber + " to say: " + newnote + " (Source: " + newsource + ")")
        log_http(
            current_user,
            action="PlayerEditedNote",
            view=current_label,
            payload={"note": newnote, "source": newsource, "tag": newtag, "note_id": noteindex}
        )
        narrator.add_history(kind="adv",who="You edited a note:",what=newnote)
        renpy.take_screenshot()
        renpy.save("1-1", save_name)
        
    def draft(argument):
        global notebook_argument
        notebook_argument = argument
        renpy.notify("Draft Argument Updated!")
        log_http(current_user, action="PlayerSavedArgument", view=current_label, payload={
            "draft": argument,
        })
        narrator.add_history(kind="adv",who="Action",what="(You wrote this argument in your notebook.)")
        renpy.take_screenshot()
        renpy.save("1-1", save_name)

    def editdraft(newargument):
        global notebook_argument
        notebook_argument = newargument
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
