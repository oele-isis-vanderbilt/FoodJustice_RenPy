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
