#### Custom screens for SciStory ################################
##  
##  Screens to support learning!


#### Travel and Notebook access - Always available buttons ####
style side_button:
    anchor (1.0, 0.0)
    pos (0.98, 0.02)

screen learningbuttons():
    zorder 90
    $ achieve_btn = Transform("images/imagebutton_achievements.png",  fit="contain", xsize=80)
    $ bee_btn = Transform("images/imagebutton_bee.png",  fit="contain", xsize=80)
    $ notebook_btn = Transform("images/imagebutton_notebook.png",  fit="contain", xsize=80)
    $ map_btn = Transform("images/imagebutton_map.png",  fit="contain", xsize=80)

    vbox style "side_button":
        imagebutton:
            tooltip "Travel"
            idle map_btn
            hover darken_hover(map_btn)
            action (Function(retaindata), Show("map_popup"))

        text "\n":
            size 8

        imagebutton:
            tooltip "Notebook"
            idle notebook_btn
            hover darken_hover(notebook_btn)
            action (Function(retaindata), Show("notebook"))

        text "\n":
            size 8

        imagebutton:
            tooltip "Ask Tulip"
            idle bee_btn
            hover darken_hover(bee_btn)
            action Call("tulipchat_from_button", from_current = True)

        text "\n":
            size 8

        imagebutton:
            tooltip "Achievements"
            idle achieve_btn
            hover darken_hover(achieve_btn)
            action (Function(retaindata), Show("achievements_screen"))

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15

#### Custom Input Screen for Long Entries ####

screen argument_writing(prompt):
    add "gui/textbox.png" xpos 0 ypos .743
    vbox:
        anchor (0.0,0.0)
        pos (0.2,0.76)
        xsize 1100
        ysize 250
        text prompt
        viewport:
            scrollbars "vertical"
            vscrollbar_unscrollable "hide"
            mousewheel True
            input color "#037426" xmaximum 1200 copypaste True multiline True
