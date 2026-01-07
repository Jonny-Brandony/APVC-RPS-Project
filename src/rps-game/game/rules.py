"""
RPS game rules module.
Contains the logic for determining winners in Rock-Paper-Scissors.
"""
from config import ROCK, PAPER, SCISSOR


def get_rps_winner(sign1, sign2):
    """
    Determine the winner of a Rock-Paper-Scissors round.
    
    Args:
        sign1: Player 1's sign (ROCK, PAPER, or SCISSOR)
        sign2: Player 2's sign (ROCK, PAPER, or SCISSOR)
    
    Returns:
        str: 'Tie', 'Player 1 Wins', or 'Player 2 Wins'
    """
    if sign1 == sign2:
        return 'Tie'
    
    if (sign1 == ROCK and sign2 == SCISSOR) or \
       (sign1 == PAPER and sign2 == ROCK) or \
       (sign1 == SCISSOR and sign2 == PAPER):
        return 'Player 1 Wins'
    
    return 'Player 2 Wins'

