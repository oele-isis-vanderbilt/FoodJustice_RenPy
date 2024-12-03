# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#regular character talking with dialogue at bottom of screen
define e = Character("Elliot")
define a = Character("Amara")
define w = Character("Wes")
define m = Character("Mayor Watson")

#character that talks via chat bubbles
define e2 = Character(None, image="elliot smile", kind=bubble)

#tells renpy where to find the movie - for playing in background of character
image bees = Movie(play="movies/beevr_snippet.webm")

default source_list = []
default note_list = []
default customnotecount = 0

init python:
    import datetime

#### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####

    def note(info,speaker):
        note_list.append(info)
        source_list.append(speaker)
        renpy.notify("Note Taken!")
        noteindex = note_list.index(info)
        notenumber = str(noteindex)
        log("Took note #" + notenumber + ": " + info + " (Source: " + speaker + ")")

    def deletenote(notetext):
        noteindex = note_list.index(notetext)
        del note_list[noteindex]
        del source_list[noteindex]
        renpy.notify("Note Deleted")
        log("Player deleted note: " + notetext)
    
    def editnote(oldtext, newnote, newsource):
        noteindex = note_list.index(oldtext)
        note_list[noteindex] = newnote
        source_list[noteindex] = newsource
        renpy.notify("Note Revised")
        notenumber = str(noteindex)
        log("Player edited note #" + notenumber + " to say: " + newnote + " (Source: " + newsource + ")")

    def log(action):
        timestamp = datetime.datetime.now()
        renpy.log(timestamp)
        renpy.log(action + "\n")

# The game starts here.

label start:

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene empty lot
    with None

    menu:
        "I live in a city":
            $ startplace = "empty lot city"
            jump begin

        "I live in a rural town":
            $ startplace = "empty lot rural"
            jump begin

        "I live in the suburbs":
            $ startplace = "empty lot suburb" 
            jump begin

    label travelmenu:
        "Where would you like to go?"
        menu:
            "The empty lot" if currentlocation != "emptylot":
                jump emptylot
            "The food lab" if currentlocation != "foodlab":
                jump foodlab
            "The community garden" if currentlocation != "garden":
                jump garden
            "Nevermind, stay here":
                $ renpy.rollback(checkpoints=3)

    label begin:
    scene expression "[startplace]"
    with dissolve
    $ currentlocation = "emptylot"
    show screen learningbuttons()

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    show elliot smile
    with dissolve

    # These display lines of dialogue.

    e "Hey what's up - you new to the neighborhood?"

# gives player choices that determine where to jump next in dialogue tree
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
        $ log("Player name: " + name)

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

## Basic student input & cleaning it (remove punctuation and make it all lowercase)
#         $ idea = renpy.input("What do you notice while watching the bees?")

# #Adds what they noticed to the notebook lists   
#         $ note(idea, "BeeVR video")    

#         $ idea = idea.strip(".?!")
#         $ idea = idea.lower()
#         $ log("Observation: " + idea)

#         e "Oh, you noticed that [idea]? Awesome!"
        
        hide bees

# this block calls the ECA via the IU server
        $ eca = renpy.input("What did you notice while watching the bees?")
        $ log("Player input to ECA: " + eca)
        $ ecaresponse = renpy.fetch("https://bl-educ-engage.educ.indiana.edu/GetECAResponse", method="POST", json={"ECAType": "GEMSTEP_Observing", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
        e "[ecaresponse]"

        $ note(ecaresponse, "Elliot")

# Embedding links to websites into dialogue
        e "Why don't you check in with your friends and {a=https://docs.google.com/document/d/1QTPBkV9XNADFgnluxhJ1SjGkWyEDG8Kug7edNoMDLHQ/edit?usp=sharing}see what evidence they've found?{/a}"

#grants achievements and tells the player it was granted
        $ achievement.grant("Helping Elliot")
        $ renpy.notify("Achievement Unlocked: Helping Elliot")

# conversation bubble instead of bottom-screen dialogue, as defined at the beginning
        e2 "Thanks for chatting!"
        jump travelmenu

    label foodlab:
        scene science lab
        with dissolve
        $ currentlocation = "foodlab"

        show amara smile
        with dissolve

        a "Hi! I'm Amara - I'm the lead scientist here at the food lab."
        jump sciencequestions

    label sciencequestions:
        a "What would you like to know about food science?"

        menu: 
            "Why does genetic diversity in plants matter?":
                jump genetics
            "What do you know about soil quality?":
                jump soil
            "What do gardens do for the environment?":
                jump environment

        label genetics:
            a "Oh, plant genetics are so interesting. Like people, plants have DNA that carries information about the different kinds of traits they have."
            jump sciencequestions

        label soil:
            a " Soil is super important for the health of plants. Dirt just looks like dirt at first glance, but there are actually 14 different nutrients in the soil that can change how plants grow."
            jump sciencequestions
        
        label environment:
            a "For the ecosystem, gardens give insects and animals a home. They provide food for pollinators and can be especially helpful if they're full of native plants."
            jump sciencequestions

    label garden:
        scene garden
        with dissolve
        $ currentlocation = "garden"

        show wes smile
        with dissolve

        w "Hey there kiddo! Welcome to the Westport Community Garden."
        jump gardenquestions

    label gardenquestions:
        w "Anything you'd like to know about the bees in our garden?"
        $ eca = renpy.input("I'm wondering...")
        $ log("Player input to ECA: " + eca)
        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "Knowledge_Pollination", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
        w "[ecaresponse]"

        jump gardenquestions

    label emptylot:
        scene expression "[startplace]"
        with dissolve
        $ currentlocation = "emptylot"

        show elliot smile
        with dissolve

        e "Welcome back! Did you find some interesting evidence for us to use in our pitch to the mayor?"

    label ideasharing:
        e "What are your ideas?"
        $ eca = renpy.input("My ideas for the mayor:")
        $ log("Player input to ECA: " + eca)
        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
        e "[ecaresponse]"
        jump ideasharing

    # This ends the game.

    return
