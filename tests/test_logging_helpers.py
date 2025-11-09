# Ensures persistent log history trims to the configured maximum size.
def test_mirror_to_persistent_caps_history(logging_module, persistent_state):
    logging_module._max_persistent_logs = 2
    persistent_state.logs = [
        {"scene": "old1"},
        {"scene": "old2"},
    ]

    logging_module._mirror_to_persistent("new_scene", "stamp", "content", "csv")

    assert len(persistent_state.logs) == 2
    assert persistent_state.logs[-1]["scene"] == "new_scene"


# Confirms unsent upload queue keeps only the newest entries within its cap.
def test_enqueue_for_upload_caps_queue(logging_module, persistent_state):
    logging_module._max_queue = 2
    persistent_state.unsent = [
        {"scene": "old1"},
        {"scene": "old2"},
    ]

    logging_module._enqueue_for_upload("new_scene", "stamp", "content", "csv")

    assert len(persistent_state.unsent) == 2
    assert persistent_state.unsent[-1]["scene"] == "new_scene"
