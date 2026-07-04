from __future__ import annotations
from datetime import datetime
import pandas as pd

from analytics.elo import add_initial_elo
from config import EXPORT_DIR, LOG_DIR, UPLOAD_TO_SUPABASE
from database.exporter import write_csv, write_report
from database.supabase_client import upsert_dataframe
from scraper.events import scrape_events
from scraper.fighters import scrape_fighters
from scraper.fights import scrape_fights

def main():
    EXPORT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    report = {"started_at": datetime.utcnow().isoformat(), "upload_to_supabase": UPLOAD_TO_SUPABASE}

    fighters = add_initial_elo(scrape_fighters(include_details=True))
    write_csv("fighters", fighters)
    report["fighters"] = len(fighters)

    events = scrape_events()
    write_csv("events", events)
    report["events"] = len(events)

    fights, fight_stats = scrape_fights(events, fighters)
    write_csv("fights", fights)
    write_csv("fight_stats", fight_stats)
    report["fights"] = len(fights)
    report["fight_stats"] = len(fight_stats)

    rankings = pd.DataFrame(columns=["id", "fighter_id", "division", "rank", "ranking_date", "data_source"])
    predictions = pd.DataFrame(columns=[
        "id", "fighter_a_id", "fighter_b_id", "fighter_a_win_probability",
        "fighter_b_win_probability", "ko_probability", "submission_probability",
        "decision_probability", "confidence_score", "explanation",
        "engine_version", "data_source"
    ])
    write_csv("rankings", rankings)
    write_csv("predictions", predictions)

    if UPLOAD_TO_SUPABASE:
        upsert_dataframe("fighters", fighters)
        upsert_dataframe("events", events)
        upsert_dataframe("fights", fights)
        upsert_dataframe("fight_stats", fight_stats)

    report["finished_at"] = datetime.utcnow().isoformat()
    write_report(report)
    print("[done]", report)

if __name__ == "__main__":
    main()
