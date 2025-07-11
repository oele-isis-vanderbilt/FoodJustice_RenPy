label toggle_qa_panel:
    if renpy.get_screen("qa_panel"):
        hide screen qa_panel
    else:
        show screen qa_panel
    return

style qa_textbutton is default:
    padding (12, 8, 12, 8)
    background "#1558b0"             
    hover_background "#021b3c"
    focus_mask True               
    xminimum 140
    yminimum 40

style qa_textbutton_text is default:
    bold True
    color "#fff"
    size 18
    font "DejaVuSans.ttf"   

screen qa_panel():
    zorder 200
    tag qa_panel

    frame:
        xalign 1.0 
        yalign 1.0 
        xsize 340
        ysize 600
        padding (20, 15)
        background Frame("gui/frame.png", 15, 15)

        viewport:
            draggable False
            mousewheel True
            scrollbars "vertical"
            vscrollbar_unscrollable "hide"

            vbox:
                spacing 10
                style_prefix "qa_"

                text "QA Tools":
                    size 22
                    color "#ffffff"

                textbutton "Write Argument Screen":
                    action Call("show_argument_screen") style "qa_textbutton"

                textbutton "Achievements":
                    action [Function(retaindata), Show("achievements_screen")] style "qa_textbutton"

                textbutton "Travel Menu":
                    action Jump("travelmenu") style "qa_textbutton"

                textbutton "Tulip Chat":
                    action Call("tulipchat", from_current=True) style "qa_textbutton"

                textbutton "Open Notebook":
                    action [Function(retaindata), Show("notebook")] style "qa_textbutton"
