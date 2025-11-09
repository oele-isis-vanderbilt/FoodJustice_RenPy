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
def test_safe_input_handles_endinteraction(helper_module, renpy_module):
    EndInteraction = renpy_module.display.core.EndInteraction
    original = renpy_module.invoke_in_new_context

    def raising(fn, *args, **kwargs):
        raise EndInteraction()

    renpy_module.invoke_in_new_context = raising

    try:
        value = helper_module.safe_renpy_input("Say something")
    finally:
        renpy_module.invoke_in_new_context = original

    assert value == ""
