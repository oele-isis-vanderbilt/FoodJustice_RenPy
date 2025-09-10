# Enable Ren'Py developer features (console, reloads, error tracing, etc.)
define config.developer = True

# Persistent store of unlocked achievements (survives saves/new games).
# 'default' sets an initial value only if none exists yet.
default persistent.achievements = {}

# This is the list of all achievements in the game.
# Each achievement has a unique "key", a display "name", "desc" (description), and "icon" path.
define achievement_list = [
    {
        "key": "FRIEND",  # Unique ID used by code
        "name": "A New Friend",  # Title shown to player
        "desc": "Talk to Elliot for the first time.",  # Subtitle/description
        "icon": "icons/icon_achieve_1_friend.png"  # 64x64 fits the popup nicely
    },
    {
        "key": "SOCIAL",
        "name": "Social Butterfly",
        "desc": "Speak to everyone in town!",
        "icon": "icons/icon_achieve_1_friend.png"
    },
    {
        "key": "ARGUMENT",
        "name": "Well-Constructed",
        "desc": "Draft your first argument.",
        "icon": "icons/icon_achieve_1_friend.png"
    },
]

# In script.rpy, you can unlock an achievement by calling:
## unlock_achievement("name_of_achievement", pause_time=10)
# 'pause_time' controls how long the popup stays visible (default 5s).

#----------DO NOT EDIT ANYTHING BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING----------

# The functions below implement unlocking + the popup behavior,
# plus a couple of helper "achieve_*" checkers you can call from story logic.

init python:
    # Fast lookup for screens
    achievement_map = {a["key"]: a for a in achievement_list}

    def unlock_achievement(key, pause_time=5):
        persistent.achievements[key] = True
        renpy.show_screen("achievement_popup", key)
        renpy.pause(pause_time, hard=True)
        renpy.hide_screen("achievement_popup")

    def ensure_unlocked(key, condition):
        if condition and not persistent.achievements.get(key, False):
            unlock_achievement(key)

    def achieve_social():
        # Works if character_directory is a dict or list
        try:
            chars = list(character_directory.values())
        except Exception:
            chars = character_directory
        ensure_unlocked("SOCIAL", all(ch.get("spoken") for ch in chars))

    def achieve_argument():
        ensure_unlocked("ARGUMENT", argument_attempts >= 1)


# ---------------------------------------------------------------------------
# Popup shown when an achievement unlocks (bottom-right)
# ---------------------------------------------------------------------------
screen achievement_popup(key):
    zorder 200
    
    $ ach = achievement_map.get(key)

    if ach:
        frame at popup_fade:
            background Frame("#222c", 12, 12)
            xalign 0.98
            yalign 0.98
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

# ---------------------------------------------------------------------------
# Reusable row for the achievements list (reduces duplication)
# ---------------------------------------------------------------------------
screen achievement_row(ach, width=700, height=100):
    fixed:
        xsize width
        ysize height

        frame:
            background Frame("#222c", 12, 12)
            xsize width
            ysize height
            padding (16, 12, 16, 12)

            hbox:
                yalign 0.5
                spacing 20

                if ach["icon"]:
                    add ach["icon"] size (64, 64) yalign 0.5

                $ unlocked = persistent.achievements.get(ach["key"], False)
                vbox:
                    yalign 0.5
                    spacing 4
                    if unlocked:
                        text ach["name"] size 26 color "#aeea00"
                        text ach["desc"] size 16 color "#ffffff"
                    else:
                        text ach["name"] size 26 color "#888"
                        text ach["desc"] size 16 color "#bbb"

        # Semi-transparent veil over locked items
        if not persistent.achievements.get(ach["key"], False):
            add Solid("#8888", xsize=width, ysize=height) xpos 0 ypos 0

# ---------------------------------------------------------------------------
# Achievements menu screen
# - If total <= 7: single centered column under the header.
# - If total  > 7: two centered columns; items after the first 7 wrap into column 2.
# ---------------------------------------------------------------------------
screen achievements_screen():
    tag menu
    modal True
    add Solid("#00000080")  # black at 50% opacity, tweak hex/alpha to taste

    # Absorb clicks outside the panel
    button:
        xysize (config.screen_width, config.screen_height)
        action NullAction()
        style "empty"

    frame:
        xalign 0.5
        yalign 0.5
        padding (24, 24)
        background Frame("#222222ed", 12, 12)
        has vbox

        # Close button (image optional)
        $ have_close_img = renpy.loadable("images/imagebutton_close.png")
        if have_close_img:
            $ iw, ih = renpy.image_size("images/imagebutton_close.png")
            $ exit_btn = Transform("images/imagebutton_close.png", zoom=50.0 / ih)
            imagebutton:
                tooltip "Close"
                idle exit_btn
                hover exit_btn
                action Hide("achievements_screen")
                anchor (1.0, 0.0)
                pos (0.98, 0.02)
        else:
            textbutton "✕" action Hide("achievements_screen") xalign 1.0

        spacing 16
        text "Achievements" size 40 xalign 0.5 color "#ffffff" bold True

        $ max_per_col = 7
        $ total = len(achievement_list)

        if total <= max_per_col:
            # -------- Single centered stack --------
            vbox:
                xalign 0.5         # center the whole stack under the header
                spacing 16
                for ach in achievement_list:
                    use achievement_row(ach)
        else:
            # -------- Two centered columns --------
            $ first_col = achievement_list[:max_per_col]     # first 7
            $ second_col = achievement_list[max_per_col:]    # everything after 7

            hbox:
                xalign 0.5         # center the column group under the header
                spacing 24

                vbox:
                    spacing 16
                    for ach in first_col:
                        use achievement_row(ach)

                vbox:
                    spacing 16
                    for ach in second_col:
                        use achievement_row(ach)

# ---------------------------------------------------------------------------
# Popup animation
# ---------------------------------------------------------------------------
transform popup_fade:
    alpha 0.0
    linear 0.3 alpha 1.0
    pause 2.2
    linear 0.3 alpha 0.0