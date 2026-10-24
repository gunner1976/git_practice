from .island import ActionError, World
from .tasks import TASKS, score


def make_world(cfg: dict, seed: int | None = None) -> World:
    """The paper's interface (world/paper.py) when `paper.enabled`, else the replication world."""
    if cfg.get("paper", {}).get("enabled"):
        from .paper import PaperWorld

        return PaperWorld(cfg, seed)
    return World(cfg, seed)


__all__ = ["World", "ActionError", "TASKS", "score", "make_world"]
