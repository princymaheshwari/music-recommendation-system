"""
Command line runner for the Music Recommender Simulation.

Functions are implemented in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tabulate import tabulate
from recommender import load_songs, recommend_songs, SCORING_STRATEGIES

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SEPARATOR = "=" * 78
THIN_SEP = "-" * 78

# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
        "danceability": 0.75,
        "valence": 0.80,
        "tempo": 0.55,
        "popularity": 75,
        "release_decade": 2020,
        "instrumentalness": 0.10,
        "lyrical_theme": "love",
        "sub_mood": "euphoric",
    },
    "Chill Lofi Listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
        "danceability": 0.55,
        "valence": 0.58,
        "tempo": 0.18,
        "popularity": 40,
        "release_decade": 2020,
        "instrumentalness": 0.85,
        "lyrical_theme": "introspection",
        "sub_mood": "contemplative",
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
        "danceability": 0.65,
        "valence": 0.45,
        "tempo": 0.85,
        "popularity": 55,
        "release_decade": 2010,
        "instrumentalness": 0.20,
        "lyrical_theme": "rebellion",
        "sub_mood": "aggressive",
    },
    "EDGE CASE -- Sad but High-Energy": {
        "genre": "r&b",
        "mood": "sad",
        "energy": 0.90,
        "likes_acoustic": False,
        "danceability": 0.80,
        "valence": 0.30,
        "tempo": 0.70,
        "popularity": 60,
        "release_decade": 2020,
        "instrumentalness": 0.05,
        "lyrical_theme": "loss",
        "sub_mood": "melancholic",
    },
    "EDGE CASE -- Acoustic Electronic": {
        "genre": "electronic",
        "mood": "energetic",
        "energy": 0.85,
        "likes_acoustic": True,
        "danceability": 0.90,
        "valence": 0.75,
        "tempo": 0.65,
        "popularity": 70,
        "release_decade": 2020,
        "instrumentalness": 0.60,
        "lyrical_theme": "empowerment",
        "sub_mood": "euphoric",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REASON_RE = re.compile(r"^(.+?):\s*.+?\s*\(\+(\d+\.\d+)\)$")
_DIVERSITY_RE = re.compile(r"^DIVERSITY:\s*(.+)$")


def _bar(score: float, width: int = 20) -> str:
    """Render a proportional Unicode bar for a 0-1 score."""
    filled = int(score * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _top_reasons(explanation: str, n: int = 3) -> str:
    """Extract the n highest-scoring reason labels from an explanation string."""
    parts = explanation.split("; ")
    scored = []
    diversity_note = ""
    for part in parts:
        dm = _DIVERSITY_RE.match(part)
        if dm:
            diversity_note = f" [DIV: {dm.group(1)}]"
            continue
        m = _REASON_RE.match(part)
        if m:
            scored.append((m.group(1).strip(), float(m.group(2))))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = [f"{lbl} (+{pts:.2f})" for lbl, pts in scored[:n]]
    return "; ".join(top) + diversity_note


# ---------------------------------------------------------------------------
# Display functions
# ---------------------------------------------------------------------------

def display_profile(name: str, prefs: dict) -> None:
    """Print the user taste profile as a two-column table."""
    print(f"\n\n{SEPARATOR}")
    print(f"  PROFILE: {name}")
    print(SEPARATOR)
    rows = [
        ["Genre", prefs["genre"]],
        ["Mood", prefs["mood"]],
        ["Energy", prefs["energy"]],
        ["Acoustic", "Yes" if prefs.get("likes_acoustic") else "No"],
        ["Danceability", prefs.get("danceability", "N/A")],
        ["Valence", prefs.get("valence", "N/A")],
        ["Tempo (norm)", prefs.get("tempo", "N/A")],
        ["Popularity", prefs.get("popularity", "N/A")],
        ["Decade", f"{prefs.get('release_decade', 'N/A')}s"],
        ["Instrumentalness", prefs.get("instrumentalness", "N/A")],
        ["Lyrical Theme", prefs.get("lyrical_theme", "N/A")],
        ["Sub-Mood", prefs.get("sub_mood", "N/A")],
    ]
    print(tabulate(rows, headers=["Preference", "Value"], tablefmt="simple_outline"))


def display_summary_table(recommendations: list, k: int, strategy: str = "") -> None:
    """Print a tabulate-formatted summary table with scores and top reasons."""
    header = f"TOP {k} — Strategy: {strategy.upper()}" if strategy else f"TOP {k}"
    print(f"\n  {header}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            song["genre"],
            f"{score:.4f}",
            _bar(score),
            _top_reasons(explanation),
        ])

    print(tabulate(
        rows,
        headers=["Rank", "Title", "Artist", "Genre", "Score", "Bar", "Top Reasons"],
        tablefmt="simple_grid",
        stralign="left",
    ))


def display_detailed(recommendations: list, strategy: str = "") -> None:
    """Print a per-song feature breakdown table for every recommended song."""
    header = f"FEATURE BREAKDOWN — {strategy.upper()}" if strategy else "FEATURE BREAKDOWN"
    print(f"\n  {header}")
    print(SEPARATOR)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  by  {song['artist']}  "
              f"({song['genre']} / {song['mood']})  —  Score: {score:.4f}")

        parts = explanation.split("; ")
        feature_rows = []
        diversity_row = None
        for part in parts:
            dm = _DIVERSITY_RE.match(part)
            if dm:
                diversity_row = dm.group(1)
                continue
            m = _REASON_RE.match(part)
            if m:
                label = m.group(1)
                pts = float(m.group(2))
                feature_rows.append([label, f"+{pts:.2f}", _bar(pts, 12)])
            else:
                feature_rows.append([part, "", ""])

        print(tabulate(
            feature_rows,
            headers=["Feature", "Points", ""],
            tablefmt="simple_outline",
            stralign="left",
        ))
        if diversity_row:
            print(f"       >>> DIVERSITY: {diversity_row}")

    print(f"\n{SEPARATOR}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run every profile through every scoring strategy and display results."""
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    k = 5
    strategies = list(SCORING_STRATEGIES.keys())

    for name, prefs in PROFILES.items():
        display_profile(name, prefs)
        for strat in strategies:
            recs = recommend_songs(prefs, songs, k=k, strategy=strat)
            display_summary_table(recs, k, strategy=strat)
            display_detailed(recs, strategy=strat)


if __name__ == "__main__":
    main()
