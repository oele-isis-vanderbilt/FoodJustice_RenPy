# character set up
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
default ecaresponse = ""

### Code for CA setup ###
## TO ADD: gpt_agent_setup function with json format and link for HTTP request###

init python:
    current_label = None
    current_user = "Unknown"
    # Change timeout to 15 for actual usage, change to 1 allows for rapid script testing when agents are turned off
    TIMEOUT = 15

    def llama_agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(note_list)
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)

        # this is old llama link, new one yeojin sent is active below
        # ca_link = "http://149.165.155.145:9999/foodjustice/" + llama_ca
        ca_link = "https://ecoquest-llm-instance.soc240019.projects.jetstream-cloud.org:443/foodjustice/" + llama_ca

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
        return ca_link, ca_json

    def flan_agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(note_list)
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)

        # ca_context = "Player has taken " + note_count + " notes. Player has shared their argument " + argument attempts + " times. Player is currently in the " + currentlocation + ". Player has already spoken to " + speakers + " and has already visited " + visits
    
        ca_json = {"ECAType": ca_type, "Context": ca_context, "Utterance": eca, "ConfidenceThreshold": 0.3}

        ## To use the NCSU flanT5 CA: ##
        ca_link = "https://tracedata-01.csc.ncsu.edu/GetECAResponse"

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
    # if renpy.emscripten:
    # import emscripten
    # result = emscripten.run_script("window.syncFlowPublisher.startPublishing('umesh', 'umesh')")
        

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

    $ current_user = renpy.input("Please enter a name")

    jump demo

label tulipchat:
    show tulip at left
    with dissolve

    t "Whenever students click on the bee button, they can chat with me! Try clicking some options to see how students can interact with me."

label tulip_help_menu:
        menu:
            "I don't know what to do.":
                t "I would start by talking to people around town to see what they have to say!"
                t "If you've done that already, try opening your notebook to see what information you've collected, and think about what else you want to know."
                hide tulip
                with dissolve
                return

            "I'd like some help with persuading the mayor.":
                t "I'd be happy to help! If you tell me what evidence you've found, I can give you some advice on improving your pursuasive writing."

                $ eca = renpy.input("What should the Mayor do with the empty lot, and why?")

                $ ca_link, ca_json = llama_agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Tulip")
                $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                $ log("Player input to ECA: " + eca)
                $ argument_attempts = argument_attempts + 1

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                
                t "[ecaresponse]"
                $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})
               
                t "Just like Riley, I can offer students feedback on their arguments! Both of our characters use the same underlying AI model."
                
                hide tulip
                with dissolve
                return

            "I need help with something else.":
                t "I can answer student questions about how to play the game if they are confused, as well as how to work well with their classmates."
                $ eca = renpy.input("What's your question?")

                $ ca_link, ca_json = llama_agent_setup("GameHelp", eca, "tulip", "Tulip")
                $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)
                $ log("Player input to ECA: " + eca)

                $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                
                t "[ecaresponse]"
                $ log_http(current_user, action="PlayerECAResponse", view="tulip", payload={"eca_response": ecaresponse})
                
                hide tulip
                with dissolve
                return

            "Buzz ya later.":
                t "Don't bee a stranger! Hehe."
                hide tulip
                with dissolve
                return

