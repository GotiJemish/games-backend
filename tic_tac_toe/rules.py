from typing import List, Optional

def get_next_turn_ttt(current: str) -> str:
    """
    Alternates between X and O.
    """
    return "O" if current == "X" else "X"

def check_winner_ttt(board: List[Optional[str]]) -> Optional[str]:
    """
    Checks the Tic-Tac-Toe board for a winner.
    Board is a flat list of size 9.
    Returns:
        - "X" if X wins
        - "O" if O wins
        - "DRAW" if the board is full and there's no winner
        - None if the game is still active
    """
    winning_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    
    for combo in winning_combos:
        if board[combo[0]] is not None and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
            
    # Check if draw (no empty cells)
    if all(cell is not None for cell in board):
        return "DRAW"
        
    return None
