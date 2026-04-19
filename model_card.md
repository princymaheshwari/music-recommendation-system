# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

VibeFinder suggests the top-k songs from a small catalog based on a user's taste profile. It is built for classroom exploration and learning about how recommender systems work. It is not designed for real users or production use.

**What it does:** Takes a set of user preferences (favorite genre, mood, energy level, acoustic preference, danceability, valence, and tempo) and finds the songs in the catalog that most closely match those preferences. Each recommendation comes with a plain-language explanation of why it was chosen.

**What it assumes:** The user knows exactly what they want and can express it as a fixed set of numeric and categorical values. It assumes taste is static — it does not adapt over time or change based on context like time of day or current activity.

**What it should NOT be used for:** Real music recommendations for actual listeners. The catalog is too small (20 songs), the scoring logic is too simple (no machine learning, no collaborative signals), and the system has known biases that would create a poor user experience at scale. It should also not be used to make assumptions about what kinds of people like what kinds of music — the profiles are fictional and the catalog was hand-crafted.

---

## 3. How the Model Works  

The system looks at each song in the catalog and asks: "How similar is this song to what the user wants?" It checks seven things and gives each one a different amount of importance.

First, it checks if the song's genre matches the user's favorite genre. This is the most important check — it is worth 25% of the total score. If the genre matches, the song gets full credit. If it does not match at all, it gets zero. There is no partial credit for being close (so "indie pop" gets the same zero as "metal" when the user wants "pop").

Second, it checks mood the same way — a match is worth 20% of the score. Happy matches happy, chill matches chill, but "happy" and "energetic" are treated as completely different even though they feel similar.

Third, it measures how close the song's energy is to what the user wants. Instead of asking "is this song high energy or low energy," it asks "is this song's energy close to the user's target?" A song with energy 0.82 scores almost perfectly for a user who wants 0.80, but a song with energy 0.30 scores poorly. This is worth 18% of the score.

Fourth, it checks acousticness — whether the song sounds like real instruments or electronic production. The user says "I like acoustic" or "I do not like acoustic," and the system rewards or penalizes the song accordingly. This is worth 13%.

Fifth through seventh, it does the same "how close is this number to what the user wants" check for danceability (10%), valence/happiness (8%), and tempo/speed (6%).

All seven scores are added up into a single number between 0.0 and 1.0. The system does this for every song, sorts them from highest to lowest, and returns the top-k as recommendations.

---

## 4. Data  

The catalog contains 20 songs stored in `data/songs.csv`. The original starter file had 10 songs. We added 10 more to improve genre and mood diversity.

**Genres represented (14 total):** pop (2), lofi (3), rock (1), ambient (2), jazz (1), synthwave (1), indie pop (1), r&b (2), hip-hop (1), classical (1), electronic (1), country (1), metal (1), reggae (1), latin (1).

**Moods represented (12 total):** happy (2), chill (3), intense (2), relaxed (2), moody (1), focused (1), romantic (2), energetic (2), sad (2), nostalgic (1), angry (1), dreamy (1).

**What is missing:** The catalog does not include any songs with lyrics in languages other than English (implied). There are no songs from genres like funk, blues, soul, K-pop, or afrobeat. The numeric features were hand-assigned, not derived from actual audio analysis, so they reflect the catalog creator's subjective impression of what each song sounds like. The dataset is too small for most genres to have more than one or two representatives, which means the system often reduces to a genre filter rather than a nuanced ranker.

---

## 5. Strengths  

The system works well for users whose preferences match a well-represented genre in the catalog. The three "normal" test profiles (Pop Fan, Lofi Listener, Rock Fan) all produced top picks with scores above 0.97, and the recommended songs felt intuitively right.

It is fully transparent. Every recommendation comes with a line-by-line breakdown showing exactly which features contributed how many points. A user can see "genre match: pop (+0.25)" and "mood mismatch: intense (+0.00)" and understand precisely why a song ranked where it did. There are no hidden weights or black-box decisions.

The proximity scoring for numeric features works well. Instead of just asking "is this song high energy," it asks "is this song's energy close to what the user wants." This means a user who wants medium energy (0.50) will get different results from a user who wants high energy (0.90), even if they agree on everything else.

The system successfully separates very different user types. The Pop Fan and Lofi Listener had zero overlap in their top 5 recommendations, which matches the intuition that these are fundamentally different listeners.

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

