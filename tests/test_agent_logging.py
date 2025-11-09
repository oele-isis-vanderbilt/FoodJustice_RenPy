from types import SimpleNamespace


# Ensures log_http gracefully logs when renpy.fetch raises (e.g., offline).
def test_log_http_handles_fetch_errors(logging_module, renpy_module):
    entries = []
    orig_fetch = renpy_module.fetch
    orig_log = renpy_module.log

    def failing_fetch(*args, **kwargs):
        raise RuntimeError("network down")

    renpy_module.fetch = failing_fetch
    renpy_module.log = lambda message: entries.append(message)

    try:
        logging_module.log_http("player1", {"k": "v"}, action="TestAction", view="start")
    finally:
        renpy_module.fetch = orig_fetch
        renpy_module.log = orig_log

    assert any("TestAction" in str(msg) for msg in entries)


# Confirms label_callback records jumps and updates the tracked current label.
def test_label_callback_updates_current_label(logging_module):
    calls = []
    logging_module.current_user = "tester"
    logging_module.current_label = "old"
    logging_module.log_http = lambda *args, **kwargs: calls.append((args, kwargs))

    logging_module.label_callback("garden", "jump")

    assert logging_module.current_label == "garden"
    assert calls, "log_http should be invoked for label transitions."
    _, kwargs = calls[0]
    assert kwargs["action"].startswith("PlayerJumpedLabel(garden")


# Spot-checks agent_setup payload contents for argument-sharing contexts.
def test_agent_setup_argument_context(eca_module, renpy_module):
    eca_module.notebook = [{"id": 1}, {"id": 2}]
    eca_module.spoken_list = ["Elliot", "Riley"]
    eca_module.visited_list = ["Garden", "Food Lab"]
    eca_module.customnotecount = 1
    eca_module.argument_attempts = 3
    eca_module.currentlocation = "garden"
    history = []
    eca_module.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history.append(kwargs)
    )

    link, payload = eca_module.agent_setup(
        "FoodJustice_RileyEvaluation", "Text", "riley", "Riley"
    )

    assert link.endswith("/riley")
    assert payload["gameState"]["contextType"] == "FoodJustice_RileyEvaluation"
    assert payload["gameState"]["numNotes"] == 2
    assert payload["gameState"]["argument"] == "Text"
    assert history, "Narrator history should capture the utterance."


# Asserts long responses are split into sequential voice lines for playback.
def test_eca_length_check_splits_long_response(eca_module):
    long_response = ("Sentence one. Sentence two is also here. Sentence three continues. " * 5).strip()
    split, first, second = eca_module.eca_length_check(long_response)
    assert split is True
    assert first.endswith(".")
    assert second
