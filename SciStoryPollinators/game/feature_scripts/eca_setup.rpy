init python:
    current_label = None
    current_user = "Unknown"
    TIMEOUT = 15

    def agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(note_list)
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)
        narrator.add_history(kind="adv",who="Player:",what=eca)
        ### Code for switching out CA models for the AI agents. Uncomment the ca_link and ca_json for the model you want to use, comment others ###

        ## To use the Llama CA: ##

        # Old links below, updated link is active
        # ca_link = "http://149.165.155.145:9999/foodjustice/" + llama_ca
        # ca_link = "https://ecoquest-llm-instance.soc240019.projects.jetstream-cloud.org:443/foodjustice/" + llama_ca

        ca_link = "https://llama-small-instance.soc240019.projects.jetstream-cloud.org/foodjustice/" + llama_ca


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

    def eca_length_check(response):
        checker = "." 
        if len(response) > 200 and checker in response:
            multi_response = [x.strip() for x in response.split(".")]
            if len(multi_response[0]+multi_response[1]) > 250:
                ecaresponse1 = multi_response[0]+"."
                del multi_response[0]
                ecaresponse2 = ". ".join(multi_response)
            else:
                ecaresponse1 = ". ".join(multi_response[0:2])+"."
                del multi_response[0:2]
                ecaresponse2 = ". ".join(multi_response)
            if len(ecaresponse2) == 0:
                ecaresponse1 = response
                ecaresponse2 = response
                return False, ecaresponse1, ecaresponse2
            else: 
                return True, ecaresponse1, ecaresponse2

        else:
            ecaresponse1 = response
            ecaresponse2 = response
            return False, ecaresponse1, ecaresponse2


        ## Possibilities for ca_type: ##
        # FoodJustice_RileyEvaluation, FoodJustice_MayorEvaluation, Knowledge_FoodJustice, Knowledge_Pollination
        # GameHelp, GameHelp_Collaboration, GEMSTEP_Observing

        ## Possbilities for llama_ca ##
        # eliot, garden, RileyEvaluation

        #### Code to copy/paste to call CA model during narrative ####
        # ca_type, the utterance, the llama_ca type, and the character name who is talking #
        # $ agent_setup("RileyEvaluation", eca, "eliot", "Elliot")
        # $ ecaresponse = renpy.fetch(ca_link, method="POST", json=ca_json, content_type="application/json", result="text")


# The game starts here.
