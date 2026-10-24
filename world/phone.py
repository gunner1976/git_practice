"""The phone on the Spire: a live line between two agents, each on their own island.

Agents are paired (agent_1 with agent_2, agent_3 with agent_4, ...). Each one's phone appears
once that agent has completed its own mission trials, so both ends of a call have earned it.
A call is live: both agents must be in a session at the same time (the runner runs the pair in
parallel), and words spoken into an open line reach the other agent on its next turn.

  press "call"       no call: rings the partner's phone if the partner is in a session and has
                     a phone, else nobody answers. The partner's phone rang: answers it.
  press "end call"   hangs up (or stops the ringing).
  speak              while the line is open and the phone is in reach, the partner hears it;
                     otherwise it is just said out loud on an empty island.

A ringing phone is heard within 15 m of it (world/paper.py PHONE_EARSHOT), a voice on the line only within 2.5 m
(held or right next to it). Ringing stops after `ring_seconds` of real time unanswered.
Everything the line delivers comes back from `poll`, which the session loop calls each turn.
"""

from __future__ import annotations

import threading
import time


class Switchboard:
    def __init__(self, agents: list[str], ring_seconds: float = 120.0, now=time.monotonic):
        self.partner = {}
        for i in range(0, len(agents) - 1, 2):
            a, b = agents[i], agents[i + 1]
            self.partner[a], self.partner[b] = b, a
        self.ring_seconds = float(ring_seconds)
        self.now = now
        self.lock = threading.Lock()
        self.worlds: dict[str, object] = {}
        self.active: set[str] = set()
        self.calls: dict[frozenset, dict] = {}   # pair -> {"state": "ringing"|"open", "from": agent, "since": t, "rang": bool}
        self.inbox: dict[str, list[tuple[str, str]]] = {}  # agent -> [(kind, text)]

    # ------------------------------------------------------------ sessions
    def attach(self, agent: str, world) -> None:
        world.line = Line(self, agent)
        with self.lock:
            self.worlds[agent] = world

    def start(self, agent: str) -> None:
        with self.lock:
            self.active.add(agent)
            self.inbox[agent] = []

    def stop(self, agent: str) -> None:
        with self.lock:
            self.active.discard(agent)
            self._hang_up(agent)
            self.inbox[agent] = []

    # ------------------------------------------------------------ internals (lock held)
    def _pair(self, agent: str) -> frozenset | None:
        p = self.partner.get(agent)
        return frozenset((agent, p)) if p else None

    def _reach(self, agent: str) -> str | None:
        w = self.worlds.get(agent)
        return w.phone_reach() if w is not None else None

    def _hang_up(self, agent: str) -> bool:
        pair = self._pair(agent)
        call = self.calls.pop(pair, None) if pair else None
        if call and call["state"] == "open":
            self.inbox.setdefault(self.partner[agent], []).append(("line", "The line goes quiet."))
        return call is not None

    def _expire(self, pair: frozenset) -> None:
        call = self.calls.get(pair)
        if call and call["state"] == "ringing" and self.now() - call["since"] > self.ring_seconds:
            del self.calls[pair]
            self.inbox.setdefault(call["from"], []).append(("line", "The phone stops ringing. Nobody answered."))

    # ------------------------------------------------------------ actions
    def press(self, agent: str, button: str) -> str:
        b = " ".join(str(button).lower().replace("_", " ").split())
        with self.lock:
            if self._reach(agent) not in ("hand", "near"):
                return "PressFailed:NothingInReach"
            pair = self._pair(agent)
            if pair:
                self._expire(pair)
            call = self.calls.get(pair) if pair else None
            if b in ("call", "answer", "green"):
                if call is None:
                    p = self.partner.get(agent)
                    if p in self.active and self.worlds[p].has_phone():
                        self.calls[pair] = {"state": "ringing", "from": agent, "since": self.now(), "rang": False}
                        return "PressSuccess:Ringing"
                    return "PressSuccess:NoAnswer"
                if call["state"] == "ringing" and call["from"] != agent:
                    call["state"] = "open"
                    self.inbox.setdefault(call["from"], []).append(("line", "The ringing stops. The line is open."))
                    return "PressSuccess:Connected"
                return "PressSuccess:Ringing" if call["state"] == "ringing" else "PressSuccess:AlreadyConnected"
            if b in ("end call", "end", "hang up", "red"):
                return "PressSuccess:CallEnded" if self._hang_up(agent) else "PressSuccess:NoCall"
            return "PressFailed:NoSuchButton"

    def speak(self, agent: str, text: str) -> str:
        text = str(text)[:1000]
        with self.lock:
            pair = self._pair(agent)
            call = self.calls.get(pair) if pair else None
            if call and call["state"] == "open" and self._reach(agent) in ("hand", "near"):
                self.inbox.setdefault(self.partner[agent], []).append(("voice", text))
                return "SpeakSuccess:IntoPhone"
            return "SpeakSuccess:NobodyHears"

    def poll(self, agent: str) -> list[str]:
        """What the agent hears this turn."""
        with self.lock:
            pair = self._pair(agent)
            if pair:
                self._expire(pair)
            out = []
            reach = self._reach(agent)
            for kind, text in self.inbox.get(agent, []):
                if kind == "voice":
                    if reach in ("hand", "near"):
                        out.append(f'A voice comes from the phone: "{text}"')
                    elif reach == "earshot":
                        out.append("A faint voice comes from the phone, too far away to make out.")
                elif reach is not None:
                    out.append(text)
            self.inbox[agent] = []
            call = self.calls.get(pair) if pair else None
            if call and call["state"] == "ringing" and call["from"] != agent and not call["rang"] and reach is not None:
                call["rang"] = True
                out.append("You hear a phone ringing nearby.")
            return out

    def status(self, agent: str) -> str:
        with self.lock:
            call = self.calls.get(self._pair(agent)) if self._pair(agent) else None
            return "quiet" if call is None else call["state"]


class Line:
    """One agent's end of the switchboard, held by its world."""

    def __init__(self, board: Switchboard, agent: str):
        self.board, self.agent = board, agent

    def press(self, button: str) -> str:
        return self.board.press(self.agent, button)

    def speak(self, text: str) -> str:
        return self.board.speak(self.agent, text)

    def poll(self) -> list[str]:
        return self.board.poll(self.agent)

    def status(self) -> str:
        return self.board.status(self.agent)


class LoggedLine:
    """Replays a logged result code (the replay has no partner on the other end)."""

    def __init__(self, code: str):
        self.code = code

    def press(self, button: str) -> str:
        return self.code

    speak = press

    def poll(self) -> list[str]:
        return []

    def status(self) -> str:
        return "quiet"