label demo:

    narrator "Welcome to the Teacher Demo of SciStory: Pollinators! In this demo, you will get to know the SciStory game, and you'll be able to test out the AI agents students can interact with."

    show tulip
    with dissolve
    
    t "Hi! I'm Tulip the honeybee. I'm the first character your students will meet. You can think of me like a helper who is always around to answer student questions."

    t "In this game, your students will interact with characters in a story while trying to solve a complicated problem. The goal of the story is to help students learn how to gather evidence and write persuasive arguments about a community problem."

    t "We have some small ways that we adapt the game to fit your students' context. For example, go ahead and pick which kind of community we should explore. This will change what art you see in the next scene."
    
    menu:
        "I live in a city":
            $ startplace = "empty lot city"
           
        "I live in a rural town":
            $ startplace = "empty lot rural"
        
        "I live in the suburbs":
            $ startplace = "empty lot suburb" 
    
    scene expression "[startplace]"
    with fade
    $ currentlocation = "emptylot"

    show tulip
    with dissolve

    t "At the beginning of the game, students will visit this empty lot, and they'll talk to Elliot, a teenager in the neighborhood who introduces them to the story."

    hide tulip

    show elliot smile at right
    with dissolve

    e "Hi! I'm Elliot. I'll introduce the player to the story's key problem: A group of neighbors are trying to convince the Mayor to use this empty lot to build a community garden."

    show cyrus smile at left
    with dissolve

    e "However, THAT guy over there - Cyrus Murphy - is a marketing executive who is trying to convince the Mayor to sell the empty lot to a developer who will turn it into a parking garage."

    e "Throughout the story, the student will explore different locations, talk to different characters, and gather evidence in their digital notebook to help them figure out what they believe the Mayor should do with the empty lot."

    hide cyrus smile
    hide elliot smile

    show screen learningbuttons()

    show watson smile
    with dissolve

    m "I'm the Mayor of this town! Once the student has gathered lots of evidence and is ready to present their argument to me, my character will use AI to evaluate their argument and let them know whether I've been convinced."

    scene science lab
    $ currentlocation = "foodlab"

    show riley smile
    with dissolve

    r "The overall goal of this story game is to help students learn how to gather both scientific and personal evidence, and to write persuasive, thoughtful arguments that consider multiple sides of a problem that doesn't have one right answer."

    r "One of the key ways that the game helps students do this is by using artificial intelligence (AI) in some of the characters in order to help students built persuasive arguments."

    r "My name is Riley, and I'm one of the key AI characters that helps students as they play. Students will bring me their draft arguments, and I use AI to give them tailored feedback about how to make their argument more convincing."

    r "Let's try it out so you can see how it works!"

    $ eca = renpy.input("What do you think we should do with the empty lot, and why?")

    $ ca_link, ca_json = llama_agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Riley")
    $ log_http(current_user, action="PlayerInputToECA", view="riley", payload=ca_json)
    $ log("Player input to ECA: " + eca)
    $ argument_attempts = argument_attempts + 1

    $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                        
    $ log_http(current_user, action="PlayerECAResponse", view="riley", payload={"eca_response": ecaresponse})
    r "[ecaresponse]"

    r "So that's how the argument feedback works! The response you just read before this was generated by AI, and students can return to me throughout the game to try out new and more detailed arguments."

    scene garden
    with dissolve
    $ currentlocation = "garden"

    show wes smile
    with dissolve

    w "This is the third main area that students explore in the game - a community garden in a different part of town, where they can learn about how gardens help the community."

    w "In addition to AI characters that give students feedback on their writing, some characters use AI to answer students' questions about relevant topics."

    show nadia smile at left
    with dissolve

    w "As a beekeeper, Nadia here can answer questions about bees, pollination, and how gardens impact our ecosystem."

    n "Hi there! Students can find me over at the beehives and can ask me all sorts of questions. But if they ask me things that are off-topic or inappropriate, I'm designed to gently encourage them to remain on task."

    $ eca = renpy.input("Try asking me a question about bees or pollination to see how the AI responds.")

    $ ca_link, ca_json = llama_agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
    $ log_http(current_user, action="PlayerInputToECA", view="nadia", payload=ca_json)
    $ log("Player input to ECA: " + eca)

    $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)

    $ log_http(current_user, action="PlayerECAResponse", view="nadia", payload={"eca_response": ecaresponse})

    n "[ecaresponse]"

    n "Later in the demo, you'll be able to try out the different AI characters more thoroughly, to see if they respond the way you would expect them to for things your students might say."

    scene beehives
    with dissolve
    $ currentlocation = "beehives"

    t "Now that you've gotten a quick crash course in how the game works, we would love to get feedback from you on the different kinds of AI characters that students will talk with."

    t "We have developed three different AI models that can be used to give students responses and feedback. In the next part of this demo, you can ask questions of different agents, and you'll receive three different possible answers to compare."

    hide tulip

