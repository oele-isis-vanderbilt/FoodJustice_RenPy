transform drop_shadow_hover:
    on hover:
        linear 0.1 xoffset 2 yoffset 2 alpha 0.85
    on idle:
        linear 0.1 xoffset 0 yoffset 0 alpha 1.0


screen map_popup():
    tag map_popup
    zorder 300
    modal True

    # Centered background image
    add Transform("background_map.png", xalign=0.5, yalign=0.5)

    # Center position of map
    default map_center_x = 0.5
    default map_center_y = 0.5

    # Food Lab (top middle)
    imagebutton:
        idle Transform("local_food.png", zoom=0.5)
        hover Transform("local_food.png", zoom=0.5)
        at drop_shadow_hover
        xpos 0.5
        ypos 0.34
        xanchor 0.5
        yanchor 0.5
        action [Hide("map_popup"), Jump("foodlab")]


    # Empty Lot (bottom left)
    imagebutton:
        idle Transform("local_lot.png", zoom=0.5)
        hover Transform("local_lot.png", zoom=0.5)
        at drop_shadow_hover
        xpos 0.43
        ypos 0.61
        xanchor 0.5
        yanchor 0.5
        action [Hide("map_popup"), Jump("emptylot")]

    # Garden (bottom right)
    imagebutton:
        idle Transform("local_garden.png", zoom=0.5)
        hover Transform("local_garden.png", zoom=0.5)
        at drop_shadow_hover
        xpos 0.57
        ypos 0.61
        xanchor 0.5
        yanchor 0.5
        action [Hide("map_popup"), Jump("garden")]

    # # Optional: Nevermind button centered below map
    # textbutton "Nevermind":
    #     action Rollback()
    #     xalign 0.5
    #     yalign 0.85

