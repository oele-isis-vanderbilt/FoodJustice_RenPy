# Validates enabling/disabling voice features resets related store state.
def test_toggle_voice_features_enabled(helper_module, renpy_store):
    helper_module.set_voice_features_enabled(False)
    assert renpy_store.voice_features_enabled is False
    assert renpy_store.voice_input_contexts == 0
    assert renpy_store.voice_input_available is False
    assert renpy_store.voice_recording_active is False

    helper_module.toggle_voice_features_enabled()
    assert renpy_store.voice_features_enabled is True


# Ensures request/release correctly increments contexts and toggles availability.
def test_request_and_release_voice_input(helper_module, renpy_store):
    assert helper_module.request_voice_input() is True
    assert renpy_store.voice_input_contexts == 1
    assert renpy_store.voice_input_available is True

    assert helper_module.release_voice_input() is True
    assert renpy_store.voice_input_contexts == 0
    assert renpy_store.voice_input_available is False


# Confirms requests fail gracefully when voice features are disabled.
def test_request_voice_input_disabled(helper_module, renpy_store):
    helper_module.set_voice_features_enabled(False)
    assert helper_module.request_voice_input() is False
    assert renpy_store.voice_input_contexts == 0
    assert renpy_store.voice_input_available is False


# Voice hardware failures are represented by disabled features; ensure recording toggle
# surfaces a notification and leaves state unchanged.
def test_toggle_voice_recording_handles_disabled_features(helper_module, renpy_store, renpy_module):
    helper_module.set_voice_features_enabled(False)
    helper_module.voice_recording_active = False
    renpy_store.voice_recording_active = False

    helper_module.toggle_voice_recording()

    assert helper_module.voice_recording_active is False
    assert renpy_store.voice_recording_active is False
    assert renpy_module._last_notify == "Voice features disabled"


# Speech input UI can raise EndInteraction when underlying OS audio tools fail.
# safe_renpy_input should convert that into an empty string instead of crashing.
def test_safe_input_handles_endinteraction(helper_module, renpy_module, monkeypatch):
    EndInteraction = renpy_module.display.core.EndInteraction

    def raising(prompt="", **kwargs):
        raise EndInteraction()

    monkeypatch.setattr(renpy_module, "input", raising)

    value = helper_module.safe_renpy_input("Say something")

    assert value == ""


def test_safe_input_discards_non_string(helper_module, renpy_module, monkeypatch):
    logged = []
    monkeypatch.setattr(helper_module, "log_player_input", lambda *a, **k: logged.append((a, k)))

    def returns_bool(prompt="", **kwargs):
        return True

    monkeypatch.setattr(renpy_module, "input", returns_bool)

    value = helper_module.safe_renpy_input("Share something")

    assert value == ""
    assert logged == []


def test_safe_input_logs_manual_entries(helper_module, renpy_module, monkeypatch):
    captured = []

    def fake_log(text, **kwargs):
        captured.append((text, kwargs))

    monkeypatch.setattr(helper_module, "log_player_input", fake_log)
    monkeypatch.setattr(renpy_module, "input", lambda prompt="", **kwargs: "   My idea   ")

    value = helper_module.safe_renpy_input("Prompt with ?")

    assert value == "   My idea   "
    assert captured, "log_player_input should be invoked for manual entries."
    text, kwargs = captured[0]
    assert text == "   My idea   "
    assert kwargs["prompt"] == "Prompt with ?"
    assert kwargs["screen"] is None
    assert kwargs["is_question"] is True
    assert kwargs["metadata"]["stripped"] == "My idea"


def test_safe_input_prefers_call_screen_when_provided(helper_module, renpy_module, monkeypatch):
    log_calls = []
    monkeypatch.setattr(helper_module, "log_player_input", lambda *a, **k: log_calls.append((a, k)))

    def fake_call_screen(name, **kwargs):
        assert name == "argument_sharing"
        assert kwargs["prompt"] == "Share soon"
        return "Screen text"

    def fail_input(*args, **kwargs):
        raise AssertionError("renpy.input should not be used when screen is provided")

    monkeypatch.setattr(renpy_module, "call_screen", fake_call_screen)
    monkeypatch.setattr(renpy_module, "input", fail_input)

    value = helper_module.safe_renpy_input("Share soon", screen="argument_sharing")

    assert value == "Screen text"
    assert log_calls, "log_player_input should record screen submissions."
    args, kwargs = log_calls[0]
    assert args[0] == "Screen text"
    assert kwargs["screen"] == "argument_sharing"


def test_safe_input_uses_cached_screen_response(helper_module, renpy_module, monkeypatch):
    monkeypatch.setattr(helper_module, "log_player_input", lambda *a, **k: None)

    def fake_call_screen(name, **kwargs):
        helper_module.cache_screen_response(name, "Cached argument text")
        return True

    monkeypatch.setattr(renpy_module, "call_screen", fake_call_screen)

    value = helper_module.safe_renpy_input("Share now", screen="argument_sharing")

    assert value == "Cached argument text"
