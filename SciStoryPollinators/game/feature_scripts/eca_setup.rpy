init python:
    import re

    current_label = None
    current_user = "Unknown"
    TIMEOUT = 15

    def agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(notebook)
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)
        record_history_entry("Player:", eca)

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