**Add genre and mood similarity instead of binary matching.** Instead of treating every genre mismatch as equally bad, build a similarity map where "indie pop" is 0.8 similar to "pop," "synthwave" is 0.6 similar to "electronic," and "metal" is 0.1 similar to "pop." This would fix the biggest bias in the system and let songs in related genres earn partial credit instead of flat zero.

**Replace the boolean acoustic preference with a numeric target.** Change `likes_acoustic` from True/False to a 0-1 value like every other feature. A user who sets acoustic preference to 0.7 would get partial credit for songs at 0.5, while a user at 1.0 would strongly prefer fully acoustic tracks. This would eliminate the blunt True/False asymmetry and make acoustic scoring consistent with the rest of the system.

**Add a diversity constraint to the ranking rule.** Currently the top-k results can all be from the same genre and mood. A simple improvement would be: after selecting the top-k by score, check if more than half come from the same genre. If so, swap the lowest-scoring duplicate for the next-highest song from a different genre. This would reduce the filter bubble effect and expose users to more variety without abandoning relevance entirely.

---

## 9. Personal Reflection  

### Biggest Learning Moment

My biggest learning moment came when I ran the "Sad but High-Energy" edge case and saw the top pick score only 0.77 — the lowest of any profile. Until that point, I assumed the scoring formula was robust because the three normal profiles all produced near-perfect results. But the edge case exposed a fundamental truth: a recommender only works well when the user's preferences align with patterns that actually exist in the data. There is no sad, high-energy R&B song in the catalog, so the system was forced to compromise, and the result felt wrong no matter which song it picked. That moment taught me that evaluation is not just about checking if the "right" song wins — it is about understanding what the system does when there is no right answer.

### How Copilot Helped and Where I Double-Checked

Copilot was instrumental throughout the project. I used it to design the weighted scoring formula, generate the expanded song catalog, build the Mermaid data flow diagram, and draft the model card. It was especially helpful for exploring ideas quickly — when I asked about the difference between collaborative and content-based filtering, or how to calculate proximity scores, Copilot gave me a clear conceptual framework that I could then implement.

But I had to double-check Copilot in several places. When it first proposed the feature weights, I manually verified them by scoring two songs by hand (Sunrise City and Storm Runner) to make sure the numbers added up and that genre mismatch actually tanked the score the way I intended. When it generated the 10 new songs for the catalog, I reviewed each one to make sure the numeric values were internally consistent — a classical song should not have 0.95 danceability, for example. I also caught that the initial `main.py` import path would break when run from the project root, which Copilot did not anticipate until the error surfaced. The lesson is that Copilot is great at generating structure and logic, but the human still needs to verify that the output makes sense in context.

### What Surprised Me About Simple Algorithms

The most surprising thing was how a weighted sum of seven numbers can feel like a real recommendation. When I saw Sunrise City score 0.97 for the Pop Fan profile and Library Rain score 0.98 for the Lofi Listener, the results genuinely felt like something a music app would suggest. There is no machine learning here, no neural network, no training data — just multiplication and addition. Yet the output feels "smart" because the features were chosen well and the weights reflect a reasonable hierarchy of what matters to a listener. It made me realize that the "intelligence" in a recommendation system is not in the algorithm — it is in the feature engineering and the weight design. A simple formula with well-chosen inputs can outperform a complex model with poor inputs.

At the same time, the Gym Hero problem showed the limits of this illusion. A song with extreme numeric values kept showing up for users who would never choose it, because the math happened to add up even without genre or mood overlap. Simple algorithms cannot understand context, intention, or the fact that a workout anthem does not belong in a sad ballad playlist. They just measure distances.

### What I Would Try Next

If I kept developing this project, I would try three things. First, I would replace the binary genre and mood matching with a similarity matrix — so "indie pop" earns 0.8 credit when the user wants "pop" instead of flat zero. This single change would probably fix the biggest flaw in the system. Second, I would add a diversity constraint to the ranking rule, so the top-k results cannot all come from the same genre. Even a simple rule like "no more than 2 songs from the same genre in the top 5" would break the filter bubble. Third, I would experiment with letting users set feature weights themselves — some listeners care deeply about mood but not at all about tempo, and the current fixed weights cannot capture that. Giving users a "what matters to you" slider for each feature would make the system far more personal without adding algorithmic complexity.
