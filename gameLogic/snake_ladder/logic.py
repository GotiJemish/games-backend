from typing import Dict, List, Tuple, Optional
from .rules import SNAKES, LADDERS

def initialize_board(player_colors: List[str]) -> Dict[str, List[int]]:
    """
    Initializes board state for Snakes & Ladders.
    Each player has 1 token starting at position 0 (off the board).
    """
    board = {}
    for color in ["RED", "GREEN", "YELLOW", "BLUE"]:
        if color in player_colors:
            board[color] = [0]
    return board

def make_move(
    board_state: Dict[str, List[int]],
    color: str,
    roll: int
) -> Tuple[Dict[str, List[int]], str]:
    """
    Executes a move for a player color and dice roll.
    Returns:
    - Updated board_state (dict)
    - Action description string
    """
    board = {k: list(v) for k, v in board_state.items()}
    curr_pos = board[color][0]
    new_pos = curr_pos + roll
    
    if new_pos > 100:
        return board, f"{color} rolled a {roll} but needs an exact roll to reach 100 (stays at {curr_pos})."
        
    msg = f"{color} rolled a {roll} and moved from {curr_pos} to {new_pos}."
    
    # Check for ladder or snake
    if new_pos in LADDERS:
        land_pos = LADDERS[new_pos]
        msg += f" Climbed a ladder to {land_pos}!"
        new_pos = land_pos
    elif new_pos in SNAKES:
        land_pos = SNAKES[new_pos]
        msg += f" Was bitten by a snake and slid down to {land_pos}."
        new_pos = land_pos
        
    board[color] = [new_pos]
    return board, msg

def check_winner(board_state: Dict[str, List[int]]) -> Optional[str]:
    """
    Checks if any player reached position 100.
    """
    for color, tokens in board_state.items():
        if tokens and tokens[0] == 100:
            return color
    return None
