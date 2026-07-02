import random
from typing import Dict, List
from .rules import get_absolute_position, get_safe_track_indices

def get_bot_move(board_state: Dict[str, List[int]], color: str, roll: int, active_colors: List[str] = None) -> int:
    """
    Given the Ludo board state, color, and roll, returns the best token index to move.
    Returns -1 if no moves are eligible.
    """
    if active_colors is None:
        active_colors = ["RED", "GREEN", "YELLOW", "BLUE"]
    num_players = len(active_colors)
    home_pos = (num_players * 13) + 4
    
    tokens = board_state[color]
    eligible = []
    for idx, pos in enumerate(tokens):
        if pos == home_pos:
            continue
        if pos == -1:
            if roll == 6:
                eligible.append(idx)
        elif pos + roll <= home_pos:
            eligible.append(idx)
            
    if not eligible:
        return -1
        
    safe_indices = get_safe_track_indices(num_players)
        
    # Heuristic 1: Capture opponent
    for idx in eligible:
        curr_pos = tokens[idx]
        new_pos = 0 if curr_pos == -1 else curr_pos + roll
        abs_pos = get_absolute_position(color, new_pos, active_colors)
        if abs_pos != -1 and abs_pos not in safe_indices:
            for opp_color, opp_tokens in board_state.items():
                if opp_color == color or opp_color not in active_colors:
                    continue
                for opp_pos in opp_tokens:
                    opp_abs = get_absolute_position(opp_color, opp_pos, active_colors)
                    if opp_abs == abs_pos:
                        return idx  # Capturing move!
                        
    # Heuristic 2: Reach Home
    for idx in eligible:
        if tokens[idx] + roll == home_pos:
            return idx
            
    # Heuristic 3: Move out of yard if rolled a 6
    if roll == 6:
        for idx in eligible:
            if tokens[idx] == -1:
                return idx
                
    # Heuristic 4: Move furthest advanced token
    best_idx = eligible[0]
    max_dist = -1
    for idx in eligible:
        if tokens[idx] > max_dist:
            max_dist = tokens[idx]
            best_idx = idx
            
    return best_idx
