# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

# regular character talking with dialogue at bottom of screen
# use the letter to trigger their dialogue rather than typing out full name
define e = Character("Elliot")
define a = Character("Amara")
define r = Character("Riley")
define w = Character("Wes")
define n = Character("Nadia")
define m = Character("Mayor Watson")
define cy = Character("Cyrus")
define x = Character("Alex")
define c = Character("Cora")
define v = Character("Victor")
define t = Character("Tulip")

# variable set up
default source_list = []
default note_list = []
default tag_list = []
default visited_list = []
default spoken_list = []
default customnotecount = 0
default emptylotvisit = False
default foodlabvisit = False
default gardenvisit = False
default hivesvisit = False
default rileychat = 0
default amarachat = 0
default elliotchat = 0
default weschat = 0
default mayorchat = 0
default cyruschat = 0
default nadiachat = 0
default victorchat = 0
default alexchat = 0
default corachat = 0
default argument_attempts = 0
default ca_context = ""

### Code for switching out CA models for the AI agents. Uncomment the ca_link and ca_json for the model you want to use, comment others ###

init python:
    current_label = None
    current_user = "Unknown"
    TIMEOUT = 15

    def agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(note_list)
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)

        ## To use the Llama CA: ##
        ca_link = "http://149.165.155.145:9999/foodjustice/" + llama_ca

        if (ca_type == "FoodJustice_RileyEvaluation") or (ca_type == "FoodJustice_MayorEvaluation"):
            ca_json = {"userID": current_user, "query": "argument evaluation", "gameState": {
                                                    "contextType": ca_type,
                                                    "numNotes": note_count,
                                                    "customNotes": customnotecount,
                                                    "numArgument": argument_attempts,
                                                    "currentSpeaker": character,
                                                    "spokeToNPC": speakers,
                                                    "visitLocation": visits,
                                                    "currentLocation": currentlocation,
                                                    "argument": eca}}
        else:
            ca_json = {"userID": current_user, "query": eca, "gameState": {
                                                    "contextType": ca_type,
                                                    "numNotes": note_count,
                                                    "customNotes": customnotecount,
                                                    "numArgument": argument_attempts,
                                                    "currentSpeaker": character,
                                                    "spokeToNPC": speakers,
                                                    "visitLocation": visits,
                                                    "currentLocation": currentlocation,
                                                    "argument": ""}}

        ## To use the flanT5 CA: ##
        # ca_context = "Player has taken " + note_count + " notes. Player has shared their argument " + argument attempts + " times. Player is currently in the " + currentlocation + ". Player has already spoken to " + speakers + " and has already visited " + visits
        # ca_json = {"ECAType": ca_type, "Context": ca_context, "Utterance": eca, "ConfidenceThreshold": 0.3}

        ## To use the NCSU flanT5 CA: ##
        # ca_link = "https://tracedata-01.csc.ncsu.edu/GetECAResponse"

        ## To use the IU flanT5 CA: ##
        # ca_link = "https://bl-educ-engage.educ.indiana.edu/GetECAResponse"
        return ca_link, ca_json


## Possibilities for ca_type: ##
# FoodJustice_RileyEvaluation, FoodJustice_MayorEvaluation, Knowledge_FoodJustice, Knowledge_Pollination
# GameHelp, GameHelp_Collaboration, GEMSTEP_Observing

## Possbilities for llama_ca ##
# eliot, garden, RileyEvaluation

#### Code to copy/paste to call CA model during narrative ####
# ca_type, the utterance, the llama_ca type, and the character name who is talking #
# $ agent_setup("RileyEvaluation", eca, "eliot", "Elliot")
# $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text")

