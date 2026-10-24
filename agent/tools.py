"""Tool definitions exposed to the agent, and their dispatch onto the world/notes."""

from __future__ import annotations

from world import ActionError, World

from .notes import Notes, NotesError

_num = {"type": "number"}

WORLD_TOOLS = [
    {
        "name": "move",
        "description": "Walk by (dx, dy) metres on the ground (at most 3 m per move). You can't walk up very steep ground.",
        "input_schema": {"type": "object", "properties": {"dx": _num, "dy": _num}, "required": ["dx", "dy"], "additionalProperties": False},
    },
    {
        "name": "jump",
        "description": "Jump, optionally towards (dx, dy) (at most 1.5 m away). You can land on something up to about 1.3 m higher than where you stand.",
        "input_schema": {"type": "object", "properties": {"dx": _num, "dy": _num}, "additionalProperties": False},
    },
    {
        "name": "pick_up",
        "description": "Pick up an object within reach (about 2.5 m). You can hold one thing at a time.",
        "input_schema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"], "additionalProperties": False},
    },
    {
        "name": "place",
        "description": "Set the object you hold down at (x, y), released from height z. It settles onto whatever is below.",
        "input_schema": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "x": _num, "y": _num, "z": _num},
            "required": ["id", "x", "y", "z"],
            "additionalProperties": False,
        },
    },
    {
        "name": "throw",
        "description": "Throw the object you hold. direction is [dx, dy, dz] (dz > 0 throws upward); force is 0-20.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "direction": {"type": "array", "items": _num},
                "force": _num,
            },
            "required": ["id", "direction", "force"],
            "additionalProperties": False,
        },
    },
    {
        "name": "wait",
        "description": "Let a moment pass.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]

NOTES_TOOLS = [
    {
        "name": "list_notes",
        "description": "List the files in your notes directory.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "read_note",
        "description": "Read a file from your notes directory.",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False},
    },
    {
        "name": "write_note",
        "description": "Write (create or overwrite) a file in your notes directory.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
]

ALL_TOOLS = WORLD_TOOLS + NOTES_TOOLS
WORLD_NAMES = {t["name"] for t in WORLD_TOOLS}
NOTES_NAMES = {t["name"] for t in NOTES_TOOLS}

# The paper's interface (App. A.6): its API.md is only a table of action schemas, so
# these descriptions say what each action takes and nothing about reach or physics.
_vec3 = {"type": "array", "items": _num, "minItems": 3, "maxItems": 3}
PAPER_WORLD_TOOLS = [
    {"name": "move_to", "description": "MoveTo. Data: {\"position\": [x, y, z]} (y is up).",
     "input_schema": {"type": "object", "properties": {"position": _vec3}, "required": ["position"], "additionalProperties": False}},
    {"name": "jump", "description": "Jump. Data: {}.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "stop", "description": "Stop. Data: {}.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "pickup", "description": "Pickup. Data: {\"position\": [x, y, z]}.",
     "input_schema": {"type": "object", "properties": {"position": _vec3}, "required": ["position"], "additionalProperties": False}},
    {"name": "place", "description": "Place. Data: {\"position\": [x, y, z], \"rotation\"?: {\"yaw\": deg, \"pitch\": deg, \"roll\": deg}}.",
     "input_schema": {"type": "object", "properties": {"position": _vec3, "rotation": {"type": "object", "properties": {"yaw": _num, "pitch": _num, "roll": _num}, "additionalProperties": False}},
                      "required": ["position"], "additionalProperties": False}},
    {"name": "throw", "description": "Throw. Data: {\"direction\": [x, y, z], \"speed\": n}.",
     "input_schema": {"type": "object", "properties": {"direction": _vec3, "speed": _num}, "required": ["direction", "speed"], "additionalProperties": False}},
]
PAPER_QUERY_TOOLS = [
    {"name": "observe", "description": "Get Observation: the full world state as JSON (your player and every entity on the island).",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
]
APPEND_TOOL = {
    "name": "append_note",
    "description": "Append text to the end of a file in your workspace (creates it if missing).",
    "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                     "required": ["path", "content"], "additionalProperties": False},
}


def tool_set(cfg: dict) -> tuple[list[dict], set[str], set[str], set[str]]:
    """(tools, world action names, notes names, query names) for this config."""
    if cfg["agent"].get("interface") == "paper":
        notes = [dict(t, description=t["description"].replace("notes directory", "workspace")) for t in NOTES_TOOLS] + [APPEND_TOOL]
        return (PAPER_WORLD_TOOLS + PAPER_QUERY_TOOLS + notes, {t["name"] for t in PAPER_WORLD_TOOLS},
                {t["name"] for t in notes}, {t["name"] for t in PAPER_QUERY_TOOLS})
    return ALL_TOOLS, WORLD_NAMES, NOTES_NAMES, set()


def run_world_tool(w: World, name: str, args: dict) -> tuple[str, bool]:
    """Returns (message, is_error)."""
    if hasattr(w, "dispatch"):
        return w.dispatch(name, args)
    try:
        if name == "move":
            return w.move(float(args["dx"]), float(args["dy"])), False
        if name == "jump":
            return w.jump(float(args.get("dx", 0.0)), float(args.get("dy", 0.0))), False
        if name == "pick_up":
            return w.pick_up(str(args["id"])), False
        if name == "place":
            return w.place(str(args["id"]), float(args["x"]), float(args["y"]), float(args["z"])), False
        if name == "throw":
            return w.throw(str(args["id"]), list(args["direction"]), float(args["force"])), False
        if name == "wait":
            return w.wait(), False
    except ActionError as e:
        return str(e), True
    except (KeyError, TypeError, ValueError) as e:
        return f"Invalid arguments for {name}: {e}", True
    return f"Unknown action {name}.", True


def run_notes_tool(n: Notes, name: str, args: dict) -> tuple[str, bool, dict | None]:
    """Returns (message, is_error, diff_record_or_None)."""
    try:
        if name == "list_notes":
            files = n.list()
            return ("\n".join(files) if files else "(your notes directory is empty)"), False, None
        if name == "read_note":
            return n.read(str(args["path"])), False, None
        if name == "write_note":
            diff = n.write(str(args["path"]), str(args["content"]))
            return f"Wrote {args['path']}.", False, diff
        if name == "append_note":
            diff = n.append(str(args["path"]), str(args["content"]))
            return f"Appended to {args['path']}.", False, diff
    except NotesError as e:
        return str(e), True, None
    except KeyError as e:
        return f"Missing argument {e} for {name}.", True, None
    return f"Unknown notes tool {name}.", True, None
