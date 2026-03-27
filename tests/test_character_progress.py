def _install_character_state(helper_module, renpy_store):
    helper_module.character_directory = [
        {"id": "riley", "name": "Riley"},
        {"id": "amara", "name": "Amara"},
        {"id": "wes", "name": "Wes"},
        {"id": "nadia", "name": "Nadia"},
        {"id": "mayor", "name": "Mayor Watson"},
    ]
    renpy_store.character_progress = {}
    renpy_store.spoken_list = []
    helper_module.spoken_list = renpy_store.spoken_list


def test_update_char_stats_uses_save_backed_progress(helper_module, renpy_store):
    _install_character_state(helper_module, renpy_store)

    helper_module.update_char_stats("Riley")
    helper_module.update_char_stats("Riley")

    assert renpy_store.character_progress["riley"]["chats"] == 2
    assert renpy_store.character_progress["riley"]["spoken"] is True
    assert helper_module.get_character_chats("Riley") == 2
    assert helper_module.get_character_spoken("Riley") is True
    assert renpy_store.spoken_list == ["Riley", "Riley"]


def test_character_progress_migrates_from_spoken_list(helper_module, renpy_store):
    _install_character_state(helper_module, renpy_store)
    renpy_store.spoken_list = ["Nadia", "Wes"]

    helper_module.ensure_character_progress_state()

    assert renpy_store.character_progress["nadia"]["spoken"] is True
    assert renpy_store.character_progress["nadia"]["chats"] == 1
    assert renpy_store.character_progress["wes"]["spoken"] is True
    assert renpy_store.character_progress["wes"]["chats"] == 1
    assert renpy_store.character_progress["riley"]["spoken"] is False
    assert renpy_store.character_progress["riley"]["chats"] == 0


def test_character_progress_preserves_legacy_record_values(helper_module, renpy_store):
    helper_module.character_directory = [
        {"id": "mayor", "name": "Mayor Watson", "chats": "3", "spoken": True, "approval": 2},
    ]
    renpy_store.character_progress = {}
    renpy_store.spoken_list = []

    helper_module.ensure_character_progress_state()

    assert renpy_store.character_progress["mayor"]["chats"] == 3
    assert renpy_store.character_progress["mayor"]["spoken"] is True
    assert renpy_store.character_progress["mayor"]["approval"] == 2


def test_achievements_read_character_progress(achievements_module, renpy_store, persistent_state):
    persistent_state.achievements.clear()
    renpy_store.character_progress = {
        "elliot": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "riley": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "amara": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "victor": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "wes": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "nadia": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "alex": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
        "cora": {"spoken": True, "chats": 1, "questions": 0, "approval": 0},
    }
    achievements_module.character_directory = [
        {"id": "elliot", "name": "Elliot"},
        {"id": "riley", "name": "Riley"},
        {"id": "amara", "name": "Amara"},
        {"id": "victor", "name": "Victor"},
        {"id": "wes", "name": "Wes"},
        {"id": "nadia", "name": "Nadia"},
        {"id": "alex", "name": "Alex"},
        {"id": "cora", "name": "Cora"},
    ]

    achievements_module.achieve_social()

    assert persistent_state.achievements.get("SOCIAL") is True
    assert persistent_state.achievements.get("GARDENCHAT") is True
    assert persistent_state.achievements.get("FOODLABCHAT") is True