label select_agent:

    scene beehives
    with dissolve
    $ currentlocation = "beehives"

    narrator "Select which agent you want to try."

    $ llama_response = ""
    $ gpt_repsonse = ""
    $ flan_response = ""

    menu:
        "Riley: Argument evaluation and feedback":
            jump riley_test
        "Nadia: Answering science questions":
            jump nadia_test
        "Tulip: Advice on how to play the game and work well with others":
            jump tulip_test

label riley_test:

    $ eca = renpy.input("What do you think we should do with the empty lot, and why?")

    r "Loading responses...{w=0.5}{nw}"

    $ ca_link, ca_json = llama_agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Riley")
    $ argument_attempts = argument_attempts + 1

    $ log_http(current_user, action="PlayerInputToECA", view="riley", payload=ca_json)

    $ llama_response = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    
    $ log_http(current_user, action="Llama Response", view="riley", payload={"eca_response": llama_response})

    $ ca_link, ca_json = flan_agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Riley")
    $ flan_response = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    
    $ log_http(current_user, action="Flan Response", view="riley", payload={"eca_response": flan_response})

    # $ ca_link, ca_json = gpt_agent_setup("FoodJustice_RileyEvaluation", eca, "riley", "Riley")
    $ gpt_response = "Add GPT calls here."

    $ log_http(current_user, action="GPT Response", view="riley", payload={"eca_response": gpt_response})

    show screen three_agents(eca, "riley smile", llama_response, gpt_response, flan_response)

    jump select_agent

label nadia_test:

    $ eca = renpy.input("What do you want to know about bees and pollination?")

    n "Loading responses...{w=0.5}{nw}"

    $ ca_link, ca_json = llama_agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")

    $ log_http(current_user, action="PlayerInputToECA", view="nadia", payload=ca_json)

    $ llama_response = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                        
    $ log_http(current_user, action="Llama Response", view="nadia", payload={"eca_response": llama_response})

    $ ca_link, ca_json = flan_agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
    $ flan_response = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                        
    $ log_http(current_user, action="Flan Response", view="nadia", payload={"eca_response": flan_response})

    # $ ca_link, ca_json = gpt_agent_setup("Knowledge_Pollination", eca, "garden", "Nadia")
    $ gpt_response = "Add GPT calls here."
    
    $ log_http(current_user, action="GPT Response", view="nadia", payload={"eca_response": gpt_response})

    show screen three_agents(eca, "nadia smile", llama_response, gpt_response, flan_response)

    jump select_agent

label tulip_test:

    $ eca = renpy.input("What questions do you have about how to play?")

    t "Loading responses...{w=0.5}{nw}"

    $ ca_link, ca_json = llama_agent_setup("GameHelp", eca, "tulip", "Tulip")
    
    $ log_http(current_user, action="PlayerInputToECA", view="tulip", payload=ca_json)

    $ llama_response = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    
    $ log_http(current_user, action="Llama Response", view="tulip", payload={"eca_response": llama_response})

    $ ca_link, ca_json = flan_agent_setup("GameHelp", eca, "tulip", "Tulip")
    $ flan_response = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text", timeout=TIMEOUT)
                    
    $ log_http(current_user, action="Flan Response", view="tulip", payload={"eca_response": flan_response})

    # $ ca_link, ca_json = gpt_agent_setup("GameHelp", eca, "tulip", "Tulip")
    $ gpt_response = "Add GPT calls here."

    $ log_http(current_user, action="GPT Response", view="tulip", payload={"eca_response": gpt_response})

    show screen three_agents(eca, "tulip", llama_response, gpt_response, flan_response)

    jump select_agent


    # This ends the game.

    return
