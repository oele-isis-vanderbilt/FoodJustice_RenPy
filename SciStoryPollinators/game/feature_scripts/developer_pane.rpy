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
    if dev_screen_enabled:
        frame:
            style "dev_frame"
            align (0.01, 0.01)
            vbox:
                spacing 6
                text "Developer Overlay" style "dev_title"
                # textbutton "Hide" action Function(toggle_dev_screen)
                # textbutton "Clear Log" action Function(dev_clear)
                null height 8
                # text "Messages:" style "dev_label"

                viewport:
                    draggable True
                    mousewheel True
                    ysize 100
                    vbox:
                        for msg in dev_screen_messages:
                            text msg style "dev_msg"
                null height 8
                text "Character Stats:" style "dev_label"
               
                vbox:
                    for _stat_char in character_dictionary:
                        text "[_stat_char['name']]: chats=[_stat_char['chats']], spoken=[_stat_char['spoken']]" style "dev_msg"
                null height 8
               
                text "Jump to Conversation:" style "dev_label"
               
                grid 2 dev_grid_rows:
                    spacing 2
                    for _btn_name, _btn_label in dev_char_labels:
                        textbutton _btn_name action Jump(_btn_label) style "dev_jump_button"

# Styles for the developer overlay
style dev_frame is default:
    background "#222f"   # More opaque dark background (f = 15/16, almost solid)
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

