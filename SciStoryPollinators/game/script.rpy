# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

# Code for switching out CA models in the narrative #
# anywhere you see "ecaresponse" in the code, a CA is being called
# Need to write a function to replace the link with a variable switch so that we only have to switch out one line rather than all the CA calls separately
# flanT5-small: 
# $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
# Only have to change ECAType based on which CA character you want to call
# Possible types:
# FoodJustice_RileyEvaluation, FoodJustice_MayorEvaluation, Knowledge_FoodJustice, Knowledge_Pollination
# GameHelp, GameHelp_Collaboration, GEMSTEP_Observing

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
default customnotecount = 0
default emptylotvisit = False
default foodlabvisit = False
default gardenvisit = False
default hivesvisit = False
default name = "Player"
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

init python:
    import datetime
    from typing import Dict, Any, Optional
    import os
    # Todo: Remove this later
    if renpy.emscripten:
        import emscripten
        result = emscripten.run_script("window.syncFlowPublisher.startPublishing('umesh', 'umesh')")
        

    #### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####
    current_label = None
    current_user = "Unknown"

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

    narrator "You open your eyes and find yourself surrounded by bright flowers and sweet-smelling fresh air. How did you get here?"
    
    narrator "You hear a quiet buzzing noise getting closer..."

    narrator "and {size=*1.5}closer...{/size}"

    narrator "and {size=*2}closer...{/size}"

    show tulip
    with dissolve

    narrator "Suddenly, tiny bee flies around your head and hovers in front of you!"

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

        menu:
            "I don't know what to do.":
                t "I would start by talking to people around town to see what they have to say!"
                t "If you've done that already, try opening your notebook to see what information you've collected, and think about what else you want to know."
                hide tulip
                with dissolve
                return
        #    "How do I get my group to listen to me?":
        #        t "Humans are a lot like bees - sometimes we're so busy buzzing around trying to be heard that we forget to listen!"
        #        t "You could try saying, “Hey, what do you think of this note I found? I think you'd have some good ideas about it."
        #        t "If you show your group that you care about what they have to say, they are more likely to listen to you in return."
        #        hide tulip
        #        with dissolve
        #        return
            "I'd like some help with persuading the mayor.":
                t "I'd be happy to help! If you tell me what evidence you've found, I can give you some advice on improving your pursuasive writing."
                $ eca = renpy.input("What should the Mayor do with the empty lot, and why?")
                $ log("Player input to ECA: " + eca)
                $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                t "[ecaresponse]"
                t "Do you have other evidence to share?"
                menu:
                    "I have more ideas to add.":
                        $ eca = renpy.input("What should the Mayor do with the empty lot, and why?")
                        $ log("Player input to ECA: " + eca)
                        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                        t "[ecaresponse]"
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
                $ log("Player input to ECA: " + eca)
                $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "GameHelp", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                t "[ecaresponse]"
                t "Any more questions?"
                menu:
                    "I have another question.":
                        $ eca = renpy.input("What's your question?")
                        $ log("Player input to ECA: " + eca)
                        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "GameHelp_Collaboration", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                        t "[ecaresponse]"
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

# player can enter their name and it removes whitespace from entry
    $ name = renpy.input("What's your name?")
    $ name = name.strip()
    # $ log("Player name: " + name)
    $ current_user = name
    $ log_http(current_user, action="PlayerIntroduced", view="intro", payload=None)

    e "Great to meet you [name]! I'm Elliot. I'm hoping you'll help me convince Mayor Watson not to sell our lot to those parking guys."

    menu:
        "What parking guys?":
            jump parkingguys
    
    label parkingguys:
        e "That guy over there in the suit is from CityPark. They want to turn our empty lot into a big parking garage for the neighborhood."
        e "But me and the other Community Gardeners have been trying to convince Mayor Watson to donate the lot to our food justice project instead."

        e "The parking garage makes money, but a community garden would be huge for this neighborhood!"

        show tulip at left
        with dissolve

        t "Hey [name]! Sorry to interrupt - but this seems like a good time to show you your notebook!"

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

    #grants achievements and tells the player it was granted
        $ achievement.grant("A New Friend")
        $ renpy.notify("Achievement Unlocked: A New Friend")

        jump emptylot

    label foodlab:
        scene science lab
        with dissolve
        $ currentlocation = "foodlab"

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
        r "Let me guess - you're [name]! Oh, it's so great to meet you."
        $ rileychat = 1

        menu:
            "That's me!":
                jump rileyintro
            "How do you know my name?":
                r "Oh, Elliot texted me and said he recruited you to help us gather notes for the Southport garden project!"
        
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
        # $ log("Player input to ECA: " + eca)
        $ log_http(current_user, action="PlayerInputToECA", view="riley", payload={"utterance": eca, "eca_type": "FoodJustice_RileyEvaluation", "context": "", "confidence_threshold": 0.3})
        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
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
                $ log("Player input to ECA (from template): " + eca)
                $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "Knowledge_FoodJustice", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                r "[ecaresponse]"
                jump foodknowledge_loop
            "How can we help everyone have access to healthy food?":
                $ eca = "How can we help everyone have access to healthy food?"
                $ log("Player input to ECA (from template): " + eca)
                $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "Knowledge_FoodJustice", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
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
        $ log("Player input to ECA: " + eca)
        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "Knowledge_FoodJustice", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
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
        jump foodlab

    label amara_2:
        a "Hey [name]! What are you up to?"
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

        v "Hello."

        jump garden
    
    label wes_chatting:
        scene garden
        with dissolve

        show wes smile
        with dissolve

        w "Hey there [name]! Welcome to the Westport Community Garden. Elliot called and said you might come by."
        jump wes_choices

    label wes_choices:
        menu:
            "I have a question.":
                jump gardenquestions
            "See you later.":
                jump garden

    label gardenquestions:
        w "Anything you'd like to know about the bees in our garden?"
        $ eca = renpy.input("I'm wondering...")
        # $ log("Player input to ECA: " + eca)
        $ log_http(current_user, action="PlayerInputToECA", view="garden", payload={"utterance": eca, "eca_type": "Knowledge_Pollination", "context": "", "confidence_threshold": 0.3})
        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "Knowledge_Pollination", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
        $ log_http(current_user, action="PlayerECAResponse", view="garden", payload={"eca_response": ecaresponse})
        w "[ecaresponse]"

        jump wes_choices

    label bees_chatting:
        scene beehives
        with dissolve
        $ currentlocation = "beehives"

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

        n "Hello." 

        jump bees_chatting     

    label alex_chatting:
        scene beehives
        with dissolve

        show alex smile
        with dissolve 

        x "Hello."     

        jump bees_chatting

    label cora_chatting:
        scene beehives
        with dissolve

        show cora concern
        with dissolve 

        c "Hello."      

        jump bees_chatting

    label emptylot:
        scene expression "[startplace]"
        with dissolve
        $ currentlocation = "emptylot"

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

        cy "Hello."

        jump emptylot
    
    label watson_chatting:
        scene expression "[startplace]"
        with dissolve

        show watson smile
        with dissolve

        w "Hello."

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
        $ log_http(current_user, action="PlayerInputToECA", view="emptylot", payload={"utterance": eca, "eca_type": "FoodJustice_RileyEvaluation", "context": "", "confidence_threshold": 0.3})
        $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
        $ log_http(current_user, action="PlayerECAResponse", view="emptylot", payload={"eca_response": ecaresponse})
        e "[ecaresponse]"
        jump ideasharing

    # This ends the game.

    return
