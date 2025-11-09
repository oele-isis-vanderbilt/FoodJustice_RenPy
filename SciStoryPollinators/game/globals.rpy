define el = Character("Elliot")
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

define character_directory = [
    { "id": "elliot", "variable": el, "name": "Elliot",        "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "amara",  "variable": a,  "name": "Amara",         "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "riley",  "variable": r,  "name": "Riley",         "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "wes",    "variable": w,  "name": "Wes",           "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "nadia",  "variable": n,  "name": "Nadia",         "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "mayor",  "variable": m,  "name": "Mayor Watson",  "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "cyrus",  "variable": cy, "name": "Cyrus",         "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "alex",   "variable": x,  "name": "Alex",          "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "cora",   "variable": c,  "name": "Cora",          "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "victor", "variable": v,  "name": "Victor",        "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "id": "tulip",  "variable": t,  "name": "Tulip",         "role": "npc", "chats": 0, "questions": 0, "approval": 0, "spoken": False },
]

# GLOBAL NOTEBOOK LISTS 
default source_list = []
default note_list = []
default tag_list = []

#GLOBAL GAME STATE VARIABLES
default visited_list = []
default spoken_list = []
default startplace = "city"
default structure = "lot"
default currentlocation = "emptylot"
default current_user = "Unknown"
default current_label = None
default save_name = "Auto Save"
default voice_recording_active = False
default voice_input_contexts = 0
default voice_input_available = False
default voice_features_enabled = True

##LOCATION VISIT TRACKING
default emptylotvisit = False
default foodlabvisit = False
default gardenvisit = False
default hivesvisit = False

##END GAME STATE TRACKING
default argument_attempts = 0
default mayor_attempts = 0
default ca_context = ""
default ecaresponse = ""
default mayorconvinced = False
default mayor_supports_parking = False
