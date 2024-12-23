import json
from pathlib import Path
from .calls import tool_objects

CURRENT_DIR = Path(__file__).parent
TOOLS_DIR = CURRENT_DIR / "tools.json"

with open(TOOLS_DIR) as f:
    tools = json.loads(f.read())

__all__ = ("tools", "tool_objects")
