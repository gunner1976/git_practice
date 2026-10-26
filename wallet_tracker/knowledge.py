"""Knowledge base: every study run stored as a dated snapshot in SQLite.

One run is a picture of the market; many runs are a history of how capital
behaves. The store keeps, per run: every wallet's class, operator group,
scores and metrics; entities with AUM and sector mix; identities with their
sources; smart-money and all-trader sector flows; migrations; and the
operator x regime matrix. Queries then answer "who is rising", "what is
smart money buying", and "how did this wallet's standing change".
"""

from __future__ import annotations

import json
import math
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY, ts INTEGER, chain_id INTEGER, wallets INTEGER, eligible INTEGER,
  significant INTEGER, luck_sharpe REAL, note TEXT);
CREATE TABLE IF NOT EXISTS wallet_snapshots (
  run_id INTEGER, address TEXT, class TEXT, operator TEXT, eligible INTEGER, rank INTEGER, score REAL,
  significant INTEGER, reputation REAL, tier TEXT, cagr REAL, sharpe REAL, max_drawdown REAL, rrs REAL,
  copy_cagr REAL, human_score REAL, final_equity REAL, entity TEXT, size_tier TEXT, metrics TEXT,
  PRIMARY KEY (run_id, address));
CREATE TABLE IF NOT EXISTS identities (
  address TEXT PRIMARY KEY, name TEXT, kind TEXT, sources TEXT, urls TEXT, first_run INTEGER, last_run INTEGER);
CREATE TABLE IF NOT EXISTS entities (
  run_id INTEGER, entity TEXT, label TEXT, members TEXT, aum REAL, operator TEXT, reputation REAL,
  tier TEXT, smart INTEGER, cagr REAL, sharpe REAL, sectors TEXT, PRIMARY KEY (run_id, entity));
CREATE TABLE IF NOT EXISTS flows (
  run_id INTEGER, cohort TEXT, month TEXT, sector TEXT, usd REAL, PRIMARY KEY (run_id, cohort, month, sector));
CREATE TABLE IF NOT EXISTS migrations (
  source TEXT, destination TEXT, ts INTEGER, usd REAL, share REAL, verified INTEGER, first_run INTEGER,
  PRIMARY KEY (source, destination, ts));
CREATE TABLE IF NOT EXISTS regime_matrix (
  run_id INTEGER, operator TEXT, regime TEXT, median_excess REAL, n INTEGER,
  PRIMARY KEY (run_id, operator, regime));
CREATE INDEX IF NOT EXISTS ws_addr ON wallet_snapshots(address);
"""


def _clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def entity_key(members: list[str]) -> str:
    """Stable-ish id across runs: the entity's lowest member address."""
    return "e:" + min(members)


