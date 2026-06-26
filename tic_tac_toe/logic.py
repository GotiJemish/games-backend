from typing import Tuple, List, Optional
from .rules import get_next_turn_ttt, check_winner_ttt

def initialize_board(difficulty: str = "medium") -> dict:
    """
    Initializes board state for Tic-Tac-Toe.
    """
    return {
        "board": [None] * 9,
        "difficulty": difficulty
    }

def make_move(board_state: dict, color: str, position: int) -> Tuple[dict, bool, str]:
    """
    Executes a move for a player.
    Returns:
    - Updated board_state (dict)
    - Success (bool)
    - Description message (str)
    """
    board = list(board_state["board"])
    
    if position < 0 or position > 8:
        return board_state, False, "Invalid board position. Must be between 0 and 8."
        
    if board[position] is not None:
        return board_state, False, "Position is already occupied."
        
    board[position] = color
    
    # Create a new dictionary to trigger SQLAlchemy JSON state update detection
    new_state = {
        "board": board,
        "difficulty": board_state.get("difficulty", "medium")
    }
    
    msg = f"Player {color} placed mark at position {position}."
    return new_state, True, msg
