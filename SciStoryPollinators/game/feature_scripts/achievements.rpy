# Enable Ren'Py developer features (console, reloads, error tracing, etc.)
define config.developer = True

# Persistent store of unlocked achievements (survives saves/new games).
# 'default' sets an initial value only if none exists yet.
default persistent.achievements = {}
default achievement_popup_uid = 0

init python:
    def clear_all_achievements():
        """Utility helper to wipe all achievement progress."""
        persistent.achievements.clear()
        renpy.save_persistent()
        renpy.notify("All achievements cleared.")

# This is the list of all achievements in the game.
# Each achievement has a unique "key", a display "name", "desc" (description), and "icon" path.
define achievement_list = [
    {
        "key": "FRIEND",
        "name": "A New Friend",
        "desc": "Talk to Elliot for the first time.",
        "icon": "icons/icon_achieve_FRIEND.png"
    },
    {
        "key": "SOCIAL",
        "name": "Social Butterfly",
        "desc": "Speak to everyone in town.",
        "icon": "icons/icon_achieve_SOCIAL.png"
    },
    {
        "key": "VISIT",
        "name": "Local Tourist",
        "desc": "Visit all the locations in town.",
        "icon": "icons/icon_achieve_VISIT.png"
    },
    {
        "key": "ARGUMENT",
        "name": "Well-Constructed",
        "desc": "Draft your first argument.",
        "icon": "icons/icon_achieve_ARGUMENT.png"
    },
    {
        "key": "REVISION5",
        "name": "Work in Progress",
        "desc": "Revise your argument 5 times.",
        "icon": "icons/icon_achieve_REVISION3.png"
    },
    {
        "key": "FEEDBACK",
        "name": "Peer Reviewed",
        "desc": "Get feedback from Riley on your argument.",
        "icon": "icons/icon_achieve_FEEDBACK.png"
    },
    {
        "key": "NOTES5",
        "name": "Note to Self",
        "desc": "Take at least 5 notes.",
        "icon": "icons/icon_achieve_NOTES5.png"
    },
    {
        "key": "NOTES10",
        "name": "Duly Noted",
        "desc": "Take at least 10 notes.",
        "icon": "icons/icon_achieve_NOTES10.png"
    },
    {
        "key": "GARDENCHAT",
        "name": "Garden Gossip",
        "desc": "Ask questions to everyone in the garden.",
        "icon": "icons/icon_achieve_GARDENCHAT.png"
    },
    {
        "key": "FOODLABCHAT",
        "name": "Food for Thought",
        "desc": "Ask questions to everyone in the food lab.",
        "icon": "icons/icon_achieve_FOODLABCHAT.png"
    },
    # {
    #     "key": "TULIP",
    #     "name": "Blooming Friendship",
    #     "desc": "Befriend Tulip.",
    #     "icon": "icons/icon_achieve_TULIP.png"
    # },
    # {
    #     "key": "NEGATIVE",
    #     "name": "Reluctant Hero",
    #     "desc": "You were hesitant to help Elliot and Tulip at first.",
    #     "icon": "icons/icon_achieve_NEGATIVE.png"
    # },
    # {
    #     "key": "POSITIVE",
    #     "name": "Eager Beaver",
    #     "desc": "You were eager to help Elliot and Tulip.",
    #     "icon": "icons/icon_achieve_POSITIVE.png"
    # },
    # {
    #     "key": "SHUTDOWN",
    #     "name": "Talk to the Hand",
    #     "desc": "You shut down Cyrus at every opportunity.",
    #     "icon": "icons/icon_achieve_SHUTDOWN.png"
    # },
    {
        "key": "UNDECIDED",
        "name": "Second Try is the Charm",
        "desc": "The mayor hasn’t been convinced…yet.",
        "icon": "icons/icon_achieve_UNDECIDED.png"
    },
    {
        "key": "CONVINCEGARDEN",
        "name": "Seeds of Change",
        "desc": "Convince the mayor to build a garden.",
        "icon": "icons/icon_achieve_GARDEN.png"
    },
    {
        "key": "CONVINCEPARKING",
        "name": "Concrete Jungle",
        "desc": "Convince the mayor to build a parking lot.",
        "icon": "icons/icon_achieve_PARKING.png"
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

    def _next_achievement_popup_uid():
        renpy.store.achievement_popup_uid += 1
        return renpy.store.achievement_popup_uid

    def unlock_achievement(key, pause_time=5):
        persistent.achievements[key] = True
        ach = achievement_map.get(key, {})
        log_http(
            current_user,
            action="AchievementUnlocked",
            view=current_label,
            payload={
                "achievement": key,
                "name": ach.get("name"),
                "location": getattr(renpy.store, "currentlocation", None),
                "character_in_discussion": last_spoken_character,
            },
        )
        _show_achievement_popup(key, pause_time)

    def _show_achievement_popup(key, pause_time=5):
        if not key:
            return

        uid = _next_achievement_popup_uid()
        renpy.hide_screen("achievement_popup")
        renpy.show_screen("achievement_popup", key=key, uid=uid, duration=pause_time)
        renpy.restart_interaction()

    def _hide_achievement_popup(uid):
        if uid == renpy.store.achievement_popup_uid:
            renpy.hide_screen("achievement_popup")

    def ensure_unlocked(key, condition):
        if condition and not persistent.achievements.get(key, False):
            unlock_achievement(key)

    def _character_records():
        directory = character_directory
        if isinstance(directory, dict):
            directory = list(directory.values())
        return [ch for ch in directory if isinstance(ch, dict)]

    def _spoken_by_name():
        spoken = {}
        for ch in _character_records():
            name = ch.get("name")
            if name:
                spoken[name] = ch.get("spoken")
        return spoken

    def achieve_social():
        chars = _character_records()
        ensure_unlocked("SOCIAL", chars and all(ch.get("spoken") for ch in chars))
        achieve_gardenchat()
        achieve_foodlabchat()

    def achieve_visit():
        required_locations = {"Food Lab", "Garden", "Beehives", "Empty Lot"}
        visited = set(getattr(renpy.store, "visited_list", []) or [])
        ensure_unlocked("VISIT", required_locations.issubset(visited))

    def achieve_argument():
        attempts = getattr(renpy.store, "argument_attempts", 0)
        edits = getattr(renpy.store, "argument_edits", 0)

        ensure_unlocked("ARGUMENT", attempts >= 1 or edits >= 1)
        ensure_unlocked("REVISION5", edits >= 5)

    def achieve_feedback():
        ensure_unlocked("FEEDBACK", True)

    def achieve_notes5():
        notes = getattr(renpy.store, "notebook", []) or []
        saved_notes = [n for n in notes if isinstance(n, dict) and n.get("type") != "placeholder-note"]
        ensure_unlocked("NOTES5", len(saved_notes) >= 5)

    def achieve_notes10():
        notes = getattr(renpy.store, "notebook", []) or []
        saved_notes = [n for n in notes if isinstance(n, dict) and n.get("type") != "placeholder-note"]
        ensure_unlocked("NOTES10", len(saved_notes) >= 10)

    def achieve_gardenchat():
        required = {"Victor", "Wes", "Nadia", "Alex", "Cora"}
        spoken = _spoken_by_name()
        ensure_unlocked("GARDENCHAT", all(spoken.get(name) for name in required))

    def achieve_foodlabchat():
        required = {"Amara", "Riley"}
        spoken = _spoken_by_name()
        ensure_unlocked("FOODLABCHAT", all(spoken.get(name) for name in required))

    def achieve_undecided():
        attempts = getattr(renpy.store, "mayor_attempts", 0)
        convinced = getattr(renpy.store, "mayorconvinced", False)
        supports_parking = getattr(renpy.store, "mayor_supports_parking", False)
        ensure_unlocked("UNDECIDED", attempts >= 1 and not convinced and not supports_parking)

    def achieve_convincegarden():
        ensure_unlocked("CONVINCEGARDEN", getattr(renpy.store, "mayorconvinced", False))

    def achieve_convinceparking():
        supports_parking = getattr(renpy.store, "mayor_supports_parking", None)
        if supports_parking is None:
            supports_parking = getattr(renpy.store, "mayor_final_decision", "") == "parking"
        ensure_unlocked("CONVINCEPARKING", bool(supports_parking))

# ---------------------------------------------------------------------------
# Popup shown when an achievement unlocks (bottom-right)
# ---------------------------------------------------------------------------
screen achievement_popup(key, uid=None, duration=5):
    zorder 200
    
    $ ach = achievement_map.get(key)

    if ach:
        if duration:
            timer duration action Function(_hide_achievement_popup, uid)

        frame at popup_fade:
            xalign 0.98
            yalign 0.98
            padding (24, 18)
            background Solid("#333333E6")
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

label _show_achievement_popup_ctx(key=None, pause_time=5):
    $ _show_achievement_popup(key, pause_time)
    return

# ---------------------------------------------------------------------------
# Reusable row for the achievements list (reduces duplication)
# ---------------------------------------------------------------------------
screen achievement_row(ach, width=600, height=70):
    fixed:
        xsize width
        ysize height
        
        $ unlocked = persistent.achievements.get(ach["key"], False)

        frame:
            if unlocked:
                background Frame("#ffffff09")
            else:
                background Frame("#ffffff32")
            xsize width
            ysize height
            padding (8, 6, 8, 6)

            # if not persistent.achievements.get(ach["key"], False):
            #     add Solid("#8888", xsize=width, ysize=height) xpos 0 ypos 0

            hbox:
                yalign 0.5
                spacing 20

                if ach["icon"]:
                    add ach["icon"] size (64, 64) yalign 0.5

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

# ---------------------------------------------------------------------------
# Achievements menu screen
# - If total <= 7: single centered column under the header.
# - If total  > 7: two centered columns; items after the first 7 wrap into column 2.
# ---------------------------------------------------------------------------
screen achievements_screen():
    tag menu
    modal True
    add Solid("#00000080") 
    on "show" action Function(lock_dialogue_advancement, "achievements")
    on "hide" action Function(unlock_dialogue_advancement, "achievements")

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
                hover darken_hover(exit_btn, 0.40)
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
                spacing 8
                for ach in achievement_list:
                    use achievement_row(ach)
        else:
            # -------- Two centered columns --------
            $ first_col = achievement_list[:max_per_col]     # first 7
            $ second_col = achievement_list[max_per_col:]    # everything after 7

            hbox:
                xalign 0.5         # center the column group under the header
                spacing 12

                vbox:
                    spacing 8
                    for ach in first_col:
                        use achievement_row(ach)

                vbox:
                    spacing 8
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
