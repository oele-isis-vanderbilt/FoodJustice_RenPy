from types import SimpleNamespace

import pytest


def _prep_agent_state(eca_module):
    eca_module.notebook = [
        {"id": 1, "type": "user-written"},
        {"id": 2, "type": "character-dialog"},
    ]
    eca_module.spoken_list = ["Elliot", "Tulip"]
    eca_module.visited_list = ["Garden", "Empty Lot"]
    eca_module.argument_attempts = 2
    eca_module.currentlocation = "garden"
    eca_module.current_user = "test-user"
    history = []
    eca_module.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history.append(kwargs)
    )
    eca_module.record_history_entry = (
        lambda who=None, what="", kind="adv": history.append(
            {"kind": kind, "who": who, "what": what}
        )
    )
    return history


# Parameterized smoke test: ensures agent_setup builds correct payloads per CA type/character.
@pytest.mark.parametrize(
    "ca_type,llama,character,utterance,expect_argument",
    [
        ("FoodJustice_RileyEvaluation", "riley", "Tulip", "Draft argument", True),
        ("FoodJustice_MayorEvaluation", "mayor", "Mayor Watson", "Mayor argument", True),
        ("GameHelp", "tulip", "Tulip", "How do I progress?", False),
        ("Knowledge_Pollination", "garden", "Nadia", "Tell me about bees", False),
        ("Knowledge_FoodJustice", "riley", "Riley", "Food justice facts?", False),
    ],
)
def test_agent_setup_builds_context(
    eca_module, ca_type, llama, character, utterance, expect_argument
):
    history = _prep_agent_state(eca_module)

    link, payload = eca_module.agent_setup(ca_type, utterance, llama, character)

    assert link.endswith("/foodjustice/respond")
    state = payload["gameState"]
    assert state["contextType"] == ca_type
    assert state["numNotes"] == len(eca_module.notebook)
    assert state["customNotes"] == 1
    assert state["currentSpeaker"] == character
    assert state["spokeToNPC"] == ", ".join(eca_module.spoken_list)
    assert state["visitLocation"] == ", ".join(eca_module.visited_list)
    assert state["currentLocation"] == eca_module.currentlocation
    assert state["argument"] == ""

    assert payload["userID"] == eca_module.current_user
    assert payload["query"] == utterance

    assert history, "Player utterance should be recorded in narrator history."


# Validates that long LLM replies are split into sentence chunks while short/plain ones stay intact.
def test_split_eca_sentences_handles_varied_llm_responses(eca_module):
    long_response = (
        "First sentence offers praise. Second sentence gives advice. "
        "Third sentence elaborates on evidence. " * 5
    )
    sentences = eca_module.split_eca_sentences(long_response)
    assert len(sentences) > 2
    assert sentences[0].endswith(".")

    short_response = "Great job!"
    sentences = eca_module.split_eca_sentences(short_response)
    assert sentences == [short_response]

    no_period_response = "This response has no punctuation despite being long" * 5
    sentences = eca_module.split_eca_sentences(no_period_response)
    assert sentences == [no_period_response]


# Ensures missing/None responses from external ECAs still return safe chunks.
def test_split_eca_sentences_handles_missing_response(eca_module):
    assert eca_module.split_eca_sentences(None) == []
