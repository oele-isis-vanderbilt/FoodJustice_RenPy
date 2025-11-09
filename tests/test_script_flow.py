import pytest


# Verifies critical entry/exit labels are defined exactly once.
def test_required_labels_exist(script_index):
    required = {"start", "begin", "end"}
    missing = required - set(script_index["labels"].keys())
    assert not missing, f"Missing required labels: {sorted(missing)}"


# Guards against duplicate label definitions that would confuse Ren'Py flow.
def test_no_duplicate_labels(script_index):
    duplicates = {
        label: paths for label, paths in script_index["duplicates"].items() if paths
    }
    assert not duplicates, f"Labels defined multiple times: {duplicates}"


# Ensures every jump references an existing label to avoid runtime crashes.
def test_all_jump_targets_are_defined(script_index):
    defined_labels = set(script_index["labels"].keys())
    undefined = script_index["jumps"] - defined_labels
    assert not undefined, f"Undefined jump targets: {sorted(undefined)}"


# Checks the hard-coded ending jump chain stays wired up for finale scenes.
def test_endgame_chain_intact(script_index):
    """
    The closing sequence relies on several specific labels being linked together.
    Even if intermediate navigation is handled via screens (and therefore invisible to our simple graph),
    we can still ensure the final jumps exist so the story can finish without crashing.
    """
    graph = script_index["graph"]
    chain_requirements = [
        ("ending_game", "final"),
        ("final", "final_garden"),
        ("final", "final_parking"),
        ("final_garden", "end"),
        ("final_parking", "end"),
    ]

    missing_edges = [
        (src, dst)
        for (src, dst) in chain_requirements
        if dst not in graph.get(src, set())
    ]
    assert not missing_edges, f"Missing endgame jump edges: {missing_edges}"


# Makes sure every `call screen` statement points to a declared screen.
def test_called_screens_are_defined(screen_index):
    undefined = screen_index["called"] - screen_index["defined"]
    assert not undefined, f"Screens called but not defined: {sorted(undefined)}"


# Ensures `show screen` usages only reference existing screens.
def test_shown_screens_are_defined(screen_index):
    undefined = screen_index["shown"] - screen_index["defined"]
    assert not undefined, f"Screens shown but not defined: {sorted(undefined)}"
