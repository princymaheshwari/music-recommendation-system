"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

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


def display_profile(prefs: dict) -> None:
    """Print the user taste profile in a readable format."""
    print(SEPARATOR)
    print("  USER TASTE PROFILE")
    print(SEPARATOR)
    print(f"  Genre:        {prefs['genre']}")
    print(f"  Mood:         {prefs['mood']}")
    print(f"  Energy:       {prefs['energy']}")
    print(f"  Acoustic:     {'Yes' if prefs.get('likes_acoustic') else 'No'}")
    print(f"  Danceability: {prefs.get('danceability', 'N/A')}")
    print(f"  Valence:      {prefs.get('valence', 'N/A')}")
    print(f"  Tempo (norm): {prefs.get('tempo', 'N/A')}")
    print(SEPARATOR)


def display_recommendations(recommendations: list, k: int) -> None:
    """Print the top-k recommendations in a clean terminal layout."""
    print(f"\n  TOP {k} RECOMMENDATIONS")
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


def main() -> None:
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
        "danceability": 0.75,
        "valence": 0.80,
        "tempo": 0.55,
    }

    k = 5
    display_profile(user_prefs)
    recommendations = recommend_songs(user_prefs, songs, k=k)
    display_recommendations(recommendations, k)


if __name__ == "__main__":
    main()
