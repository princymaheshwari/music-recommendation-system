"""
Command line runner for the Music Recommender Simulation.

Functions are implemented in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recommender import load_songs, recommend_songs

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SEPARATOR = "=" * 62
THIN_SEP = "-" * 62

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
# Display helpers
# ---------------------------------------------------------------------------

def display_profile(name: str, prefs: dict) -> None:
    """Print the user taste profile header."""
    print(f"\n\n{SEPARATOR}")
    print(f"  PROFILE: {name}")
    print(SEPARATOR)
    print(f"  Genre:            {prefs['genre']}")
    print(f"  Mood:             {prefs['mood']}")
    print(f"  Energy:           {prefs['energy']}")
    print(f"  Acoustic:         {'Yes' if prefs.get('likes_acoustic') else 'No'}")
    print(f"  Danceability:     {prefs.get('danceability', 'N/A')}")
    print(f"  Valence:          {prefs.get('valence', 'N/A')}")
    print(f"  Tempo (norm):     {prefs.get('tempo', 'N/A')}")
    print(f"  Popularity:       {prefs.get('popularity', 'N/A')}")
    print(f"  Decade:           {prefs.get('release_decade', 'N/A')}s")
    print(f"  Instrumentalness: {prefs.get('instrumentalness', 'N/A')}")
    print(f"  Lyrical Theme:    {prefs.get('lyrical_theme', 'N/A')}")
    print(f"  Sub-Mood:         {prefs.get('sub_mood', 'N/A')}")
    print(SEPARATOR)


def display_quick_ranking(recommendations: list, k: int) -> None:
    """Print a compact ranked list showing only title, artist, and score."""
    print(f"\n  TOP {k} AT A GLANCE")
    print(THIN_SEP)
    for rank, (song, score, _) in enumerate(recommendations, start=1):
        bar = "#" * int(score * 30)
        print(f"  #{rank}  {song['title']:.<30s} {score:.4f}  {bar}")
    print(THIN_SEP)


def display_detailed(recommendations: list) -> None:
    """Print the full per-feature breakdown for every recommended song."""
    print(f"\n  DETAILED BREAKDOWN")
    print(SEPARATOR)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  by  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Score: {score:.4f}")
        print(f"       {THIN_SEP}")

        reasons = explanation.split("; ")
        for reason in reasons:
            print(f"         {reason}")

    print(f"\n{SEPARATOR}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the recommender for every profile and display results."""
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    k = 5

    for name, prefs in PROFILES.items():
        display_profile(name, prefs)
        recs = recommend_songs(prefs, songs, k=k)
        display_quick_ranking(recs, k)
        display_detailed(recs)


if __name__ == "__main__":
    main()
