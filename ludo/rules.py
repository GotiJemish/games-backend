from typing import List, Set

def get_safe_track_indices(num_players: int) -> Set[int]:
    """Dynamically generate safe spots: start of each player, and the star (usually +8 from start)."""
    safe_spots = set()
    for i in range(num_players):
        start = i * 13
        safe_spots.add(start)
        safe_spots.add(start + 8)
    return safe_spots

def get_absolute_position(color: str, step_count: int, active_colors: List[str]) -> int:
    """
    Returns the absolute common track position.
    Returns -1 if the token is in yard (-1) or in home column/home.
    """
    num_players = len(active_colors)
    track_size = num_players * 13
    home_stretch_start = track_size - 2
    
    if step_count < 0 or step_count > home_stretch_start:
        return -1
        
    try:
        player_idx = active_colors.index(color)
    except ValueError:
        return -1
        
    start = player_idx * 13
    return (start + step_count) % track_size

def get_next_turn(current_color: str, active_colors: List[str]) -> str:
    """
    Calculates the next player's turn clockwise dynamically.
    """
    if not active_colors:
        return current_color
    try:
        idx = active_colors.index(current_color)
        return active_colors[(idx + 1) % len(active_colors)]
    except ValueError:
        return active_colors[0]

def has_valid_moves(color: str, tokens: List[int], roll: int, active_colors: List[str]) -> bool:
    """
    Checks if a player has any valid moves with the rolled dice.
    """
    num_players = len(active_colors)
    track_size = num_players * 13
    home_pos = track_size + 4
    
    for pos in tokens:
        if pos == home_pos:
            continue
        if pos == -1:
            if roll == 6:
                return True
        elif pos + roll <= home_pos:
            return True
    return False
