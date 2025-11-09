# Ensures normalize_tags splits string inputs into trimmed tag lists.
def test_normalize_tags_handles_strings(notebook_module):
    normalize = notebook_module.normalize_tags
    assert normalize("bee, garden ,  community") == ["bee", "garden", "community"]


# Verifies normalize_tags passes through iterable inputs without collapsing case.
def test_normalize_tags_handles_iterables(notebook_module):
    normalize = notebook_module.normalize_tags
    assert normalize(["Bee", "bee", "Garden"]) == ["Bee", "bee", "Garden"]


# Checks auto_character_tags maps content to bucket/library tags without duplicates.
def test_auto_character_tags_respects_buckets(notebook_module, renpy_store):
    renpy_store.tagLibrary = ["garden"]
    renpy_store.tagBuckets = {
        "pollinators": ["bee", "bees"],
        "equity / fairness": ["community"],
    }

    auto_tags = notebook_module.auto_character_tags
    tags = auto_tags(
        "Bees help our community garden thrive.", existing_tags=["custom", "pollinators"]
    )

    assert "pollinators" in tags
    assert "equity / fairness" in tags
    assert "garden" in tags
    assert tags.count("pollinators") == 1
