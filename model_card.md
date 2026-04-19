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

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

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
