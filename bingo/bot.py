import random
from typing import List

def get_bot_move(board_state: dict, bot_color: str, difficulty: str) -> int:
    """
    Computes bot move based on difficulty.
    Returns a selected number (1 to 25) that has not been crossed yet.
    """
    crossed = board_state.get("crossed", [])
    bot_board = board_state.get("boards", {}).get(bot_color, [])
    
    uncrossed = [num for num in range(1, 26) if num not in crossed]
    if not uncrossed:
        raise ValueError("No uncrossed numbers left.")
        
    difficulty = difficulty.lower()
    
    # 1. Easy mode: Random choice
    if difficulty == "easy" or not bot_board:
        return random.choice(uncrossed)
        
    # 2. Medium/Hard: Smart utility heuristic
    winning_combos = [
        # Rows
        [0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24],
        # Columns
        [0, 5, 10, 15, 20], [1, 6, 11, 16, 21], [2, 7, 12, 17, 22], [3, 8, 13, 18, 23], [4, 9, 14, 19, 24],
        # Diagonals
        [0, 6, 12, 18, 24], [4, 8, 12, 16, 20]
    ]
    
    crossed_set = set(crossed)
    best_num = uncrossed[0]
    best_score = -1
    
    for num in uncrossed:
        try:
            cell_idx = bot_board.index(num)
        except ValueError:
            continue
            
        score = 0
        # Check all winning lines containing this cell_idx
        for combo in winning_combos:
            if cell_idx in combo:
                # Count how many cells in this combo are already crossed
                crossed_count = sum(1 for idx in combo if bot_board[idx] in crossed_set)
                # Exponential weight: higher weight for lines closer to completion
                score += (3 ** crossed_count)
                
        if score > best_score:
            best_score = score
            best_num = num
            
    return best_num
