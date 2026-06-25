from typing import Dict, List, Tuple, Optional
from .rules import get_absolute_position, SAFE_TRACK_INDICES

def initialize_board(player_colors: List[str]) -> Dict[str, List[int]]:
    """
    Initializes board state with 4 tokens in yard (-1) for all colors.
    Active colors are those assigned to players; others are empty or not initialized.
    """
    board = {}
    for color in ["RED", "GREEN", "YELLOW", "BLUE"]:
        if color in player_colors:
            board[color] = [-1, -1, -1, -1]
    return board

def make_move(
    board_state: Dict[str, List[int]],
    color: str,
    token_idx: int,
    roll: int
) -> Tuple[Dict[str, List[int]], bool, str]:
    """
    Executes a move for a given token index and dice roll.
    Returns a tuple of:
    - The updated board_state
    - A boolean indicating if a capture occurred
    - A log message describing what happened
    """
    tokens = list(board_state[color])
    curr_pos = tokens[token_idx]
    
    # 1. Validate the move
    if curr_pos == 56:
        return board_state, False, f"Token {token_idx} is already Home."
        
    if curr_pos == -1:
        if roll != 6:
            return board_state, False, "Need a 6 to bring token out of yard."
        new_pos = 0
    else:
        if curr_pos + roll > 56:
            return board_state, False, "Cannot move token: roll exceeds home limit."
        new_pos = curr_pos + roll

    # 2. Update token position
    tokens[token_idx] = new_pos
    board_state[color] = tokens
    
    # 3. Check for captures (only if on common track, i.e., 0 <= new_pos <= 50)
    captured = False
    capture_msg = ""
    abs_pos = get_absolute_position(color, new_pos)
    
    if abs_pos != -1 and abs_pos not in SAFE_TRACK_INDICES:
        for opp_color, opp_tokens in board_state.items():
            if opp_color == color:
                continue
            opp_tokens_list = list(opp_tokens)
            opp_updated = False
            for opp_idx, opp_pos in enumerate(opp_tokens_list):
                opp_abs = get_absolute_position(opp_color, opp_pos)
                if opp_abs == abs_pos:
                    # Capture! Reset opponent token to yard (-1)
                    opp_tokens_list[opp_idx] = -1
                    opp_updated = True
                    captured = True
                    capture_msg = f" Captured {opp_color}'s token {opp_idx}!"
            if opp_updated:
                board_state[opp_color] = opp_tokens_list

    move_desc = f"{color} token {token_idx} moved to step {new_pos}."
    if new_pos == 56:
        move_desc += " Reached Home!"
    if captured:
        move_desc += capture_msg
        
    return board_state, captured, move_desc

def check_winner(board_state: Dict[str, List[int]]) -> Optional[str]:
    """
    Checks if any player has all 4 tokens in Home (56).
    Returns the winning color if true, else None.
    """
    for color, tokens in board_state.items():
        if all(pos == 56 for pos in tokens):
            return color
    return None
