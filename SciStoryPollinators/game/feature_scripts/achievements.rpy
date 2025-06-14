define config.developer = True

default persistent.achievements = {}

#this is the list of all the achievements throughout the game. each one should have a name, description, and an icon.
#icons should be a 64x64 pixel white icon on a transparent background, and should be placed in the "icons" folder with the filename "icon_achieve_#_name.png" where X is the number of the achievement and name is a shorted 1-word reference for the achievement

define achievement_list = [
    {
        "name": "A New Friend",
        "desc": "Talk to Elliot for the first time.",
        "icon": "icons/icon_achieve_1_friend.png"
    },
]

#in script.rpy, you can unlock an achievement by calling the function unlock_achievement("name_of_achievement", pause_time=10) 
#the pause_time is optional and defaults to 5 seconds, which is how long the achievement popup will be displayed before it fades out


#everything below this point is the logic for displaying the achievement popup when an achievement is unlocked and shouldn't need to be touched for individual achievement edits

transform popup_fade:
    alpha 0.0
    linear 0.3 alpha 1.0
    pause 2.2
    linear 0.3 alpha 0.0

init python:
    def unlock_achievement(name, pause_time=5):
        persistent.achievements[name] = True
        renpy.show_screen("achievement_popup", name)
        renpy.pause(pause_time, hard=True)
        renpy.hide_screen("achievement_popup")