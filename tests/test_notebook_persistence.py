from types import SimpleNamespace


def _setup_notebook_module(notebook_module):
    notebook_module.notebook = []
    notebook_module.note_id_counter = 0
    notebook_module.current_user = "tester"
    notebook_module.current_label = "start"
    notebook_module.save_name = "slot-1"
    notebook_module.edited_note_id = None
    history = []
    notebook_module.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history.append(kwargs)
    )
    return history


# Checks new_note logs, auto-tags, and triggers screenshot/save side effects.
def test_new_note_records_log_and_media(notebook_module, renpy_store, renpy_module):
    history = _setup_notebook_module(notebook_module)
    logs = []
    notebook_module.log_http = lambda *args, **kwargs: logs.append((args, kwargs))

    shots = {"count": 0, "saves": 0, "blocked": 0}
    orig_take = renpy_module.take_screenshot
    orig_save = renpy_module.save
    orig_block = renpy_module.block_rollback

    renpy_module.take_screenshot = lambda: shots.__setitem__("count", shots["count"] + 1)
    renpy_module.save = lambda *_args, **_kwargs: shots.__setitem__(
        "saves", shots["saves"] + 1
    )
    renpy_module.block_rollback = lambda: shots.__setitem__(
        "blocked", shots["blocked"] + 1
    )

    renpy_store.tagBuckets = {"pollinators": ["bee"]}
    renpy_store.auto_tag_user_notes = True

    try:
        note_id = notebook_module.new_note(
            "Bee facts help the garden", "Player", ["custom"], "user-written"
        )
    finally:
        renpy_module.take_screenshot = orig_take
        renpy_module.save = orig_save
        renpy_module.block_rollback = orig_block

    assert note_id == 0
    assert notebook_module.note_id_counter == 1
    assert notebook_module.notebook[0]["tags"] == ["custom", "pollinators"]
    assert logs and logs[0][0][0] == "tester"
    assert shots["count"] == 1
    assert shots["saves"] == 1
    assert shots["blocked"] >= 1
    assert history, "Narrator history should record the new note."


# Prevents duplicate character-dialog notes by returning the existing ID.
def test_new_note_deduplicates_character_dialog(notebook_module, renpy_store, renpy_module):
    _setup_notebook_module(notebook_module)
    notebook_module.notebook = [
        {
            "id": 12,
            "source": "Elliot",
            "content": "Gardens feed everyone!",
            "tags": ["garden"],
            "type": "character-dialog",
        }
    ]
    notebook_module.note_id_counter = 13

    note_id = notebook_module.new_note(
        "Gardens feed everyone!", "Elliot", ["garden"], "character-dialog"
    )

    assert note_id == 12
    assert len(notebook_module.notebook) == 1
    assert renpy_module._last_notify == "Note Already Saved"


# Verifies auto-tagging honors the global toggle for user-written notes.
def test_auto_tag_respects_toggle(notebook_module, renpy_store):
    _setup_notebook_module(notebook_module)
    renpy_store.tagBuckets = {"pollinators": ["bee"]}

    renpy_store.auto_tag_user_notes = False
    notebook_module.new_note("Bees rule.", "Player", ["custom"], "user-written")

    assert notebook_module.notebook[0]["tags"] == ["custom"]


# Ensures deletenote updates notebook state, logs, notifications, and screenshots.
def test_deletenote_removes_and_logs(notebook_module, renpy_module):
    history = _setup_notebook_module(notebook_module)
    notebook_module.notebook = [
        {
            "id": 1,
            "source": "Tulip",
            "content": "Take more notes!",
            "tags": [],
            "type": "character-dialog",
        }
    ]

    logs = []
    notebook_module.log_http = lambda *args, **kwargs: logs.append((args, kwargs))

    shots = {"count": 0}
    orig_take = renpy_module.take_screenshot
    orig_save = renpy_module.save
    renpy_module.take_screenshot = lambda: shots.__setitem__("count", shots["count"] + 1)
    renpy_module.save = lambda *_args, **_kwargs: None

    try:
        notebook_module.deletenote(1)
    finally:
        renpy_module.take_screenshot = orig_take
        renpy_module.save = orig_save

    assert notebook_module.notebook == []
    assert renpy_module._last_notify == "Note Deleted"
    assert logs and logs[0][0][0] == "tester"
    assert history and history[-1]["who"].startswith("You erased")
    assert shots["count"] == 1
