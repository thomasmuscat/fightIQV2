import pandas as pd

def add_initial_elo(fighters_df: pd.DataFrame) -> pd.DataFrame:
    if fighters_df.empty:
        return fighters_df
    if "elo_rating" not in fighters_df.columns:
        fighters_df["elo_rating"] = 1500
    fighters_df["elo_rating"] = fighters_df["elo_rating"].fillna(1500)
    return fighters_df
