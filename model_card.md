# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

**Genre binary matching creates a filter bubble.** The scoring logic uses all-or-nothing matching for genre (1.0 or 0.0 with a 0.25 weight), which means a song in the "wrong" genre starts with a 0.25-point deficit that the five numeric features can rarely overcome. During experiments, the "Acoustic Electronic" edge case profile demonstrated this clearly: Neon Pulse (electronic/energetic) scored 0.8521 as the top pick, but its acousticness contribution was just +0.00 because the user wanted acoustic music while the song had 0.03 acousticness. The system prioritized the genre and mood match so heavily that it recommended a song that directly contradicted the user's acoustic preference. In a real product, this would trap users in a narrow genre lane and suppress cross-genre discovery entirely.

**The energy proximity formula disadvantages users with conflicting taste profiles.** When the "Sad but High-Energy" edge case was tested (a user who wants sad R&B but at energy 0.90), the top match — Echoes of You — only scored 0.7683 because its actual energy (0.38) produced an energy similarity of just 0.48. The system has no way to understand that "sad" and "high-energy" are a rare combination in the catalog, so it penalizes the energy gap on every sad song. Users with unconventional or contradictory preferences are structurally underserved because the linear proximity formula treats every feature independently without recognizing that certain feature combinations barely exist in the data.

**Sparse genres eliminate meaningful ranking.** Eight out of fourteen genres in the catalog have only a single song (rock, jazz, synthwave, classical, metal, country, reggae, latin). For any user who prefers one of these genres, the lone matching song will always rank first regardless of how poorly the numeric features align. The scoring system becomes a simple genre filter rather than a nuanced recommender, and the user has no way to discover that a nearby genre might serve them better.

**No mood or genre similarity awareness.** The system treats "indie pop" versus "pop" as exactly the same mismatch as "metal" versus "pop" — both receive a 0.0 genre score. Similarly, the moods "happy" and "energetic" are treated as entirely unrelated despite being conceptually adjacent. This penalizes songs that are clearly in the right neighborhood but happen to use a slightly different label, and it means the system cannot gracefully handle the subjective, overlapping nature of genre and mood categories.

**Acousticness is the only boolean feature in an otherwise numeric system.** Every other preference uses 0-1 proximity scoring, but `likes_acoustic` is a True/False toggle. A user who slightly prefers acoustic music is treated identically to one who exclusively listens to unplugged sessions. This asymmetry means acoustic preference is the least nuanced dimension in the scoring logic and can produce outsized swings — an otherwise perfect match can lose 0.13 points (the full acousticness weight) just because its acoustic character falls on the wrong side of the binary divide.

---

## 7. Evaluation  

Five user profiles were tested to evaluate the recommender across normal and adversarial conditions.

**Profiles tested:**

| Profile | Genre | Mood | Energy | Acoustic | Purpose |
|---|---|---|---|---|---|
| High-Energy Pop Fan | pop | happy | 0.8 | No | Baseline — clear preferences, multiple catalog matches |
| Chill Lofi Listener | lofi | chill | 0.35 | Yes | Opposite end of the energy spectrum |
| Deep Intense Rock | rock | intense | 0.92 | No | Single-song genre, high-energy dark preferences |
| Sad but High-Energy | r&b | sad | 0.90 | No | Adversarial — contradictory mood and energy |
| Acoustic Electronic | electronic | energetic | 0.85 | Yes | Adversarial — acoustic preference clashes with electronic genre |

**What I looked for:** For each profile, I checked whether the top-ranked songs made intuitive sense — does a pop fan get pop songs first? Does a lofi listener get ambient or jazz tracks as fallbacks instead of metal? I also checked whether the reason breakdowns correctly showed which features drove each score up or down.

**What matched expectations:** The three normal profiles worked almost perfectly. The Pop Fan got Sunrise City at 0.97, the Lofi Listener got Library Rain at 0.98, and the Rock profile got Storm Runner at 0.98. In each case, the top pick was the song with both a genre and mood match plus strong numeric alignment. The fallback songs also made sense — the Pop Fan's second pick was Gym Hero (same genre, different mood), and the Lofi Listener's fourth pick was Spacewalk Thoughts (different genre but matching chill mood and high acousticness).

**What surprised me:** "Gym Hero" kept appearing in the top 5 for profiles that had nothing to do with intense workout music. It showed up at #2 for the Pop Fan (who wanted happy, not intense) and at #5 for the Sad but High-Energy edge case (who wanted R&B, not pop). The reason is that Gym Hero has very high energy (0.93), very low acousticness (0.05), and high danceability (0.88) — so it scores well on the numeric features for any user who wants loud, electronic-leaning, danceable music, even if the genre and mood are wrong. In plain language: Gym Hero is a "numeric chameleon" — its numbers are so extreme that they partially compensate for categorical mismatches. This is like a streaming app recommending a workout playlist song to someone browsing sad ballads just because the underlying audio features happen to overlap.

**The edge cases revealed real weaknesses:** The "Sad but High-Energy" user's top pick scored only 0.77 — the lowest top-pick score of any profile. That is because sad songs in the catalog tend to have low energy (Echoes of You has 0.38, Autumn Letters has 0.22), so the energy proximity feature punished every song that matched the mood. The system cannot understand that the user's request is unusual — it just measures distances feature by feature. The "Acoustic Electronic" profile exposed a different problem: Neon Pulse won at 0.85 despite getting +0.00 for acousticness. The genre and mood match (contributing +0.45 together) completely overrode the acoustic preference. This means the system would recommend the least acoustic song in the catalog to someone who explicitly asked for acoustic music, just because the genre label matched.

**Tests run:** Automated pytest tests confirmed that the Recommender class returns the correct number of songs and that a pop/happy profile ranks pop songs above lofi songs. Manual inspection of all 20 song scores for the Pop Fan profile confirmed scores decreased monotonically from genre+mood matches down to songs with zero categorical overlap.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
