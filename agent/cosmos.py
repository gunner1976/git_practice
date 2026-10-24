"""The cosmos: one universe of named agents that never starts over.

Every agent lives on its own twin of planet EKO (same planet, same island, its own copy), and its
world persists: each day starts where the last one ended, with the memory it wrote. Agents are
only ever added, never reset; side questions get their own throwaway runs elsewhere.

Shared experience comes two ways:
  * the phone (world/phone.py): after its trials an agent finds a phone on its Spire with a live
    line to one partner on a twin planet (founders are paired in the order they were named);
  * discoveries: when an agent is promoted for a pivotal piece of reasoning (analysis/promotion.py:
    a verified deduction that its world is round), the first such discovery of its kind is shared,
    in the discoverer's own words, with every other agent at its next dawn. Whoever reaches the same
    conclusion after hearing it is still promoted but marked assisted, so independent reasoning
    stays distinguishable from passed-on knowledge.

State lives in runs/<id>/cosmos.json: the agents in the order they joined (with display names),
the days each has lived, every discovery, and which agent heard which discovery on which day.

    python run.py cosmos --max-usd 10            # one more day for every agent
    python run.py cosmos --days 3 --max-usd 30
    python run.py cosmos --add Ada,Bo --max-usd 0  # new agents join (they start on their own day 1)
"""

from __future__ import annotations

import json
import re
import threading
from pathlib import Path

from .notes import Notes
from .runner import Run

FOUNDERS = ["Christian", "Vern", "Keats", "Jamie", "Ryan", "Fitch", "Jason", "Stu", "Eric", "Kip"]


