init python:
    # --- character stats functions ---
    def update_char_stats(char_name):
        for char in character_directory:
            if char["name"] == char_name:
                char["chats"] += 1
                char["spoken"] = True
                break

    def get_character_spoken(char_name):
        for char in character_directory:
            if char["name"] == char_name:
                return char["spoken"]
        return False

    def get_character_chats(char_name):
        for char in character_directory:
            if char["name"] == char_name:
                return char["chats"]
        return 0

label toggle_argument_screen:
    if renpy.get_screen("argument_writing"):
        hide screen argument_writing
    else:
        show screen argument_writing("Why should the mayor care?")
    return


label toggle_map_popup:
    if renpy.get_screen("map_popup"):
        hide screen map_popup
    else:
        show screen map_popup with dissolve
    return

label toggle_achievements_screen:
    if renpy.get_screen("achievements_screen"):
        hide screen achievements_screen
    else:
        show screen achievements_screen with dissolve
    return

label toggle_notebook:
    if renpy.get_screen("notebook"):
        hide screen notebook
    else:
        show screen notebook with dissolve
    return
