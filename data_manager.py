import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "performance_data.csv")

class DataManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.columns = ["Date","Player","Sport","Duration","Distance","Speed","Calories","Goals","Assists","Stamina","Notes"]
        if not os.path.exists(DATA_FILE):
            pd.DataFrame(columns=self.columns).to_csv(DATA_FILE, index=False)
        self.df = pd.read_csv(DATA_FILE, parse_dates=["Date"], dayfirst=False)
        self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")

    def refresh_data(self):
        """Reload data from CSV file to ensure freshness"""
        if os.path.exists(DATA_FILE):
            self.df = pd.read_csv(DATA_FILE, parse_dates=["Date"], dayfirst=False)
            self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")

    def add_performance(self, rec: dict):
        # rec: Date (str)/Player/Sport/Duration/Distance/Speed/Calories/Goals/Assists/Stamina/Notes
        row = {c: "" for c in self.columns}
        row.update({k: rec.get(k, "") for k in rec})
        # Date normalization
        if not row["Date"]:
            row["Date"] = datetime.now()
        else:
            row["Date"] = pd.to_datetime(row["Date"], errors="coerce")
        # numeric safe conversions
        try:
            duration = float(row.get("Duration") or 0)
        except:
            duration = 0.0
        try:
            distance = float(row.get("Distance") or 0)
        except:
            distance = 0.0
        try:
            speed = float(row.get("Speed")) if row.get("Speed") not in (None, "", "N/A") else None
        except:
            speed = None
        try:
            calories = float(row.get("Calories") or 0)
        except:
            calories = 0.0

        sport = str(row.get("Sport") or "").strip()

        # compute speed for Running/Swimming when missing (km/h)
        if sport in ("Running","Swimming") and (not speed) and duration > 0:
            hrs = duration / 60.0
            speed = (distance / hrs) if hrs > 0 else 0.0

        row["Speed"] = round(float(speed or 0.0), 2)
        row["Duration"] = round(duration, 2)
        row["Distance"] = round(distance, 3)
        row["Calories"] = round(calories, 1)

        if sport == "Football":
            try:
                row["Goals"] = int(rec.get("Goals") or 0)
            except:
                row["Goals"] = 0
            try:
                row["Assists"] = int(rec.get("Assists") or 0)
            except:
                row["Assists"] = 0
            try:
                row["Stamina"] = float(rec.get("Stamina") or 0)
            except:
                row["Stamina"] = 0
        else:
            row["Goals"] = ""
            row["Assists"] = ""
            row["Stamina"] = ""

        row["Player"] = rec.get("Player", "").strip()
        row["Notes"] = rec.get("Notes", "")

        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
        self._save()
        return row

    def _save(self):
        # ensure folder exists and write CSV
        os.makedirs(DATA_DIR, exist_ok=True)
        self.df.to_csv(DATA_FILE, index=False, date_format="%Y-%m-%d")

    def get_players(self):
        return sorted(self.df["Player"].dropna().unique().tolist())

    def get_sports(self):
        return sorted(self.df["Sport"].dropna().unique().tolist())

    def get_players_for_sport(self, sport: str):
        """Return sorted unique players who have records for the given sport.
        If sport is falsy or 'All', return all players.
        """
        if not sport or sport == "All":
            return self.get_players()
        df = self.df[self.df["Sport"] == sport]
        return sorted(df["Player"].dropna().unique().tolist())

    def get_player_sport_df(self, player, sport):
        df = self.df[(self.df["Player"] == player) & (self.df["Sport"] == sport)].copy()
        df = df.sort_values("Date")
        return df

    def get_latest_for_player_sport(self, player, sport):
        df = self.get_player_sport_df(player, sport)
        if df.empty:
            return None
        return df.iloc[-1].to_dict()

    def aggregate_stats_for_player_sport(self, player, sport):
        df = self.get_player_sport_df(player, sport)
        if df.empty:
            return {"sessions":0, "total_duration":0, "total_distance":0, "avg_speed":0, "last_date": None}
        sessions = len(df)
        total_duration = float(df["Duration"].sum())
        total_distance = float(df["Distance"].sum())
        # avoid empty speed column
        try:
            avg_speed = float(df["Speed"].replace("",0).astype(float).mean())
        except:
            avg_speed = 0.0
        last_date = df["Date"].max()
        return {"sessions": sessions, "total_duration": total_duration, "total_distance": total_distance, "avg_speed": round(avg_speed,2), "last_date": last_date}

    def get_all_data(self):
        return self.df.copy()