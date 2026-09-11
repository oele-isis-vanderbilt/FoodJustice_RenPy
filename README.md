# Note
The OpenAI enabled version requires an agent sidecar exe that isn't stored in the repo. It is built from the python package found here:
https://drive.google.com/drive/folders/1hcZLf55nxlIOmujpKMdFHVnVBYvw7aLe

The resulting exe must be place in:
SciStoryPollinators\game\agent\

and be called: "agent_sidecar.exe"

# FoodJustice_RenPy

A repo for developing the lightweight, RenPy version of the Food Justice environment.

# Local Setup

## **Local Run Steps**

* Clone https://github.com/oele-isis-vanderbilt/FoodJustice_RenPy.git and work from main, branching for feature work if needed so you don’t ship unstable code to the live server (README.md (line 9)).
* Download the Ren’Py SDK (e.g., renpy-8.3.7-sdk), unzip it, and keep the SDK folder beside FoodJustice_RenPy inside the same parent directory so the launcher can find the project (README.md (line 16)-README.md (line 20)).
* From a terminal, cd into the SDK directory once and run chmod +x renpy.sh so the launcher script is executable; you shouldn’t need to repeat this unless you re-download the SDK (README.md (line 21)-README.md (line 23)).
* To run the GUI build locally, cd into the parent folder that contains both the SDK and the repo, then execute ./renpy.sh SciStoryPollinators/. If you see “permission denied,” rerun chmod +x renpy.sh inside the SDK directory and try again (README.md (line 25)-README.md (line 33)).

## **Web Build Option**

* Double‑click renpy.app inside the SDK folder to open the Ren’Py launcher, select the SciStoryPollinators project in the left pane, then choose Web under Actions (README.md (line 38)-README.md (line 40)).
* Use **Build Web Application** to produce a deployable web.zip/SciStoryPollinators-1.0-dists bundle, or **Build and Run in Browser** to have Ren’Py serve the game locally at a URL like http://127.0.0.1:8042/index.html; refresh the page as you tweak code (README.md (line 42)-README.md (line 48)).
* Approve the prompt to download “RenPy Web” if it appears, and check **Force Recompile** before building when switching branches or if the browser view looks stale (README.md (line 48)-README.md (line 49)).
* The generated SciStoryPollinators-1.0-dists folder inside the repo contains the assets you would upload to a server if you need to host the game online later (README.md (line 54)-README.md (line 55)).

# **Logging Overview**

| Event Type | Payload Fields | Purpose |
|----|----|----|
| **PlayerDialogueChoice** | `text`, `timestamp`, `delivery`, `is_question`, `question_target`, `auto_generated`, `origin`, … | Captures which choice the player clicked, when, and the surrounding context. |
| **PlayerDialogueInput** | `text`, `prompt`, `screen`, `delivery`, `is_question`, `metadata` | Records what the player typed and where the input occurred. |
| **PlayerDialogueLine / NPCDialogueLine** | `speaker_id`, `speaker_name`, `text`, `role`, `content_source`, `content_metadata`, `segment_start`, `segment_end` | Logs each spoken line, who said it, and whether it came from script or AI. |
| **PlayerLocationChoice** | `startplace` | Records the player’s initial hometown/background selection. |
| **PlayerInputToECA / _fromtemplate** | Full `ca_json` dict (userID, typed query, game-state snapshot) | Logs the player’s question + state sent to the tutoring agent. |
| **PlayerECAResponse** | `eca_response` | Saves the tutoring agent’s returned response. |
| **AgentError** | `details` | Error text if an agent call fails. |
| **MayorEvaluation** | `mayor_convinced` ("Convincing Argument" \| "Not Convinced") | Whether the mayor was persuaded. |
| **PlayerTookNote** | `note`, `source`, `tags`, `requested_tags`, `auto_tags_added`, `auto_tagged`, `auto_tagging_allowed`, `tag_origin`, `note_id`, `type` | Full detail of newly created notebook notes. |
| **PlayerDeletedNote** | `note`, `source`, `note_id` | Content removed from the notebook. |
| **PlayerEditedNote** | `note`, `source`, `tags`, `note_id`, `changes`, `tags_added`, `tags_removed`, `auto_tags_added`, `tag_origin` | Before/after edits to a notebook entry. |
| **PlayerSavedArgument / PlayerEditedArgument** | `draft`, `previous`, `change_summary` → {`previous_length`, `new_length`, `delta_length`} | Logs argument drafts + revision metrics. |
| **NotebookEvent** | `message`, …extra | Lightweight UI/UX events (e.g., opened notebook). |
| **CharacterApprovalChanged** | `character`, `delta`, `new_total`, `change_type`, `choice`, `message` | How/why NPC approval changed. |
| **AchievementUnlocked** | `achievement`, `name`, `location`, `character_in_discussion` | Records an earned achievement. |
| **PlayerJumpedLabel** | *(none)* | Breadcrumb marking a scene/label transition. |
| **Scene Export log_event** | `t`, `kind`, `data` | Timeline events for CSV/JSON scene export. |
| **Persistent Archive Record** | `scene`, `when`, `session`, `ext`, `hash`, `content` | Metadata for stored transcripts. |
| **Upload Queue Entry** | `scene`, `when`, `session`, `ext`, `hash`, `payload`, `attempts`, `last_error` | Tracks pending uploads + errors. |
| **_try_upload HTTP Body** | `scene`, `when`, `session`, `ext`, `hash`, `payload`, `game_version`, `platform` | Upload request containing log plus environment metadata. |