class KnowledgeBase:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    # ------------------------------------------------------------- ingest
    def record(self, study, chain_id: int = 1, note: str = "", ts: int | None = None) -> int:
        lb = study.boards
        cur = self.db.execute(
            "INSERT INTO runs (ts, chain_id, wallets, eligible, significant, luck_sharpe, note) VALUES (?,?,?,?,?,?,?)",
            (ts or int(time.time()), chain_id, len(study.reports), len(lb.active),
             sum(1 for r in lb.active if r.metrics.get("significant")), lb.luck_sharpe, note))
        run = cur.lastrowid
        ent_of = {a: entity_key(e.members) for e in study.entities for a in e.members}
        for r in study.reports:
            m = r.metrics
            rep = r.reputation
            self.db.execute(
                "INSERT INTO wallet_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (run, r.address, r.wallet_class.value, r.group, int(r.eligible), r.rank or None, r.score,
                 int(bool(m.get("significant"))), rep.score if rep else None, rep.tier if rep else None,
                 _clean(m.get("cagr")), _clean(m.get("sharpe")), _clean(m.get("max_drawdown")),
                 _clean(m.get("regime_robustness")), _clean(m.get("copy_cagr")),
                 r.operator.get("human_score"), m.get("final_equity_usd"), ent_of.get(r.address), r.size_tier,
                 json.dumps({k: _clean(v) for k, v in m.items()})))
            ident = r.identity
            if ident is not None and ident.attested:
                self.db.execute(
                    """INSERT INTO identities VALUES (?,?,?,?,?,?,?)
                       ON CONFLICT(address) DO UPDATE SET name=excluded.name, kind=excluded.kind,
                       sources=excluded.sources, urls=excluded.urls, last_run=excluded.last_run""",
                    (r.address, ident.name, ident.kind, json.dumps(ident.sources), json.dumps(ident.urls), run, run))
        for e in study.entities:
            self.db.execute("INSERT INTO entities VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (run, entity_key(e.members), e.label, json.dumps(e.members), e.aum_usd, e.group,
                             e.reputation, e.tier, int(e.smart), _clean(e.cagr), _clean(e.sharpe),
                             json.dumps(e.sectors_avg)))
        for cohort, table in (("smart", study.flows_smart), ("all", study.flows_all)):
            for month, secs in table.items():
                for sector, usd in secs.items():
                    self.db.execute("INSERT INTO flows VALUES (?,?,?,?,?)", (run, cohort, month, sector, usd))
        for mg in study.migrations:
            self.db.execute("INSERT OR IGNORE INTO migrations VALUES (?,?,?,?,?,?,?)",
                            (mg.source, mg.destination, mg.timestamp, mg.usd, mg.share, int(mg.verified), run))
        for group, cells in study.operator_regime.items():
            for regime, c in cells.items():
                self.db.execute("INSERT INTO regime_matrix VALUES (?,?,?,?,?)",
                                (run, group, regime, c["median_excess"], c["n"]))
        self.db.commit()
        return run

    # ------------------------------------------------------------- queries
    def runs(self) -> list[tuple]:
        return self.db.execute("SELECT id, ts, wallets, eligible, significant, luck_sharpe, note "
                               "FROM runs ORDER BY id").fetchall()

    def latest_run(self) -> int | None:
        row = self.db.execute("SELECT MAX(id) FROM runs").fetchone()
        return row[0] if row else None

    def top(self, limit: int = 25, run: int | None = None) -> list[tuple]:
        """Ranked wallets in a run, with their rank in the previous run (None = new)."""
        run = run or self.latest_run()
        prev = self.db.execute("SELECT MAX(id) FROM runs WHERE id < ?", (run,)).fetchone()[0]
        return self.db.execute("""
            SELECT w.rank, w.address, w.score, w.significant, w.tier, w.reputation, w.operator, w.cagr,
                   w.sharpe, w.rrs, w.copy_cagr, p.rank, i.name
            FROM wallet_snapshots w
            LEFT JOIN wallet_snapshots p ON p.address = w.address AND p.run_id = ?
            LEFT JOIN identities i ON i.address = w.address
            WHERE w.run_id = ? AND w.eligible = 1 ORDER BY w.rank LIMIT ?""", (prev, run, limit)).fetchall()

    def wallet(self, address: str) -> list[tuple]:
        return self.db.execute("""
            SELECT r.id, r.ts, w.class, w.rank, w.score, w.significant, w.tier, w.reputation, w.cagr, w.sharpe,
                   w.final_equity
            FROM wallet_snapshots w JOIN runs r ON r.id = w.run_id
            WHERE w.address = ? ORDER BY r.id""", (address.lower(),)).fetchall()

    def flows(self, cohort: str = "smart", months: int = 6) -> dict[str, dict[str, float]]:
        """Latest known value for each month (later runs supersede earlier ones)."""
        rows = self.db.execute("""
            SELECT f.month, f.sector, f.usd FROM flows f
            JOIN (SELECT month, MAX(run_id) AS run_id FROM flows WHERE cohort = ? GROUP BY month) last
              ON last.month = f.month AND last.run_id = f.run_id
            WHERE f.cohort = ?""", (cohort, cohort)).fetchall()
        out: dict[str, dict[str, float]] = {}
        for month, sector, usd in rows:
            out.setdefault(month, {})[sector] = usd
        keep = sorted(out)[-months:]
        return {m: out[m] for m in keep}

    def movers(self) -> dict[str, list[tuple]]:
        """New entrants, drop-outs and the biggest rank changes between the last two runs."""
        run = self.latest_run()
        prev = self.db.execute("SELECT MAX(id) FROM runs WHERE id < ?", (run,)).fetchone()[0]
        if prev is None:
            return {"new": [], "dropped": [], "moved": []}
        q = """SELECT address, rank FROM wallet_snapshots WHERE run_id = ? AND eligible = 1"""
        now = dict(self.db.execute(q, (run,)).fetchall())
        before = dict(self.db.execute(q, (prev,)).fetchall())
        moved = sorted(((a, before[a], now[a]) for a in now.keys() & before.keys()),
                       key=lambda x: abs(x[1] - x[2]), reverse=True)
        return {"new": sorted(((a, now[a]) for a in now.keys() - before.keys()), key=lambda x: x[1]),
                "dropped": sorted(((a, before[a]) for a in before.keys() - now.keys()), key=lambda x: x[1]),
                "moved": [m for m in moved if m[1] != m[2]][:20]}
