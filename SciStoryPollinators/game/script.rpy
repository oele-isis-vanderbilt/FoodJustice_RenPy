label start:

    # if useAudio: 
    #     play music "JaracandaLoop.wav" volume 0.1

    # Show a background
    scene flowers muted
    with fade

    hide screen learningbuttons

    $ current_user = safe_renpy_input("Please enter your player ID")
    
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
            $ startplace = "city"
            $ structure = "garage"
           
        "I live in a rural town":
            $ startplace = "rural"
            $ structure = "lot"
        
        "I live in the suburbs":
            $ startplace = "suburb" 
            $ structure = "lot"

    $ log_http(current_user, action="PlayerLocationChoice", view="tulip", payload={"startplace": startplace})

    t "Wonderful! We'll explore a neighborhood that's kinda like yours that needs your help."

    t "I'm here as your guide, so if you get stuck or need advice, just click on my button and I'll buzz on by."

    t "We should get going then. Lots to do, lots to see! Are you ready?"

    menu:
        "Let's go!":
            t "Yay! Let's zoom!"
        "I guess.":
            t "Don't worry, I'll be right by your side if you need help! We're two bees in a pod. Hehe."

    jump begin

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
                t "I'd be happy to help! If you tell me what evidence you've found, I can give you some advice on improving your persuasive writing."

                $ eca = safe_renpy_input("What should the Mayor do with the empty lot, and why?", screen="argument_sharing")
                if not isinstance(eca, str) or not eca.strip():
                    t "No problem. Let me know when you're ready to share!"
                    jump tulip_help_menu
                $ eca = eca.strip()

                $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Tulip")
                $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                $ log("Player input to ECA: " + eca)
                $ argument_attempts = argument_attempts + 1
                $ achieve_argument()

                python:
                    try:
                        ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    except Exception as e:
                        log_http(current_user, action="AgentError", view="tulip", payload={"details": str(e)})
                        ecaresponse = "I'm having some trouble right now. Try raising your hand and asking one of the researchers to look at your argument!"
                # $ ecaresponse = renpy.fetch("https://tracedata-01.csc.ncsu.edu/GetECAResponse", method="POST", json={"ECAType": "FoodJustice_RileyEvaluation", "Context": "", "Utterance": eca, "ConfidenceThreshold": 0.3}, content_type="application/json", result="text")
                
                $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                $ start_generated_dialogue("eca", {"character": "Tulip", "context": "FoodJustice_RileyEvaluation"})
                if ecasplit == True:
                    $ playAudio(ecaresponse1)
                    t "[ecaresponse1]"
                    $ playAudio(ecaresponse2)
                    t "[ecaresponse2]"
                else:
                    $ playAudio(ecaresponse)
                    t "[ecaresponse]"
                $ finish_generated_dialogue()

                $ stopAudio()

                $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})

                $ savedraft = renpy.confirm("Do you want to save this argument as your new draft? This will replace your existing argument in the notebook.")

                if savedraft == True:
                    $ save_draft(eca)
                else:
                    pass
               
                t "Do you have other evidence to share?"
                menu:
                    "I have more ideas to add.":
                        $ eca = safe_renpy_input("What should the Mayor do with the empty lot, and why?", screen="argument_sharing")
                        if not isinstance(eca, str) or not eca.strip():
                            t "Okay! Come back when you're ready."
                            hide tulip
                            with dissolve
                            return
                        $ eca = eca.strip()

                        $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Tulip")
                        $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                        $ log("Player input to ECA: " + eca)
                        $ argument_attempts = argument_attempts + 1
                        $ achieve_argument()

                        python:
                            try:
                                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                            except Exception as e:
                                log_http(current_user, action="AgentError", view="tulip", payload={"details": str(e)})
                                ecaresponse = "I'm having some trouble right now. Try raising your hand and asking one of the researchers to look at your argument!"

                        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                        $ start_generated_dialogue("eca", {"character": "Tulip", "context": "FoodJustice_RileyEvaluation"})
                        if ecasplit == True:
                            $ playAudio(ecaresponse1)
                            t "[ecaresponse1]"
                            $ playAudio(ecaresponse2)
                            t "[ecaresponse2]"

                        else:
                            $ playAudio(ecaresponse)
                            t "[ecaresponse]"
                        $ finish_generated_dialogue()

                        $ stopAudio()

                        $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})

                        $ savedraft = renpy.confirm("Do you want to save this argument as your new draft? This will replace your existing argument in the notebook.")
                        
                        if savedraft == True:
                            $ save_draft(eca)
                        else:
                            pass

                        t "You're doing great! Keep exploring and gathering notes, and your argument will get even stronger."
                        hide tulip
                        with dissolve
                        return
                    "Not right now.":
                        t "Okay! I'm here if you need me."
                        $ renpy.take_screenshot()
                        $ renpy.save("1-1", save_name)
                        hide tulip
                        with dissolve
                        return
            "I need help with something else.":
                $ eca = safe_renpy_input("I love questions! What's your question?", screen="argument_sharing")
                if not isinstance(eca, str) or not eca.strip():
                    t "Okay! I'm here if you need me."
                    hide tulip
                    with dissolve
                    return
                $ eca = eca.strip()

                $ ca_link, ca_json = agent_setup("GameHelp", eca, "tulip", "Tulip")
                $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                $ log("Player input to ECA: " + eca)

                python:
                    try:
                        ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    except Exception as e:
                        log_http(current_user, action="AgentError", view="tulip", payload={"details": str(e)})
                        ecaresponse = "I'm having some trouble right now. Try raising your hand and asking one of the researchers your question!"
                
                $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)
                
                $ start_generated_dialogue("eca", {"character": "Tulip", "context": "GameHelp"})
                if ecasplit == True:
                    $ playAudio(ecaresponse1)
                    t "[ecaresponse1]"
                    $ playAudio(ecaresponse2)
                    t "[ecaresponse2]"

                else:
                    $ playAudio(ecaresponse)
                    t "[ecaresponse]"
                $ finish_generated_dialogue()

                $ stopAudio()
                $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})

                
                t "Any more questions?"
                menu:
                    "I have another question.":
                        $ eca = safe_renpy_input("What's your question?", screen="argument_sharing")
                        if not isinstance(eca, str) or not eca.strip():
                            t "No worries! Buzz me again if something comes up."
                            hide tulip
                            with dissolve
                            return
                        $ eca = eca.strip()

                        $ ca_link, ca_json = agent_setup("GameHelp_Collaboration", eca, "tulip", "Tulip")
                        $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                        $ log("Player input to ECA: " + eca)

                        python:
                            try:
                                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                            except Exception as e:
                                log_http(current_user, action="AgentError", view="tulip", payload={"details": str(e)})
                                ecaresponse = "I'm having some trouble right now. Try raising your hand and asking one of the researchers your question!"
                        
                        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                        $ start_generated_dialogue("eca", {"character": "Tulip", "context": "GameHelp_Collaboration"})
                        if ecasplit == True:

                            $ playAudio(ecaresponse1)
                            t "[ecaresponse1]"
                            $ playAudio(ecaresponse2)
                            t "[ecaresponse2]"

                        else:

                            $ playAudio(ecaresponse)
                            t "[ecaresponse]"
                        $ finish_generated_dialogue()

                        $ stopAudio()
                        
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
                
                #tracking speakers & checking for SOCIAL achievement
                $ update_char_stats("Tulip")
                $ achieve_social()
                
                return
    label begin:
    show screen learningbuttons()
    scene expression "empty lot [startplace]"
    with fade
    $ currentlocation = "emptylot"

    show elliot smile
    with dissolve

    $ renpy.take_screenshot()
    $ renpy.save("1-1", save_name)

    "Friendly Stranger" "Hey what's up - you new to the neighborhood?"

    menu:
        "Yeah, just moved here!":
            "Friendly Stranger" "Welcome to the neighborhood! I live right down the street."
        "Maybe.":
            "Friendly Stranger" "I dunno where you moved from, but we don't do the whole 'mysterious stranger' thing here."
    "Friendly Stranger" "Anyway, I'm glad you're here, new kid." 
    el "I'm Elliot. I'm hoping you'll help me convince Mayor Watson not to sell our lot to those parking guys."

    menu:
        "What parking guys?":
            $ character_approval("Elliot", 0)
            jump parkingguys
    
    label parkingguys:
        el "That guy over there in the suit is from CityPark. They want to turn our empty lot into a big parking [structure] for the neighborhood."
        el "But me and the other Community Gardeners have been trying to convince Mayor Watson to donate the lot to our food justice project instead."
        el "The parking [structure] makes money, but a community garden would be huge for this neighborhood!"

        show tulip at left
        with dissolve

        t "Hey! Sorry to interrupt - but this seems like a good time to show you your notebook!"
        $ notebook_unlocked = True
        t "See the + button to the left? This automatically adds whatever is being said to your notebook!"
        t "If you want to open your notebook and see what notes you've taken, you can click on the Notes button in the top right!"
        t "You can edit notes you've taken, or write your own custom notes! You can also delete notes you don't want."
        t "Hope that helps!"

        hide tulip
        with dissolve

        el "Whoa, a bee just flew past your face! You know, I bet if we built a garden here, the bees would love it."
        el "The garden would be great for people too. The nearest grocery store is miles away, and most folks don't have a car."

        menu:
            "How can I help?":
                $ ask_character_question("Elliot")
                jump explain_problem
            "What's food justice?":
                $ ask_character_question("Elliot")
                $ character_approval("Elliot", 1, "Elliot appreciates your curiosity.")
                jump foodjusticeexplain
            "Sure, I'll help.":
                jump agreement
            "Hmm. I should go.":
                jump talk_later

    label explain_problem:
        el "Our food justice project needs space to build a community garden in our neighborhood, so that folks here can grow fresh food that doesn't cost so much."
        el "Gardens are awesome, obviously, but for some reason the Mayor says he wants to see data about the benefits before making a decision."
        el "I'm trying to gather some evidence to convince him, but I could really use some help."
        menu: 
            "What's food justice?":
                $ ask_character_question("Elliot")
                $ character_approval("Elliot", 1, "Elliot appreciates your curiosity.")
                jump foodjusticeexplain
            "I'll see what I can do.":
                jump talk_later
    
    label agreement:
        el "Awesome! I really appreciate it."
        jump explain_problem

    label foodjusticeexplain:
        el "Food justice is this idea that everybody deserves access to healthy food that they can afford."
        el "Food in our community should also include stuff that makes sense for each person's culture, because not everyone eats the same kinds of foods."
        el "So many people in the U.S. only have access to fast-food restaurants, gas station food, and other places that sell food that is super processed."
        el "There's nothing wrong with eating that food sometimes, but if that's the only kind of food people in your neighborhood can buy that is affordable, then everyone has more trouble eating healthy and feeling good."
        menu:
            "How can I help?":
                $ ask_character_question("Elliot")
                jump explain_problem
            "I'll see what I can do.":
                jump talk_later
    
    label talk_later:
        el "If you're interested, you should go talk with the Community Gardeners. Wes and Nadia, the head gardeners, are over at Westgate Community Garden on the other side of the city."
        el "It would be so great if we could have a garden like that in our neighborhood! They even have beehives!"
        el "You can also check out the science lab, where my friend Riley has been hanging out to learn about food science." 

        #FRIEND achievement unlock
        $ unlock_achievement("FRIEND");

        #checking for SOCIAL achievement; track recent speaker
        $ update_char_stats("Elliot")
        $ achieve_social()

        jump emptylot

    label foodlab:
        scene science lab
        with dissolve
        $ currentlocation = "foodlab"
        $ visited_list.append("Food Lab")
        $ achieve_visit()

        show amara smile at left
        with dissolve

        show riley smile at right
        with dissolve

        $ renpy.take_screenshot()
        $ renpy.save("1-1", save_name)

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

        if get_character_chats("Riley") == 0:
            jump riley_1
        else:
            jump riley_2

    label riley_1:
        r "Hi there! Elliot texted me and said he recruited you to help us gather notes for the Southport garden project."
        jump rileyintro
        
    label rileyintro:
        r "We're so grateful for your help! I'm Riley. I'm a member of the Community Gardeners."
        r "My job is to advocate for the neighborhood and write persuasive proposals to help us get things we need for the community."
        r "Sometimes the city's budget office forgets about the important things, like green spaces where we can breathe fresh air."
        r "What do you think about the empty lot?"

        menu:
            "I think a community garden is a better idea than a parking [structure].":
                jump riley_support
            "I'm not sure, the parking [structure] actually sounds like a good idea.":
                jump riley_against
            "I've already got some ideas to persuade the Mayor!":
                jump riley_plan

    label riley_support:
        r "It really is! I'm glad we're on the same page. Elliot knew you'd be a great addition to our team."
        r "Now we just need to figure out how to make sure the Mayor gets it, too. Do you have any ideas for how to convince him?"

        menu:
            "Wait, but what is your job?":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley explains patiently.")
                jump long_intro
            "I have a few ideas.":
                jump riley_plan
            "Not yet, but I will.":
                jump bye_riley2
    
    label long_intro:
        r "I'm the director of a nonprofit organization called CareWorks. We advocate for the needs of our neighborhood by setting up programs that help the people here." 
        r "We help run things like community food pantries and after-school activities for kids. My work with the Community Gardeners is part of that!"
        r "We do research to help present proposals to the City, so that we can convince them to use money and resources in ways that will help our community grow."
        r "I'd love your help gathering notes to improve our persuasive writing about why community gardens matter! We're going to share it with the Mayor when we're ready."
        r "There are several other community gardens in the city, but they're all pretty far from this neighborhood, and folks here could really use a reliable source of fresh food."

        menu:
            "I have a few ideas to help with that.":
                jump riley_plan
            "I'm going to find some ideas to help!":
                jump bye_riley2
            "Hmm.":
                jump not_convinced
    
    label riley_against:
        r "Oh really? I'm curious why you think that."
        $ progarage = argument_sharing("Why do you support the parking [structure]?")
        if not isinstance(progarage, str) or not progarage.strip():
            r "Alright, maybe you'll think of a reason later."
            jump riley_plan
        $ progarage = progarage.strip()
        $ log("Player argument for garage: " + progarage)
        r "Hmm. That's fair. I still think the garden has more benefits for the people and the environment, but that's worth considering."
        r "The government often relies on data and algorithms. But some things, like the value of a community garden, can't be measured in money alone. It's measured in how it helps empower the people who live here."
        
        menu:
            "Wait, but what is your job?":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley explains patiently.")
                jump long_intro
            "I have a few ideas about the garden's benefits, too.":
                jump riley_plan
            "I should go.":
                jump bye_riley2

    label riley_plan:
        r "I bet if we work together we can make a presentation so persuasive that it blows the socks off the Mayor and runs CityPark right out of town."
        r "I'd love to hear your ideas!"

        menu:
            "Sure, I'll share my ideas.":
                r "Sweet. What do you think we should say to convince the Mayor that a community garden is good for the neighborhood?"
                jump ca_eval_riley
            "I should gather more notes first.":
                jump bye_riley2
            "Wait, but what is your job?":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley explains patiently.")
                jump long_intro

    label ca_eval_riley:
        $ eca = safe_renpy_input("My persuasive ideas for the Mayor:", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            r "No worries. We can brainstorm when you're ready."
            jump riley_plan
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Riley")
        $ log_http(current_user, action="PlayerInputToECA", view="riley", payload=ca_json)
        $ log("Player input to ECA: " + eca)
        $ argument_attempts = argument_attempts + 1
        $ achieve_argument()

        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="riley", payload={"details": str(e)})
                ecaresponse = "I'm a little overwhelmed right now. You can ask one of the researchers to read your argument, or you can try again in a little while."
                                     
        $ log_http(current_user, action="PlayerECAResponse", view="riley", payload={"eca_response": ecaresponse})

        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        $ start_generated_dialogue("eca", {"character": "Riley", "context": "FoodJustice_RileyEvaluation"})
        if ecasplit == True:

            $ playAudio(ecaresponse1)
            r "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            r "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            r "[ecaresponse]"
        $ finish_generated_dialogue()
            
        $ stopAudio()
        $ achieve_feedback()

        $ savedraft = renpy.confirm("Do you want to save this argument as your new draft? This will replace your existing argument in the notebook.")

        if savedraft == True:
            $ save_draft(eca)
        else:
            pass

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


    label bye_riley2:
        r "Awesome! If you want to run any ideas by me before you talk to the Mayor, I'd be happy to help you workshop your argument. See ya!"

        #checking for SOCIAL achievement; track recent speaker
        $ update_char_stats("Riley")
        $ achieve_social()
        jump foodlab
    
    label riley_2:
        r "Back again! I'm glad. What's up?"
        
        menu:
            "What do you know about food justice?":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley appreciates your interest.")
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
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley seems encouraged by your support.")
                $ eca = "Why is access to healthy food important?"

                $ ca_link, ca_json = agent_setup("Knowledge_FoodJustice", eca, "riley", "Riley")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="riley", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                python:
                    try:
                        ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    except Exception as e:
                        log_http(current_user, action="AgentError", view="riley", payload={"details": str(e)})
                        ecaresponse = "Access to healthy food is important because it helps us grow, stay healthy, and have the energy we need to do the things we love. Healthy food can also prevent diseases like obesity, heart disease, and diabetes."
                  
                $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                $ start_generated_dialogue("eca", {"character": "Riley", "context": "Knowledge_FoodJustice"})
                if ecasplit == True:

                    $ playAudio(ecaresponse1)
                    r "[ecaresponse1]"
                    
                    $ playAudio(ecaresponse2)
                    r "[ecaresponse2]"

                else:
                    $ playAudio(ecaresponse)
                    r "[ecaresponse]"
                $ finish_generated_dialogue()
                $ stopAudio()

                jump foodknowledge_loop
            "How can we help everyone have access to healthy food?":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley seems encouraged by your support.")
                $ eca = "How can we help everyone have access to healthy food?"

                $ ca_link, ca_json = agent_setup("Knowledge_FoodJustice", eca, "riley", "Riley")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="riley", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                python:
                    try:
                        ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    except Exception as e:
                        log_http(current_user, action="AgentError", view="riley", payload={"details": str(e)})
                        ecaresponse = "One way to help everyone get access to affordable and healthy food options is by supporting local farmers markets and community gardens. It's also important to advocate for policies that promote healthy food options."

                $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                if ecasplit == True:
                    $ playAudio(ecaresponse1)
                    r "[ecaresponse1]"
                    $ playAudio(ecaresponse2)
                    r "[ecaresponse2]"

                else:
                    $ playAudio(ecaresponse)
                    r "[ecaresponse]"
                
                $ stopAudio()

                jump foodknowledge_loop
            "I have another question.":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley is glad you want to learn more.")
                jump foodknowledge
            "Nevermind.":
                jump byeriley
        
    label foodknowledge_loop:
        r "Anything else you'd like to know?"

        menu:
            "I have another question.":
                $ ask_character_question("Riley")
                $ character_approval("Riley", 1, "Riley is glad you want to learn more.")
                jump foodknowledge
            "I have some ideas for our pitch to the Mayor.":
                r "Amazing! What ideas have you found about how we should use the empty lot?"
                jump ca_eval_riley
            "Nah I'm okay.":
                jump byeriley

    label foodknowledge:
        $ eca = safe_renpy_input("I'm wondering...", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            r "No worries. Ask me again anytime."
            jump foodknowledge_loop
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("Knowledge_FoodJustice", eca, "riley", "Riley")
        $ log_http(current_user, action="PlayerInputToECA", view="riley", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="riley", payload={"details": str(e)})
                ecaresponse = "I'm struggling a bit right now. Maybe you can chat with Amara about her food science work, and you and I can chat more later?"

        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        if ecasplit == True:

            $ playAudio(ecaresponse1)
            r "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            r "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            r "[ecaresponse]"

        $ stopAudio()

        jump foodknowledge_loop
    
    label byeriley:
        r "Keep doing great things! I'll be here if you need me."
        $ update_char_stats("Riley")
        jump foodlab

    label amara_chatting:
        scene science lab
        with dissolve
        
        show amara smile
        with dissolve

        if get_character_chats("Amara") == 0:
            jump amara_1
        else:
            jump amara_2

    label amara_1:

        a "Hi! I'm Amara - I'm the lead scientist here at the food lab. Great to meet you."
        jump intro_amara_questions

    label intro_amara_questions:
        $ amara_menu = set()
        menu:
            set amara_menu
            "What's a food scientist?":
                $ ask_character_question("Amara")
                $ character_approval("Amara", 1, "Amara smiles, pleased you asked.")
                jump foodscientist
            "Do you know anything about the garden project?":
                $ ask_character_question("Amara")
                $ character_approval("Amara", 1, "Amara seems glad you asked.")
                jump garden_info
            "What kind of stuff do you do here?":
                $ ask_character_question("Amara")
                jump lab_stuff
            "Nice to meet you! Gotta go.":
                jump bye_amara

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
                $ ask_character_question("Amara")
                $ character_approval("Amara", 1, "Amara seems glad you're listening.")
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

    label bye_amara:
        a "Oh okay! Well you're welcome to hang out, let me know if you get curious about anything!"
      
        #checking for SOCIAL achievement; track recent speaker
        $ update_char_stats("Amara")
        $ achieve_social()
        
        jump foodlab

    label amara_2:
        a "Hey there! What are you up to?"
        jump amara_revisit

    label amara_revisit:
        menu:
            "I'm trying to gather evidence about gardens.":
                a "Oh, I'm full of facts. Maybe I can help!"
                jump sciencequestions
            "I'm trying to gather evidence about parking [structure]s.":
                $ ask_character_question("Amara")
                $ character_approval("Amara", 1, "Amara nods thoughtfully.")
                jump parkingquestions
            "Actually, we should talk later.":
                jump byeamara
    
    label sciencequestions:
        a "What are you curious about?"

        menu: 
            "Why does genetic diversity in plants matter?":
                $ ask_character_question("Amara")
                $ character_approval("Amara", 1, "Amara smiles, happy to explain.")
                jump genetics
            "What do you know about soil quality?":
                $ ask_character_question("Amara")
                jump soil
            "What do gardens do for the environment?":
                $ ask_character_question("Amara")
                jump environment
            "See you later.":
                jump foodlab

        label genetics:
            a "Oh, plant genetics are so interesting. Like people, plants have DNA that carries information about the different kinds of traits they have."
            a "And just like with people, diversity makes plants stronger. Genetic diversity means that plants have lots of unique traits, so that a pest or weather change that harms one plant might not bother another."
            a "When our local ecosystem has a large variety of plants with diverse genetics, the overall ecosystem is healthier and more resilient."
            
        menu:
            "Tell me more!":
                $ ask_character_question("Amara")
                jump genetics2
            "I have a different question.":
                jump sciencequestions

        label genetics2:
            a "Okay! So the thing with big farms and genetic diversity is that many of them like to pick the strongest and best-producing plants to grow over and over."
            a "For example, if all the big farms choose to grow the same type of strawberry plant because it grows big berries, then we start to lose some of the interesting local varieties that might be smaller, but have unique flavors or taste extra sweet."
            a "Someday the big strawberry plant might not be able to grow very well as our environment changes, so we need to protect genetic diversity to protect our future food system!"
            jump sciencequestions

        label soil:
            a "Soil is super important for the health of plants. Dirt just looks like dirt at first glance, but there are actually 14 different nutrients in the soil that can change how plants grow."
            a "Different plants need different amounts of nutrients, but they all need the same ones - the big ones are nitrogen, phosphorus, and potassium. But calcium, magnesium, and sulfur are important too."
            a "It's very important to keep track of the nutrients in the soil, because healthier soil can grow stronger plants, more food, and in some cases even healthier food."
            
        menu:
            "Tell me more!":
                $ ask_character_question("Amara")
                jump soil2
            "I have a different question.":
                jump sciencequestions

        label soil2:
            a "Some people like to grow their own food, because then they can be in control of the soil quality and the kinds of pesticides that are used on the food they eat."
            a "Learning to grow your own food can also help to teach people useful skills and knowledge about food science, health, and farming pratices!"
            jump sciencequestions
        
        label environment:
            a "For the ecosystem, gardens give insects and animals a home. They provide food for pollinators and can be especially helpful if they're full of native plants."
            a "For our air, gardens help to filter pollution, especially if you have large plants like trees that can filter out lots of pollutants. Plants also produce oxygen for us to breathe."
            a "Local gardens also let us grow food that doesn't need to be driven a long way in order to get to us - so they help to make our food system more sustainable."
            
        menu:
            "Tell me more!":
                $ ask_character_question("Amara")
                jump environment2
            "I have a different question.":
                jump sciencequestions

        label environment2:
            a "Food systems are so big and complex, and there isn't just one right answer for how to get healthy food to people and how to do it well. But I love complicated problems! That's why I'm a scientist."
            a "And every family is different - sometimes our family recipes need ingredients that aren't easy to find in the grocery store."
            a "So we should ask ourselves: how do we make sure everyone can find the foods they need and want, so that everyone has a voice in how they grow and buy their food?"
            jump sciencequestions

    label parkingquestions:
        a "Ah, so you're curious about how the parking [structure] will impact the neighborhood?"
        a "I mostly study food, so I don't know a ton about the economic impact of parking [structure]s or how cars change the environment."
        a "Wes might know more - he did a lot of that research when he was building the Westgate community garden!"
        jump amara_revisit

    label byeamara:

        a "Have a great day! Let me know if I can help with your research."
        jump foodlab

    label garden:
        scene garden
        with dissolve
        $ currentlocation = "garden"
        $ visited_list.append("Garden")
        $ achieve_visit()

        show victor smile at left
        with dissolve

        show wes smile
        with dissolve

        show beehives travel at right
        with dissolve

        $ renpy.take_screenshot()
        $ renpy.save("1-1", save_name)

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

    label victormenu:
        menu:
            "Do you live nearby?":
                $ ask_character_question("Victor")
                $ character_approval("Victor", 1, "Victor nods politely.")
                jump gardenfar
            "Do you know a lot about growing things?":
                $ ask_character_question("Victor")
                $ character_approval("Victor", 1, "Victor seems pleased by your question.")
                jump gardenknowledge
            "So you like the garden idea?":
                $ ask_character_question("Victor")
                $ character_approval("Victor", 1, "Victor smiles approvingly.")
                jump victoropinion
            "I'll talk to you later.":
                v "Okay! See you later."
                
                #checking for SOCIAL achievement; track recent speaker
                $ update_char_stats("Victor")
                $ achieve_social()

                jump garden

    label victoropinion:
        v "Yeah! I think a garden would be a great use of land for the neighborhood. It will let us grow heirloom produce that we can't find in stores."
        v "A neighborhood garden would also give everybody access to fresh food, even if they don't have a lot of money to spend on groceries."
        v "Since some neighborhoods don't have supermarkets, a garden would give more people healthy food options. And it can be fun to grow things yourself!"

    label heirloommenu:
        menu:
            "What's heirloom produce?":
                $ ask_character_question("Victor")
                $ character_approval("Victor", 1, "Victor enjoys explaining.")
                jump heirloom
            "Why do you want to grow heirloom produce?":
                $ ask_character_question("Victor")
                $ character_approval("Victor", 1, "Victor lights up as he explains.")
                jump whyheirloom
            "I have a different question":
                jump victormenu
            "I'll talk to you later.":
                v "Okay! See you later."

                #checking for SOCIAL achievement; track recent speaker
                $ update_char_stats("Victor")
                $ achieve_social()

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

        if get_character_chats("Wes") == 0:
            jump wes_1
        else:
            jump wes_2

    label wes_1:
        w "Hey there! Welcome to the Westport Community Garden. Elliot called and said you might come by."
        w "Feel free to explore the garden, and let me know if you are curious about anything."
        jump wes_choices

    label wes_choices:
        default wes_menu = set()
        menu:
            set wes_menu
            "Tell me about the food you're growing.":
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes grins and starts explaining.")
                jump growing_food
            "Is the garden good for the neighborhood?":
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes brightens at your question.")
                jump garden_benefits
            "How can we pollinate plants in the garden?":
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes seems excited by your enthusiasm.")
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
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes nods and begins to teach.")
                jump wes_pollen
            "What types of pollinators exist?":
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes nods and begins to teach.")
                jump types_pollinators
            "How do plants help pollinators?":
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes nods and begins to teach.")
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
        $ eca = safe_renpy_input("I'm wondering...", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            w "Alright, just flag me down if you think of something."
            jump wes_choices
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Wes")
        $ log_http(current_user, action="PlayerInputToECA", view="wes", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="wes", payload={"details": str(e)})
                ecaresponse = "Sorry kid, I'm having a bit of trouble, actually. Why don't you go check out the beehives, and you and I can catch up more later."

        $ log_http(current_user, action="PlayerECAResponse", view="wes", payload={"eca_response": ecaresponse})

        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        $ start_generated_dialogue("eca", {"character": "Wes", "context": "Knowledge_Pollination"})
        if ecasplit == True:
            $ playAudio(ecaresponse1)
            w "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            w "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            w "[ecaresponse]"
        $ finish_generated_dialogue()
        $ finish_generated_dialogue()

        $ stopAudio()

        jump wes_choices

    label bye_wes:
        w "It was great talking with you. Come by anytime, kid."

        #checking for SOCIAL achievement; track recent speaker
        $ update_char_stats("Wes")
        $ achieve_social()

        jump garden

    label wes_2:
        w "Hope you're enjoying the garden, friend. Can I help with anything?"
        jump wes_questions

    label wes_questions:
        menu:
            "I have a question about the garden":
                $ ask_character_question("Wes")
                $ character_approval("Wes", 1, "Wes listens closely.")
                jump wes_ca
            "I should go.":
                jump bye_wes2

    label bye_wes2:
        w "No problem. Enjoy the garden!"
        $ update_char_stats("Wes")
        jump garden

    label wes_ca:
        w "What would you like to know?"
        $ eca = safe_renpy_input("I'm wondering...", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            w "All good. Come find me if you have another question."
            jump wes_questions
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Wes")
        $ log_http(current_user, action="PlayerInputToECA", view="wes", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="wes", payload={"details": str(e)})
                ecaresponse = "Sorry kid, I'm having a bit of trouble, actually. Why don't you go check out the beehives, and you and I can catch up more later."

        $ log_http(current_user, action="PlayerECAResponse", view="wes", payload={"eca_response": ecaresponse})

        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        if ecasplit == True:
            $ playAudio(ecaresponse1)
            w "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            w "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            w "[ecaresponse]"

        $ stopAudio()
        
        w "Would you like to know anything else?"

        jump wes_questions

    label bees_chatting:
        scene beehives
        with dissolve
        $ currentlocation = "beehives"
        $ visited_list.append("Beehives")
        $ achieve_visit()

        show nadia smile at left
        with dissolve

        show alex smile at right
        with dissolve

        show cora concern at right
        with dissolve

        $ renpy.take_screenshot()
        $ renpy.save("1-1", save_name)

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

        if get_character_chats("Nadia") == 0:            
            jump nadia_1
        else:
            jump nadia_2

    label nadia_1:
        n "Hi, I'm Nadia. I'm a beekeeper, though you can probably tell that from the outfit. I take care of the beehives in several community gardens around town." 
        n "If you have any questions about bees, plants, and pollination, I'd be happy to tell you what I know."
        default nadia_menu = set()
        jump nadia_questions
      
    label nadia_questions:
        menu:
            set nadia_menu
            "Why did you become a beekeeper?":
                $ ask_character_question("Nadia")
                $ character_approval("Nadia", 1, "Nadia smiles warmly.")
                jump beekeeper
            "How do bees help with pollination?":
                $ ask_character_question("Nadia")
                $ character_approval("Nadia", 1, "Nadia nods and explains.")
                $ eca = "How do bees help with pollination?"

                $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="nadia", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                python:
                    try:
                        ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    except Exception as e:
                        log_http(current_user, action="AgentError", view="nadia", payload={"details": str(e)})
                        ecaresponse = "Bees help with pollination by transferring pollen from one flower to another while collecting nectar. This helps the plant grow healthy fruits."

                $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                $ start_generated_dialogue("eca", {"character": "Nadia", "context": "Knowledge_Pollination"})
                if ecasplit == True:
                    $ playAudio(ecaresponse1)
                    n "[ecaresponse1]"
                    $ playAudio(ecaresponse2)
                    n "[ecaresponse2]"

                else:
                    $ playAudio(ecaresponse)
                    n "[ecaresponse]"
                $ finish_generated_dialogue()
                $ finish_generated_dialogue()

                $ stopAudio()

                $ AddToSet(nadia_menu, "How do bees help with pollination?")
                jump nadia_questions
            "How do plants get pollinated?":
                $ ask_character_question("Nadia")
                $ character_approval("Nadia", 1, "Nadia enjoys sharing her knowledge.")
                $ eca = "How do plants get pollinated?"

                $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
                $ log_http(current_user, action="PlayerInputToECA_fromtemplate", view="nadia", payload=ca_json)
                $ log("Player input to ECA (from template): " + eca)

                python:
                    try:
                        ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    except Exception as e:
                        log_http(current_user, action="AgentError", view="nadia", payload={"details": str(e)})
                        ecaresponse = "The flowers on plants can be pollinated by wind, by animals and insects, and by people. A flower is pollinated when pollen is moved from the male part of the flower to the female part of the flower."

                $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

                if ecasplit == True:
                    $ playAudio(ecaresponse1)
                    n "[ecaresponse1]"
                    $ playAudio(ecaresponse2)
                    n "[ecaresponse2]"

                else:
                    $ playAudio(ecaresponse)
                    n "[ecaresponse]"

                $ stopAudio()

                $ AddToSet(nadia_menu, "How do plants get pollinated?")
                jump nadia_questions
            "I have a different question.":
                $ ask_character_question("Nadia")
                jump nadia_ca
            "See you later.":
                jump bye_nadia
    
    label beekeeper:
        n "I grew up on a farm, and I always thought bees were amazing. They're so small, but also so coordinated and intelligent!"
        n "Did you know that bees communicate the locations of flowers to each other by dancing? How cool is that?"
        n "Anyway, bees are just such an important part of our ecosystem that I wanted to do something to help take care of them."
        n "Bees are important for pollinating lots of crops, such as almonds, apples, and blueberries. Without bees, many crops would have to be pollinated by hand, which would take a ton of time and money."
        $ AddToSet(nadia_menu, "Why did you become a beekeeper?")
        jump nadia_questions

    label nadia_ca:
        $ eca = safe_renpy_input("I'm wondering...", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            n "Alright! Come back if you want to talk more about bees."
            jump nadia_questions
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
        $ log_http(current_user, action="PlayerInputToECA", view="nadia", payload=ca_json)
        $ log("Player input to ECA: " + eca)

        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="nadia", payload={"details": str(e)})
                ecaresponse = "Oh, I'm having a bit of trouble. Can you chat with others in the garden and come back later? Sorry about that!"

        $ log_http(current_user, action="PlayerECAResponse", view="nadia", payload={"eca_response": ecaresponse})

        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        $ start_generated_dialogue("eca", {"character": "Nadia", "context": "Knowledge_Pollination"})
        if ecasplit == True:
            $ playAudio(ecaresponse1)
            n "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            n "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            n "[ecaresponse]"
        $ finish_generated_dialogue()

        $ stopAudio()

        n "Do you have any other questions?"
        menu:
            "I have more questions.":
                jump nadia_ca
            "No, I should go.":
                if get_character_chats("Nadia") == 0:                    
                    jump bye_nadia
                else:
                    jump bye_nadia2
    
    label bye_nadia:
        n "It was nice to meet you. Let me know if you have any more questions as you explore the garden!"
        $ update_char_stats("Nadia")
        $ achieve_social()

        jump bees_chatting

    label nadia_2:
        n "Hello dear! Can I help you with anything?"

        menu:
            "I have a question for you.":
                $ ask_character_question("Nadia")
                jump nadia_ca
            "Actually, I'll talk to you later":
                jump bye_nadia2

    label bye_nadia2:
        n "No problem at all. Enjoy your visit!"
        $ update_char_stats("Nadia")
        jump bees_chatting

    label alex_chatting:
        scene beehives
        with dissolve

        show alex smile
        with dissolve 

        if get_character_chats("Alex") == 0:
            jump x_1
        else:
            jump x_2

    label x_1:
        x "Hi! Are you a gardener?"     
    
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
                $ ask_character_question("Alex")
                $ character_approval("Alex", 1, "Alex smiles shyly.")
                jump gardenthink
            "Do you live near the empty lot?":
                $ ask_character_question("Alex")
                $ character_approval("Alex", 1, "Alex nods and tells you more.")
                jump alex_lot
            "What kind of food do you wanna grow?":
                $ ask_character_question("Alex")
                $ character_approval("Alex", 1, "Alex looks excited to share.")
                jump alex_growfood
            "Buzz ya later!":
                jump bye_alex

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

    label bye_alex:
        x "Hahaha! Buzz you later!"

        #checking for SOCIAL achievement; track recent speaker
        $ update_char_stats("Alex")
        $ achieve_social()

        jump bees_chatting

    label sadkid:
        x "Ohh..."
        jump bees_chatting

    label x_2:
        x "Buzzzz... buzz buzz buzz!"
        menu:
            "I have a question for you.":
                jump questions_alex
            "Nevermind, have fun!":
                jump alex_buzz
    
    label alex_buzz:
        x "There's a bee by your head. I think it likes you!"

        show tulip at left
        with dissolve

        t "Oh I love that kid. By the way, do you need any help? You can always click my button to say hi if you get bored!"

        $ call("tulip_help_menu")

        jump bees_chatting

    label cora_chatting:
        scene beehives
        with dissolve

        show cora concern
        with dissolve 

        if get_character_chats("Cora") == 0:
            jump cora_1
        else:
            jump cora_2

    label cora_1:
        c "Oh Alex, be careful! Don't get too close to the hives! There's so many of them..."
        $ update_char_stats("Cora")
        $ achieve_social()

        menu:
            "Not a fan of bees?":
                jump coranext

    label coranext:
        c "Goodness, no. I know they're good for the environment and all but...ugh. Bugs are too creepy and crawly. Alex loves them, though."    

        menu:
            "They're pretty gentle, actually.":
                $ ask_character_question("Cora")
                $ character_approval("Cora", 1, "Cora relaxes a little.")
                jump gentlebees
            "What do you think of the garden?":
                $ ask_character_question("Cora")
                $ character_approval("Cora", 1, "Cora appreciates being asked.")
                jump corathoughts
            "Enjoy the garden.":
                jump bye_cora

    label gentlebees:
        c "Hm, well I'll have to take your word for it. I'm not becoming a beekeeper anytime soon."
        c "I am curious about the garden though. They put up flyers all over our neighborhood about wanting to build another garden down the street from our apartment."

       

        menu:
            "What do you think of the garden?":
                $ ask_character_question("Cora")
                $ character_approval("Cora", 1, "Cora appreciates being asked.")
                jump corathoughts
            "Enjoy the garden.":
                jump bye_cora

    label corathoughts:
        c "Other than the bees flying everywhere, it seems like a good place for the neighborhood."
        c "It's been really hard lately to get across town to get fresh fruits and vegetables from the store, since we don't have a car."
        c "And the stores just keep getting more expensive! My paycheck only goes so far. If we had a garden like this in our neighborhood, maybe I could grow some fresh food for the kids, y'know?"
        c "I try my best to give them healthy things to eat, but on nights when I work late, I don't have time for much more than throwing a frozen meal in the microwave."
        c "I don't know, maybe the garden would be just as tiring. But at least I would have food in my own backyard! That's more than we've got right now."

        menu:
            "I'm working to convince the Mayor to build a garden in your neighborhood.":
                $ ask_character_question("Cora")
                $ character_approval("Cora", 2, "Cora smiles warmly at your support.")
                jump coragarden
            "I'm trying to convince the Mayor to build a parking [structure] instead.":
                jump coraparking
            "Enjoy the garden.":
                jump bye_cora

    label coragarden:
        c "Oh! That's great. Will you tell the Mayor the families in the neighborhood want a garden too?"
        c "Maybe we will get to grow our own food after all. Alex will be so excited! We can learn about growing fresh fruits and vegetables together."
        jump bees_chatting

    label coraparking:
        c "Oh. That won't really do anything for my family...we don't have a car anyway. I'd rather build something we can all use."
        jump bees_chatting

    label bye_cora:
        c "Thank you, dear. You too."
        $ update_char_stats("Cora")
        jump bees_chatting

    label cora_2:
        menu:
            "How's it going?":
                $ ask_character_question("Cora")
                jump corastress
            "What do you think of the garden?":
                $ ask_character_question("Cora")
                $ character_approval("Cora", 1, "Cora appreciates being asked.")
                jump corathoughts
            "Enjoy the garden.":
                jump bye_cora

    label corastress:
        c "Oh it's alright, Alex is just - ALEX! Do not touch the bee!!"
        jump cora_2

    label emptylot:
        scene expression "empty lot [startplace]"
        with dissolve
        $ currentlocation = "emptylot"
        $ visited_list.append("Empty Lot")
        $ achieve_visit()

        show elliot smile at left
        with dissolve

        show cyrus smile at right
        with dissolve
        
        show watson smile
        with dissolve

        $ renpy.take_screenshot()
        $ renpy.save("1-1", save_name)

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
        scene expression "empty lot [startplace]"
        with dissolve

        show cyrus smile
        with dissolve

        if get_character_chats("Cyrus") == 0:
            jump cy_1
        else:
            jump cy_2

    label cy_1:
        cy "Hey there, kiddo. Cyrus Murphy, Marketing Executive for CityPark."
        cy "Nice to meet ya."

    menu:
        "Great to meet you!":
            $ character_approval("Cyrus", 2, "Cyrus appreciates your enthusiasm.")
            jump excited_cy
        "Hey.":
            $ character_approval("Cyrus", 0)
            jump normal_cy
        "Don't respond.":
            $ character_disapproval("Cyrus", 2, "Cyrus looks put off by your silence.")
            jump dislike_cy

    label excited_cy:
        cy "It's great to see young people in this neighborhood so passionate about growth in their community!"
        cy "Our team at CityPark is looking forward to meeting more people like you while we get ready to build our new parking [structure]."
        jump cy_menu

    label normal_cy:
        cy "I'm glad so many folks have come by to say hello - our team at CityPark is all about working with the community."
        cy "Are you excited about the new parking [structure]?"
        jump cy_menu

    label dislike_cy:
        cy "Hey, I get it, you've got better things to do than talk with some stranger in a suit. But I look forward to getting to know you and your neighbors better as we begin construction!"
        jump cy_menu
    
    label cy_menu:
        menu:
            "New [structure]?":
                $ ask_character_question("Cyrus")
                $ character_approval("Cyrus", 1, "Cyrus is pleased you're curious.")
                jump cy_pitch
            "Can't wait!":
                $ character_approval("Cyrus", 2, "Cyrus grins at your support.")
                jump agree_garage
            "We don't want a parking [structure].":
                $ character_disapproval("Cyrus", 2, "Cyrus stiffens at your pushback.")
                jump dislike_garage
            "I gotta go.":
                $ character_approval("Cyrus", 0)
                jump bye_cyrus

    label cy_pitch:
        cy "This empty lot here is the future site of a CityPark Park Express [structure]! It will be a prime location to encourage new businesses to move in on this street."
        cy "As soon as we get the sign-off from Mayor Watson, we're going to begin construction."

        menu:
            "Can't wait!":
                $ character_approval("Cyrus", 2, "Cyrus grins at your support.")
                jump agree_garage
            "We don't want a new parking [structure].":
                $ character_disapproval("Cyrus", 2, "Cyrus stiffens at your pushback.")
                jump dislike_garage
            "I gotta go.":
                $ character_approval("Cyrus", 0)
                jump bye_cyrus
    
    label agree_garage:
        cy "That's what I'm talking about - you're a bright kid. Make sure to tell your friends all about CityPark and what a great choice we are for your neighborhood!"
        jump bye_cyrus
    
    label dislike_garage:
        cy "Hey now, I know change can be scary, but just think about how much money the parking [structure] could make for the city!"
        cy "And that money can help fix roads, fund schools, and support the community. More parking means more businesses, more neighborhood growth - you're gonna love it, I swear."
        
        show elliot smile at left
        with dissolve

        hide cyrus smile

        show cyrus smile at right
        with dissolve

        el "We're NOT going to love it, Mr. Murphy. The [structure] might make money for you and your company, but the people here need food, not a place to park cars."

        cy "Now Elliot, we've been over this! When we get this [structure] built, I'm sure a big grocery store will move right into town, and wouldn't you rather just go buy your food rather than having to spend all that time growing it?"

        menu:
            "Actually, a grocery store sounds nice.":
                $ ask_character_question("Cyrus")
                $ character_approval("Cyrus", 2, "Cyrus nods in agreement.")
                jump grocery
            "A garden is better for the neighborhood, and I'm gonna prove it.":
                $ character_disapproval("Cyrus", 3, "Cyrus bristles at the challenge.")
                jump cy_challenge
            "I'm not sure.":
                $ character_approval("Cyrus", 0)
                jump unsure
    
    label unsure:
        cy "It's a complex problem, kid. Perhaps you should learn more about it before you fall in with these gardeners."

        el "Ugh, ignore him. But it is a good idea to talk to the others in the neighborhood. We'll need their support to convince the Mayor!"
        $ update_char_stats("Cyrus")
        $ achieve_social()

        jump emptylot

    label grocery:

        el "I know, it would be great if a grocery store moved in. But big chain stores don't usually move into low-income neighborhoods like this one because they don't think they'll make enough money."
        el "I'm not convinced a parking [structure] will change that."

        cy "You never know until you try! We've been gathering economic data on how parking [structure]s impact neighborhood growth. You'll need a lot of evidence to beat our pitch to the Mayor, kid."

        menu:
            "We'll find the evidence.":
                $ character_disapproval("Cyrus", 1, "Cyrus smirks, unconvinced.")
                jump cy_challenge
            "I need to go.":
                $ character_approval("Cyrus", 0)
                jump bye_cyrus

    label cy_challenge:
        el "That's right! We're working hard to build a persuasive argument for the Mayor to support the community garden project."

        cy "Alright kiddo, whatever you say. Best of luck, and may the best argument win."
        $ update_char_stats("Cyrus")
        $ achieve_social()

        jump emptylot

    label bye_cyrus:
        cy "Great talking with you, kiddo! Take it easy."
        $ update_char_stats("Cyrus")
        $ achieve_social()

        jump emptylot

    label cy_2:
        cy "Ah, our resident investigator, back again. What can I do for you?"
        jump cy_questions

    label cy_questions:
        menu:
            "What evidence do you have about the benefits of the parking [structure]?":
                $ ask_character_question("Cyrus")
                $ character_approval("Cyrus", 1, "Cyrus seems pleased by your professionalism.")
                jump garage_benefits
            "Have you considered how car pollution might impact the neighborhood?":
                $ ask_character_question("Cyrus")
                $ character_approval("Cyrus", 1, "Cyrus seems thoughtful.")
                jump cy_pollution
            "Nevermind, I should go.":
                jump bye_cyrus2

    label garage_benefits:
        cy "Ah, so you're coming around to our plan? Wonderful!"
        cy "Parking [structure]s can be great for local businesses. If people from out of town can easily park in the neighborhood, then more people will stop here and spend money on shopping trips."
        cy "More parking means more businesses can move in, which makes the economy of the neighborhood stronger! It might even bring new jobs to the area."
        jump cy_questions

    label cy_pollution:
        cy "Oh, cars are everywhere. One more [structure] won't change anything. The pollution isn't as important as the money the [structure] will make for the city."
        
        menu:
            "What about the pollinators?":
                $ ask_character_question("Cyrus")
                jump cy_bees
            "I guess you're right.":
                cy "That's the spirit. CityPark will make this neighborhood a shopping hotspot for the city!"
                jump cy_questions
    
    label cy_bees:
        cy "What about them? The bees can just go somewhere else to find flowers. We should care more about the people here, and making the local economy stronger."
        jump cy_questions

    label bye_cyrus2:
        $ update_char_stats("Cyrus")
        cy "Alright then. Tell your friends to sign up for our CityPark newsletter!"
        jump emptylot
    
    label watson_chatting:
        scene expression "empty lot [startplace]"
        with dissolve

        show watson smile
        with dissolve

        if get_character_chats("Mayor") < 1:
            jump mayor_1
        else:
            jump mayor_2

    label mayor_1:
        m "Hello there! I'm Mayor Watson. I'm out here today gathering community opinions on the empty lot."
        m "Do you have any thoughts about it?"

        menu:
            "I think you should let the Community Gardeners use the lot for growing food.":
                jump garden_m
            "I think you should let CityPark build a parking [structure] for the neighborhood.":
                jump parking_m
            "I'm not sure.":
                jump uncertain_m

    label garden_m:
        m "Ah, interesting. The garden would provide some food for the neighborhood, though the parking [structure] might be more financially useful for the city."
        m "I need to consider the research and figure out what is best for our community."
        jump mayor_request

    label parking_m:
        m "Oh really? I do think the parking [structure] would give the city some useful income that we could use to improve our schools."
        m "But the Community Gardeners feel strongly that a garden would be more beneficial to the neighborhood."
        m "I need to consider the research and figure out what is best for our community."
        jump mayor_request

    label uncertain_m:
        m "That's okay, I'm not sure either! I'm going to talk with the Community Gardeners and the CityPark representative to see what kind of data they have for their proposals."
        jump mayor_request

    label mayor_request:
        m "If you gather any information you think I'd find interesting, feel free to come back and let me know!"
        $ update_char_stats("Mayor")
        $ achieve_social()

        jump emptylot

    label mayor_2:
        m "Hello there! What can I do for you?"

        menu:
            "What kind of information are you looking for?":
                jump what_evidence
            "How can we convince you to support the Community Garden?":
                jump good_argument
            "I have a persuasive argument to share about the empty lot.":
                jump mayor_eval

    label what_evidence:
        m "I want to gather many different kinds of evidence. Opinions of the community members, but also concrete information about how the garden and the parking [structure] will impact the community."
        m "Scientific evidence about how the garden would impact the environment would be convincing. It would also be helpful to gather data about economic and health impacts on the community."
        m "Gathering information from different sources will make for a more convincing argument. I know CityPark has been gathering lots of data to persuade me to support their plan."

        menu:
            "I'll look for some evidence.":
                jump continue_search
            "I have an argument to share about the empty lot.":
                jump mayor_eval

    label good_argument:
        m "A persuasive argument brings together many different types of evidence and tells a good story about why someone should agree with your point of view."
        m "If I am going to support the Community Garden project, I need to know how the garden will benefit the people in the community."
        m "I also need to be convinced that the benefits of the garden are more important than the money and business that the parking [structure] will bring."

        menu:
            "I'll look for some evidence.":
                jump continue_search
            "I have an argument to share about the empty lot.":
                jump mayor_eval

    label mayor_eval:
        m "I'd love to hear it. What have you found?"

        $ eca = safe_renpy_input("My persuasive argument for what the Mayor should do with the empty lot:", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            m "That's alright. Come back when you're ready to share your ideas."
            jump mayor_2
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("FoodJustice_MayorEvaluation", eca, "mayor", "Mayor Watson")
        $ log_http(current_user, action="PlayerInputToECA", view="mayor", payload=ca_json)
        $ log("Player input to ECA: " + eca)
        $ argument_attempts = argument_attempts + 1
        $ achieve_argument()
        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="mayor", payload={"details": str(e)})
                ecaresponse = "Thank you for sharing your ideas with me! I can't give you feedback right now, but please do come back and share more later."

        $ log_http(current_user, action="PlayerECAResponse", view="mayor", payload={"eca_response": ecaresponse})

        if "Accept." in ecaresponse:
            $ mayorconvinced = True
            $ mayor_supports_parking = False
            $ ecaresponse = ecaresponse.replace("Accept. ", "", 1)
            $ log_http(current_user, action="MayorEvaluation", view="mayor", payload={"mayor_convinced": "Convincing Argument"})
        elif "Reject." in ecaresponse:
            $ mayorconvinced = False
            $ ecaresponse = ecaresponse.replace("Reject. ", "", 1)
            $ log_http(current_user, action="MayorEvaluation", view="mayor", payload={"mayor_convinced": "Not Convinced"})
        else:
            pass

        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        $ start_generated_dialogue("eca", {"character": "Mayor Watson", "context": "FoodJustice_MayorEvaluation"})
        if ecasplit == True:
            $ playAudio(ecaresponse1)
            m "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            m "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            m "[ecaresponse]"
        $ finish_generated_dialogue()

        $ stopAudio()

        $ mayor_attempts = mayor_attempts + 1
        if mayorconvinced == True:
            $ achieve_convincegarden()
        else:
            $ achieve_undecided()

        $ savedraft = renpy.confirm("Do you want to save this argument as your new draft? This will replace your existing argument in the notebook.")

        if savedraft == True:
            $ save_draft(eca)
        else:
            pass
    
    label bye_mayor:
        m "Thank you for sharing your ideas with me. Engaged citizens make our community stronger!"
        $ update_char_stats("Mayor")

        jump tulip_endgame

    label continue_search:
        m "Wonderful. I look forward to hearing your argument when it is ready to share."
        $ update_char_stats("Mayor")

        jump emptylot

    label elliot_chatting:
        scene expression "empty lot [startplace]"
        with dissolve

        show elliot smile
        with dissolve

        el "Welcome back! Did you find some interesting evidence for us to use in our pitch to the mayor?"

        menu:
            "Yeah! I've got a pretty persuasive argument for the mayor.":
                jump ideasharing
            "Some, but I think I need to find more.":
                jump still_investigating

    label still_investigating:
        el "The sign of a great investigator is knowing when you need to learn more!"
        el "The folks over at the Food Lab know a lot about soil and nutrients, so they could probably help us figure out what kind of evidence we need to gather to convince the mayor."
        el "And the gardeners at the community garden across town know a whole lot about bees and plants. They could tell us more about what benefits a garden can bring to a neighborhood."
        el "When you feel like you've gathered enough info to present our persuasive argument to the mayor, let me or Riley know, and we can workshop together!"
        $ update_char_stats("Elliot")
        jump emptylot

    label ideasharing:
        el "Sweet. So pretend I'm the mayor! Hey there good citizen! What do you think about this garden idea? Should I support it?"
        $ eca = safe_renpy_input("My ideas to persuade the mayor:", screen="argument_sharing")
        if not isinstance(eca, str) or not eca.strip():
            el "That's okay! Come back when you're ready to try out an argument."
            jump elliot_chatting
        $ eca = eca.strip()

        $ ca_link, ca_json = agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Elliot")
        $ log_http(current_user, action="PlayerInputToECA", view="elliot", payload=ca_json)
        $ log("Player input to ECA: " + eca)
        $ argument_attempts = argument_attempts + 1
        $ achieve_argument()

        python:
            try:
                ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
            except Exception as e:
                log_http(current_user, action="AgentError", view="elliot", payload={"details": str(e)})
                ecaresponse = "I'm having some trouble right now. Why don't you try asking Riley about this argument and see if she can give you some feedback?"

        $ log_http(current_user, action="PlayerECAResponse", view="elliot", payload={"eca_response": ecaresponse})
        
        $ ecasplit, ecaresponse1, ecaresponse2 = eca_length_check(ecaresponse)

        $ start_generated_dialogue("eca", {"character": "Elliot", "context": "FoodJustice_RileyEvaluation"})
        if ecasplit == True:
            $ playAudio(ecaresponse1)
            el "[ecaresponse1]"
            $ playAudio(ecaresponse2)
            el "[ecaresponse2]"

        else:
            $ playAudio(ecaresponse)
            el "[ecaresponse]"
        $ finish_generated_dialogue()

        $ stopAudio()

        $ savedraft = renpy.confirm("Do you want to save this argument as your new draft? This will replace your existing argument in the notebook.")

        if savedraft == True:
            $ save_draft(eca)
        else:
            pass

        el "Are there other ideas you want to run by me?"

        menu:
            "I have more evidence to share":
                jump ideasharing
            "That's all for now.":
                el "Okay! Let me know if you find new evidence later!"
                $ update_char_stats("Elliot")

                jump emptylot

    label tulip_endgame:
        scene expression "empty lot [startplace]"
        with dissolve

        show tulip
        with dissolve

        $ renpy.take_screenshot()
        $ renpy.save("1-1", save_name)

        $ note_count = len(notebook)  # <-- updated

        if get_character_chats("Riley") > 0 and get_character_chats("Nadia") > 0 and get_character_chats("Wes") > 0 and get_character_chats("Amara") > 0 and note_count > 5:
            t "Great job sharing your ideas with the Mayor! How do you think it went?"
            jump choices_eval
        elif get_character_chats("Riley") == 0 or get_character_chats("Nadia") == 0 or get_character_chats("Wes") == 0 or get_character_chats("Amara") == 0:
            t "Nice work sharing your argument! There are more folks around town we should talk to - let's make sure we include evidence from lots of different sources to be extra convincing!"
            jump emptylot
        else:
            t "Wonderful! You've been chatting with lots of different folks to improve your argument. Why don't you try taking some more notes in your notebook so we remember all of the most important parts of your argument?"
            jump emptylot

    label choices_eval:
        menu:
            "I don't think he's convinced yet.":
                jump needmore
            "He seemed kinda convinced, but I'm not sure.":
                jump maybeconvinced
            "He was really convinced by my argument!":
                jump convinced_endprep

    label needmore:
        t "That's okay! Don't be discouraged. A strong argument is going to need evidence from different sources, and it needs to cover different layers of the problem."
        t "This empty lot decision is going to impact people, bees like me, and the environment. As you talk to folks, think about what layers might be missing in your argument."
        jump emptylot

    label maybeconvinced:
        if mayor_attempts > 3:
            t "That's a good sign! I wonder if there are pieces of evidence in your notebook that you could add to your argument to make it more specific?"
            jump ending_game
        else:
            t "You're on the right track, then! Maybe there are a few more pieces of evidence you can gather in your notebook to make your argument more persuasive."
            jump emptylot

    label convinced_endprep:
        t "Amazing! I'm so glad."
        jump ending_game
    
    label ending_game:
        t "If you are satisfied with your persuasive argument, we can end the game and see what happens to the empty lot."
        t "But if you want to try to make your argument even more persuasive, you can keep exploring for a while and end the game later."
        t "What do you want to do?"

        menu:
            "I want to keep exploring.":
                t "Okay! I bet you can find even more evidence for your notebook if you talk with more people!"
                jump emptylot
            "I want to end the game.":
                t "Okay! Oooo, I'm so excited to see what happens, I'm practically buzzing with excitement!"
                jump final

    label final:
        if mayorconvinced == True:
            jump final_garden
        else:
            jump final_parking

    label final_garden:
        $ mayor_supports_parking = False
        $ achieve_convincegarden()
        scene expression "garden [startplace]"
        with dissolve

        show elliot smile at left
        with dissolve

        el "We did it! Thanks to all of your help, we were able to convince Mayor Watson to build a community garden for the neighborhood."

        show riley smile at right
        with dissolve

        r "The garden is becoming a favorite hangout spot for everyone. Wes has been coming here to teach workshops on how to care for the plants, and our first harvest is almost ready!"

        hide elliot smile
        with dissolve

        hide riley smile
        with dissolve

        show cora concern at right
        with dissolve

        show alex smile
        with dissolve

        c "You know, I had my doubts about the bees, but the garden has been really good for the neighborhood. The air even feels fresher around here!"

        x "Wes is teaching me how to grow tomatoes! We planted some seeds in the spring, and now they're HUGE!"

        show victor smile at left
        with dissolve

        v "Wes is such a great teacher! I've been learning too, and the veggies are almost ready for soup season!"

        hide victor smile
        with dissolve

        hide alex smile
        with dissolve

        hide cora concern
        with dissolve

        show tulip
        with dissolve

        t "The garden has been wonderful for the bees, too! Nadia helped the community plant some native flowers, so we have lots of tasty food to choose from."
        t "It seems like the people here are really happy to have fresh, healthy food to grow in their backyard! You should be proud of all the work you did to convince the mayor that this was the best plan."
        t "I'll see you around, human friend. Thanks for bee-ing a part of our community! Hehe."

        hide tulip
        with dissolve

        jump end

    label final_parking:
        $ mayor_supports_parking = True
        $ achieve_convinceparking()
        scene expression "parking [startplace]"
        with dissolve

        show cyrus smile at left
        with dissolve

        show watson smile at right
        with dissolve

        cy "Look at that beautiful parking [structure]! See kid, I told you this would be a great addition to the neighborhood."

        m "This really has been a great economic investment for the neighborhood. More people from out of town are visiting, which has been great for the local businesses."

        hide cyrus smile
        with dissolve

        hide watson smile
        with dissolve

        show elliot smile at left
        with dissolve

        el "Well, I guess the mayor is happy with his choice. A grocery store never moved in though, so it feels like this is good for business but not really good for the people who live here."

        show cora concern at right
        with dissolve

        c "We don't own a car, so the parking [structure] hasn't done much for us. The streets are also so busy now that I worry about Alex playing outside."

        hide cora concern
        with dissolve

        hide elliot smile
        with dissolve

        show tulip
        with dissolve

        t "Hmm, it seems like some folks are happy with the parking [structure], but it didn't solve all the problems."
        t "For the bees, there isn't a lot of green space left around here, so we won't find much food. The air is also getting a little polluted lately."
        t "We're going to head out and find a different neighborhood to explore that might have more food for us."
        t "Thanks for bee-ing my human friend! Hehe. I'll see you around!"

        jump end

    label end:
        narrator "Thanks for playing! Raise your hand to let the researchers know that you're finished."

    # This ends the game.

    return
