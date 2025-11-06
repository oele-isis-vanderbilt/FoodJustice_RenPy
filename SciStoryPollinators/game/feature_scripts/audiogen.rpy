# AUDIO 
define azureKey = "3da59f8a4fc643ffbec6e4c076c77b7b"
define ecaVoice = "en-US-JennyNeural"

##Audio
define useAudio = False
init python:
    def playAudio(dialogLine: str):
        if useAudio:
            if renpy.emscripten:
                import emscripten
                test = emscripten.run_script_int(f"window.playAzureAudio(\"{dialogLine}\", \"{ecaVoice}\", \"{azureKey}\", 100);")
    def stopAudio():
        if useAudio:
            if renpy.emscripten:
                import emscripten
                test = emscripten.run_script_int(f"window.stopAzureAudio();")
    def StartAudioRecord():
        if renpy.emscripten:
                import emscripten
                test = emscripten.run_script_int(f"window.microphoneUtil.StartRecordingJS();")
    def EndAudioRecord():
        if renpy.emscripten:
                import emscripten
                test = emscripten.run_script_int(f"window.microphoneUtil.StopRecordingJS();")

screen my_button_screen():
    $ recording_tooltip = None
    if not renpy.emscripten:
        $ recording_tooltip = "This feature isn't available on desktop."

    vbox:
        spacing 20 
        textbutton "Start Record":
            action Function(StartAudioRecord)
            xalign 0.5 
            if recording_tooltip:
                tooltip recording_tooltip
        textbutton "End Record":
            action Function(EndAudioRecord)
            xalign 0.5 
            if recording_tooltip:
                tooltip recording_tooltip

screen voice_recording_toggle():
    zorder 1000
    modal False

    frame:
        style "voice_record_frame"
        align (0.02, 0.02)

        textbutton ("Stop Voice Recording" if voice_recording_active else "Start Voice Recording"):
            style "voice_record_button"
            action Function(toggle_voice_recording)

style voice_record_frame is default
style voice_record_frame:
    background Solid("#1b1b1bcc")
    padding (6, 8)
    xminimum 200

style voice_record_button is default
style voice_record_button:
    background "#2a7de1"
    hover_background "#1f5eb0"
    padding (4, 12)
    color "#ffffff"
    bold True