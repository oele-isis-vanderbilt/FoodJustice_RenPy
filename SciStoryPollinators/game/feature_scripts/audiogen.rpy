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
                     


style tag_button:
    background "#d1c7ff"
    padding (4, 4)

style tag_button_text:
    font "DejaVuSans.ttf"
    size 14
    color "#000000"
    xalign 0.5
    yalign 0.5

style selected_tag_button:
    background "#8076ae"