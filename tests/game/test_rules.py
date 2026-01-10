"""
Unit tests for the RPS game rules module.

This module contains comprehensive tests for the get_rps_winner function,
covering all possible combinations of Rock, Paper, Scissor, and Gun signs.
"""
import unittest
import sys
from pathlib import Path

# Add the src/rps-game directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "rps-game"))

from game.rules import get_rps_winner
from config import ROCK, PAPER, SCISSOR, GUN


class TestRPSRulesParameterized(unittest.TestCase):
    """
    Parameterized test cases for comprehensive coverage.
    
    Uses a data-driven approach to test all combinations systematically.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Define all test cases: (sign1, sign2, expected_result, description)
        self.test_cases = [
            # Ties
            (ROCK, ROCK, 'Tie', 'Rock vs Rock'),
            (PAPER, PAPER, 'Tie', 'Paper vs Paper'),
            (SCISSOR, SCISSOR, 'Tie', 'Scissor vs Scissor'),
            (GUN, GUN, 'Tie', 'Gun vs Gun'),
            
            # Player 1 Wins - Standard
            (ROCK, SCISSOR, 'Player 1 Wins', 'Rock beats Scissor'),
            (PAPER, ROCK, 'Player 1 Wins', 'Paper beats Rock'),
            (SCISSOR, PAPER, 'Player 1 Wins', 'Scissor beats Paper'),
            
            # Player 1 Wins - Gun
            (GUN, ROCK, 'Player 1 Wins', 'Gun beats Rock'),
            (GUN, PAPER, 'Player 1 Wins', 'Gun beats Paper'),
            (GUN, SCISSOR, 'Player 1 Wins', 'Gun beats Scissor'),
            
            # Player 2 Wins - Standard
            (SCISSOR, ROCK, 'Player 2 Wins', 'Scissor loses to Rock'),
            (ROCK, PAPER, 'Player 2 Wins', 'Rock loses to Paper'),
            (PAPER, SCISSOR, 'Player 2 Wins', 'Paper loses to Scissor'),
            
            # Player 2 Wins - Gun
            (ROCK, GUN, 'Player 2 Wins', 'Rock loses to Gun'),
            (PAPER, GUN, 'Player 2 Wins', 'Paper loses to Gun'),
            (SCISSOR, GUN, 'Player 2 Wins', 'Scissor loses to Gun'),
        ]
    
    def test_all_parameterized_cases(self):
        """Test all parameterized test cases."""
        for sign1, sign2, expected, description in self.test_cases:
            with self.subTest(sign1=sign1, sign2=sign2, description=description):
                result = get_rps_winner(sign1, sign2)
                self.assertEqual(
                    result, 
                    expected,
                    f"Failed for {description}: expected {expected}, got {result}"
                )


if __name__ == '__main__':
    # Configure test runner with verbosity
    unittest.main(verbosity=2)
