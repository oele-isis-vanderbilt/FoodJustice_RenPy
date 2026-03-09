
screen argument_sharing(prompt):
    modal True
    zorder 100

    default user_argument = ""
    default argumentinput = ScreenVariableInputValue("user_argument")
    # default voice_request_active = False

    # if not voice_request_active:
    #     $ request_voice_input()
    #     $ voice_request_active = True

    # on "hide" action If(
    #     voice_request_active,
    #     true=[Function(release_voice_input), SetScreenVariable("voice_request_active", False)],
    #     false=SetScreenVariable("voice_request_active", False)
    # )

    use my_button_screen

    frame:
        xpos 1.0
        ypos 1.0
        anchor (1.0, 1.0)
        xsize 500
        ysize 700
        background Transform("images/screen_speaking.png", fit="contain")
        padding (40, 28, 40, 80)

        vbox:
            spacing 10
            xfill True
            yfill True

            text prompt:
                size 20
                bold True
                xalign 0.0
                xmaximum 400

            # Scrollable input container
            viewport:
                xmaximum 400
                ymaximum 320
                scrollbars "vertical"
                mousewheel True

                input:
                    value argumentinput
                    multiline True
                    copypaste True
                    style "argument_input"
                    xmaximum 600

            vbox:
                spacing 8
                xmaximum 400
                xalign 0.5

                hbox:
                    spacing 10
                    xsize 400
                    xalign 0.5
                    
                    frame:
                        background None
                        xsize 195
                        textbutton "Nevermind":
                            style "share_action_button"
                            action Return(None)
                            tooltip "Close"
                            xfill True

                    frame:
                        background None
                        xsize 195
                        textbutton "Share":
                            style "share_action_button"
                            action [
                                Function(cache_screen_response, "argument_sharing", user_argument),
                                Return(user_argument)
                            ]
                            xfill True

                hbox:
                    spacing 10
                    xsize 400
                    xalign 0.5
                    
                    frame:
                        background None
                        xsize 195
                        textbutton "Use Notebook Draft":
                            style "share_action_button"
                            action SetScreenVariable("user_argument", notebook_argument)
                            xfill True

                    frame:
                        background None
                        xsize 195
                        textbutton "Save to Notbook":
                            style "share_action_button"
                            action [
                                Function(argument_edit, user_argument),
                                Function(cache_screen_response, "argument_sharing", user_argument),
                            ]
                            xfill True

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15

style share_action_button is standard_button:
    padding (8, 6)
    xminimum 186
    yminimum 48
    xalign 0.5

style share_action_button_text is standard_button_text:
    size 14


screen question_asking(prompt):
    modal True
    zorder 100

    default user_argument = ""
    default argumentinput = ScreenVariableInputValue("user_argument")
    # default voice_request_active = False

    # if not voice_request_active:
    #     $ request_voice_input()
    #     $ voice_request_active = True

    # on "hide" action If(
    #     voice_request_active,
    #     true=[Function(release_voice_input), SetScreenVariable("voice_request_active", False)],
    #     false=SetScreenVariable("voice_request_active", False)
    # )

    use my_button_screen

    frame:
        xpos 1.0
        ypos 1.0
        anchor (1.0, 1.0)
        xsize 500
        ysize 700
        background Transform("images/screen_speaking.png", fit="contain")
        padding (40, 28, 40, 80)

        vbox:
            spacing 10

            text prompt:
                size 20
                bold True
                xalign 0.0

            # Scrollable input container
            viewport:
                xmaximum 400
                ymaximum 400
                scrollbars "vertical"
                mousewheel True

                input:
                    value argumentinput
                    multiline True
                    copypaste True
                    style "argument_input"
                    xmaximum 600

                hbox:
                    spacing 10
                    xsize 320
                    xalign 0.5
                    
                    frame:
                        background None
                        xsize 160
                        textbutton "Nevermind":
                            style "standard_button"
                            action Return(None)
                            tooltip "Close"
                            xfill True

                    frame:
                        background None
                        xsize 160
                        textbutton "Ask Question":
                            style "standard_button"
                            action [
                                Function(cache_screen_response, "argument_sharing", user_argument),
                                Return(user_argument)
                            ]
                            xfill True

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15
