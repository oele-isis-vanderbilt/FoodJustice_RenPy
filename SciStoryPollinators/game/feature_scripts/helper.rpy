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

label show_argument_screen:
    call screen argument_writing("Why should the mayor care about this?")
    return