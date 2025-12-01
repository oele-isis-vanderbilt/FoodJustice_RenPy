# ---------- Images ----------
image map_suburb = "map_suburb.png"
image map_rural  = "map_rural.png"
image map_urban  = "map_urban.png"

image pin_empty  = "map_pin_emptylot.png"   # brown rectangle (empty lot)
image pin_garden = "map_pin_garden.png"     # park bench + trees
image pin_food   = "map_pin_foodlab.png"    # yellow/blue/red buildings

# ---------- Direct pin coordinates (relative to the 750x750 map) ----------
init python:
    # (x, y) is where the TIP of the pin should touch
    PIN_POS = {
        "rural": {   # circular map
            "empty":  (400, 225),
            "garden": (600, 525),
            "food":   (275, 75),
        },
        "suburb": {  # wavy map
            "empty":  (350, 272),
            "garden": (525, 400),
            "food":   (155, 90),
        },
        "city": {    # dense/urban map
            "empty":  (275, 300),
            "garden": (450, 525),
            "food":   (150, 200),
        },
    }

    # If your code ever sets startplace to "urban", alias it to "city".
    def _canonical_place(s):
        return "city" if s == "urban" else s

screen map_popup():
    modal True   # make clicks go only to this screen
    on "show" action Function(lock_dialogue_advancement, "map_popup")
    on "hide" action Function(unlock_dialogue_advancement, "map_popup")
    default shown_w = 750
    default shown_h = 750

    # 1) Dim the whole screen (background overlay)
    add Solid("#00000080")  # black at 50% opacity, tweak hex/alpha to taste

    # 2) Then your popup container
    fixed:
        xysize (shown_w, shown_h)
        xalign 0.5
        yalign 0.2

        add ConditionSwitch(
            "startplace == 'suburb'", "map_suburb",
            "startplace == 'rural'",  "map_rural",
            "startplace == 'city'",   "map_urban",
            "True",                   "map_urban"
        ) pos (0, 0) xsize shown_w ysize shown_h matrixcolor SaturationMatrix(0.7)

        # Use direct 750x750 coordinates + downward offsets
        $ sp = _canonical_place(startplace)
        $ ex, ey = PIN_POS[sp]["empty"]
        $ gx, gy = PIN_POS[sp]["garden"]
        $ fx, fy = PIN_POS[sp]["food"]


        $ empty_idle  = Transform("images/map_pin_emptylot.png")
        $ empty_hover = Transform(
            brighten_hover("images/map_pin_emptylot.png")
        )

        imagebutton:
            idle empty_idle
            hover empty_hover
            anchor (0.5, 1.0)
            xpos ex
            ypos ey
            action [Hide("map_popup"), Jump("emptylot")]

        $ garden_idle  = Transform("images/map_pin_garden.png")
        $ garden_hover = Transform(
            brighten_hover("images/map_pin_garden.png")
        )

        imagebutton:
            idle garden_idle
            hover garden_hover
            anchor (0.5, 1.0)
            xpos gx
            ypos gy
            action [Hide("map_popup"), Jump("garden")]

        $ food_idle  = Transform("images/map_pin_foodlab.png")
        $ food_hover = Transform(
            brighten_hover("images/map_pin_foodlab.png")
        )

        imagebutton:
            idle food_idle
            hover food_hover
            anchor (0.5, 1.0)
            xpos fx
            ypos fy
            action [Hide("map_popup"), Jump("foodlab")]

        $ iw, ih = renpy.image_size("images/imagebutton_close.png")
        $ exit_btn = Transform("images/imagebutton_close.png", zoom=50.0 / ih)

        imagebutton:
            tooltip "Close"
            idle exit_btn
            hover darken_hover(exit_btn, 0.40)
            action Hide("map_popup")
            anchor (1.0, 0.0)
            pos (0.98, 0.02)

    $ tooltip = GetTooltip()
    if tooltip:
        nearrect:
            focus "tooltip"

            frame:
                xalign 0.5
                text tooltip:
                    size 15

#### Invisible Character Selection Screen ####

screen characterselect3(c_left, c_center, c_right):
    zorder 80

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.2, 0.25)
        action Jump(c_left + "_chatting")

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.5, 0.25)
        action Jump(c_center + "_chatting")

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.8, 0.25)
        action Jump(c_right + "_chatting")

screen characterselect2(c_left, c_right):
    zorder 80

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.2, 0.25)
        action Jump(c_left + "_chatting")

    button:
        xysize (600, 900)
        anchor (0.5, 0.0)
        pos (0.8, 0.25)
        action Jump(c_right + "_chatting")
