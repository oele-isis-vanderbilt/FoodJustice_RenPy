label show_argument_writing(prompt):
    call screen argument_writing(prompt)
    return

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

    def toggle_question_input():
        if renpy.get_screen("dialog_bubble_input"):
            renpy.hide_screen("dialog_bubble_input")
        else:
            renpy.show_screen("dialog_bubble_input")

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

    def darken_hover(disp, amount=0.40):
        """
        Darkens any displayable by multiplying RGB with (1 - amount).
        amount: 0.0–1.0 (0.40 -> 60% brightness)
        smaller amount means less darkening.
        """
        f = max(0.0, 1.0 - float(amount))
        mat = Matrix([
            f, 0, 0, 0,
            0, f, 0, 0,
            0, 0, f, 0,
            0, 0, 0, 1.0,
        ])
        return Transform(disp, matrixcolor=mat)


    def brighten_hover(disp, amount=0.40):
        """
        Brightens any displayable by multiplying RGB with (1 + amount).
        amount: 0.0–1.0 (0.40 -> 140% brightness).
        smaller amount means less brightening.
        """
        f = 1.0 + float(amount)
        mat = Matrix([
            f, 0, 0, 0,
            0, f, 0, 0,
            0, 0, f, 0,
            0, 0, 0, 1.0,
        ])
        return Transform(disp, matrixcolor=mat)

    def grow_hover(disp, amount=0.20, center=True):
        """
        Returns `disp` scaled up by (1 + amount).
        Set center=False if you don't want the scaling to pivot around the center.
        """
        z = 1.0 + float(amount)
        if center:
            return Transform(disp, zoom=z, xanchor=0.5, yanchor=0.5)
        return Transform(disp, zoom=z)

    def shrink_hover(disp, amount=0.20, center=True):
        """
        Returns `disp` scaled down by (1 - amount).
        """
        z = max(0.01, 1.0 - float(amount))
        if center:
            return Transform(disp, zoom=z, xanchor=0.5, yanchor=0.5)
        return Transform(disp, zoom=z)


