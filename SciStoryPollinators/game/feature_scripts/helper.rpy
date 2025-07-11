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

    def toggle_argument_screen():
        if renpy.get_screen("argument_writing"):
            renpy.hide_screen("argument_writing")
            if not renpy.get_screen("say"):
                renpy.show_screen("say")
            if not renpy.get_screen("quick_menu"):
                renpy.show_screen("quick_menu")
        else:
            # Hide other UI layers
            renpy.hide_screen("quick_menu")
            renpy.hide_screen("say")
            # Open the screen in a new context to prevent click-through
            renpy.call_in_new_context("show_argument_writing", "Write your argument")


    def toggle_map_popup():
        if renpy.get_screen("map_popup"):
            renpy.hide_screen("map_popup")
        else:
            renpy.show_screen("map_popup")

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

label show_argument_writing(prompt):
    call screen argument_writing(prompt)
return