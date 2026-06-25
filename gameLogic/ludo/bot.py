import random
from typing import Dict, List
from .rules import get_absolute_position, SAFE_TRACK_INDICES

def get_bot_move(board_state: Dict[str, List[int]], color: str, roll: int) -> int:
    """
    Given the Ludo board state, color, and roll, returns the best token index to move.
    Returns -1 if no moves are eligible.
    """
    tokens = board_state[color]
    eligible = []
    for idx, pos in enumerate(tokens):
        if pos == 56:
            continue
        if pos == -1:
            if roll == 6:
                eligible.append(idx)
        elif pos + roll <= 56:
            eligible.append(idx)
            
    if not eligible:
        return -1
        
    # Heuristic 1: Capture opponent
    for idx in eligible:
        curr_pos = tokens[idx]
        new_pos = 0 if curr_pos == -1 else curr_pos + roll
        abs_pos = get_absolute_position(color, new_pos)
        if abs_pos != -1 and abs_pos not in SAFE_TRACK_INDICES:
            for opp_color, opp_tokens in board_state.items():
                if opp_color == color:
                    continue
                for opp_pos in opp_tokens:
                    opp_abs = get_absolute_position(opp_color, opp_pos)
                    if opp_abs == abs_pos:
                        return idx  # Capturing move!
                        
    # Heuristic 2: Reach Home
    for idx in eligible:
        if tokens[idx] + roll == 56:
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
