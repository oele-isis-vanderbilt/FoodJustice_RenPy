init python:
    import re
    import requests
    import subprocess

    current_label = None
    current_user = "Unknown"
    TIMEOUT = 15
    SIDECAR_URL = "http://127.0.0.1:8765"

    def agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(notebook)
        speakers = spoken_list
        visits = visited_list
        record_history_entry("Player:", eca)

        ca_link = "https://foodjustice-new.soc240019.projects.jetstream-cloud.org/foodjustice/respond"

        ca_json = {
            "userID": current_user, 
            "query": eca, 
            "gameState": {
                "contextType": ca_type,
                "numNotes": note_count,
                "customNotes": customnotecount,
                "numArgument": argument_attempts,
                "currentSpeaker": character.lower(),
                "spokeToNPC": speakers,
                "visitLocation": visits,
                "currentLocation": currentlocation,
                "argument": ""
            }
        }
        return ca_link, ca_json 
    
    def split_eca_sentences(response):
        """Return the response split into sentence-like fragments for paced dialogue."""
        if response is None:
            return []
        text = response if isinstance(response, str) else str(response)
        text = text.strip().replace("\n", " ")
        if not text:
            return []

        fragments = re.split(r"(?<=[.!?])\s+", text)
        cleaned = [fragment.strip() for fragment in fragments if fragment.strip()]
        return cleaned if cleaned else [text]
    
    def loadAPIKey():
        import os
        print("loading api key")
        apikey = ""
        message = ""
        file_path = os.path.join(config.basedir, "apikey.txt")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                apikey = f.read()
                f.close()
        else:
            apikey = "API key file not found!"
        if apikey != "":
            open_ai_key = apikey
        print("done loading api key")
        return open_ai_key     

    def getGPTResponse(prompt):
        print(prompt)
        print("test test")
        print(SIDECAR_URL)
        print(prompt["gameState"])
        jsonobj={
                "session_id": prompt["userID"],
                "npc_id": prompt["gameState"]["currentSpeaker"].lower(),
                "player_text": prompt["query"],
                "game_state": prompt["gameState"],
            }
        print(jsonobj)
        result = renpy.fetch(
            SIDECAR_URL + "/v1/reply",
            json=jsonobj,
            result="json",
            timeout=30,
        )
        print(result)
        print(result["text"])
        return result["text"]

    def start_agent_sidecar(openai_api_key):
        print("starting sidecar")
        sidecar_path = os.path.join(renpy.config.gamedir, "agent", "agent_sidecar.exe")

        if not os.path.isfile(sidecar_path):
            raise RuntimeError("The local conversational-agent executable is missing.")

        # Pass the player-provided key to the child process only; do not save it
        # in an .rpy file or distribute it with the game.
        sidecar_environment = os.environ.copy()
        sidecar_environment["OPENAI_API_KEY"] = openai_api_key
        subprocess.Popen([sidecar_path], env=sidecar_environment)

        # The one-file executable needs time to unpack its embedded resources.
        for _ in range(40):
            try:
                health = renpy.fetch(
                    SIDECAR_URL + "/health", result="json", timeout=1
                )
                if health.get("status") == "ok":
                    return
            except renpy.FetchError:
                pass
            renpy.pause(0.25)

        raise RuntimeError("The local conversational agent did not start.")