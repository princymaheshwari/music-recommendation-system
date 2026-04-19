import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness"}
INT_FIELDS = {"id", "tempo_bpm"}

WEIGHTS = {
    "genre": 0.25,
    "mood": 0.20,
    "energy": 0.18,
    "acousticness": 0.13,
    "danceability": 0.10,
    "valence": 0.08,
    "tempo": 0.06,
}

TEMPO_MIN = 56
TEMPO_MAX = 168


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in FLOAT_FIELDS:
                row[field] = float(row[field])
            for field in INT_FIELDS:
                row[field] = int(row[field])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def _normalize_tempo(bpm: float) -> float:
    """Convert raw BPM to a 0-1 scale using the catalog's range."""
    return (bpm - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    # --- Genre (categorical, binary match) ---
    genre_sim = 1.0 if song["genre"] == user_prefs["genre"] else 0.0
    genre_pts = WEIGHTS["genre"] * genre_sim
    score += genre_pts
    label = "match" if genre_sim == 1.0 else "mismatch"
    reasons.append(f"genre {label}: {song['genre']} (+{genre_pts:.2f})")

    # --- Mood (categorical, binary match) ---
    mood_sim = 1.0 if song["mood"] == user_prefs["mood"] else 0.0
    mood_pts = WEIGHTS["mood"] * mood_sim
    score += mood_pts
    label = "match" if mood_sim == 1.0 else "mismatch"
    reasons.append(f"mood {label}: {song['mood']} (+{mood_pts:.2f})")

    # --- Energy (numeric, proximity) ---
    energy_sim = 1.0 - abs(user_prefs["energy"] - song["energy"])
    energy_pts = WEIGHTS["energy"] * energy_sim
    score += energy_pts
    reasons.append(f"energy proximity: {energy_sim:.2f} (+{energy_pts:.2f})")

    # --- Acousticness (directional based on boolean preference) ---
    if user_prefs.get("likes_acoustic", False):
        acoustic_sim = song["acousticness"]
    else:
        acoustic_sim = 1.0 - song["acousticness"]
    acoustic_pts = WEIGHTS["acousticness"] * acoustic_sim
    score += acoustic_pts
    reasons.append(f"acoustic preference: {acoustic_sim:.2f} (+{acoustic_pts:.2f})")

    # --- Danceability (numeric, proximity) ---
    dance_sim = 1.0 - abs(user_prefs.get("danceability", 0.5) - song["danceability"])
    dance_pts = WEIGHTS["danceability"] * dance_sim
    score += dance_pts
    reasons.append(f"danceability proximity: {dance_sim:.2f} (+{dance_pts:.2f})")

    # --- Valence (numeric, proximity) ---
    valence_sim = 1.0 - abs(user_prefs.get("valence", 0.5) - song["valence"])
    valence_pts = WEIGHTS["valence"] * valence_sim
    score += valence_pts
    reasons.append(f"valence proximity: {valence_sim:.2f} (+{valence_pts:.2f})")

    # --- Tempo (normalized numeric, proximity) ---
    song_tempo_norm = _normalize_tempo(song["tempo_bpm"])
    user_tempo_norm = user_prefs.get("tempo", 0.5)
    tempo_sim = 1.0 - abs(user_tempo_norm - song_tempo_norm)
    tempo_pts = WEIGHTS["tempo"] * tempo_sim
    score += tempo_pts
    reasons.append(f"tempo proximity: {tempo_sim:.2f} (+{tempo_pts:.2f})")

    return (round(score, 4), reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    return [
        (song, score, "; ".join(reasons))
        for song, score, reasons in ranked[:k]
    ]
