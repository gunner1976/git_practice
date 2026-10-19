"""Entry point: python -m scriptbot [--config config.yaml] [--dry-run] [--force]"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import anthropic

from . import gdoc
from .config import load_config
from .feeds import collect_stories
from .store import Store
from .writer import write_script

log = logging.getLogger("scriptbot")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write today's AI news script to Google Docs.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the script; don't touch Drive or the database")
    parser.add_argument("--force", action="store_true",
                        help="Run even if today's script already exists")
    parser.add_argument("--not-before-hour", type=int, default=None,
                        help="Exit quietly if the local hour is earlier than this")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = load_config(args.config)
    now_local = datetime.now(ZoneInfo(cfg.timezone))
    today = now_local.date()

    if args.not_before_hour is not None and now_local.hour < args.not_before_hour and not args.force:
        log.info("Local time %s is before %02d:00; nothing to do.", now_local.strftime("%H:%M %Z"),
                 args.not_before_hour)
        return 0

    store = Store(cfg.database)
    try:
        if (existing := store.has_run(today)) and not (args.force or args.dry_run):
            log.info("Script for %s already exists: %s", today, existing)
            return 0

        since = datetime.now(timezone.utc) - timedelta(hours=cfg.lookback_hours)
        stories = collect_stories(
            cfg.feeds, since, store.used_keys(),
            timeout=cfg.feed_timeout_seconds,
            summary_chars=cfg.max_summary_chars,
            max_candidates=cfg.max_candidates,
        )
        log.info("%d new candidate stories from the last %dh", len(stories), cfg.lookback_hours)
        if not stories:
            log.error("No unused stories in the lookback window; no script written.")
            return 1

        script = write_script(
            anthropic.Anthropic(), stories, store.recent_titles(today, cfg.recent_history_days), today,
            model=cfg.model, effort=cfg.effort, max_tokens=cfg.max_tokens, top_n=cfg.top_n,
        )
        log.info("Script: %d words, ~%ds", script.word_count, script.est_seconds)

        title = f"{cfg.doc_title_prefix} - {today.isoformat()}"
        if args.dry_run:
            print(f"# {title}: {script.episode_title}\n")
            print(script.spoken_text)
            print("\nSources:")
            for r in script.roundup:
                print(f"- {r.story.title} ({r.story.source}) {r.story.url}")
            return 0

        drive = gdoc.drive_service()
        folder_id = gdoc.find_folder(drive, cfg.folder_name)
        doc_id, doc_url = gdoc.create_doc(drive, folder_id, title, gdoc.render_html(script, today, cfg.timezone))
        store.record_run(today, doc_id, doc_url, script.stories)
        log.info("Created %s", doc_url)
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    sys.exit(main())
