import re


# Validates every startplace has pin coordinates for empty/garden/food destinations.
def test_pin_positions_cover_all_locations(travel_module):
    pin_pos = travel_module.PIN_POS
    required = {"empty", "garden", "food"}
    for region in ("rural", "suburb", "city"):
        assert region in pin_pos
        assert required.issubset(pin_pos[region].keys())


# Ensures map pin jumps land on real labels in the main script graph.
def test_map_jump_targets_exist(game_dir, script_index):
    travel_path = game_dir / "feature_scripts" / "travel.rpy"
    text = travel_path.read_text(encoding="utf-8")
    targets = re.findall(r'Jump\("([A-Za-z_][\w]*)"\)', text)
    labels = set(script_index["labels"].keys())
    missing = {target for target in targets if target not in labels}
    assert not missing, f"Missing travel targets: {sorted(missing)}"
