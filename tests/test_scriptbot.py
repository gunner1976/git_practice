import json
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from scriptbot import gdoc
from scriptbot.config import Feed, load_config
from scriptbot.feeds import collect_stories
from scriptbot.store import Store, normalize_url
from scriptbot.writer import ScriptError, parse_script, write_script

NOW = datetime.now(timezone.utc)


def rss(*items):
    body = "".join(
        f"<item><title>{t}</title><link>{u}</link>"
        f"<pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>"
        f"<description>&lt;p&gt;About {t}&lt;/p&gt;</description></item>"
        for t, u, d in items
    )
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>{body}</channel></rss>'.encode()


def test_normalize_url_strips_tracking_and_www():
    assert normalize_url("http://www.Example.com/a/?utm_source=x&id=2#frag") == "https://example.com/a?id=2"


def test_collect_filters_window_used_and_duplicates():
    feeds = [Feed("A", "a"), Feed("B", "b"), Feed("Broken", "c")]
    content = {
        "a": rss(
            ("Fresh story", "https://a.com/1", NOW - timedelta(hours=2)),
            ("Old story", "https://a.com/2", NOW - timedelta(hours=30)),
            ("Used story", "https://a.com/3", NOW - timedelta(hours=1)),
        ),
        "b": rss(("Fresh Story!", "https://b.com/9", NOW - timedelta(hours=3)),
                 ("Other news", "https://b.com/1?utm_campaign=z", NOW - timedelta(hours=4))),
    }

    def fetch(feed, timeout):
        if feed.url == "c":
            raise OSError("boom")
        return content[feed.url]

    stories = collect_stories(feeds, NOW - timedelta(hours=24), {normalize_url("https://a.com/3")}, fetch=fetch)
    assert [s.title for s in stories] == ["Fresh story", "Other news"]
    assert stories[0].summary == "About Fresh story"
    assert all(s.id.startswith("s") for s in stories)


def test_collect_raises_when_every_feed_fails():
    def fetch(feed, timeout):
        raise OSError("down")

    with pytest.raises(RuntimeError):
        collect_stories([Feed("A", "a")], NOW, set(), fetch=fetch)


def make_stories(n):
    def fetch(feed, timeout):
        return rss(*[(f"Story {i}", f"https://x.com/{i}", NOW - timedelta(minutes=i)) for i in range(n)])

    return collect_stories([Feed("X", "x")], NOW - timedelta(hours=24), set(), fetch=fetch)


def model_output(stories, ids=None):
    ids = ids or [s.id for s in stories[:5]]
    return {
        "episode_title": "AI news",
        "ranking": [{"id": i, "why": "big"} for i in ids],
        "hook": "Hook line.",
        "roundup": [{"id": i, "line": f"Line {i}."} for i in ids],
        "take": {"id": ids[0], "text": "My take."},
        "signoff": "Bye, says the robot.",
    }


def test_parse_script_drops_hallucinated_ids():
    stories = make_stories(8)
    data = model_output(stories, [stories[0].id, "bogus", stories[1].id, stories[1].id])
    script = parse_script(data, stories, 5)
    assert [r.story.id for r in script.roundup] == [stories[0].id, stories[1].id]
    assert script.word_count > 0

    with pytest.raises(ScriptError):
        parse_script(model_output(stories, ["nope"]), stories, 5)


class FakeClient:
    def __init__(self, payload, stop_reason="end_turn"):
        self.calls = []
        response = SimpleNamespace(
            _request_id="req_1", model="claude-opus-5-5", stop_reason=stop_reason, stop_details=None,
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
            content=[SimpleNamespace(type="text", text=json.dumps(payload))],
        )
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: self.calls.append(kw) or response))


def test_write_script_request_and_refusal():
    stories = make_stories(6)
    client = FakeClient(model_output(stories))
    script = write_script(client, stories, ["Old title"], date(2026, 10, 19),
                          model="claude-opus-5-5", effort="high", max_tokens=16000, top_n=5)
    assert len(script.roundup) == 5
    call = client.calls[0]
    assert call["fallbacks"] == "default"
    assert call["output_config"]["format"]["type"] == "json_schema"
    assert "Old title" in call["messages"][0]["content"]

    with pytest.raises(ScriptError):
        write_script(FakeClient({}, stop_reason="refusal"), stories, [], date(2026, 10, 19),
                     model="m", effort="high", max_tokens=10, top_n=5)


def test_store_round_trip(tmp_path):
    store = Store(tmp_path / "db.sqlite")
    stories = make_stories(2)
    day = date(2026, 10, 19)
    assert store.has_run(day) is None
    store.record_run(day, "doc1", "https://docs/1", stories)
    assert store.has_run(day) == "https://docs/1"
    assert normalize_url(stories[0].url) in store.used_keys()
    assert set(store.recent_titles(day, 7)) == {s.title for s in stories}
    store.record_run(day, "doc2", "https://docs/2", stories)  # --force rerun
    assert store.has_run(day) == "https://docs/2"


def test_render_html_escapes_and_links():
    stories = make_stories(5)
    stories[0].title = "A <b>bold</b> & claim"
    script = parse_script(model_output(stories), stories, 5)
    out = gdoc.render_html(script, date(2026, 10, 19), "America/Edmonton")
    assert "A &lt;b&gt;bold&lt;/b&gt; &amp; claim" in out
    assert out.count('href="https://x.com/') == 11  # 5 roundup + 5 sources + take


def test_repo_config_loads():
    cfg = load_config("config.yaml")
    assert cfg.timezone == "America/Edmonton" and cfg.folder_name == "AI Channel Scripts"
    assert len(cfg.feeds) >= 5
