# Ensures unlocking an achievement flips the persistent flag and shows/hides the popup.
def test_unlock_achievement_sets_flag(achievements_module, persistent_state, renpy_module):
    persistent_state.achievements.clear()
    calls = []
    orig_show = renpy_module.show_screen
    orig_hide = renpy_module.hide_screen
    orig_pause = renpy_module.pause

    def show(name, *args, **kwargs):
        calls.append(("show", name))
        return orig_show(name, *args, **kwargs)

    def hide(name, *args, **kwargs):
        calls.append(("hide", name))
        return orig_hide(name, *args, **kwargs)

    def pause(*args, **kwargs):
        calls.append(("pause", args, kwargs))
        return None

    renpy_module.show_screen = show
    renpy_module.hide_screen = hide
    renpy_module.pause = pause

    try:
        achievements_module.unlock_achievement("FRIEND", pause_time=0)
    finally:
        renpy_module.show_screen = orig_show
        renpy_module.hide_screen = orig_hide
        renpy_module.pause = orig_pause

    assert persistent_state.achievements.get("FRIEND") is True
    assert ("show", "achievement_popup") in calls
    assert any(event[0] == "hide" for event in calls)


# Verifies SOCIAL unlock waits until every tracked character is marked as spoken and
# location-specific chat achievements unlock as soon as their subsets are complete.
def test_character_speaking_achievements(achievements_module, persistent_state):
    persistent_state.achievements.clear()
    achievements_module.character_directory = [
        {"name": "Elliot", "spoken": True},
        {"name": "Riley", "spoken": False},
        {"name": "Amara", "spoken": False},
        {"name": "Victor", "spoken": True},
        {"name": "Wes", "spoken": True},
        {"name": "Nadia", "spoken": True},
        {"name": "Alex", "spoken": True},
        {"name": "Cora", "spoken": True},
    ]

    achievements_module.achieve_social()
    assert persistent_state.achievements.get("SOCIAL") is not True
    assert persistent_state.achievements.get("GARDENCHAT") is True
    assert persistent_state.achievements.get("FOODLABCHAT") is not True

    achievements_module.character_directory[1]["spoken"] = True
    achievements_module.character_directory[2]["spoken"] = True
    achievements_module.achieve_social()
    assert persistent_state.achievements.get("SOCIAL") is True
    assert persistent_state.achievements.get("FOODLABCHAT") is True


# Confirms visit and note-count achievements unlock only after meeting their thresholds.
def test_visit_and_notes_achievements(achievements_module, persistent_state, renpy_store):
    persistent_state.achievements.clear()
    renpy_store.visited_list = ["Food Lab", "Garden", "Beehives"]
    achievements_module.achieve_visit()
    assert persistent_state.achievements.get("VISIT") is not True

    renpy_store.visited_list.append("Empty Lot")
    achievements_module.achieve_visit()
    assert persistent_state.achievements.get("VISIT") is True

    renpy_store.notebook = [{"type": "user-written"} for _ in range(5)]
    achievements_module.achieve_notes5()
    assert persistent_state.achievements.get("NOTES5") is True

    renpy_store.notebook.extend({"type": "user-written"} for _ in range(5))
    achievements_module.achieve_notes10()
    assert persistent_state.achievements.get("NOTES10") is True


# Checks argument and revision milestones alongside the Riley feedback unlock.
def test_argument_progress_and_feedback(achievements_module, persistent_state, renpy_store):
    persistent_state.achievements.clear()
    renpy_store.argument_attempts = 0
    renpy_store.argument_edits = 0

    achievements_module.achieve_argument()
    assert persistent_state.achievements.get("ARGUMENT") is not True

    renpy_store.argument_attempts = 1
    achievements_module.achieve_argument()
    assert persistent_state.achievements.get("ARGUMENT") is True

    renpy_store.argument_edits = 4
    achievements_module.achieve_argument()
    assert persistent_state.achievements.get("REVISION5") is not True

    renpy_store.argument_edits = 5
    achievements_module.achieve_argument()
    assert persistent_state.achievements.get("REVISION5") is True

    achievements_module.achieve_feedback()
    assert persistent_state.achievements.get("FEEDBACK") is True


# Ensures mayor outcome achievements cover undecided, garden, and parking results.
def test_mayor_outcome_achievements(achievements_module, persistent_state, renpy_store):
    persistent_state.achievements.clear()
    renpy_store.mayor_attempts = 1
    renpy_store.mayorconvinced = False
    renpy_store.mayor_supports_parking = False

    achievements_module.achieve_undecided()
    assert persistent_state.achievements.get("UNDECIDED") is True

    renpy_store.mayorconvinced = True
    achievements_module.achieve_convincegarden()
    assert persistent_state.achievements.get("CONVINCEGARDEN") is True

    renpy_store.mayorconvinced = False
    renpy_store.mayor_supports_parking = True
    achievements_module.achieve_convinceparking()
    assert persistent_state.achievements.get("CONVINCEPARKING") is True
