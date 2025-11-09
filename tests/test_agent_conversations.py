from types import SimpleNamespace

import pytest


def _prep_agent_state(eca_module):
    eca_module.notebook = [{"id": 1}, {"id": 2}]
    eca_module.spoken_list = ["Elliot", "Tulip"]
    eca_module.visited_list = ["Garden", "Empty Lot"]
    eca_module.customnotecount = 1
    eca_module.argument_attempts = 2
    eca_module.currentlocation = "garden"
    history = []
    eca_module.narrator = SimpleNamespace(
        add_history=lambda **kwargs: history.append(kwargs)
    )
    return history


# Parameterized smoke test: ensures agent_setup builds correct payloads per CA type/character.
@pytest.mark.parametrize(
    "ca_type,llama,character,utterance,expect_argument,expect_query",
    [
        ("FoodJustice_RileyEvaluation", "riley", "Tulip", "Draft argument", True, "argument evaluation"),
        ("FoodJustice_MayorEvaluation", "mayor", "Mayor Watson", "Mayor argument", True, "argument evaluation"),
        ("GameHelp", "tulip", "Tulip", "How do I progress?", False, "How do I progress?"),
        ("Knowledge_Pollination", "garden", "Nadia", "Tell me about bees", False, "Tell me about bees"),
        ("Knowledge_FoodJustice", "riley", "Riley", "Food justice facts?", False, "Food justice facts?"),
    ],
)
def test_agent_setup_builds_context(
    eca_module, ca_type, llama, character, utterance, expect_argument, expect_query
):
    history = _prep_agent_state(eca_module)

    link, payload = eca_module.agent_setup(ca_type, utterance, llama, character)

    assert link.endswith(f"/{llama}")
    state = payload["gameState"]
    assert state["contextType"] == ca_type
    assert state["numNotes"] == len(eca_module.notebook)
    assert state["customNotes"] == eca_module.customnotecount
    assert state["currentSpeaker"] == character
    assert state["spokeToNPC"] == ", ".join(eca_module.spoken_list)
    assert state["visitLocation"] == ", ".join(eca_module.visited_list)
    assert state["currentLocation"] == eca_module.currentlocation
    if expect_argument:
        assert state["argument"] == utterance
        assert payload["query"] == "argument evaluation"
    else:
        assert state["argument"] == ""
        assert payload["query"] == expect_query

    assert history, "Player utterance should be recorded in narrator history."


# Validates that long LLM replies are split into chunks while short/plain ones stay intact.
def test_eca_length_check_handles_varied_llm_responses(eca_module):
    long_response = (
        "First sentence offers praise. Second sentence gives advice. "
        "Third sentence elaborates on evidence. " * 5
    )
    split, first, second = eca_module.eca_length_check(long_response)
    assert split is True
    assert first.endswith(".")
    assert second

    short_response = "Great job!"
    split, first, second = eca_module.eca_length_check(short_response)
    assert split is False
    assert first == second == short_response

    no_period_response = "This response has no punctuation despite being long" * 5
    split, first, second = eca_module.eca_length_check(no_period_response)
    assert split is False
    assert first == second == no_period_response


# Ensures missing/None responses from external ECAs still return safe strings.
def test_eca_length_check_handles_missing_response(eca_module):
    split, first, second = eca_module.eca_length_check(None)
    assert split is False
    assert first == second == ""
