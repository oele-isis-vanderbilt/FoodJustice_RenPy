import ast
"""
Test Suite Table of Contents
1. test_script_flow.py          — Validates Ren'Py labels, jumps, screen references, and endgame chain.
2. test_helper_voice.py         — Exercises voice-feature toggles and recording availability logic.
3. test_notebook_tags.py        — Covers notebook tag normalization and auto-tag buckets.
4. test_notebook_persistence.py — Verifies note creation/deletion side effects (logs, saves, history).
5. test_logging_helpers.py      — Ensures logging buffer capping for persistent archives and upload queue.
6. test_achievements.py         — Confirms achievement unlocking pathways and prerequisites.
7. test_travel.py               — Checks travel map pin coverage and jump targets.
8. test_agent_logging.py        — Tests logging callbacks, CA payload construction, and response splitting.
9. test_agent_conversations.py  — Parameterizes conversational agent setup across NPCs and response handling.
"""

import re
import sys
import textwrap
import types
from collections import defaultdict
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GAME_DIR = PROJECT_ROOT / "SciStoryPollinators" / "game"

LABEL_PATTERN = re.compile(r"^\s*label\s+([A-Za-z_][\w\.]*):", re.MULTILINE)
JUMP_PATTERN = re.compile(r"^\s*jump\s+(?!expression\b)([A-Za-z_][\w\.]*)", re.MULTILINE)
SCREEN_PATTERN = re.compile(r"^\s*screen\s+([A-Za-z_][\w]*)", re.MULTILINE)
CALL_SCREEN_PATTERN = re.compile(r"\bcall\s+screen\s+([A-Za-z_][\w]*)")
SHOW_SCREEN_PATTERN = re.compile(r"\bshow\s+screen\s+([A-Za-z_][\w]*)")

_MODULE_CACHE = {}
_PERSISTENT_STUB = types.SimpleNamespace()


