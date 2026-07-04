from __future__ import annotations
import pandas as pd
from config import MAX_EVENTS
from scraper.http import soup_from_url
from utils import clean_text, slugify, stable_uuid, to_int

def parse_event_fights(event: dict, fighter_lookup: dict[str, str]) -> tuple[list[dict], list[dict]]:
    url = event.get("ufcstats_url")
    if not url:
        return [], []
    soup = soup_from_url(url)
    rows = soup.select("tr.b-fight-details__table-row")
    fights = []
    stats = []
    for index, row in enumerate(rows):
        cols = row.select("td")
        if len(cols) < 10:
            continue
        fighter_links = cols[1].select("a")
        names = [clean_text(a.get_text(" ", strip=True)) for a in fighter_links]
        names = [n for n in names if n]
        if len(names) < 2:
            continue
        red_name, blue_name = names[0], names[1]
        red_slug, blue_slug = slugify(red_name), slugify(blue_name)
        red_id = fighter_lookup.get(red_slug, stable_uuid("fighter", red_slug))
        blue_id = fighter_lookup.get(blue_slug, stable_uuid("fighter", blue_slug))
        result_text = clean_text(cols[0].get_text(" ", strip=True))
        winner_id = red_id if result_text and "win" in result_text.lower() else None
        weight_class = clean_text(cols[6].get_text(" ", strip=True)) if len(cols) > 6 else None
        method = clean_text(cols[7].get_text(" ", strip=True)) if len(cols) > 7 else None
        round_num = to_int(cols[8].get_text(" ", strip=True)) if len(cols) > 8 else None
        time_text = clean_text(cols[9].get_text(" ", strip=True)) if len(cols) > 9 else None
        fight_slug = slugify(f"{event['slug']}-{red_slug}-vs-{blue_slug}")
        fight_id = stable_uuid("fight", fight_slug)
        fights.append({
            "id": fight_id,
            "event_id": event["id"],
            "fighter_red_id": red_id,
            "fighter_blue_id": blue_id,
            "winner_id": winner_id,
            "weight_class": weight_class,
            "method": method,
            "round": round_num,
            "time": time_text,
            "is_title_fight": False,
            "is_main_event": index == 0,
            "data_source": "ufcstats_github_actions",
        })
    return fights, stats

def scrape_fights(events_df: pd.DataFrame, fighters_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    fighter_lookup = {row.slug: row.id for row in fighters_df.itertuples()} if not fighters_df.empty else {}
    events = events_df.to_dict("records")
    if MAX_EVENTS:
        events = events[:int(MAX_EVENTS)]
    all_fights, all_stats = [], []
    for i, event in enumerate(events, start=1):
        print(f"[fights] event {i}/{len(events)} {event.get('name')}")
        try:
            fights, stats = parse_event_fights(event, fighter_lookup)
            all_fights.extend(fights)
            all_stats.extend(stats)
            print(f"[fights] found={len(fights)}")
        except Exception as exc:
            print(f"[fights] failed {event.get('name')}: {exc}")
    fights_df = pd.DataFrame(all_fights)
    stats_df = pd.DataFrame(all_stats)
    if not fights_df.empty:
        fights_df = fights_df.drop_duplicates("id").reset_index(drop=True)
    return fights_df, stats_df
