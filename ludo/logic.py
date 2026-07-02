from typing import Dict, List, Tuple, Optional
from .rules import get_absolute_position, get_safe_track_indices

def initialize_board(player_colors: List[str], num_pawns: int = 4) -> Dict[str, List[int]]:
    """
    Initializes board state with pawns in yard (-1) for all active colors.
    """
    board = {}
    for color in player_colors:
        board[color] = [-1] * num_pawns
    return board

def make_move(
    board_state: Dict[str, List[int]],
    color: str,
    token_idx: int,
    roll: int,
    active_colors: List[str] = None
) -> Tuple[Dict[str, List[int]], bool, str]:
    """
    Executes a move for a given token index and dice roll.
    Returns a tuple of:
    - The updated board_state
    - A boolean indicating if a capture occurred
    - A log message describing what happened
    """
    if active_colors is None:
        active_colors = ["RED", "GREEN", "YELLOW", "BLUE"]
        
    num_players = len(active_colors)
    track_size = num_players * 13
    home_stretch_start = track_size - 2
    home_pos = track_size + 4

    tokens = list(board_state[color])
    curr_pos = tokens[token_idx]
    
    # 1. Validate the move
    if curr_pos == home_pos:
        return board_state, False, f"Token {token_idx} is already Home."
        
    if curr_pos == -1:
        if roll != 6:
            return board_state, False, "Need a 6 to bring token out of yard."
        new_pos = 0
    else:
        if curr_pos + roll > home_pos:
            return board_state, False, "Cannot move token: roll exceeds home limit."
        new_pos = curr_pos + roll

    # 2. Update token position
    tokens[token_idx] = new_pos
    board_state[color] = tokens
    
    # 3. Check for captures (only if on common track, i.e., 0 <= new_pos <= home_stretch_start)
    captured = False
    capture_msg = ""
    abs_pos = get_absolute_position(color, new_pos, active_colors)
    safe_indices = get_safe_track_indices(num_players)
    
    if abs_pos != -1 and abs_pos not in safe_indices:
        for opp_color, opp_tokens in board_state.items():
            if opp_color == color or opp_color not in active_colors:
                continue
            opp_tokens_list = list(opp_tokens)
            opp_updated = False
            for opp_idx, opp_pos in enumerate(opp_tokens_list):
                opp_abs = get_absolute_position(opp_color, opp_pos, active_colors)
                if opp_abs == abs_pos:
                    # Capture! Reset opponent token to yard (-1)
                    opp_tokens_list[opp_idx] = -1
                    opp_updated = True
                    captured = True
                    capture_msg = f" Captured {opp_color}'s token {opp_idx}!"
            if opp_updated:
                board_state[opp_color] = opp_tokens_list

    move_desc = f"{color} token {token_idx} moved to step {new_pos}."
    if new_pos == home_pos:
        move_desc += " Reached Home!"
    if captured:
        move_desc += capture_msg
        
    return board_state, captured, move_desc

def check_winner(board_state: Dict[str, List[int]], active_colors: List[str] = None) -> Optional[str]:
    """
    Checks if any player has all tokens in Home.
    """
    if active_colors is None:
        active_colors = ["RED", "GREEN", "YELLOW", "BLUE"]
    num_players = len(active_colors)
    home_pos = (num_players * 13) + 4
    
    for color, tokens in board_state.items():
        if color not in active_colors:
            continue
        if all(pos == home_pos for pos in tokens):
            return color
    return None
