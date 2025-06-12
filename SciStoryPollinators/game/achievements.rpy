init python:
# each 'achievement(_)' block defines a specific achievement

    config.achievements = [
        Achievement(
            "A New Friend", #achievement title
            "Talk to Elliot for the first time.", #achievement description
            "gui/achv_friend.png"  #path to achievement icon
        ),
        Achievement(
            "Garden Expert",
            "Convince the mayor to build a garden.",
            "gui/achv_garden.png"
        ),
        Achievement(
            "Bee Curious",
            "Ask Nadia three questions about bees.",
            "gui/achv_bee.png"
        ),
        Achievement(
            "Food Scientist",
            "Learn about food science from Amara.",
            "gui/achv_science.png"
        ),
    ]

    screen achievement_popup(name):
    # Find the achievement object by name
    $ ach = None
    for a in config.achievements:
        if a.name == name:
            ach = a
            break

    if ach:
        frame:
            background "#222c"
            xalign 0.98
            yalign 0.1
            padding (20, 20)
            vbox:
                if ach.icon:
                    add ach.icon size (64, 64)
                text "[ach.name]" size 28 color "#ffd700" bold True
                text ach.description size 20 color "#fff"

    #call this function in script.rpy to unlaoack an achievement! 
    #name is the achievement title (case sensitive!); pause_time is a duration
    init python:
    def unlock_achievement(name):
        achievement.grant(name)
        renpy.show_screen("achievement_popup", name)
        renpy.pause(2.5, hard=True)
        renpy.hide_screen("achievement_popup")
