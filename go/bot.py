import random
from typing import Dict, List, Tuple, Optional
from .rules import get_neighbors, find_group, count_liberties, get_next_turn_go
from .logic import make_move

def get_bot_move(board_state: dict, color: str) -> Tuple[Optional[int], Optional[int], bool]:
    """
    Evaluates all valid intersections and returns (row, col, pass_turn).
    Uses capture and atari heuristics with position score weights.
    """
    size = board_state["size"]
    stones = board_state["stones"]
    
    # 1. Find all empty valid intersections
    valid_moves = []
    for r in range(size):
        for c in range(size):
            key = f"{r}_{c}"
            if key in stones:
                continue
            
            # Check suicide and Ko rules by simulating the move
            sim_state = {
                "size": size,
                "stones": dict(stones),
                "captured": dict(board_state["captured"]),
                "consecutive_passes": board_state["consecutive_passes"],
                "previous_stones": board_state.get("previous_stones")
            }
            _, success, _ = make_move(sim_state, color, r, c)
            if success:
                valid_moves.append((r, c))
                
    if not valid_moves:
        return None, None, True  # Must pass
        
    opponent = get_next_turn_go(color)
    best_move = None
    best_score = -9999
    
    # 2. Score each valid intersection
    for r, c in valid_moves:
        score = 0
        
        # Heuristic A: Capture opponent stones
        sim_state = {
            "size": size,
            "stones": dict(stones),
            "captured": {color: 0},
            "consecutive_passes": 0,
            "previous_stones": board_state.get("previous_stones")
        }
        updated_state, _, _ = make_move(sim_state, color, r, c)
        caps = updated_state["captured"].get(color, 0)
        if caps > 0:
            score += caps * 100
            
        # Heuristic B: Atari defense (save own stones under attack)
        for nr, nc in get_neighbors(r, c, size):
            nkey = f"{nr}_{nc}"
            if stones.get(nkey) == color:
                group = find_group(stones, nr, nc, size)
                if len(count_liberties(stones, group, size)) == 1:
                    score += 50
                    
        # Heuristic C: Put opponent group in Atari
        for nr, nc in get_neighbors(r, c, size):
            nkey = f"{nr}_{nc}"
            if stones.get(nkey) == opponent:
                group = find_group(stones, nr, nc, size)
                if len(count_liberties(stones, group, size)) > 1:
                    # Check if placing stone reduces opponent liberties to 1
                    sim_stones = dict(stones)
                    sim_stones[f"{r}_{c}"] = color
                    if len(count_liberties(sim_stones, group, size)) == 1:
                        score += 30
                        
        # Heuristic D: Proximity to Center
        center = (size - 1) / 2
        dist = abs(r - center) + abs(c - center)
        score += (size - dist) * 1.5
        
        # Add random noise to make the bot less predictable
        score += random.random() * 4.0
        
        if score > best_score:
            best_score = score
            best_move = (r, c)
            
    # Heuristic E: Pass if board is crowded (> 70% full) and no good moves left
    if len(stones) > (size * size * 0.7) and best_score < 8:
        return None, None, True
        
    if best_move:
        return best_move[0], best_move[1], False
        
    return None, None, True