# Narrative Overview

*SciStory: Pollinators* is an interactive, story-driven game where players investigate food access, pollinator ecology, and community decision-making. The adventure unfolds across several neighborhood locations, each filled with characters who share evidence, perspectives, and expertise.

Players collect notes, build arguments, ask free-form questions, and ultimately try to convince the mayor to support a **community garden** instead of a proposed **parking garage**.

This section gives newcomers a simple outline of **the story**, **the spaces**, **key characters**, and **how the endings work**.

## 🌼 Narrative Arc (What Happens in the Story)

### 1. A Dreamlike Beginning

You wake up in a surreal field and meet **Tulip**, a friendly talking honeybee. Tulip orients you, sets up the game world based on your chosen *hometown type*, and introduces the **Notebook**, where you’ll save quotes and evidence during your investigation.

### 2. The Central Conflict

In the neighborhood, **Elliot**, a youth organizer, explains the main problem:

* The community wants the empty lot to become a **garden** for culturally relevant, affordable food.
* The **mayor** wants strong, multi-perspective evidence before rejecting **CityPark’s** proposal for a **parking garage**.

Your job is to gather evidence, speak with residents and experts, and construct an argument that can persuade Mayor Watson.

### 3. Explore the Neighborhood & Collect Evidence

Gameplay loops through several neighborhood locations:

* **Food Lab**
* **Westport Community Garden**
* **The Beehives**
* **The Empty Lot**

At each stop, you talk to characters, collect notes, and can ask **free-form questions** answered by the game’s AI knowledge agent.

### 4. Preparing for the Debate

Back at the empty lot, you debate **Cyrus** from CityPark, revise your arguments with Elliot and Riley, and prepare for the final pitch.

### 5. The Mayor’s Decision

You present your case to **Mayor Watson**, who evaluates your evidence (via an AI scoring agent).He decides whether the lot becomes:

* A **Community Garden**, or
* A **Parking Structure**.

Tulip wraps up the story depending on which outcome you achieve and how well you explored the evidence.

## 🗺️ Spaces & Activities

### 🌽 Food Lab

**Characters:**

* **Riley** — persuasive-writing coach; provides feedback and food justice explanations.
* **Amara** — food scientist providing data on nutrients, soil, chemistry, and biodiversity.

**Activities:**

* Collect scientific evidence.
* Practice arguments with AI-supported feedback.

### 🌿 Westport Community Garden

**Characters:**

* **Victor** — newcomer who shares stories about heirloom crops and cultural foods.
* **Wes** — master gardener explaining crop science, pollination, and ecology.

**Activities:**

* Learn about agriculture and pollination.
* Ask open-ended questions to the Pollination Knowledge Agent (Wes)

### 🐝 The Beehives

**Characters:**

* **Nadia** — beekeeper teaching bee ecology.
* **Alex** — child providing a kid’s perspective on food access.
* **Cora** — caregiver discussing safety, affordability, and family needs.

**Activities:**

* Explore how bees support ecosystems and food systems.
* Hear community experiences from different perspectives.

### 🏙️ The Empty Lot

**Characters:**

* **Cyrus** — CityPark representative promoting the parking garage.
* **Elliot** — helps you cross-check your evidence and arguments.
* **Mayor Watson** — evaluates your final pitch.

