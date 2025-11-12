init python:
    current_label = None
    current_user = "Unknown"
    TIMEOUT = 15

    def agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(notebook)
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)
        narrator.add_history(kind="adv",who="Player:",what=eca)

        ca_link = "https://foodjustice-new.soc240019.projects.jetstream-cloud.org/foodjustice/respond"

        ca_json = {
            "userID": current_user, "query": eca, "gameState": {
            "contextType": ca_type,
            "numNotes": note_count,
            "customNotes": customnotecount,
            "numArgument": argument_attempts,
            "currentSpeaker": character,
            "spokeToNPC": speakers,
            "visitLocation": visits,
            "currentLocation": currentlocation,
            "argument": ""
        }}
        return ca_link, ca_json 

    def eca_length_check(response):
        if response is None:
            response = ""
        elif not isinstance(response, str):
            response = str(response)
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
