from typing import List

# Standard Snakes and Ladders board layout
SNAKES = {
    17: 7,
    54: 34,
    62: 19,
    64: 60,
    87: 24,
    93: 73,
    95: 75,
    98: 79
}

LADDERS = {
    4: 14,
    9: 31,
    20: 38,
    21: 42,
    28: 84,
    36: 44,
    51: 67,
    71: 91,
    80: 100
}

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
