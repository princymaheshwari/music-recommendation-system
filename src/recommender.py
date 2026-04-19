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
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.5
    lyrical_theme: str = ""
    sub_mood: str = ""

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

FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness", "instrumentalness"}
INT_FIELDS = {"id", "tempo_bpm", "popularity", "release_decade"}

SCORING_STRATEGIES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 0.20, "mood": 0.14, "energy": 0.12, "acousticness": 0.09,
        "danceability": 0.07, "valence": 0.06, "tempo": 0.04,
        "popularity": 0.08, "release_decade": 0.06, "instrumentalness": 0.05,
        "lyrical_theme": 0.05, "sub_mood": 0.04,
    },
    "genre-first": {
        "genre": 0.40, "mood": 0.10, "energy": 0.06, "acousticness": 0.05,
        "danceability": 0.04, "valence": 0.03, "tempo": 0.02,
        "popularity": 0.08, "release_decade": 0.06, "instrumentalness": 0.04,
        "lyrical_theme": 0.08, "sub_mood": 0.04,
    },
    "mood-first": {
        "genre": 0.08, "mood": 0.30, "energy": 0.06, "acousticness": 0.05,
        "danceability": 0.04, "valence": 0.08, "tempo": 0.03,
        "popularity": 0.06, "release_decade": 0.04, "instrumentalness": 0.04,
        "lyrical_theme": 0.10, "sub_mood": 0.12,
    },
    "energy-focused": {
        "genre": 0.06, "mood": 0.06, "energy": 0.25, "acousticness": 0.12,
        "danceability": 0.15, "valence": 0.04, "tempo": 0.12,
        "popularity": 0.04, "release_decade": 0.03, "instrumentalness": 0.05,
        "lyrical_theme": 0.04, "sub_mood": 0.04,
    },
}

DEFAULT_STRATEGY = "balanced"
WEIGHTS = SCORING_STRATEGIES[DEFAULT_STRATEGY]

TEMPO_MIN = 56
TEMPO_MAX = 168
POPULARITY_MAX = 100
DECADE_OPTIONS = [1980, 1990, 2000, 2010, 2020]


def load_songs(csv_path: str) -> List[Dict]:
    """Parse songs.csv into a list of dicts with numeric fields converted to int/float."""
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


def score_song(
    user_prefs: Dict, song: Dict, strategy: str = DEFAULT_STRATEGY
) -> Tuple[float, List[str]]:
    """Return a (score, reasons) tuple using the given scoring strategy's weights."""
    w = SCORING_STRATEGIES[strategy]
    score = 0.0
    reasons: List[str] = []

    genre_sim = 1.0 if song["genre"] == user_prefs["genre"] else 0.0
    genre_pts = w["genre"] * genre_sim
    score += genre_pts
    label = "match" if genre_sim == 1.0 else "mismatch"
    reasons.append(f"genre {label}: {song['genre']} (+{genre_pts:.2f})")

    mood_sim = 1.0 if song["mood"] == user_prefs["mood"] else 0.0
    mood_pts = w["mood"] * mood_sim
    score += mood_pts
    label = "match" if mood_sim == 1.0 else "mismatch"
    reasons.append(f"mood {label}: {song['mood']} (+{mood_pts:.2f})")

    energy_sim = 1.0 - abs(user_prefs["energy"] - song["energy"])
    energy_pts = w["energy"] * energy_sim
    score += energy_pts
    reasons.append(f"energy proximity: {energy_sim:.2f} (+{energy_pts:.2f})")

    if user_prefs.get("likes_acoustic", False):
        acoustic_sim = song["acousticness"]
    else:
        acoustic_sim = 1.0 - song["acousticness"]
    acoustic_pts = w["acousticness"] * acoustic_sim
    score += acoustic_pts
    reasons.append(f"acoustic preference: {acoustic_sim:.2f} (+{acoustic_pts:.2f})")

    dance_sim = 1.0 - abs(user_prefs.get("danceability", 0.5) - song["danceability"])
    dance_pts = w["danceability"] * dance_sim
    score += dance_pts
    reasons.append(f"danceability proximity: {dance_sim:.2f} (+{dance_pts:.2f})")

    valence_sim = 1.0 - abs(user_prefs.get("valence", 0.5) - song["valence"])
    valence_pts = w["valence"] * valence_sim
    score += valence_pts
    reasons.append(f"valence proximity: {valence_sim:.2f} (+{valence_pts:.2f})")

    song_tempo_norm = _normalize_tempo(song["tempo_bpm"])
    user_tempo_norm = user_prefs.get("tempo", 0.5)
    tempo_sim = 1.0 - abs(user_tempo_norm - song_tempo_norm)
    tempo_pts = w["tempo"] * tempo_sim
    score += tempo_pts
    reasons.append(f"tempo proximity: {tempo_sim:.2f} (+{tempo_pts:.2f})")

    user_pop = user_prefs.get("popularity", 50)
    pop_sim = 1.0 - abs(user_pop - song["popularity"]) / POPULARITY_MAX
    pop_pts = w["popularity"] * pop_sim
    score += pop_pts
    reasons.append(f"popularity proximity: {pop_sim:.2f} (+{pop_pts:.2f})")

    user_decade = user_prefs.get("release_decade", 2020)
    decade_gap = abs(user_decade - song["release_decade"]) / 10
    decade_sim = max(0.0, 1.0 - decade_gap * 0.25)
    decade_pts = w["release_decade"] * decade_sim
    score += decade_pts
    reasons.append(f"decade {'match' if decade_gap == 0 else 'proximity'}: {song['release_decade']}s (+{decade_pts:.2f})")

    inst_sim = 1.0 - abs(user_prefs.get("instrumentalness", 0.5) - song.get("instrumentalness", 0.5))
    inst_pts = w["instrumentalness"] * inst_sim
    score += inst_pts
    reasons.append(f"instrumentalness proximity: {inst_sim:.2f} (+{inst_pts:.2f})")

    user_theme = user_prefs.get("lyrical_theme", "")
    theme_sim = 1.0 if user_theme and song.get("lyrical_theme", "") == user_theme else 0.0
    theme_pts = w["lyrical_theme"] * theme_sim
    score += theme_pts
    label = "match" if theme_sim == 1.0 else "mismatch"
    reasons.append(f"lyrical theme {label}: {song.get('lyrical_theme', 'N/A')} (+{theme_pts:.2f})")

    user_sub = user_prefs.get("sub_mood", "")
    sub_sim = 1.0 if user_sub and song.get("sub_mood", "") == user_sub else 0.0
    sub_pts = w["sub_mood"] * sub_sim
    score += sub_pts
    label = "match" if sub_sim == 1.0 else "mismatch"
    reasons.append(f"sub-mood {label}: {song.get('sub_mood', 'N/A')} (+{sub_pts:.2f})")

    return (round(score, 4), reasons)

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, strategy: str = DEFAULT_STRATEGY
) -> List[Tuple[Dict, float, str]]:
    """Score all songs with the chosen strategy, sort descending, return top-k."""
    scored = [
        (song, *score_song(user_prefs, song, strategy=strategy))
        for song in songs
    ]

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    return [
        (song, score, "; ".join(reasons))
        for song, score, reasons in ranked[:k]
    ]
