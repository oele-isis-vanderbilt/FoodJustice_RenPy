init python:
    import os
    import re

    current_label = None
    current_user = "Unknown"
    TIMEOUT = 15

    def _service_url(path):
        route = path if str(path).startswith("/") else f"/{path}"
        base_url = (os.getenv("SERVICE_URL") or "").strip()
        if base_url:
            return f"{base_url.rstrip('/')}{route}"
        return route

    def agent_setup(ca_type, eca, llama_ca, character):
        note_count = len(notebook)
        custom_note_count = sum(
            1
            for note in notebook
            if isinstance(note, dict) and note.get("type") == "user-written"
        )
        speakers = ", ".join(spoken_list)
        visits = ", ".join(visited_list)
        record_history_entry("Player:", eca)

        ca_link = _service_url("/foodjustice/respond")

        ca_json = {
            "userID": current_user, "query": eca, "gameState": {
            "contextType": ca_type,
            "numNotes": note_count,
            "customNotes": custom_note_count,
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
