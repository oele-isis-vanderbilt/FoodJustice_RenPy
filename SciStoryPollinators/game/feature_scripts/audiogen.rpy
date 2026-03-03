# AUDIO 
define azureKey = "3da59f8a4fc643ffbec6e4c076c77b7b"
define ecaVoice = "en-US-JennyNeural"
define ecaSpeechRate = "+30%"

##Audio
define useAudio = True
init python:
    import json
    import re

    # Voice presets for character dialogue. Keys are lowercase character names.
    ECA_VOICE_BY_CHARACTER = {
        "tulip": "en-US-AnaNeural",
        "???": "en-US-AnaNeural",
        "elliot": "en-US-DustinMultilingualNeural",
        "friendly stranger": "en-US-DustinMultilingualNeural",
        "amara": "en-US-SerenaMultilingualNeural",
        "riley": "en-US-Alloy:DragonHDLatestNeural",
        "wes": "en-US-LewisMultilingualNeural",
        "nadia": "en-US-Emma2:DragonHDLatestNeural",
        "mayor": "en-US-OnyxTurboMultilingualNeural",
        "mayor watson": "en-US-OnyxTurboMultilingualNeural",
        "cyrus": "en-US-Andrew3:DragonHDLatestNeural",
        "cyrus murphy": "en-US-Andrew3:DragonHDLatestNeural",
        "alex": "zh-CN-XiaoyouMultilingualNeural",
        "cora": "en-US-LolaMultilingualNeural",
        "victor": "zh-CN-YunyiMultilingualNeural",
    }



    # Optional speaking style by character.
    ECA_STYLE_BY_CHARACTER = {
        "amara": "serious",
            }

    def _voice_for_speaker(speaker_name):
        if speaker_name is None:
            return ecaVoice
        key = str(speaker_name).strip().lower()
        return ECA_VOICE_BY_CHARACTER.get(key, ecaVoice)

    def _style_for_speaker(speaker_name):
        if speaker_name is None:
            return ""
        key = str(speaker_name).strip().lower()
        return ECA_STYLE_BY_CHARACTER.get(key, "")

    def _tts_feature_active():
        return bool(useAudio and getattr(renpy.store, "tts_enabled", True))

    def _ensure_web_tts_bridge():
        if not renpy.emscripten:
            return False

        import emscripten
        return bool(emscripten.run_script_int("""
            (function() {
                if (typeof window.playAzureAudio === "function" && typeof window.stopAzureAudio === "function") {
                    return 1;
                }
                window.playAzureAudio = function(utterance, voice, key, volume, rate, style) {
                    window.AzureTtsRequestId = (window.AzureTtsRequestId || 0) + 1;
                    const requestId = window.AzureTtsRequestId;
                    if (window.AzureTtsAbortController) {
                        try { window.AzureTtsAbortController.abort(); } catch (e) {}
                    }
                    window.AzureTtsAbortController = new AbortController();
                    const abortSignal = window.AzureTtsAbortController.signal;
                    if (window.AzureAudio != null) {
                        try {
                            window.AzureAudio.pause();
                            window.AzureAudio.currentTime = 0;
                        } catch (e) {}
                    }
                    const audio = document.createElement("audio");
                    const url = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1";
                    const escapedUtterance = (utterance || "")
                        .replace(/&/g, "&amp;")
                        .replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;");
                    const safeRate = (rate || "0%").toString();
                    const safeStyle = (style || "").toString().trim();
                    const styleOpen = safeStyle ? "<mstts:express-as style=\\"" + safeStyle + "\\">" : "";
                    const styleClose = safeStyle ? "</mstts:express-as>" : "";
                    const ssml = "<speak version=\\"1.0\\" xmlns=\\"http://www.w3.org/2001/10/synthesis\\" xmlns:mstts=\\"http://www.w3.org/2001/mstts\\" xml:lang=\\"en-US\\"><voice name=\\"" + voice + "\\">" + styleOpen + "<prosody rate=\\"" + safeRate + "\\">" + escapedUtterance + "</prosody>" + styleClose + "</voice></speak>";

                    fetch(url, {
                        "headers": {
                            "content-type": "application/ssml+xml",
                            "Ocp-Apim-Subscription-Key": key,
                            "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3"
                        },
                        "body": ssml,
                        "method": "POST",
                        "signal": abortSignal
                    })
                    .then(resp => {
                        if (!resp.ok) {
                            throw new Error("Azure TTS request failed with status " + resp.status);
                        }
                        return resp.blob();
                    })
                    .then(URL.createObjectURL)
                    .then(blobUrl => {
                        if (requestId !== window.AzureTtsRequestId) {
                            try { URL.revokeObjectURL(blobUrl); } catch (e) {}
                            throw new Error("Azure TTS superseded by newer request.");
                        }
                        audio.src = blobUrl;
                        audio.volume = volume / 100;
                        return audio.play();
                    })
                    .then(() => {
                        if (requestId !== window.AzureTtsRequestId) {
                            try {
                                audio.pause();
                                audio.currentTime = 0;
                            } catch (e) {}
                            return;
                        }
                        window.AzureAudio = audio;
                    })
                    .catch(err => {
                        if (abortSignal.aborted) {
                            return;
                        }
                        console.error("Azure TTS playback failed:", err);
                    });
                };

                window.stopAzureAudio = function() {
                    window.AzureTtsRequestId = (window.AzureTtsRequestId || 0) + 1;
                    if (window.AzureTtsAbortController) {
                        try { window.AzureTtsAbortController.abort(); } catch (e) {}
                    }
                    if (window.AzureAudio != null) {
                        window.AzureAudio.pause();
                        window.AzureAudio.currentTime = 0;
                    }
                };

                return 1;
            })();
        """))

    def initialize_web_tts_bridge():
        if _tts_feature_active() and renpy.emscripten:
            try:
                _ensure_web_tts_bridge()
            except Exception:
                # Keep gameplay running even if bridge initialization fails.
                pass

    def playAudio(dialogLine: str, speaker_name=None, speech_rate=None, speaking_style=None):
        if _tts_feature_active():
            if renpy.emscripten:
                if not _ensure_web_tts_bridge():
                    return
                import emscripten
                resolved_voice = _voice_for_speaker(speaker_name)
                resolved_rate = speech_rate if speech_rate is not None else ecaSpeechRate
                resolved_style = speaking_style if speaking_style is not None else _style_for_speaker(speaker_name)
                js_call = "window.playAzureAudio({}, {}, {}, 100, {}, {});".format(
                    json.dumps(dialogLine or ""),
                    json.dumps(resolved_voice),
                    json.dumps(azureKey),
                    json.dumps(str(resolved_rate)),
                    json.dumps(str(resolved_style or "")),
                )
                emscripten.run_script_int(js_call)

    _character_tts_enabled = False
    _last_dialogue_signature = None

    def _is_predicting_dialogue():
        try:
            predictor = getattr(renpy, "predicting", None)
            if callable(predictor):
                return bool(predictor())
        except Exception:
            pass
        try:
            predictor = getattr(renpy, "is_predicting", None)
            if callable(predictor):
                return bool(predictor())
        except Exception:
            pass
        return False

    def _clean_tts_text(value):
        text = value if isinstance(value, str) else str(value or "")
        # Remove Ren'Py text tags like {i}, {size=*1.5}, etc.
        text = re.sub(r"\{[^}]*\}", "", text)
        return text.strip()

    def maybe_play_dialogue_tts(who, what):
        global _last_dialogue_signature
        if not _tts_feature_active():
            return
        if not _character_tts_enabled:
            return
        if who is None or what is None:
            return
        if _is_predicting_dialogue():
            return

        speaker_name = _clean_tts_text(who)
        spoken = _clean_tts_text(what)
        if not speaker_name or not spoken:
            return

        signature = (speaker_name, spoken)
        if signature == _last_dialogue_signature:
            return

        _last_dialogue_signature = signature
        playAudio(spoken, speaker_name=speaker_name)

    def enable_character_tts():
        global _character_tts_enabled, _last_dialogue_signature
        if not _tts_feature_active():
            _character_tts_enabled = False
            return False
        if not renpy.emscripten:
            _character_tts_enabled = False
            return False
        initialize_web_tts_bridge()
        _character_tts_enabled = True
        _last_dialogue_signature = None
        return True

    def set_tts_enabled(enabled):
        global _character_tts_enabled, _last_dialogue_signature
        enabled = bool(enabled)
        renpy.store.tts_enabled = enabled
        _last_dialogue_signature = None
        if not enabled:
            _character_tts_enabled = False
            stopAudio()
            return False
        return enable_character_tts()

    def toggle_tts_enabled():
        current = bool(getattr(renpy.store, "tts_enabled", True))
        return set_tts_enabled(not current)

    def stopAudio():
        if useAudio:
            if renpy.emscripten:
                import emscripten
                emscripten.run_script_int("window.stopAzureAudio();")
    def StartAudioRecord():
        if renpy.emscripten:
                import emscripten
                test = emscripten.run_script_int(f"window.microphoneUtil.StartRecordingJS();")
    def EndAudioRecord():
        if renpy.emscripten:
                import emscripten
                test = emscripten.run_script_int(f"window.microphoneUtil.StopRecordingJS();")

init 1 python:
    initialize_web_tts_bridge()

screen my_button_screen():
    $ recording_tooltip = None
    if not renpy.emscripten:
        $ recording_tooltip = "This feature isn't available on desktop."

    # vbox:
    #     spacing 20 
    #     textbutton "Start Record":
    #         action Function(StartAudioRecord)
    #         xalign 0.5 
    #         if recording_tooltip:
    #             tooltip recording_tooltip
    #     textbutton "End Record":
    #         action Function(EndAudioRecord)
    #         xalign 0.5 
    #         if recording_tooltip:
    #             tooltip recording_tooltip

    # zorder 1000
    # modal False
    # $ recording_tooltip = None

    # if voice_input_available:
    #     if not renpy.emscripten:
    #         $ recording_tooltip = "This feature isn't available on desktop."

    #     vbox:
    #         frame:
    #             style "voice_record_frame"

    #             textbutton ("Start Voice Recording"):
    #                 style "tag_button"
    #                 action [
    #                     Function(StartAudioRecord),
    #                     style "edit_tag_support"
    #                 ]

    #             textbutton ("Stop Voice Recording"):
    #                 style "tag_button"
    #                 action [
    #                     Function(EndAudioRecord),
    #                     style "edit_tag_support"
    #                 ]