**Activities:**

* Debate the parking structure proposal.
* Collect the mayor’s evidence requirements.
* Deliver your final persuasive argument.

## 👥 Key Characters

| Character | Role & Description |
|----|----|
| **Tulip** | A talkative honeybee who explains mechanics, gives hints, and frames the ending based on the player’s evidence. |
| **Elliot** | Youth organizer who launches the food-justice investigation and helps the player rehearse arguments before the mayoral pitch. |
| **Riley** | Community advocate and persuasive-writing coach who evaluates the player’s arguments and provides food-justice background. |
| **Amara** | Food scientist offering lab-based evidence on nutrients, soil health, and environmental systems. |
| **Wes** | Master gardener who teaches crop science and pollinator ecology, supported by the Pollination Knowledge Agent. |
| **Victor** | Newcomer who shares heirloom-crop stories and highlights the cultural relevance of community-grown food. |
| **Nadia** | Beekeeper who teaches bee ecology and hive health. |
| **Alex** | A kid offering a youth perspective on food access and neighborhood life. |
| **Cora** | Caregiver raising concerns about affordability, time, and safety for families. |
| **Cyrus Murphy** | CityPark marketer promoting the parking-garage proposal and challenging the player’s evidence. |
| **Mayor Watson** | Decision-maker who evaluates the player’s final argument and chooses the game’s ending. |

## 🌳 Endings

### 🌼 Garden Victory

If you persuade the mayor, the lot becomes a **community garden**.Residents, pollinators, and families benefit — and the final scenes celebrate the success of your evidence-based advocacy.

### 🏗️ Parking Structure

If your evidence isn’t strong or complete enough, **CityPark’s parking garage** is approved.Commerce improves, but families lose access to fresh food and pollinator habitats. Tulip reflects on the inequities that remain.



# Tech Stack

## **Game Client**

* Ren’Py drives both SciStoryPollinators (student edition) and SciStoryTeacherDemo, with extensive Python helpers layered into scripts; the logging module records every dialogue line, choice, and upload-ready payload so gameplay analytics stay synchronized with back-end services
* The in-game notebook runs on custom tag normalization/auto-tagging logic that inspects dialogue text, enforces player overrides, and logs edits so saved notes remain queryable for later analysis
* Conversational-agent hooks assemble HTTP payloads that encode the player’s state (visited locations, notes, argument attempts) before calling hosted Food Justice agents, plus response-splitting safeguards for long LLM replies
* Voice features are toggled via Ren’Py screens that proxy to browser JavaScript, enabling Azure TTS playback and mic recording on the web build

## **Realtime + Voice Integrations**

* The exported web build loads custom helpers: azuretts.js streams speech from Azure Cognitive Services, microphoneUtility.js uploads WAV blobs to the ASR endpoint, and syncflow-publisher.js forwards telemetry and screen shares to LiveKit/SyncFlow rooms when enabled

## **Backend Service**

* A FastAPI app logs player events, serves the packaged Ren’Py build, and fan-outs routers for SyncFlow controls and admin auth; logging is persisted through rotating file handlers so live sessions can be audited
* Configuration relies on Pydantic settings models that read .env.app and .env.syncflow, define JWT claims, and expose runtime toggles for camera/mic/screen capture per session
* The /syncflow API authenticates against project credentials (syncflow-python-client) to create LiveKit sessions and mint access tokens, while a lightweight admin login issues signed cookies backed by bcrypt/pyjwt

## **Control Dashboard**

* Observability for facilitators lives in a SvelteKit + Vite single-page app styled with Tailwind/Flowbite; scripts provide dev/build/lint routines and TypeScript tooling for the ControlDashboard bundle served by the FastAPI middleware

## **Dependencies & Tooling**

* Python requirements stay minimal—FastAPI (with Uvicorn extras), bcrypt, PyJWT, and the SyncFlow client—while requirements-dev.txt pins pytest for the harnessed unit suite
* The automated pytest harness stubs Ren’Py/Pygame modules so you can validate labels, notebook logic, logging caps, travel pins, and agent payloads without launching the engine

## **Deployment**

* A multi-stage Dockerfile builds the Ren’Py web bundle, compiles the dashboard, installs service deps, and finally runs uvicorn app.main:app; docker-compose variants point the container at either the student or teacher build and mount log volumes/env secrets


