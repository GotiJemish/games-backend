import random
from typing import Tuple, List
from .rules import calculate_lines

def initialize_board(difficulty: str = "medium") -> dict:
    """
    Initializes board state for Bingo.
    """
    return {
        "boards": {},
        "crossed": [],
        "difficulty": difficulty,
        "player_lines": {}
    }

def initialize_player_board() -> List[int]:
    """
    Generates a 5x5 board containing numbers 1 to 25 randomly shuffled.
    """
    nums = list(range(1, 26))
    random.shuffle(nums)
    return nums

def setup_game_boards(board_state: dict, active_colors: List[str]) -> dict:
    """
    Prepares boards for active players if they are not already set up.
    Returns a new dict copy.
    """
    boards = dict(board_state.get("boards", {}))
    player_lines = dict(board_state.get("player_lines", {}))
    crossed = list(board_state.get("crossed", []))
    
    for color in active_colors:
        if color not in boards:
            boards[color] = initialize_player_board()
            player_lines[color] = 0
            
    return {
        "boards": boards,
        "crossed": crossed,
        "difficulty": board_state.get("difficulty", "medium"),
        "player_lines": player_lines
    }

def make_move(board_state: dict, color: str, number: int) -> Tuple[dict, bool, str]:
    """
    Crosses out a number on both boards.
    Returns:
    - Updated board_state (dict)
    - Success (bool)
    - Description message (str)
    """
    crossed = list(board_state.get("crossed", []))
    boards = board_state.get("boards", {})
    
    if number < 1 or number > 25:
        return board_state, False, "Number must be between 1 and 25."
        
    if number in crossed:
        return board_state, False, f"Number {number} is already selected."
        
    # Append the number
    new_crossed = crossed + [number]
    
    # Recalculate completed lines for both players
    new_player_lines = {}
    for col, brd in boards.items():
        new_player_lines[col] = calculate_lines(brd, new_crossed)
        
    # Create new dict to force SQLAlchemy change detection
    new_state = {
        "boards": boards,
        "crossed": new_crossed,
        "difficulty": board_state.get("difficulty", "medium"),
        "player_lines": new_player_lines
    }
    
    msg = f"Player {color} selected number {number}."
    return new_state, True, msg
