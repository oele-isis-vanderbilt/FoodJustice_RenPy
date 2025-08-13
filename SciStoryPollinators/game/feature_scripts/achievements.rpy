define config.developer = True

default persistent.achievements = {}

#this is the list of all the achievements throughout the game. each one should have a name, description, and an icon.

define achievement_list = [
    {
        "key": "FRIEND",  # <-- comma after each field
        "name": "A New Friend",
        "desc": "Talk to Elliot for the first time.",
        "icon": "icons/icon_achieve_1_friend.png"
    },
    {
        "key": "SOCIAL",
        "name": "Social Butterfly",
        "desc": "You spoke to everyone in town!",
        "icon": "icons/icon_achieve_1_friend.png"
    },
]

# in script.rpy, you can unlock an achievement by calling the function 
## unlock_achievement("name_of_achievement", pause_time=10) 

# the pause_time is optional and defaults to 5 seconds, which is how long the achievement popup will be displayed before it fades out

#----------DO NOT EDIT ANYTHING BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING----------



# everything below this point is the logic for displaying the achievement popup when an achievement is unlocked and shouldn't need to be touched for individual achievement edits

init python:
    def unlock_achievement(key, pause_time=5):
        persistent.achievements[key] = True
        renpy.show_screen("achievement_popup", key)
        renpy.pause(pause_time, hard=True)
        renpy.hide_screen("achievement_popup")

    # SOCIAL BUTTERFLY achievement logic
    ## called at the end of any conversation with any character
    def achieve_social():
        # Unlock if all characters in the dictionary have spoken == True
        if all(char["spoken"] for char in character_directory):
            if not persistent.achievements.get("SOCIAL", False):
                unlock_achievement("SOCIAL")

    def safe_show_say():
        # Only show the say screen if in-game and not in the main menu
        if not renpy.context()._main_menu:
            renpy.show_screen("say")

screen achievement_popup(key):
    zorder 200
    $ ach = [a for a in achievement_list if a["key"] == key][0]
    frame at popup_fade:
        background Frame("#222c", 12, 12)
        xalign 0.98
        yalign 0.98   # Bottom right corner
        padding (24, 18)
        xmaximum 420
        yminimum 90
        vbox:
            spacing 8
            hbox:
                spacing 16
                if ach["icon"]:
                    add ach["icon"] size (64, 64)
                vbox:
                    text "Achievement Unlocked!" size 18 color "#ffffff" bold True
                    text "[ach['name']]" size 26 color "#ffffff" bold True
                    text ach["desc"] size 16 color "#ccc" xalign 0.0 italic True

screen achievements_screen():
    tag menu
    modal True

    # This transparent button absorbs all clicks outside the popup
    button:
        xysize (config.screen_width, config.screen_height)
        action NullAction()
        style "empty"

    frame:
        xalign 0.5
        yalign 0.5
        padding (20, 20)
        background Frame("#222c", 12, 12)
        has vbox

        # Small X button at top-right with padding
        imagebutton:
            idle Transform("icons/button_exit-popup.png", xysize=(36,36))
            hover Transform("icons/button_exit-popup_hover.png", xysize=(36,36))
            action [Return(), Function(safe_show_say)]
            anchor (1.0, 0.0)
            pos (0.98, 0.02)  # 2% padding from top-right

        spacing 16
        text "Achievements" size 32 xalign 0.5

        $ max_per_col = 7 # Maximum achievements per column 
        $ total = len(achievement_list)
        if total <= max_per_col:
            # Single centered column
            hbox:
                spacing 20
                null width 500  # left spacer to center
                vbox:
                    spacing 12
                    for ach in achievement_list:
                        fixed:
                            xsize 500
                            ysize 80
                            frame:
                                background Frame("#222c", 12, 12)
                                xsize 500
                                ysize 80
                                padding (12, 8, 12, 8)
                                hbox:
                                    yalign 0.5
                                    spacing 16
                                    if ach["icon"]:
                                        add ach["icon"] size (48, 48) yalign 0.5
                                    vbox:
                                        yalign 0.5
                                        spacing 2
                                        if persistent.achievements.get(ach["key"], False):
                                            text ach["name"] size 20 color "#aeea00"
                                            text ach["desc"] size 14 color "#fff"
                                        else:
                                            text ach["name"] size 20 color "#888"
                                            text ach["desc"] size 14 color "#bbb"
                        # Overlay must be inside the fixed block, after the frame!
                        if not persistent.achievements.get(ach["key"], False):
                            add Solid("#8888", xsize=500, ysize=80) xpos 0 ypos 0
                null width 500  # right spacer to center
        else:
            # Two columns, up to 7 per column
            $ col1 = achievement_list[:max_per_col]
            $ col2 = achievement_list[max_per_col:max_per_col*2]
            hbox:
                spacing 20
                for col in [col1, col2]:
                    vbox:
                        spacing 12
                        for ach in col:
                            fixed:
                                xsize 500
                                ysize 80
                                frame:
                                    background Frame("#222c", 12, 12)
                                    xsize 500
                                    ysize 80
                                    padding (12, 8, 12, 8)
                                    hbox:
                                        yalign 0.5
                                        spacing 16
                                        if ach["icon"]:
                                            add ach["icon"] size (48, 48) yalign 0.5
                                        vbox:
                                            yalign 0.5
                                            spacing 2
                                            if persistent.achievements.get(ach["key"], False):
                                                text ach["name"] size 20 color "#aeea00"
                                                text ach["desc"] size 14 color "#fff"
                                            else:
                                                text ach["name"] size 20 color "#888"
                                                text ach["desc"] size 14 color "#bbb"
                                if not persistent.achievements.get(ach["key"], False):
                                    add Solid("#8888", xsize=500, ysize=80) xpos 0 ypos 0
        textbutton "Return" action Return() xalign 0.5

transform popup_fade:
    alpha 0.0
    linear 0.3 alpha 1.0
    pause 2.2
    linear 0.3 alpha 0.0
