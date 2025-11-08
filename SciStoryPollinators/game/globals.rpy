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
    { "variable": el, "name": "Elliot",        "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": a,  "name": "Amara",         "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": r,  "name": "Riley",         "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": w,  "name": "Wes",           "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": n,  "name": "Nadia",         "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": m,  "name": "Mayor Watson",  "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": cy, "name": "Cyrus",         "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": x,  "name": "Alex",          "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": c,  "name": "Cora",          "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": v,  "name": "Victor",        "chats": 0, "questions": 0, "approval": 0, "spoken": False },
    { "variable": t,  "name": "Tulip",         "chats": 0, "questions": 0, "approval": 0, "spoken": False },
]

# GLOBAL NOTEBOOK LISTS 
default source_list = []
default note_list = []
default tag_list = []

#GLOBAL GAME STATE VARIABLES
default visited_list = []
default spoken_list = []
default startplace = ""
default structure = ""
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
