from __future__ import annotations
from bs4 import BeautifulSoup
import pandas as pd
from config import FIGHTERS_URL, LETTERS, MAX_FIGHTERS
from scraper.http import soup_from_url
from utils import clean_text, height_to_cm, parse_date, reach_to_cm, slugify, stable_uuid, to_float, to_int

def parse_fighter_list_page(soup: BeautifulSoup) -> list[dict]:
    rows = soup.select("tr.b-statistics__table-row")
    fighters = []
    for row in rows:
        cols = row.select("td")
        if len(cols) < 11:
            continue
        first_link = cols[0].select_one("a")
        last_link = cols[1].select_one("a")
        first = clean_text(first_link.get_text(" ", strip=True) if first_link else cols[0].get_text(" ", strip=True))
        last = clean_text(last_link.get_text(" ", strip=True) if last_link else cols[1].get_text(" ", strip=True))
        if not first or not last:
            continue
        full_name = f"{first} {last}"
        slug = slugify(full_name)
        fighters.append({
            "id": stable_uuid("fighter", slug),
            "full_name": full_name,
            "nickname": None,
            "slug": slug,
            "nationality": None,
            "country_code": None,
            "date_of_birth": None,
            "stance": clean_text(cols[6].get_text(" ", strip=True)),
            "height_cm": height_to_cm(cols[3].get_text(" ", strip=True)),
            "reach_cm": reach_to_cm(cols[5].get_text(" ", strip=True)),
            "weight_class": None,
            "wins": to_int(cols[7].get_text(" ", strip=True)),
            "losses": to_int(cols[8].get_text(" ", strip=True)),
            "draws": to_int(cols[9].get_text(" ", strip=True)),
            "no_contests": 0,
            "wins_ko": None,
            "wins_sub": None,
            "wins_decision": None,
            "losses_ko": None,
            "losses_sub": None,
            "losses_decision": None,
            "slpm": None,
            "sapm": None,
            "strike_accuracy": None,
            "strike_defense": None,
            "takedown_avg": None,
            "takedown_accuracy": None,
            "takedown_defense": None,
            "submission_avg": None,
            "elo_rating": 1500,
            "current_rank": None,
            "is_champion": False,
            "is_active": True,
            "photo_url": None,
            "ufcstats_url": first_link.get("href") if first_link else None,
            "data_source": "ufcstats_github_actions",
        })
    return fighters

def parse_detail_page(url: str) -> dict:
    soup = soup_from_url(url)
    detail = {}
    nickname = soup.select_one(".b-content__Nickname")
    if nickname:
        detail["nickname"] = clean_text(nickname.get_text(" ", strip=True))
    for item in soup.select(".b-list__box-list-item"):
        text = clean_text(item.get_text(" ", strip=True))
        if not text or ":" not in text:
            continue
        key, value = text.split(":", 1)
        key = key.lower().strip()
        value = clean_text(value)
        if "height" in key:
            detail["height_cm"] = height_to_cm(value)
        elif "reach" in key:
            detail["reach_cm"] = reach_to_cm(value)
        elif "stance" in key:
            detail["stance"] = value
        elif "dob" in key:
            detail["date_of_birth"] = parse_date(value)
        elif "slpm" in key:
            detail["slpm"] = to_float(value)
        elif "sapm" in key:
            detail["sapm"] = to_float(value)
        elif "str. acc" in key:
            detail["strike_accuracy"] = to_float(value)
        elif "str. def" in key:
            detail["strike_defense"] = to_float(value)
        elif "td avg" in key:
            detail["takedown_avg"] = to_float(value)
        elif "td acc" in key:
            detail["takedown_accuracy"] = to_float(value)
        elif "td def" in key:
            detail["takedown_defense"] = to_float(value)
        elif "sub. avg" in key:
            detail["submission_avg"] = to_float(value)
    return detail

def scrape_fighters(include_details: bool = True) -> pd.DataFrame:
    all_fighters, seen = [], set()
    for letter in LETTERS:
        url = FIGHTERS_URL.format(char=letter)
        print(f"[fighters] {letter.upper()} {url}")
        soup = soup_from_url(url)
        found = parse_fighter_list_page(soup)
        print(f"[fighters] found={len(found)}")
        for fighter in found:
            if fighter["slug"] not in seen:
                seen.add(fighter["slug"])
                all_fighters.append(fighter)

    limit = int(MAX_FIGHTERS) if MAX_FIGHTERS else len(all_fighters)
    if include_details:
        for i, fighter in enumerate(all_fighters[:limit], start=1):
            if not fighter.get("ufcstats_url"):
                continue
            print(f"[fighters] detail {i}/{limit} {fighter['full_name']}")
            try:
                detail = parse_detail_page(fighter["ufcstats_url"])
                for key, value in detail.items():
                    if value is not None:
                        fighter[key] = value
            except Exception as exc:
                print(f"[fighters] detail failed {fighter['full_name']}: {exc}")

    df = pd.DataFrame(all_fighters)
    if not df.empty:
        df = df.drop_duplicates("slug").sort_values("full_name").reset_index(drop=True)
    return df