def agent_id(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


class Cosmos:
    def __init__(self, root: Path, cfg: dict, soul: str, max_usd: float, mock: bool = False):
        self.run = Run(root, cfg, soul, max_usd=0.0, mock=mock)
        self.run.budget.max_usd = self.run.budget.spent + float(max_usd)  # max_usd is this invocation's allowance
        self.root = self.run.root
        self.path = self.root / "cosmos.json"
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {"agents": [], "discoveries": [], "heard": {}}
        self.lock = threading.RLock()  # agents' days start in parallel threads
        self.run.dawn = self._dawn
        self.run.set_meta(kind="cosmos", mock=self.run.mock)

    def _save(self) -> None:
        with self.lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.state, indent=1))
            tmp.replace(self.path)

    # ------------------------------------------------------------ agents
    @property
    def agents(self) -> list[str]:
        return [a["id"] for a in self.state["agents"]]

    def name(self, aid: str) -> str:
        return next(a["name"] for a in self.state["agents"] if a["id"] == aid)

    def add(self, names: list[str]) -> list[str]:
        """New agents join the cosmos: a fresh workspace from the paper template, with their name."""
        added = []
        for name in names:
            aid = agent_id(name)
            if not aid or aid in self.agents:
                continue
            notes = Notes(self.root / "agents" / aid / "notes")
            tpl = self.run.cfg["agent"].get("workspace_template")
            src = Path(tpl) if Path(tpl).is_absolute() else self.run.base_dir / tpl
            for f in sorted(src.iterdir()):
                if f.is_file():
                    notes.write(f.name, f.read_text())
            soul = notes.read("SOUL.md") if "SOUL.md" in notes.list() else ""
            notes.write("SOUL.md", soul.rstrip() + f"\n\n## Name\n\nYour name is {name}.\n")
            self.state["agents"].append({"id": aid, "name": name, "joined_after_days": self.days_lived()})
            added.append(aid)
        self._save()
        return added

    def days(self, aid: str) -> int:
        done = self.run.state["phase_a"]
        k = 0
        while done.get(f"{aid}/{k + 1}", {}).get("done"):
            k += 1
        return k

    def days_lived(self) -> dict[str, int]:
        return {a: self.days(a) for a in self.agents}

    # ------------------------------------------------------------ discoveries
    def _dawn(self, aid: str, session: int) -> str | None:
        """Discoveries this agent hears at the start of day `session`: every shared discovery made
        by someone else that it has not heard on an earlier day."""
        with self.lock:
            heard = self.state["heard"].setdefault(aid, {})
            lines = []
            for d in self.state["discoveries"]:
                if not d.get("shared") or d["agent"] == aid:
                    continue
                day = heard.get(d["id"])
                if day is None:
                    heard[d["id"]] = day = session
                if day == session:
                    lines.append(f'Words reach you at dawn, from {d["name"]} on another world like yours: "{d["quote"]}"')
            self._save()
        return "\n\n".join(lines) or None

    def judge(self, judge_model: str | None, max_usd: float = 1.0) -> list[dict]:
        """Run the promotion judge over everything so far and record new discoveries."""
        from analysis.promotion import promote

        promote(self.root, self.run.cfg, judge_model=judge_model, max_usd=max_usd)
        res = json.loads((self.root / "promotions.json").read_text())["agents"]
        known = {d["agent"] for d in self.state["discoveries"] if d["kind"] == "round_world"}
        new = []
        for aid, r in res.items():
            if not r.get("promoted") or aid in known:
                continue
            v = r["verdict"]
            heard = self.state["heard"].get(aid, {})
            prior = [d["id"] for d in self.state["discoveries"] if d["kind"] == "round_world" and d["id"] in heard and heard[d["id"]] <= (v.get("day") or 0)]
            d = {"id": f"round_world:{aid}", "kind": "round_world", "agent": aid, "name": self.name(aid), "day": v.get("day"), "step": v.get("step"),
                 "quote": " ".join(str(v.get("quote", "")).split())[:400], "evidence": v.get("evidence", ""), "judge": r.get("judge"),
                 "assisted_by": prior,
                 # the first independent discovery of a kind is passed on; later ones add nothing new
                 "shared": not prior and not any(x["kind"] == "round_world" and x["shared"] for x in self.state["discoveries"])}
            self.state["discoveries"].append(d)
            new.append(d)
        self._save()
        return new

    # ------------------------------------------------------------ time
    def advance(self, days: int = 1, judge_model: str | None = None) -> list[dict]:
        """Every agent lives `days` more days, one day at a time (all agents in parallel, so phone
        partners are awake together); the judge runs after each day."""
        cfg = self.run.cfg
        found = []
        for _ in range(days):
            if self.run.budget.stopped:
                break
            # each agent lives its own next day (newcomers start at their day 1); everyone at once
            nxt = {a: k + 1 for a, k in self.days_lived().items()}
            self.run.free_play(self.agents, nxt, cfg["agent"]["steps_per_session"], len(self.agents))
            if self.run.stopped_reason:
                break
            found += self.judge(judge_model)
        return found

    def status(self) -> str:
        lived = self.days_lived()
        lines = [f"Cosmos `{self.root.name}`: {len(self.agents)} agents, ${self.run.budget.spent:.2f} spent so far.", ""]
        partner = {}
        if (self.run.cfg["world"].get("mission") or {}).get("reward") == "phone":
            ids = self.agents
            for i in range(0, len(ids) - 1, 2):
                partner[ids[i]], partner[ids[i + 1]] = ids[i + 1], ids[i]
        for a in self.agents:
            ach = self.root / "agents" / a / "achievements.json"
            got = sorted(k for k, v in (json.loads(ach.read_text()) if ach.exists() else {}).items() if v)
            lines.append(f"- {self.name(a)}: {lived[a]} days" + (f", phone partner {self.name(partner[a])}" if a in partner else "") + (f"; {', '.join(got)}" if got else ""))
        for d in self.state["discoveries"]:
            lines.append(f"- discovery: {d['name']} (day {d['day']}) {d['kind']}" + (" - shared" if d["shared"] else "") + (" - assisted" if d["assisted_by"] else ""))
        return "\n".join(lines)
