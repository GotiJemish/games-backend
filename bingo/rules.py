from typing import List, Optional

def get_next_turn_bingo(current: str) -> str:
    """
    Alternates between BLUE and RED.
    """
    return "RED" if current == "BLUE" else "BLUE"

def calculate_lines(board: List[int], crossed: List[int]) -> int:
    """
    Calculates completed Bingo lines (rows, columns, diagonals) on a 5x5 board.
    board: list of 25 integers (numbers 1 to 25).
    crossed: list of integers (numbers 1 to 25 that have been selected).
    """
    if not board:
        return 0
        
    crossed_set = set(crossed)
    lines_count = 0
    
    # 1. Row indices
    row_combos = [
        [0, 1, 2, 3, 4],
        [5, 6, 7, 8, 9],
        [10, 11, 12, 13, 14],
        [15, 16, 17, 18, 19],
        [20, 21, 22, 23, 24]
    ]
    for row in row_combos:
        if all(board[idx] in crossed_set for idx in row):
            lines_count += 1
            
    # 2. Column indices
    col_combos = [
        [0, 5, 10, 15, 20],
        [1, 6, 11, 16, 21],
        [2, 7, 12, 17, 22],
        [3, 8, 13, 18, 23],
        [4, 9, 14, 19, 24]
    ]
    for col in col_combos:
        if all(board[idx] in crossed_set for idx in col):
            lines_count += 1
            
    # 3. Diagonal indices
    diag_combos = [
        [0, 6, 12, 18, 24], # Top-left to bottom-right
        [4, 8, 12, 16, 20]  # Top-right to bottom-left
    ]
    for diag in diag_combos:
        if all(board[idx] in crossed_set for idx in diag):
            lines_count += 1
            
    return lines_count

def check_winner_bingo(board_state: dict) -> Optional[str]:
    """
    Checks if a player has reached 5 completed lines.
    If both players reach 5 lines simultaneously, compares who has more lines.
    If equal, returns "DRAW".
    """
    lines = board_state.get("player_lines", {})
    if not lines:
        return None
        
    blue_lines = lines.get("BLUE", 0)
    red_lines = lines.get("RED", 0)
    
    if blue_lines >= 5 or red_lines >= 5:
        if blue_lines > red_lines:
            return "BLUE"
        elif red_lines > blue_lines:
            return "RED"
        else:
            return "DRAW"
            
    return None
