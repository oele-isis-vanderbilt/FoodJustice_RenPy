default dev_screen_enabled = False
default dev_screen_messages = []

init python:
    def dev_print(msg):
        dev_screen_messages.append(str(msg))
        dev_screen_messages[:] = dev_screen_messages[-10:]

    def dev_clear():
        dev_screen_messages.clear()

    def toggle_dev_screen():
        global dev_screen_enabled
        dev_screen_enabled = not dev_screen_enabled

# List of character conversation labels for jump buttons
define dev_char_labels = [
    ("Elliot", "elliot_chatting"),
    ("Amara", "amara_chatting"),
    ("Riley", "riley_chatting"),
    ("Wes", "wes_chatting"),
    ("Nadia", "nadia_chatting"),
    ("Victor", "victor_chatting"),
    ("Alex", "alex_chatting"),
    ("Cora", "cora_chatting"),
    ("Cyrus", "cyrus_chatting"),
    ("Mayor Watson", "watson_chatting"),
    ("Tulip", "tulipchat"),
]

# Calculate number of rows for the grid
define dev_grid_rows = (len(dev_char_labels) + 1) // 2

# The developer overlay screen
screen developer_overlay():
    zorder 2000  # Make sure this is higher than any other screen in your project

    if dev_screen_enabled:
        frame:
            style "dev_frame"
            align (0.01, 0.01)
            viewport:
                draggable True
                mousewheel True
                scrollbars "vertical"
                ysize 900  # Adjust as needed for your window size
                vbox:
                    null height 12

                    text "Game States:" style "dev_label"
                    null height 8
                    vbox:
                        spacing 4
                        text "Argument Attempts: [argument_attempts]" style "dev_msg"
                        text "Mayor Attempts: [mayor_attempts]" style "dev_msg"               
                        text "Mayor Convinced? [mayorconvinced]" style "dev_msg"

                        hbox:
                            spacing 8
                            textbutton "Toggle" action SetVariable("mayorconvinced", not mayorconvinced) style "dev_jump_button"                   

                    null height 12

                    text "Notebook:" style "dev_label"
                    null height 8
                    vbox:
                        spacing 4
                        $ total_notes = len(notebook)
                        $ character_saved_notes = len([n for n in notebook if n.get("type") == "character-saved"])
                        $ user_written_notes = len([n for n in notebook if n.get("type") == "user-written"])
                        text "Total Note Count: [total_notes]" style "dev_msg"
                        text "Character-Saved Notes: [character_saved_notes]" style "dev_msg"
                        text "User-Written Notes: [user_written_notes]" style "dev_msg"
                        text "Argument Edits: [argument_edits]" style "dev_msg"
                        textbutton "Add Placeholder Note":
                            action Function(note, "lorem ipsom...", "example speaker", ["tag1", "tag2"], "character-saved")
                            style "dev_jump_button"

                    null height 12

                    text "Location States:" style "dev_label"
                    null height 8
                    vbox:
                        spacing 4
                        text "Hives Visited? [hivesvisit]" style "dev_msg"
                        text "Lot Visited? [emptylotvisit]" style "dev_msg"
                        text "Lab Visited? [foodlabvisit]" style "dev_msg"
                        text "Garden Visited? [gardenvisit]" style "dev_msg"
                        text "Starting Place: [startplace]" style "dev_msg"

                        null height 8

                        text "Set Starting Place:" style "dev_label"
                        null height 8

                        hbox:
                            spacing 8
                            for _label, _value, _structure in [("City", "city", "garage"), ("Rural", "rural", "lot"), ("Suburb", "suburb", "lot")]:
                                vbox:
                                    textbutton _label action [SetVariable("startplace", _value), SetVariable("structure", _structure)] selected (startplace == _value) style "dev_jump_button"
                                    if startplace == _value:
                                        text "(structure: [_structure])" style "dev_msg"

                    null height 12

                    text "Character States:" style "dev_label"
                    null height 8
                    vbox:
                        spacing 4
                        for char in character_directory:
                            text "[char['name']] | chats = [char['chats']] | spoken = [char['spoken']]" style "dev_msg"

                    null height 12

                    text "Jump to Conversation:" style "dev_label"
                    null height 8
                    grid 2 dev_grid_rows:
                        spacing 4
                        for _btn_name, _btn_label in dev_char_labels:
                            textbutton _btn_name action Jump(_btn_label) style "dev_jump_button"

                    null height 12

# Styles for the developer overlay
style dev_frame is default:
    background "#222f"
    padding (10, 10, 10, 10)
    xalign 0.0
    yalign 0.0
    xsize 600

style dev_title is default:
    color "#ff9"
    size 22
    bold True

style dev_label is default:
    color "#fff"
    size 16
    bold True

style dev_msg is default:
    color "#0f0"
    size 14

style dev_jump_button is default:
    padding (12, 8, 12, 8)
    background "#1558b0"               # Button background color
    hover_background "#021b3c"
    focus_mask True                     # Ensures focus is visible
    xminimum 140
    yminimum 40

style dev_jump_button_text is default:
    bold True
    color "#fff"
    size 18
    font "DejaVuSans.ttf"               # Use a readable sans-serif font

    
# Show the developer overlay on top of all screens
init -999 python:
    config.overlay_screens.append("developer_overlay")

# Keybind to toggle the developer overlay (Shift+D)
define config.keymap['toggle_dev_screen'] = [ 'shift_d' ]

