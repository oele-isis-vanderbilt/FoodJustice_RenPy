# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#regular character talking with dialogue at bottom of screen
define e = Character("Elliot")

#character that talks via chat bubbles
define e2 = Character(None, image="elliot standing", kind=bubble)

#tells renpy where to find the movie - for playing in background of character
image bees = Movie(play="movies/beevr_snippet.webm")

#adds python module to use date and time tracking for logs
init python:
    import datetime

# The game starts here.

label start:

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene empty lot
    with None

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    show elliot standing
    with dissolve

    # These display lines of dialogue.

    e "Hey what's up - you new to the neighborhood?"

#gives player choices that determine where to jump next in dialogue tree
    menu:

        "Yeah, just moved here!":
            jump friendly

        "Maybe.":
            jump standoffish

    label friendly:

        e "Welcome to the neighborhood! I live right down the street."
        jump intro

    label standoffish:

        e "I dunno where you moved from, but we don't do the whole 'mysterious stranger' thing here."
        jump intro

    label intro:

        e "Anyway, I'm glad you're here, new kid."

# player can enter their name and it removes whitespace from entry
        $ name = renpy.input("What's your name?")
        $ name = name.strip()
        $ timestamp = datetime.datetime.now()
        $ renpy.log(timestamp)
        $ renpy.log("Player name: " + name + "\n")

        e "Great to meet you [name]! I'm Elliot. I'm hoping you'll help me convince Mayor Watson not to sell our lot to those parking guys."

    label video:

        e "Let me show you some honeybees in action."

#Play video fullscreen until click or end of vid
        $ renpy.movie_cutscene("movies/beevr_snippet.webm")

        e "Cool, right?"

#Play video in the background until hide
        show bees behind elliot:
            xpos 100
            ypos 100
            zoom 0.5

        e "I think watching how the bees explore the garden can help us find some evidence to convince the Mayor."

# Basic student input & cleaning it (remove punctuation and make it all lowercase)
        $ idea = renpy.input("What do you notice while watching the bees?")
        $ idea = idea.strip(".?!")
        $ idea = idea.lower()
        $ timestamp = datetime.datetime.now()
        $ renpy.log(timestamp)
        $ renpy.log("Observation: " + idea + "\n")

        e "Oh, you noticed that [idea]? Awesome!"
        hide bees

# this block calls the ECA via the IU server
        $ eca = renpy.input("Ask something to the GEMSTEP ECA.")
        $ timestamp = datetime.datetime.now()
        $ renpy.log(timestamp)
        $ renpy.log("Player input to ECA: " + eca + "\n")
        $ ecaresponse = renpy.fetch("https://bl-educ-engage.educ.indiana.edu/GetECAResponse", method="POST", json={"ECAType": "GEMSTEP_Observing", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
        e "[ecaresponse]"

# Embedding links to websites into dialogue
        e "Why don't you check in with your friends and {a=https://docs.google.com/document/d/1QTPBkV9XNADFgnluxhJ1SjGkWyEDG8Kug7edNoMDLHQ/edit?usp=sharing}see what evidence they've found?{/a}"

#grants achievements and tells the player it was granted
        $ achievement.grant("Helping Elliot")
        $ renpy.notify("Achievement Unlocked: Helping Elliot")

# conversation bubble instead of bottom-screen dialogue, as defined at the beginning
        e2 "Thanks for chatting!"

    # This ends the game.

    return