init python:
    import datetime
    from typing import Dict, Any, Optional
    import os
    # Todo: Remove this later
    if renpy.emscripten:
        import emscripten
        result = emscripten.run_script("window.syncFlowPublisher.startPublishing('umesh', 'umesh')")
        

    #### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####

    def label_callback(label, interaction):
        if not label.startswith("_"):
            log_http(current_user, action=f"PlayerJumpedLabel({label}|{interaction})", view=label, payload=None)
            global current_label
            current_label = label

    config.label_callbacks = [label_callback]

    def note(info, speaker, tag):
        note_list.append(info)
        source_list.append(speaker)
        tag_list.append(tag)
        renpy.notify("Note Taken!")
        noteindex = note_list.index(info)
        notenumber = str(noteindex)
        # log("Took note #" + notenumber + ": " + info + " (Source: " + speaker + ")")
        log_http(current_user, action="PlayerTookNote", view=current_label, payload={
            "note": info,
            "source": speaker,
            "note_id": noteindex
        })

    def deletenote(notetext):
        noteindex = note_list.index(notetext)
        notetext = note_list[noteindex]
        note_source = source_list[noteindex]
        del note_list[noteindex]
        del source_list[noteindex]
        del tag_list[noteindex]
        renpy.notify("Note Deleted")
        # log("Player deleted note: " + notetext)
        log_http(
            current_user,
            action="PlayerDeletedNote",
            view=current_label,
            payload={"note": notetext, "source": note_source, "note_id": noteindex}
        )
    
    def editnote(oldtext, newnote, newsource, newtag):
        noteindex = note_list.index(oldtext)
        note_list[noteindex] = newnote
        source_list[noteindex] = newsource
        tag_list[noteindex] = newtag
        renpy.notify("Note Revised")
        notenumber = str(noteindex)
        # log("Player edited note #" + notenumber + " to say: " + newnote + " (Source: " + newsource + ")")
        log_http(
            current_user,
            action="PlayerEditedNote",
            view=current_label,
            payload={"note": newnote, "source": newsource, "note_id": noteindex}
        )

    def log(action):
        timestamp = datetime.datetime.now()
        renpy.log(timestamp)
        renpy.log(action + "\n")

    def log_http(user: str, payload: Optional[Dict[str, Any]], action: str, view: str = None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.getenv("SERVICE_URL") is None:
            base_url = ""
        else:
            base_url = os.getenv("SERVICE_URL")
            
        log_entry = {
            "action": action,
            "timestamp": timestamp,
            "user": user,
            "view": view,
            "payload": payload
        }
        try:
            renpy.fetch(
                f"{base_url}/player-log",
                method="POST",
                json=log_entry,
            )
        except Exception as e:
            renpy.log(timestamp)
            renpy.log(f"{action}\n")

# The game starts here.

label start:

    # Show a background
    scene flowers muted
    with fade

    $ current_user = renpy.input("Please enter your player ID")

    narrator "You open your eyes and find yourself surrounded by bright flowers and sweet-smelling fresh air. How did you get here?"
    
    narrator "You hear a quiet buzzing noise getting closer..."

    narrator "and {size=*1.5}closer...{/size}"

    narrator "and {size=*2}closer...{/size}"

    show tulip
    with dissolve

    narrator "Suddenly, a tiny bee flies around your head and hovers in front of you!"

    "???" "Hey there human friend!"

    menu:
        "Um...hi?":
            "???" "Hello hello! Don't bee shy. We're going to get along buzzingly!"
        "You're a talking bee??":
            "???" "A honey bee, to be exact! But yes!"
        "Hello bee friend!":
            "???" "Hello hello! So glad you're here. I'm absolutely buzzing with excitement!"

    t "I'm Tulip! The hive chose me as your guide for today. If you have any trouble while you're exploring, you can ask me for help!"

    t "Before we get started, tell me about yourself! What kind of place did you come from?"

    menu:
        "I live in a city":
            $ startplace = "empty lot city"
           
        "I live in a rural town":
            $ startplace = "empty lot rural"
        
        "I live in the suburbs":
            $ startplace = "empty lot suburb" 

    t "Wonderful! We'll explore a neighborhood that's kinda like yours that needs your help."

    t "I'm here as your guide, so if you get stuck or need advice, just click on my button and I'll buzz on by."

    t "We should get going then. Lots to do, lots to see! Are you ready?"

    menu:
        "Let's go!":
            t "Yay! Let's zoom!"
        "I guess.":
            t "Don't worry, I'll be right by your side if you need help! We're two bees in a pod. Hehe."

    jump begin

    label travelmenu:
        narrator "Where would you like to go?"
        menu:
            "The empty lot" if currentlocation != "emptylot":
                jump emptylot
            "The food lab" if currentlocation != "foodlab":
                jump foodlab
            "The community garden" if currentlocation != "garden":
                jump garden
            "Nevermind, stay here":
                $ renpy.rollback(checkpoints=3)

    label tulipchat:
        show tulip at left
        with dissolve

        t "Hi human friend! How's it going?"

    label tulip_help_menu:
        menu:
            "I don't know what to do.":
                t "I would start by talking to people around town to see what they have to say!"
                t "If you've done that already, try opening your notebook to see what information you've collected, and think about what else you want to know."
                hide tulip
                with dissolve
                return
        #    "How do I get my group to listen to me?":
        #        t "Humans are a lot like bees - sometimes we're so busy buzzing around trying to be heard that we forget to listen!"
        #        t "You could try saying, "Hey, what do you think of this note I found? I think you'd have some good ideas about it."
        #        t "If you show your group that you care about what they have to say, they are more likely to listen to you in return."
        #        hide tulip
        #        with dissolve
        #        return
            "I'd like some help with persuading the mayor.":
                t "I'd be happy to help! If you tell me what evidence you've found, I can give you some advice on improving your pursuasive writing."

                $ eca = renpy.input("What should the Mayor do with the empty lot, and why?")

                $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Tulip")
                $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                $ log("Player input to ECA: " + eca)
                $ argument_attempts = argument_attempts + 1

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                
                # $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                
                t "[ecaresponse]"
                $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})
               
                t "Do you have other evidence to share?"
                menu:
                    "I have more ideas to add.":
                        $ eca = renpy.input("What should the Mayor do with the empty lot, and why?")

                        $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Tulip")
                        $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                        $ log("Player input to ECA: " + eca)
                        $ argument_attempts = argument_attempts + 1

                        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                        
                        t "[ecaresponse]"
                        $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})

                        t "You're doing great! Keep exploring and gathering notes, and your argument will get even stronger."
                        hide tulip
                        with dissolve
                        return
                    "Not right now.":
                        t "Okay! I'm here if you need me."
                        hide tulip
                        with dissolve
                        return
            "I need help with something else.":
                $ eca = renpy.input("I love questions! What's your question?")

                $ ca_link, ca_json = agent_setup("GameHelp", eca, "tulip", "Tulip")
                $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                $ log("Player input to ECA: " + eca)

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                
                t "[ecaresponse]"
                $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})


                t "Any more questions?"
                menu:
                    "I have another question.":
                        $ eca = renpy.input("What's your question?")

                        $ ca_link, ca_json = agent_setup("GameHelp_Collaboration", eca, "tulip", "Tulip")
                        $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                        $ log("Player input to ECA: " + eca)

                        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                        
                        t "[ecaresponse]"
                        $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})

                        t "Let me know if you need anything else!"
                        hide tulip
                        with dissolve
                        return
                    "No, that's all.":
                        t "Okay! I'm here if you need me."
                        hide tulip
                        with dissolve
                        return
            "Buzz ya later.":
                t "Don't bee a stranger! Hehe."
                hide tulip
                with dissolve
                return

    label begin:
    scene expression "[startplace]"
    with fade
    $ currentlocation = "emptylot"
    show screen learningbuttons()

    show elliot smile
    with dissolve

    "Friendly Stranger" "Hey what's up - you new to the neighborhood?"

    menu:

        "Yeah, just moved here!":
            "Friendly Stranger" "Welcome to the neighborhood! I live right down the street."

        "Maybe.":
            "Friendly Stranger" "I dunno where you moved from, but we don't do the whole 'mysterious stranger' thing here."


    "Friendly Stranger" "Anyway, I'm glad you're here, new kid." 

    e "I'm Elliot. I'm hoping you'll help me convince Mayor Watson not to sell our lot to those parking guys."

    menu:
        "What parking guys?":
            jump parkingguys
    
    label parkingguys:
        e "That guy over there in the suit is from CityPark. They want to turn our empty lot into a big parking garage for the neighborhood."
        e "But me and the other Community Gardeners have been trying to convince Mayor Watson to donate the lot to our food justice project instead."

        e "The parking garage makes money, but a community garden would be huge for this neighborhood!"

        show tulip at left
        with dissolve

        t "Hey! Sorry to interrupt - but this seems like a good time to show you your notebook!"

        t "See this pencil button at the bottom left? Any time you click that, you will make a note of what is being said."

        t "If you want to open your notebook and see what notes you've taken, you can click on that button in the top right!"

        t "You can edit notes you've taken, or write your own custom notes! You can also delete notes you don't want."

        t "Hope that helps!"

        hide tulip
        with dissolve

        e "Whoa, a bee just flew past your face! You know, I bet if we built a garden here, the bees would love it."

        e "The garden would be great for people too. The nearest grocery store is miles away, and most folks don't have a car."

        menu:
            "How can I help?":
                jump explain_problem
            "What's food justice?":
                jump foodjusticeexplain
            "Sure, I'll help.":
                jump agreement
            "Hmm. I should go.":
                jump talk_later

    label explain_problem:
        e "Our food justice project needs space to build a community garden in our neighborhood, so that folks here can grow fresh food that doesn't cost so much."
        e "Gardens are awesome, obviously, but for some reason the Mayor says he wants to see data about the benefits before making a decision."
        e "I'm trying to gather some evidence to convince him, but I could really use some help."
        menu: 
            "What's food justice?":
                jump foodjusticeexplain
            "I'll see what I can do.":
                jump talk_later
    
    label agreement:
        e "Awesome! I really appreciate it."
        jump explain_problem

    label foodjusticeexplain:
        e "Food justice is this idea that everybody deserves access to healthy food that they can afford."
        e "Food in our community should also include stuff that makes sense for each person's culture, because not everyone eats the same kinds of foods."
        e "So many people in the U.S. only have access to fast-food restaurants, gas station food, and other places that sell food that is super processed."
        e "There's nothing wrong with eating that food sometimes, but if that's the only kind of food people in your neighborhood can buy that is affordable, then everyone has more trouble eating healthy and feeling good."
        menu:
            "How can I help?":
                jump explain_problem
            "I'll see what I can do.":
                jump talk_later
    
    label talk_later:
        e "If you're interested, you should go talk with the Community Gardeners. Wes and Nadia, the head gardeners, are over at Westgate Community Garden on the other side of the city."
        e "It would be so great if we could have a garden like that in our neighborhood! They even have beehives!"
        e "You can also check out the science lab, where my friend Riley has been hanging out to learn about food science." 
        $ spoken_list.append("Elliot")

    #grants achievements and tells the player it was granted
        $ achievement.grant("A New Friend")
        $ renpy.notify("Achievement Unlocked: A New Friend")

        jump emptylot

    label foodlab:
        scene science lab
        with dissolve
        $ currentlocation = "foodlab"
        $ visited_list.append("Food Lab")

        show amara smile at left
        with dissolve

        show riley smile at right
        with dissolve

        if foodlabvisit == False:
            narrator "You step into a bustling room full of scientific equipment. A woman in a lab coat is currently sorting vials on a nearby counter."
            narrator "Over by the table, another person is sorting papers and taking notes. You see brightly colored posters that read 'Community Gardeners'."
            $ foodlabvisit = True
        else:
            jump labregular

    label labregular:
        narrator "Click the person you want to talk to, or click the map to travel somewhere else."

        call screen characterselect2("amara", "riley")

    label riley_chatting:
        scene science lab
        with dissolve
        
        show riley smile
        with dissolve

        if rileychat == 0:
            jump riley_1
        else:
            jump riley_2

    label riley_1:
        r "Hi there! Elliot texted me and said he recruited you to help us gather notes for the Southport garden project."
        $ rileychat = 1
        jump rileyintro
        
    label rileyintro:
        r "We're so grateful for your help! I'm Riley. I'm a member of the Community Gardeners."
        r "My job is to advocate for the neighborhood and write persuasive proposals to help us get things we need for the community."
        r "Sometimes the city's budget office forgets about the important things, like green spaces where we can breathe fresh air."
        r "What do you think about the empty lot?"

        menu:
            "I think a community garden is a better idea than a parking lot.":
                jump riley_support
            "I'm not sure, the garage actually sounds like a good idea.":
                jump riley_against
            "I've already got some ideas to persuade the Mayor!":
                jump riley_plan

    label riley_support:
        r "It really is! I'm glad we're on the same page. Elliot knew you'd be a great addition to our team."
        r "Now we just need to figure out how to make sure the Mayor gets it, too. Do you have any ideas for how to convince him?"

        menu:
            "Wait, but what is your job?":
                jump long_intro
            "I have a few ideas.":
                jump riley_plan
            "Not yet, but I will.":
                jump riley_later
    
    label long_intro:
        r "I'm the director of a nonprofit organization called CareWorks. We advocate for the needs of our neighborhood by setting up programs that help the people here." 
        r "We help run things ike community food pantries and after-school activities for kids. My work with the Community Gardeners is part of that!"
        r "We do research to help present proposals to the City, so that we can convince them to use money and resources in ways that will help our community grow."
        r "I'd love your help gathering notes to improve our persuasive writing about why community gardens matter! We're going to share it with the Mayor when we're ready."
        r "There are several other community gardens in the city, but they're all pretty far from this neighborhood, and folks here could really use a reliable source of fresh food."

        menu:
            "I have a few ideas to help with that.":
                jump riley_plan
            "I'm going to find some ideas to help!":
                jump riley_later
            "Hmm.":
                jump not_convinced
    
    label riley_against:
        r "Oh really? I'm curious why you think that."
        $ progarage = renpy.input("Why do you support the parking garage?")
        $ log("Player argument for garage: " + progarage)
        r "Hmm. That's fair. I still think the garden has more benefits for the people and the environment, but that's worth considering."
        r "The government often relies on data and algorithms. But some things, like the value of a community garden, can't be measured in money alone. It's measured in how it helps empower the people who live here."
        
        menu:
            "Wait, but what is your job?":
                jump long_intro
            "I have a few ideas about the garden's benefits, too.":
                jump riley_plan
            "I should go.":
                jump riley_later

    label riley_plan:
        r "I bet if we work together we can make a presentation so persuasive that it blows the socks off the Mayor and runs CityPark right out of town."
        r "I'd love to hear your ideas!"

        menu:
            "Sure, I'll share my ideas.":
                r "Sweet. What do you think we should say to convince the Mayor that a community garden is good for the neighborhood?"
                jump ca_eval_riley
            "I should gather more notes first.":
                jump riley_later
            "Wait, but what is your job?":
                jump long_intro

    label ca_eval_riley:
        $ eca = renpy.input("My persuasive ideas for the Mayor:")

        $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Riley")
        $ log_http(current_user, action="PlayerInputToECA", view="riley", payload=ca_json)
        $ log("Player input to ECA: " + eca)
        $ argument_attempts = argument_attempts + 1

        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                        
        $ log_http(current_user, action="PlayerECAResponse", view="riley", payload={"eca_response": ecaresponse})
        r "[ecaresponse]"

        r "Are there other ideas you want to run by me?"

        menu:
            "I have more evidence to share":
                jump ca_eval_riley
            "That's all for now.":
                r "Okay! Let me know if I can help as you gather more notes."
                jump foodlab
    
    label not_convinced:
        r "Hey, I'm used to convincing skeptical people. Don't you worry! I bet if you talk to folks around town and hear what they have to say, you might see it a little differently."
        jump foodlab


    label riley_later:
        r "Awesome! If you want to run any ideas by me before you talk to the Mayor, I'd be happy to help you workshop your argument. See ya!"
        $ spoken_list.append("Riley")
        jump foodlab
    
    label riley_2:
        r "Back again! I'm glad. What's up?"
        
        menu:
            "What do you know about food justice?":
                jump ca_foodjustice
            "I have some ideas for our pitch to the Mayor.":
                r "Amazing! What ideas have you found about how we should use the empty lot?"
                jump ca_eval_riley
            "See you later.":
                jump byeriley

    label ca_foodjustice:
        r "Oh, all sorts of things! What are you curious about?"

        menu:
            "Why is access to healthy food important?":
                $ eca = "Why is access to healthy food important?"

                $ ca_link, ca_json = agent_setup("Knowledge_FoodJustice", eca, "riley", "Riley")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="riley", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

                r "[ecaresponse]"
                jump foodknowledge_loop
            "How can we help everyone have access to healthy food?":
                $ eca = "How can we help everyone have access to healthy food?"

                $ ca_link, ca_json = agent_setup("Knowledge_FoodJustice", eca, "riley", "Riley")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="riley", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

                r "[ecaresponse]"
                jump foodknowledge_loop
            "I have another question.":
                jump foodknowledge
            "Nevermind.":
                jump byeriley
        
    label foodknowledge_loop:
        r "Anything else you'd like to know?"

        menu:
            "I have another question.":
                jump foodknowledge
            "I have some ideas for our pitch to the Mayor.":
                r "Amazing! What ideas have you found about how we should use the empty lot?"
                jump ca_eval_riley
            "Nah I'm okay.":
                jump byeriley

    label foodknowledge:
        $ eca = renpy.input("I'm wondering...")

        $ ca_link, ca_json = agent_setup("Knowledge_FoodJustice", eca, "riley", "Riley")
        $ log_http(current_user, action="PlayerInputToECA", view="riley", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

        r "[ecaresponse]"
        jump foodknowledge_loop
    
    label byeriley:
        r "Keep doing great things! I'll be here if you need me."
        $ rileychat = rileychat + 1
        jump foodlab

    label amara_chatting:
        scene science lab
        with dissolve
        
        show amara smile
        with dissolve

        if amarachat == 0:
            jump amara_1
        else:
            jump amara_2

    label amara_1:

        a "Hi! I'm Amara - I'm the lead scientist here at the food lab. Great to meet you."
        $ amarachat = 1
        jump intro_amara_questions

    label intro_amara_questions:
        default amara_menu = set()
        menu:
            set amara_menu
            "What's a food scientist?":
                jump foodscientist
            "Do you know anything about the garden project?":
                jump garden_info
            "What kind of stuff do you do here?":
                jump lab_stuff
            "Nice to meet you! Gotta go.":
                jump amara_later

    label foodscientist:
        a "Food scientists use chemistry, biology, and other sciences to study and analyze nutritional content like protein, fats, and vitamins."
        a "We look at food quality, how to make nutrients last longer, and what causes food go bad. It can really help with making processed foods safe and healthy."
        a "So, basically, our aim is to help everyone have fresh, safe, and nutritious food."
        $ AddToSet(amara_menu, "What's a food scientist?")
        jump intro_amara_questions

    label garden_info:
        a "The neighborhood has been buzzing with discussion about the empty lot and that parking company that wants to buy it up."
        a "From a food scientist's perspective, I really hope the Mayor supports the community garden."

        menu:
            "Why?":
                jump reasons
            "Yeah, me too.":
                a "I knew I liked you!"
                jump reasons
    
    label reasons:
        a "People without local produce markets or community gardens mostly have to rely on shipped and preserved food."
        a "Shipping food isn't bad, necessarily, but it makes getting fresh, healthy food more complicated."
        a "In order to ship food from different places, you need to process the food to preserve its taste and prevent it from going bad."
        a "We usually freeze, cook, or can foods, or add some chemicals, which are also known as food additives."
        a "When we process food, the food loses some nutrients and often ends up having high levels of sugar, salt, and fat, and not all food additives are good for our bodies."
        a "That means if we only have access to shipped foods, we might have issues with lack of nutrition or we might eat too much of these unhealthy food additives."
        a "Anyway, a community garden doesn't fix everything, but it gives the people in the neighborhood another option for how to get affordable, fresh food."
        $ AddToSet(amara_menu, "Do you know anything about the garden project?")
        jump intro_amara_questions

    label lab_stuff:
        a "I research things about food, how it grows, and how our bodies use it."
        a "When I was younger, I got so interested in food, especially fruits and vegetables that have a variety of colors."
        a "Did you know that fruits and vegetables with different colors usually provide our bodies with different kinds of nutrients?"
        a "Those are the kinds of things I explore in my lab - what kinds of nutrients different foods have, and how to make sure foods are safe and healthy for our bodies."
        $ AddToSet(amara_menu, "What kind of stuff do you do here?")
        jump intro_amara_questions

    label amara_later:
        a "Oh okay! Well you're welcome to hang out, let me know if you get curious about anything!"
        $ spoken_list.append("Amara")
        jump foodlab

    label amara_2:
        a "Hey there! What are you up to?"
        jump amara_revisit

    label amara_revisit:
        menu:
            "I'm trying to gather evidence about gardens.":
                jump sciencequestions
            "I'm trying to gather evidence about parking lots.":
                jump parkingquestions
            "Actually, we should talk later.":
                jump amarabye
    
    label sciencequestions:
        a "Oh, I'm full of facts. Maybe I can help! What are you curious about?"

        menu: 
            "Why does genetic diversity in plants matter?":
                jump genetics
            "What do you know about soil quality?":
                jump soil
            "What do gardens do for the environment?":
                jump environment
            "See you later.":
                jump foodlab

        label genetics:
            a "Oh, plant genetics are so interesting. Like people, plants have DNA that carries information about the different kinds of traits they have."
            jump sciencequestions

        label soil:
            a " Soil is super important for the health of plants. Dirt just looks like dirt at first glance, but there are actually 14 different nutrients in the soil that can change how plants grow."
            jump sciencequestions
        
        label environment:
            a "For the ecosystem, gardens give insects and animals a home. They provide food for pollinators and can be especially helpful if they're full of native plants."
            jump sciencequestions

    label parkingquestions:
        a "Ah, so you're curious about how the parking lot will impact the neighborhood?"
        a "I mostly study food, so I don't know a ton about the economic impact of garages or how cars change the environment."
        a "Wes might know more - he did a lot of that research when he was building the Westgate community garden!"
        jump amara_revisit

    label amarabye:
        a "Have a great day! Let me know if I can help with your research."
        jump foodlab

    label garden:
        scene garden
        with dissolve
        $ currentlocation = "garden"
        $ visited_list.append("Garden")

        show victor smile at left
        with dissolve

        show wes smile
        with dissolve

        show beehives travel at right
        with dissolve

        if gardenvisit == False:
            narrator "You arrive at a community garden across town after a long bus ride. The garden is full of colorful fruits and vegetables growing in planter boxes and plots on the ground."
            narrator "A friendly looking older man gives you a wave. Others are walking through the garden or tending to plants, and beyond them, you see a row of beehives."
            $ gardenvisit = True
        else:
            jump gardenregular

    label gardenregular:
        narrator "Click the person you want to talk to, click the button to visit the beehives, or click the map to travel somewhere else."

        call screen characterselect3("victor", "wes", "bees")
         
    label victor_chatting:
        scene garden
        with dissolve

        show victor smile
        with dissolve

        v "Hi, I'm Victor. I just moved here a few months ago. Great to meet you!"
        v "There's a really delicious soup from my hometown that I've been craving ever since I moved."
        v "But the grocery stores here don't sell the kinds of vegetables that my family uses to make the soup extra flavorful and special."
        v "I really want to make a soup that tastes like home. I wonder if the community gardeners would let me grow my own vegetables here?"
        v "I don't even have a balcony at my apartment, much less a yard. But maybe if I lived near a garden, I could learn how to grow things."
        $ victorchat = 1

    label victormenu:
        menu:
            "Do you live nearby?":
                jump gardenfar
            "Do you know a lot about growing things?":
                jump gardenknowledge
            "So you like the garden idea?":
                jump victoropinion
            "I'll talk to you later.":
                v "Okay! See you later."
                $ spoken_list.append("Victor")
                jump garden

    label victoropinion:
        v "Yeah! I think a garden would be a great use of land for the neighborhood. It will let us grow heirloom produce that we can't find in stores."
        v "A neighborhood garden would also give everybody access to fresh food, even if they don't have a lot of money to spend on groceries."
        v "Since some neighborhoods don't have supermarkets, a garden would give more people healthy food options. And it can be fun to grow things yourself!"

    label heirloommenu:
        menu:
            "What's heirloom produce?":
                jump heirloom
            "Why do you want to grow heirloom produce?":
                jump whyheirloom
            "I have a different question":
                jump victormenu
            "I'll talk to you later.":
                v "Okay! See you later."
                $ spoken_list.append("Victor")
                jump garden
            
    label heirloom:
        v "Heirloom fruits and vegetables are varieties of plants that have been passed down for many generations through seeds."
        v "Heirloom produce has unique colors, shapes, and flavors that you won't find at most grocery stores, because these types of plants aren't used in the big commercial farms that make most of our food."
        v "Big farms use plants that make large, nice looking fruit, because it sells better at the store."
        v "Those big farm varieties are also bred to be more resistant to disease and weather, so the crops survive better."
        v "But the tradeoff is that without heirloom versions of plants, we have less variety in tasty and unique flavors of produce."
        jump heirloommenu

    label whyheirloom:
        v "I really love the taste of heirloom fruits and veggies better. They're just extra juicy and have unique flavors."
        v "Growing up, my family used heirloom plants that our neighbors grew to make my favorite foods, like the soup I want to make!"
        v "So those different varieties of heirloom produce remind me of home. The grocery store versions just don't taste the same, if I can find them at all."
        jump heirloommenu

    label gardenknowledge:
        v "Not at all! I've never grown anything before. But Wes said he would be happy to teach me."
        v "I thought growing my own food would be too hard, but the community gardeners have lots of guides to help us figure out how to care for different kinds of plants."
        jump victormenu
    
    label gardenfar:
        v "No, it took me 45 minutes to get here on the bus. But I heard that the gardeners are trying to turn the empty lot near my house into a garden!"
        v "That lot is only a 10 minute walk from my apartment. If we had a garden there, it would be a lot easier for me to grown my own vegetables."
        jump victormenu

    
    label wes_chatting:
        scene garden
        with dissolve

        show wes smile
        with dissolve

        if weschat == 0:
            jump wes_1
        else:
            jump wes_2

    label wes_1:
        w "Hey there! Welcome to the Westport Community Garden. Elliot called and said you might come by."
        w "Feel free to explore the garden, and let me know if you are curious about anything."
        $ weschat = 1
        jump wes_choices

    label wes_choices:
        default wes_menu = set()
        menu:
            set wes_menu
            "Tell me about the food you're growing.":
                jump growing_food
            "Is the garden good for the neighborhood?":
                jump garden_benefits
            "How can we pollinate plants in the garden?":
                jump wes_plants
            "I have a different question.":
                jump gardenquestions
            "See you later.":
                jump bye_wes

    label growing_food:
        w "We grow all sorts of food here! Tomatoes, watermelon, zucchini, cucumbers, bell peppers, strawberries - the list goes on!"
        w "Some of the plants, like tomatoes, we grow in containers, and others like the melons need more space to spread out."
        w "Growing your own food means the fruits and vegetables will be fresher and tastier, because they don't have to travel from other states or countries to get to your plate."
        w "Homegrown fruits and vegetables are also good for our health because we can control the soil quality - and better soil means more nutritious produce."
        $ AddToSet(wes_menu, "Tell me about the food you're growing.")
        jump wes_choices

    label garden_benefits:
        w "Absolutely! Gardens are really useful for people and for the insects and animals that live around here."
        w "The people in the neighborhood can grow fresh fruits and vegetables, and all the different plants and flowers provide food for pollinators."
        $ AddToSet(wes_menu, "Is the garden good for the neighborhood?")
        jump pollen_questions

    label pollen_questions:
        menu:
            "What are pollinators?":
                jump wes_pollen
            "What types of pollinators exist?":
                jump types_pollinators
            "How do plants help pollinators?":
                jump plants_help
            "I have a different question.":
                jump gardenquestions
            "See you later.":
                jump bye_wes

    label wes_pollen:
        w "Pollinators are creatures like bees and butterflies that transfer pollen from one flower to another."
        w "This helps the plants reproduce and grow food - lots of plants can't grow their fruits without the help of pollinators!"
        jump pollen_questions

    label types_pollinators:
        w "Honeybees are a particularly important pollinator for humans, because they pollinate a lot of the food crops that we grow."
        w "Flies, butterflies, birds, and even bats also pollinate particular types of flowers in different regions of the world."
        w "But insects are definitely the most common pollinators when it comes to the foods that humans eat."
        jump pollen_questions

    label plants_help:
        w "Many pollinators, like honeybees, get food from plants by drinking flower nectar and eating pollen."
        w "When the pollinators visit the plants, they move pollen from one part of the flower to another while they are gathering food."
        w "It's a happy little accident - they're just trying to get food for themselves, but they end up helping us grow our food, too!"
        w "Pollination helps the plants grow nice healthy fruits, which gives us yummy things to eat!"
        jump pollen_questions

    label wes_plants:
        w "Plants can be pollinated by wind, by insects and animals, and by people. This happens when pollen from a plant's flower is moved from the male part of the flower to the female part of the flower."
        w "People can pollinate some plants by using cotton swabs to help transfer pollen between flowers. This can be helpful when there aren't lots of pollinators around, but it takes a lot of time."
        w "If we want to grow lots of food, it's better to have pollinators nearby who can help the plants grow healthy."
        $ AddToSet(wes_menu, "How can we pollinate plants in the garden?")
        jump wes_choices
   
    label gardenquestions:
        w "What would you like to know about the garden?"
        $ eca = renpy.input("I'm wondering...")

        $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Wes")
        $ log_http(current_user, action="PlayerInputToECA", view="wes", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

        $ log_http(current_user, action="PlayerECAResponse", view="wes", payload={"eca_response": ecaresponse})

        w "[ecaresponse]"

        jump wes_choices

    label bye_wes:
        w "It was great talking with you. Come by anytime, kid."
        $ spoken_list.append("Wes")
        jump garden

    label wes_2:
        w "Hope you're enjoying the garden, friend. Can I help with anything?"
        jump wes_questions

    label wes_questions:
        menu:
            "I have a question about the garden":
                jump wes_ca
            "I should go.":
                jump bye_wes2

    label bye_wes2:
        w "No problem. Enjoy the garden!"
        $ weschat = weschat + 1
        jump garden

    label wes_ca:
        w "What would you like to know?"
        $ eca = renpy.input("I'm wondering...")

        $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Wes")
        $ log_http(current_user, action="PlayerInputToECA", view="wes", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

        $ log_http(current_user, action="PlayerECAResponse", view="wes", payload={"eca_response": ecaresponse})

        w "[ecaresponse]"

        w "Would you like to know anything else?"

        jump wes_questions

    label bees_chatting:
        scene beehives
        with dissolve
        $ currentlocation = "beehives"
        $ visited_list.append("Beehives")

        show nadia smile at left
        with dissolve

        show alex smile
        with dissolve

        show cora concern at right
        with dissolve

        if hivesvisit == False:
            narrator "There are lots of bees buzzing about as you approach the beehives. The beekeeper smiles warmly at you."
            narrator "A small child is grinning and laughing as he watches the bees fly by. A worried-looking woman watches him carefully."
            $ hivesvisit = True
        else:
            jump hivesregular

    label hivesregular:
        narrator "Click the person you want to talk to, or click the map to travel somewhere else."

        call screen characterselect3("nadia", "alex", "cora")
    
    label nadia_chatting:
        scene beehives
        with dissolve

        show nadia smile
        with dissolve 

        if nadiachat == 0:
            jump nadia_1
        else:
            jump nadia_2

    label nadia_1:
        n "Hi, I'm Nadia. I'm a beekeeper, though you can probably tell that from the outfit. I take care of the beehives in several community gardens around town." 
        n "If you have any questions about bees, plants, and pollination, I'd be happy to tell you what I know."
        $ nadiachat = 1
        default nadia_menu = set()
        jump nadia_questions
      
    label nadia_questions:
        menu:
            set nadia_menu
            "Why did you become a beekeeper?":
                jump beekeeper
            "How do bees help with pollination?":
                $ eca = "How do bees help with pollination?"

                $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="nadia", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

                n "[ecaresponse]"
                $ AddToSet(nadia_menu, "How do bees help with pollination?")
                jump nadia_questions
            "How do plants get pollinated?":
                $ eca = "How do plants get pollinated?"

                $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="nadia", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

                n "[ecaresponse]"
                $ AddToSet(nadia_menu, "How do plants get pollinated?")
                jump nadia_questions
            "I have a different question.":
                jump nadia_ca
            "See you later.":
                jump nadia_bye
    
    label beekeeper:
        n "I grew up on a farm, and I always thought bees were amazing. They're so small, but also so coordinated and intelligent!"
        n "Did you know that bees communicate the locations of flowers to each other by dancing? How cool is that?"
        n "Anyway, bees are just such an important part of our ecosystem that I wanted to do something to help take care of them."
        n "Bees are important for pollinating lots of crops, such as almonds, apples, and blueberries. Without bees, many crops would have to be pollinated by hand, which would take a ton of time and money."
        $ AddToSet(nadia_menu, "Why did you become a beekeeper?")
        jump nadia_questions

    label nadia_ca:
        $ eca = renpy.input("I'm wondering...")

        $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
        $ log_http(current_user, action="PlayerInputToECA", view="nadia", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

        $ log_http(current_user, action="PlayerECAResponse", view="nadia", payload={"eca_response": ecaresponse})

        n "[ecaresponse]"

        n "Do you have any other questions?"
        menu:
            "I have more questions.":
                jump nadia_ca
            "No, I should go.":
                if nadiachat == 1:
                    jump nadia_bye
                else:
                    jump byenadia2
    
    label nadia_bye:
        n "It was nice to meet you. Let me know if you have any more questions as you explore the garden!"
        $ spoken_list.append("Nadia")

        jump bees_chatting

    label nadia_2:
        n "Hello dear! Can I help you with anything?"

        menu:
            "I have a question for you.":
                jump nadia_ca
            "Actually, I'll talk to you later":
                jump byenadia2

    label byenadia2:
        n "No problem at all. Enjoy your visit!"
        jump bees_chatting

    label alex_chatting:
        scene beehives
        with dissolve

        show alex smile
        with dissolve 

        if alexchat == 0:
            jump x_1
        else:
            jump x_2

    label x_1:
        x "Hi! Are you a gardener?"     
        $ alexchat = 1

        menu:
            "No, I'm just visiting.":
                jump alex_visitor
            "I want to be!":
                jump alex_gardener
            "I'm busy.":
                jump sadkid

    label alex_visitor:
        x "Us too! Mom says they might build a garden like this next door to our apartment building."
        x "I love the bees buzzing! Buzzzz buzzz buzzz..."
        jump questions_alex

    label alex_gardener:
        x "Whoa! Me too. I like worms. And dirt. And BEES!"
        jump questions_alex

    label questions_alex:
        menu:
            "What do you think about the garden?":
                jump gardenthink
            "Do you live near the empty lot?":
                jump alex_lot
            "What kind of food do you wanna grow?":
                jump alex_growfood
            "Buzz ya later!":
                jump buzzbye_alex

    label gardenthink:
        x "I like this garden! There's so many bees. Mom thinks they're creepy but I like them!"
        x "And Wes gave me a tomato! It was yummy. Maybe I could grow big tomatoes like that if I was a gardener."
        jump questions_alex

    label alex_lot:
        x "The big old dirt patch? Yeah. I throw rocks at the fence sometimes. Don't tell my mom."
        jump questions_alex

    label alex_growfood:
        x "I don't know. Can you grow pizza in a garden?"
        x "Mom says she wants to grow spinach and tomatoes. Tomatoes are pizza! So we can grow part of the pizza."
        x "I like blueberries too. We don't get the fresh ones lots but they're way juicier than the frozen bag ones."
        jump questions_alex

    label buzzbye_alex:
        x "Hahaha! Buzz you later!"
        $ spoken_list.append("Alex")
        jump bees_chatting

    label sadkid:
        x "Ohh..."
        $ spoken_list.append("Alex")
        jump bees_chatting

    label x_2:
        x "Buzzzz... buzz buzz buzz!"
        x "There's a bee by your head. I think it likes you!"

        show tulip at left
        with dissolve

        t "Oh I love that kid. By the way, do you need any help? You can always click my button to say hi if you get bored!"

        $ renpy.call("tulip_help_menu")

        jump bees_chatting

    label cora_chatting:
        scene beehives
        with dissolve

        show cora concern
        with dissolve 

        c "Hello."  
        $ corachat = 1
        $ spoken_list.append("Cora")    

        jump bees_chatting

    label emptylot:
        scene expression "[startplace]"
        with dissolve
        $ currentlocation = "emptylot"
        $ visited_list.append("Empty Lot")

        show elliot smile at left
        with dissolve

        show cyrus smile at right
        with dissolve
        
        show watson smile
        with dissolve

        if emptylotvisit == False:
            narrator "The empty lot isn't much - just a wide patch of dirt. Elliot is exploring, likely imagining what a garden would look like here."
            narrator "You see two men in suits sizing up the empty lot. You wonder what so many people are doing wandering around an empty bit of land."
            $ emptylotvisit = True
        else:
            jump emptylotregular

    label emptylotregular:
        narrator "Click the person you want to talk to, or click the map to travel somewhere else."

        call screen characterselect3("elliot", "watson", "cyrus")
    
    label cyrus_chatting:
        scene expression "[startplace]"
        with dissolve

        show cyrus smile
        with dissolve

        if cyruschat == 0:
            jump cy_1
        else:
            jump cy_2

    label cy_1:
        cy "Hey there, kiddo. Cyrus Murphy, Marketing Executive for CityPark."
        cy "Nice to meet ya."
        $ cyruschat = 1

        menu:
            "Great to meet you!":
                jump excited_cy
            "Hey.":
                jump normal_cy
            "Don't respond.":
                jump dislike_cy

    label excited_cy:
        cy "It's great to see young people in this neighborhood so passionate about growth in their community!"
        cy "Our team at CityPark is looking forward to meeting more people like you while we get ready to build our new garage."
        jump cy_menu

    label normal_cy:
        cy "I'm glad so many folks have come by to say hello - our team at CityPark is all about working with the community."
        cy "Are you excited about the new garage?"
        jump cy_menu

    label dislike_cy:
        cy "Hey, I get it, you've got better things to do than talk with some stranger in a suit. But I look forward to getting to know you and your neighbors better as we begin building our new garage!"
        jump cy_menu
    
    label cy_menu:
        menu:
            "New garage?":
                jump cy_pitch
            "Can't wait!":
                jump agree_garage
            "We don't want a new garage.":
                jump dislike_garage
            "I gotta go.":
                jump bye_cy

    label cy_pitch:
        cy "This empty lot here is the future site of a CityPark Park Express garage! It will have six levels, state-of-the-art elevators, and a prime location to encourage new businesses to move in on this street."
        cy "As soon as we get the sign-off from Mayor Watson, we're going to begin construction."

        menu:
            "Can't wait!":
                jump agree_garage
            "We don't want a new garage.":
                jump dislike_garage
            "I gotta go.":
                jump bye_cy
    
    label agree_garage:
        cy "That's what I'm talking about - you're a bright kid. Make sure to tell your friends all about CityPark and what a great choice we are for your neighborhood!"
        jump bye_cy
    
    label dislike_garage:
        cy "Hey now, I know change can be scary, but just think about how much money the garage could make for the city!"
        cy "And that money can help fix roads, fund schools, and support the community. More parking means more businesses, more neighborhood growth - you're gonna love it, I swear."
        
        show elliot smile at left
        with dissolve

        hide cyrus smile

        show cyrus smile at right
        with dissolve

        e "We're NOT going to love it, Mr. Murphy. The garage might make money for you and your company, but the people here need food, not a place to park cars."

        cy "Now Elliot, we've been over this! When we get this garage built, I'm sure a big grocery store will move right into town, and wouldn't you rather just go buy your food rather than having to spend all that time growing it?"

        menu:
            "Actually, a grocery store sounds nice.":
                jump grocery
            "A garden is better for the neighborhood, and I'm gonna prove it.":
                jump cy_challenge
            "I'm not sure.":
                jump unsure
    
    label unsure:
        cy "It's a complex problem, kid. Perhaps you should learn more about it before you fall in with these gardeners."

        e "Ugh, ignore him. But it is a good idea to talk to the others in the neighborhood. We'll need their support to convince the Mayor!"
        $ spoken_list.append("Cyrus")
        jump emptylot

    label grocery:

        e "I know, it would be great if a grocery store moved in. But big chain stores don't usually move into low-income neighborhoods like this one because they don't think they'll make enough money."
        e "I'm not convinced a parking garage will change that."

        cy "You never know until you try! We've been gathering economic data on how garages impact neighborhood growth. You'll need a lot of evidence to beat our pitch to the Mayor, kid."

        menu:
            "We'll find the evidence.":
                jump cy_challenge
            "I need to go.":
                jump bye_cy

    label cy_challenge:
        e "That's right! We're working hard to build a persuasive argument for the Mayor to support the community garden project."

        cy "Alright kiddo, whatever you say. Best of luck, and may the best argument win."
        $ spoken_list.append("Cyrus")
        jump emptylot

    label bye_cy:
        cy "Great talking with you, kiddo! Take it easy."
        $ spoken_list.append("Cyrus")
        jump emptylot

    label cy_2:
        cy "Ah, our resident investigator, back again. What can I do for you?"
        jump cy_questions

    label cy_questions:
        menu:
            "What evidence do you have about the benefits of the parking garage?":
                jump garage_benefits
            "Have you considered how car pollution might impact the neighborhood?":
                jump cy_pollution
            "Nevermind, I should go.":
                jump later_cy

    label garage_benefits:
        cy "Ah, so you're coming around to our plan? Wonderful!"
        cy "Parking garages can be great for local businesses. If people from out of town can easily park in the neighborhood, then more people will stop here and spend money on shopping trips."
        cy "More parking means more businesses can move in, which makes the economy of the neighborhood stronger! It might even bring new jobs to the area."
        jump cy_questions

    label cy_pollution:
        cy "Oh, cars are everywhere. One more garage won't change anything. The pollution isn't as important as the money the garage will make for the city."
        
        menu:
            "What about the pollinators?":
                jump cy_bees
            "I guess you're right.":
                cy "That's the spirit. CityPark will make this neighborhood a shopping hotspot for the city!"
                jump cy_questions
    
    label cy_bees:
        cy "What about them? The bees can just go somewhere else to find flowers. We should care more about the people here, and making the local economy stronger."
        jump cy_questions

    label later_cy:
        cy "Alright then. Tell your friends to sign up for our CityPark newsletter!"
        $ cyruschat = cyruschat + 1
        jump emptylot
    
    label watson_chatting:
        scene expression "[startplace]"
        with dissolve

        show watson smile
        with dissolve

        m "Hello."
        $ mayorchat = 1
        $ spoken_list.append("Mayor Watson")

        jump emptylot

    label elliot_chatting:
        scene expression "[startplace]"
        with dissolve

        show elliot smile
        with dissolve

        e "Welcome back! Did you find some interesting evidence for us to use in our pitch to the mayor?"
        jump ideasharing

    label ideasharing:
        e "What are your ideas?"
        $ eca = renpy.input("My ideas for the mayor:")

        $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Elliot")
        $ log_http(current_user, action="PlayerInputToECA", view="elliot", payload=ca_json)
        $ log("Player input to ECA: " + eca)
        $ argument_attempts = argument_attempts + 1

        $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

        $ log_http(current_user, action="PlayerECAResponse", view="elliot", payload={"eca_response": ecaresponse})
        e "[ecaresponse]"

        e "Are there other ideas you want to run by me?"

        menu:
            "I have more evidence to share":
                jump ideasharing
            "That's all for now.":
                e "Okay! Let me know if you find new evidence later!"
                jump emptylot

    # This ends the game.

    return
