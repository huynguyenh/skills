#!/usr/bin/env python3
"""
Sangousha game session score calculator.

Usage:
    python score_sgs.py <total_amount> <player1>:<score1> <player2>:<score2> ...

Example:
    python score_sgs.py 100000 hnh:25 cat:1 dat:4 tuan:7 jim:9 tieubao:9 antran:4
"""

import sys




def calculate_scores(total_amount: float, player_scores: dict[str, int]) -> dict[str, float]:
    """
    Calculate each player's payment based on Sangousha ranking rules.

    Ranking: highest score = 1st place (pays least).
    Weight formula: N = 1 + 2 + ... + num_players
    Each rank position's payment = position / N * total_amount
    Tied players share the average of the positions they span.
    """
    num_players = len(player_scores)
    N = num_players * (num_players + 1) // 2

    # Sort players by score descending
    sorted_players = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)

    # Group by score to handle ties
    payments = {}
    i = 0
    while i < len(sorted_players):
        # Find all players with the same score
        current_score = sorted_players[i][1]
        tied_players = []
        while i < len(sorted_players) and sorted_players[i][1] == current_score:
            tied_players.append(sorted_players[i][0])
            i += 1

        # Positions are 1-indexed: first player in sorted order = position 1
        start_pos = i - len(tied_players) + 1
        end_pos = i
        avg_pos = (start_pos + end_pos) / 2

        for player in tied_players:
            payments[player] = round(avg_pos / N * total_amount)

    # Fix rounding: adjust the largest payer so total matches exactly
    total_paid = sum(payments.values())
    diff = int(total_amount) - total_paid
    if diff != 0:
        # Find the player paying the most (last place) and adjust
        max_player = max(payments, key=payments.get)
        payments[max_player] += diff

    return payments


def parse_args(args: list[str]) -> tuple[float, dict[str, int]]:
    total_amount = float(args[0])
    player_scores = {}
    for arg in args[1:]:
        name, score = arg.split(":")
        player_scores[name.strip()] = int(score.strip())
    return total_amount, player_scores


def main():
    if len(sys.argv) < 3:
        print("Usage: python score_sgs.py <total_amount> <player1>:<score1> <player2>:<score2> ...")
        sys.exit(1)

    total_amount, player_scores = parse_args(sys.argv[1:])
    payments = calculate_scores(total_amount, player_scores)

    # Print payments sorted by amount ascending (winner first)
    max_name_len = max(len(name) for name in payments)
    for player, amount in sorted(payments.items(), key=lambda x: x[1]):
        print(f"{player:<{max_name_len}}  {amount:,.0f}")

    # Print total as verification
    print(f"{'TOTAL':<{max_name_len}}  {sum(payments.values()):,.0f}")


if __name__ == "__main__":
    main()
