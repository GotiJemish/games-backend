from typing import List

# Constants
STARTING_TRACK_INDICES = {
    "RED": 0,
    "GREEN": 13,
    "YELLOW": 26,
    "BLUE": 39
}

SAFE_TRACK_INDICES = {0, 8, 13, 21, 26, 34, 39, 47}

def get_absolute_position(color: str, step_count: int) -> int:
    """
    Returns the absolute common track position (0-51) of a token.
    Returns -1 if the token is in yard (-1) or in home column/home (51-56).
    """
    if step_count < 0 or step_count > 50:
        return -1
    start = STARTING_TRACK_INDICES[color]
    return (start + step_count) % 52

def get_next_turn(current_color: str, active_colors: List[str]) -> str:
    """
    Calculates the next player's turn clockwise: RED -> GREEN -> YELLOW -> BLUE -> RED.
    Skips colors that are not currently in the game.
    """
    order = ["RED", "GREEN", "YELLOW", "BLUE"]
    filtered_order = [c for c in order if c in active_colors]
    if not filtered_order:
        return current_color
    try:
        idx = filtered_order.index(current_color)
        return filtered_order[(idx + 1) % len(filtered_order)]
    except ValueError:
        return filtered_order[0]

def has_valid_moves(color: str, tokens: List[int], roll: int) -> bool:
    """
    Checks if a player has any valid moves with the rolled dice.
    """
    for pos in tokens:
        if pos == 56:
            continue
        if pos == -1:
            if roll == 6:
                return True
        elif pos + roll <= 56:
            return True
    return False
