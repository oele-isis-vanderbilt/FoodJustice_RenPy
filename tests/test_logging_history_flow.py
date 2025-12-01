from types import SimpleNamespace


def test_log_with_history_updates_both_streams(logging_module, renpy_store, monkeypatch):
    history_calls = []
    renpy_store.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history_calls.append(kwargs)
    )

    captured = []

    def _fake_log_http(user, action, view, payload):
        captured.append(
            {"user": user, "action": action, "view": view, "payload": payload}
        )

    monkeypatch.setattr(logging_module, "log_http", _fake_log_http)
    logging_module.current_user = "tester"
    logging_module.current_label = "intro"

    logging_module.log_with_history(
        action="NotebookEvent",
        payload={"message": "opened"},
        history_who="Narrator",
        history_what="Player opened the notebook",
        history_kind="event",
    )

    assert captured == [
        {
            "user": "tester",
            "action": "NotebookEvent",
            "view": "intro",
            "payload": {"message": "opened"},
        }
    ]
    assert history_calls == [
        {"kind": "event", "who": "Narrator", "what": "Player opened the notebook"}
    ]


def test_record_history_entry_is_safe_without_narrator(logging_module, renpy_store):
    if hasattr(renpy_store, "narrator"):
        delattr(renpy_store, "narrator")

    # Should not raise even when narrator is missing.
    logging_module.record_history_entry("Narrator", "Text")


def test_log_player_choice_emits_history(logging_module, renpy_store, monkeypatch):
    history_calls = []
    renpy_store.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history_calls.append(kwargs)
    )
    renpy_store.__ = lambda text: f"T({text})"

    captured = []

    def _fake_log_http(user, action, view, payload):
        captured.append(
            {"user": user, "action": action, "view": view, "payload": payload}
        )

    monkeypatch.setattr(logging_module, "log_http", _fake_log_http)
    logging_module.current_user = "tester"
    logging_module.current_label = "scene1"

    logging_module.remember_menu_choice("Help me")
    logging_module.log_player_choice()

    assert captured and captured[0]["payload"]["text"] == "Help me"
    assert history_calls[-1]["who"] == "T(Choice:)"
    assert history_calls[-1]["what"] == "T(Help me)"


def test_notify_with_history(logging_module, renpy_module, renpy_store, monkeypatch):
    history_calls = []
    renpy_store.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history_calls.append(kwargs)
    )
    notified = []
    monkeypatch.setattr(renpy_module, "notify", lambda message: notified.append(message))

    logging_module.notify_with_history("Mission update", history_who="System", history_what="Mission update")

    assert notified == ["Mission update"]
    assert history_calls and history_calls[-1]["who"] == "System"


def test_set_current_location_logs(logging_module, renpy_store, monkeypatch):
    history_calls = []
    renpy_store.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history_calls.append(kwargs)
    )
    captured = []

    def _fake_log_http(user, action, view, payload):
        captured.append({"action": action, "payload": payload})

    monkeypatch.setattr(logging_module, "log_http", _fake_log_http)
    logging_module.current_user = "tester"
    logging_module.current_label = "start"

    logging_module.set_current_location("garden")

    assert renpy_store.currentlocation == "garden"
    assert captured and captured[-1]["action"] == "LocationChanged"
    assert history_calls and "garden" in history_calls[-1]["what"].lower()
