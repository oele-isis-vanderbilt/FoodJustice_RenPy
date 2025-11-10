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

#### Custom functions to control adding, editing, and deleting notes, as well as logging to txt file #####

# GLOBAL NOTEBOOK Variables 
default notebook = []
default argument_history = []

default tagLibrary = [
    "access to food",
    "health / nutrition",
    "environmental factors",
    "community action",
    "economic factors",
    "cultural factors",
    "sustainability",
    "pollinators",
    "equity / fairness"
]

default tagBuckets = {
    "access to food": [
        "grocery",
        "groceries",
        "store",
        "stores",
        "supermarket",
        "market",
        "markets",
        "farmers market",
        "food pantry",
        "pantry",
        "access",
        "available",
        "availability",
        "affordable",
        "affordability",
        "cost",
        "costs",
        "expensive",
        "price",
        "prices",
        "fresh food",
        "fresh produce",
        "healthy food",
        "local food",
        "local produce",
        "far away",
        "no place to buy",
        "food desert",
        "transportation",
        "delivery",
        "truck",
        "ship"
    ],

    "health / nutrition": [
        "healthy",
        "healthier",
        "health",
        "nutrition",
        "nutritious",
        "nutrients",
        "vitamin",
        "vitamins",
        "sugar",
        "sugars",
        "salt",
        "fats",
        "fat",
        "protein",
        "proteins",
        "calories",
        "balanced diet",
        "diet",
        "junk food",
        "fast food",
        "fresh vegetables",
        "fruits",
        "veggies",
        "eat",
        "eating",
        "eats",
        "eaten",
        "meal",
        "meals",
        "energy",
        "tired",
        "sick",
        "disease",
        "illness",
        "wellness",
        "exercise"
    ],

    "environmental factors": [
        "environment",
        "environmental",
        "ecosystem",
        "soil",
        "dirt",
        "ground",
        "water",
        "rainfall",
        "rainwater",
        "sunlight",
        "compost",
        "composting",
        "fertilizer",
        "pollution",
        "polluted",
        "trash",
        "waste",
        "recycling",
        "recycle",
        "reused",
        "reuse",
        "nature",
        "natural",
        "plants growing",
        "growing",
        "grow",
        "grows",
        "greenhouse",
        "clean air",
        "fresh air"
    ],

    "community action": [
        "together",
        "teamwork",
        "helping",
        "help",
        "helped",
        "volunteer",
        "volunteering",
        "local project",
        "project",
        "projects",
        "group",
        "working together",
        "cooperation",
        "join",
        "joining",
        "garden",
        "community garden"
    ],

    "economic factors": [
        "cost",
        "costs",
        "price",
        "prices",
        "budget",
        "budgeting",
        "money",
        "dollar",
        "dollars",
        "funding",
        "funded",
        "fundraiser",
        "donation",
        "donate",
        "business",
        "businesses",
        "company",
        "companies",
        "job",
        "jobs",
        "employment",
        "career",
        "work",
        "working",
        "profit",
        "sell",
        "selling",
        "sales",
        "buying",
        "affordable",
        "expensive",
        "income",
        "economy",
        "economic",
        "market",
        "markets"
    ],

    "cultural factors": [
        "culture",
        "cultures",
        "cultural",
        "tradition",
        "traditions",
        "heritage",
        "recipe",
        "recipes",
        "cook",
        "cooks",
        "cooking",
        "cooked",
        "cuisine",
        "flavor",
        "flavors",
        "spices",
        "food culture",
        "family meal",
        "family meals",
        "grandma",
        "grandfather",
        "grandparent",
        "parents",
        "mom",
        "dad",
        "family",
        "families",
        "household",
        "together",
        "dinner",
        "celebration"
    ],

    "sustainability": [
        "sustainability",
        "sustainable",
        "conserve",
        "conservation",
        "renewable",
        "renew",
        "recycle",
        "recycling",
        "reuse",
        "reused",
        "reducing waste",
        "reduce",
        "reduced",
        "preserving",
        "preservation",
        "protect",
        "protecting",
        "eco-friendly",
        "green",
        "compost",
        "composting",
        "earth",
        "planet",
        "resources",
        "natural resources",
        "save the earth",
        "take care of planet"
    ],

    "pollinators": [
        "bee",
        "bees",
        "beehive",
        "hives",
        "honey",
        "honeybee",
        "honeybees",
        "pollinate",
        "pollinates",
        "pollination",
        "pollinator",
        "pollinators",
        "nectar",
        "pollen",
        "insect",
        "insects",
        "butterfly",
        "butterflies",
        "bug",
        "bugs",
        "flower",
        "flowers",
        "crops",
        "fruit",
        "fruits",
        "vegetable",
        "vegetables",
        "growing food"
    ],

    "equity / fairness": [
        "justice",
        "fairness",
        "fair",
        "unfair",
        "equal",
        "equality",
        "equity",
        "deserve",
        "deserving",
        "everyone",
        "everybody",
        "all people",
        "poor",
        "poverty",
        "low-income",
        "rich",
        "wealth",
        "wealthy",
        "access",
        "opportunity",
        "opportunities",
        "community",
        "helping others",
        "help others",
        "together",
        "people",
        "neighborhood"
    ]
}


default note_id_counter = 0
default edited_note_id = None
default argument_edits = 0
default customnotecount = 0
default copied_argument = ""

default new_note_text_template = "whats your evidence?"

default notebook_unlocked = False
default editing_argument = False

default notebook_argument = "Draft your argument here."
default last_notebook_argument = "Draft your argument here."
default auto_tag_user_notes = True