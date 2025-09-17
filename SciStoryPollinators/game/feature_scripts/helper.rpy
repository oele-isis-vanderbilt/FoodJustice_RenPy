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
        return ""

    def get_character_chats(char_name):
        for char in character_directory:
            if char["name"] == char_name:
                return char["chats"]
        return ""

    def get_note_by_id(note_id):
        for note in notebook: 
            if note["id"] == note_id:
                return note

    def toggle_argument_share_screen():
        if renpy.get_screen("argument_sharing"):
            renpy.hide_screen("argument_sharing")
        else:
            renpy.show_screen("argument_sharing")



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