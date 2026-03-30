---
name: hnh-score-sgs
description: Calculate Sangousha (SGS) game session payment splits based on player scores and a total pot. Use this skill whenever the user mentions Sangousha, SGS, "score sgs", game scores with player names and numbers, or wants to split a game pot based on rankings. Also trigger when the user pastes something that looks like "player1: X player2: Y" with a total amount — even if they don't say "Sangousha" explicitly.
---

# Sangousha Score Calculator

Calculate how much each player pays from a game session pot based on their scores.

## How the formula works

1. **Rank players** by score (highest = 1st place, pays least)
2. **Total weight** N = 1 + 2 + ... + num_players (e.g., 7 players → N = 28)
3. **Each rank's share** = rank_position / N × total_amount
4. **Ties**: players sharing a rank get the average of the positions they span
   - Example: two players tied at 2nd → they each get position (2+3)/2 = 2.5

## Running the calculator

```bash
python ~/.claude/skills/hnh-score-sgs/scripts/score_sgs.py <total_amount> <player1>:<score1> <player2>:<score2> ...
```

### Parsing user input

The user will typically paste scores in a loose format like:
```
hnh: 25 cat: 1 dat: 4 tuan: 7 jim: 9 tieubao: 9 antran: 4
```

Parse this into `name:score` pairs for the script. The total amount may be stated separately (e.g., "total 100k" or "pot is 200000").

If the user says "100k", interpret as 100000. If they say "50k", interpret as 50000.

### Output

The script prints each player's payment amount, sorted from least to most (winner first), plus a verification total. Just show this output directly — no extra commentary needed.
