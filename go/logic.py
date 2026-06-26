from typing import Dict, List, Tuple, Optional, Set
from .rules import get_next_turn_go, get_neighbors, find_group, count_liberties

def initialize_board(size: int = 9) -> dict:
    """
    Initializes board state for Go.
    """
    return {
        "size": size,
        "stones": {},  # "r_c" -> "BLACK" or "WHITE"
        "captured": {"BLACK": 0, "WHITE": 0},
        "consecutive_passes": 0,
        "previous_stones": None  # For Ko rule check
    }

def make_move(
    board_state: dict,
    color: str,
    row: int,
    col: int
) -> Tuple[dict, bool, str]:
    """
    Executes a move for a player.
    Returns:
    - Updated board_state (dict)
    - Success (bool)
    - Description message (str)
    """
    size = board_state["size"]
    stones = dict(board_state["stones"])
    key = f"{row}_{col}"

    if key in stones:
        return board_state, False, "Intersection is already occupied."

    opponent = get_next_turn_go(color)
    old_stones = dict(stones)

    # 1. Place the stone
    stones[key] = color

    # 2. Check and remove captured opponent stones
    captured_count = 0
    opponents_to_check = []
    
    for nr, nc in get_neighbors(row, col, size):
        nkey = f"{nr}_{nc}"
        if stones.get(nkey) == opponent:
            opponents_to_check.append((nr, nc))

    captured_coords = set()
    for orr, oc in opponents_to_check:
        if (orr, oc) in captured_coords:
            continue
        group = find_group(stones, orr, oc, size)
        if len(count_liberties(stones, group, size)) == 0:
            for gr, gc in group:
                gkey = f"{gr}_{gc}"
                if gkey in stones:
                    del stones[gkey]
                    captured_count += 1
                captured_coords.add((gr, gc))

    # 3. Check for suicide
    own_group = find_group(stones, row, col, size)
    if len(count_liberties(stones, own_group, size)) == 0:
        return board_state, False, "Suicide move is invalid."

    # 4. Check for Ko rule
    def get_hashable_dict(d):
        return tuple(sorted(d.items()))

    if board_state.get("previous_stones") and get_hashable_dict(stones) == get_hashable_dict(board_state["previous_stones"]):
        return board_state, False, "Ko rule violation: Cannot recreate immediate previous board state."

    # Move is valid
    new_captured = dict(board_state.get("captured", {}))
    if color not in new_captured:
        new_captured[color] = 0
    new_captured[color] += captured_count

    new_board_state = {
        "size": size,
        "stones": stones,
        "captured": new_captured,
        "consecutive_passes": 0,
        "previous_stones": old_stones
    }

    msg = f"{color} placed a stone at ({row}, {col})."
    if captured_count > 0:
        msg += f" Captured {captured_count} opponent stone(s)!"

    return new_board_state, True, msg

def calculate_score(board_state: dict) -> dict:
    """
    Computes area score (stones + territory).
    Includes 6.5 Komi for WHITE.
    """
    size = board_state["size"]
    stones = board_state["stones"]

    # 1. Count stones
    black_stones = sum(1 for color in stones.values() if color == "BLACK")
    white_stones = sum(1 for color in stones.values() if color == "WHITE")

    # 2. Find territories using BFS on empty intersections
    visited = set()
    black_territory = 0
    white_territory = 0

    for r in range(size):
        for c in range(size):
            if f"{r}_{c}" in stones or (r, c) in visited:
                continue

            component = set()
            queue = [(r, c)]
            borders = set()

            while queue:
                curr = queue.pop(0)
                if curr in component:
                    continue
                component.add(curr)
                visited.add(curr)

                for nr, nc in get_neighbors(curr[0], curr[1], size):
                    nkey = f"{nr}_{nc}"
                    if nkey in stones:
                        borders.add(stones[nkey])
                    elif (nr, nc) not in component:
                        queue.append((nr, nc))

            if len(borders) == 1:
                border_color = list(borders)[0]
                if border_color == "BLACK":
                    black_territory += len(component)
                elif border_color == "WHITE":
                    white_territory += len(component)

    komi = 6.5
    black_total = black_stones + black_territory
    white_total = white_stones + white_territory + komi

    return {
        "BLACK": black_total,
        "WHITE": white_total,
        "black_stones": black_stones,
        "white_stones": white_stones,
        "black_territory": black_territory,
        "white_territory": white_territory,
        "komi": komi,
        "winner": "BLACK" if black_total > white_total else "WHITE"
    }