def _iter_label_blocks(text: str):
    matches = list(LABEL_PATTERN.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        yield match.group(1), text[start:end]


def _install_stub_modules():
    if "renpy" in sys.modules:
        return

    renpy = types.ModuleType("renpy")

    store_module = types.ModuleType("renpy.store")
    store_module.voice_features_enabled = True
    store_module.voice_input_contexts = 0
    store_module.voice_input_available = False
    store_module.voice_recording_active = False
    store_module.auto_tag_user_notes = True
    renpy.store = store_module

    display_module = types.ModuleType("renpy.display")
    core_module = types.ModuleType("renpy.display.core")

    class EndInteraction(Exception):
        pass

    core_module.EndInteraction = EndInteraction

    transform_module = types.ModuleType("renpy.display.transform")

    class Transform:
        def __init__(self, displayable, **kwargs):
            self.displayable = displayable
            self.kwargs = kwargs

    transform_module.Transform = Transform

    matrix_module = types.ModuleType("renpy.display.matrix")

    class Matrix(list):
        pass

    matrix_module.Matrix = Matrix

    display_module.core = core_module
    display_module.transform = transform_module
    display_module.matrix = matrix_module
    renpy.display = display_module

    def _record_notification(message):
        renpy._last_notify = message

    renpy.notify = _record_notification
    renpy._shown_screens = set()
    renpy.get_screen = lambda name: name if name in renpy._shown_screens else None

    def _show_screen(name, *args, **kwargs):
        renpy._shown_screens.add(name)

    def _hide_screen(name, *args, **kwargs):
        renpy._shown_screens.discard(name)

    renpy.show_screen = _show_screen
    renpy.hide_screen = _hide_screen
    renpy.invoke_in_new_context = lambda fn, *a, **k: fn(*a, **k)
    renpy.input = lambda prompt="", **kwargs: ""
    renpy.call_screen = lambda screen, **kwargs: ""
    renpy.take_screenshot = lambda: None
    renpy.save = lambda slot, name: None
    renpy.block_rollback = lambda: None
    renpy.save_persistent = lambda: None
    renpy.fetch = lambda *args, **kwargs: None
    renpy.confirm = lambda prompt="": False
    renpy.pause = lambda *args, **kwargs: None
    renpy.log = lambda *args, **kwargs: None
    renpy.loadable = lambda path: False
    renpy.image_size = lambda path: (100, 100)
    renpy.retain_after_load = lambda: None
    renpy.emscripten = False
    renpy.platform = "test"

    sys.modules["renpy"] = renpy
    sys.modules["renpy.store"] = store_module
    sys.modules["renpy.display"] = display_module
    sys.modules["renpy.display.core"] = core_module
    sys.modules["renpy.display.transform"] = transform_module
    sys.modules["renpy.display.matrix"] = matrix_module

    pygame_module = types.ModuleType("pygame")
    pygame_scrap = types.ModuleType("pygame.scrap")
    pygame_module.scrap = pygame_scrap
    sys.modules["pygame"] = pygame_module
    sys.modules["pygame.scrap"] = pygame_scrap

    config_module = types.ModuleType("config")
    config_module.savedir = str(PROJECT_ROOT / "tmp_saves")
    config_module.version = "test"
    config_module.start_callbacks = []
    config_module.label_callbacks = []
    sys.modules["config"] = config_module


def _get_persistent_stub():
    if not hasattr(_PERSISTENT_STUB, "logs"):
        _PERSISTENT_STUB.logs = []
    if not hasattr(_PERSISTENT_STUB, "unsent"):
        _PERSISTENT_STUB.unsent = []
    return _PERSISTENT_STUB


def _extract_python_blocks(text: str):
    blocks = []
    lines = text.splitlines()
    capture = False
    indent_level = None
    body_indent = None
    current = []

    def flush():
        nonlocal current
        if current:
            blocks.append("\n".join(current))
            current = []

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        if not capture:
            if stripped.startswith("init") and "python" in stripped:
                capture = True
                indent_level = len(line) - len(line.lstrip())
                body_indent = None
            idx += 1
            continue

        if stripped and (len(line) - len(line.lstrip())) <= (indent_level or 0):
            flush()
            capture = False
            continue

        if stripped == "":
            current.append("")
        else:
            leading = len(line) - len(line.lstrip())
            if body_indent is None:
                body_indent = leading
            current.append(line[body_indent:])
        idx += 1

    flush()
    return blocks


def _extract_literal_list(text: str, define_name: str):
    marker = f"define {define_name}"
    idx = text.find(marker)
    if idx == -1:
        return None
    start = text.find("[", idx)
    if start == -1:
        return None
    depth = 0
    end = start
    while end < len(text):
        char = text[end]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                break
        end += 1
    if depth != 0:
        return None
    literal_text = text[start : end + 1]
    try:
        return ast.literal_eval(literal_text)
    except Exception:
        return None


def load_rpy_module(relative_path: str, module_name: str):
    _install_stub_modules()
    key = (relative_path, module_name)
    if key in _MODULE_CACHE:
        return _MODULE_CACHE[key]

    path = GAME_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Ren'Py file not found: {path}")

    text = path.read_text(encoding="utf-8")
    blocks = _extract_python_blocks(text)
    code = "\n\n".join(textwrap.dedent(block) for block in blocks if block.strip())

    module = types.ModuleType(module_name)
    module.__file__ = str(path)

    def _dummy_label_callback(label=None, interaction=None, **kwargs):
        return None

    predefs = {}
    if "achievements.rpy" in relative_path:
        literal = _extract_literal_list(text, "achievement_list")
        if literal is not None:
            predefs["achievement_list"] = literal
        predefs.setdefault("log_http", lambda *args, **kwargs: None)
        predefs.setdefault("current_user", "test-user")
        predefs.setdefault("current_label", "test-label")
        predefs.setdefault("last_spoken_character", "Elliot")
        predefs.setdefault("last_spoken_character", "Elliot")
    if "helper.rpy" in relative_path:
        predefs.setdefault("log_player_input", lambda *args, **kwargs: None)
        predefs.setdefault("log_http", lambda *args, **kwargs: None)
        predefs.setdefault("current_user", "test-user")
        predefs.setdefault("current_label", "test-label")

    global_scope = module.__dict__
    global_scope.update(
        {
            "__file__": str(path),
            "__name__": module_name,
            "renpy": sys.modules["renpy"],
            "config": sys.modules["config"],
            "persistent": _get_persistent_stub(),
            "label_callback": _dummy_label_callback,
        }
    )
    global_scope.update(predefs)

    exec(code, global_scope)
    _MODULE_CACHE[key] = module
    return module


@pytest.fixture(autouse=True)
def reset_stubs():
    _install_stub_modules()
    renpy = sys.modules["renpy"]
    store = renpy.store
    store.voice_features_enabled = True
    store.voice_input_available = False
    store.voice_input_contexts = 0
    store.voice_recording_active = False
    store.auto_tag_user_notes = True
    store.tagLibrary = []
    store.tagBuckets = {}
    store.notebook = []

    renpy._shown_screens = set()
    renpy._last_notify = None
    renpy.notify = lambda message: setattr(renpy, "_last_notify", message)
    renpy.get_screen = lambda name: name if name in renpy._shown_screens else None

    def _show_screen(name, *args, **kwargs):
        renpy._shown_screens.add(name)

    def _hide_screen(name, *args, **kwargs):
        renpy._shown_screens.discard(name)

    renpy.show_screen = _show_screen
    renpy.hide_screen = _hide_screen
    renpy.invoke_in_new_context = lambda fn, *a, **k: fn(*a, **k)
    renpy.input = lambda prompt="", **kwargs: ""
    renpy.call_screen = lambda screen, **kwargs: ""
    renpy.take_screenshot = lambda: None
    renpy.save = lambda slot, name: None
    renpy.block_rollback = lambda: None
    renpy.save_persistent = lambda: None
    renpy.fetch = lambda *args, **kwargs: None
    renpy.confirm = lambda prompt="": False
    renpy.pause = lambda *args, **kwargs: None
    renpy.log = lambda *args, **kwargs: None
    renpy.loadable = lambda path: False
    renpy.image_size = lambda path: (100, 100)
    renpy.retain_after_load = lambda: None
    renpy._saves = {"count": 0}

    persistent = _get_persistent_stub()
    persistent.logs = []
    persistent.unsent = []
    persistent.achievements = {}
    yield


@pytest.fixture(scope="session")
def script_index():
    if not GAME_DIR.exists():
        pytest.skip(f"Ren'Py game directory not found at {GAME_DIR}")

    label_origins = {}
    duplicate_labels = defaultdict(list)
    all_jumps = set()
    graph = defaultdict(set)

    for path in sorted(GAME_DIR.rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")

        for label, body in _iter_label_blocks(text):
            if label in label_origins:
                duplicate_labels[label].append(path)
            else:
                label_origins[label] = path

            graph.setdefault(label, set()).update(JUMP_PATTERN.findall(body))

        all_jumps.update(JUMP_PATTERN.findall(text))

    return {
        "labels": label_origins,
        "duplicates": duplicate_labels,
        "jumps": all_jumps,
        "graph": graph,
    }


@pytest.fixture(scope="session")
def screen_index():
    defined = set()
    called = set()
    shown = set()

    for path in sorted(GAME_DIR.rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        defined.update(SCREEN_PATTERN.findall(text))
        called.update(CALL_SCREEN_PATTERN.findall(text))
        shown.update(SHOW_SCREEN_PATTERN.findall(text))

    return {"defined": defined, "called": called, "shown": shown}


@pytest.fixture(scope="session")
def helper_module():
    return load_rpy_module("feature_scripts/helper.rpy", "helper_module")


@pytest.fixture(scope="session")
def notebook_module():
    return load_rpy_module("feature_scripts/notebook.rpy", "notebook_module")


@pytest.fixture(scope="session")
def logging_module():
    return load_rpy_module("feature_scripts/logging.rpy", "logging_module")


@pytest.fixture(scope="session")
def achievements_module():
    return load_rpy_module("feature_scripts/achievements.rpy", "achievements_module")


@pytest.fixture(scope="session")
def travel_module():
    return load_rpy_module("feature_scripts/travel.rpy", "travel_module")


@pytest.fixture(scope="session")
def eca_module():
    return load_rpy_module("feature_scripts/eca_setup.rpy", "eca_module")


@pytest.fixture
def renpy_store():
    return sys.modules["renpy.store"]


@pytest.fixture
def persistent_state():
    return _get_persistent_stub()


@pytest.fixture
def renpy_module():
    return sys.modules["renpy"]


@pytest.fixture(scope="session")
def game_dir():
    return GAME_DIR
