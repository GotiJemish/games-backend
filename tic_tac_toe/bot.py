import random
from typing import List, Optional
from .rules import check_winner_ttt, get_next_turn_ttt

def get_bot_move(board: List[Optional[str]], bot_color: str, difficulty: str) -> int:
    """
    Computes bot move based on difficulty level.
    Returns board position index (0 to 8).
    """
    empty_indices = [i for i, cell in enumerate(board) if cell is None]
    if not empty_indices:
        raise ValueError("No empty positions on the board.")
        
    difficulty = difficulty.lower()
    
    # 1. Easy mode: Random moves
    if difficulty == "easy":
        return random.choice(empty_indices)
        
    # 2. Medium mode: Win/Block, else random
    opponent_color = get_next_turn_ttt(bot_color)
    if difficulty == "medium":
        # Check if we can win in one move
        for move in empty_indices:
            board_copy = list(board)
            board_copy[move] = bot_color
            if check_winner_ttt(board_copy) == bot_color:
                return move
                
        # Check if opponent can win in one move and block them
        for move in empty_indices:
            board_copy = list(board)
            board_copy[move] = opponent_color
            if check_winner_ttt(board_copy) == opponent_color:
                return move
                
        # Otherwise, random choice
        return random.choice(empty_indices)
        
    # 3. Hard mode: Optimal minimax
    best_val = -1000
    best_move = empty_indices[0]
    
    for move in empty_indices:
        board_copy = list(board)
        board_copy[move] = bot_color
        
        # Call minimax for opponent's turn (minimize score)
        move_val = minimax(board_copy, 0, False, bot_color, opponent_color)
        
        if move_val > best_val:
            best_val = move_val
            best_move = move
            
    return best_move

def minimax(board: List[Optional[str]], depth: int, is_max: bool, bot_color: str, opp_color: str) -> int:
    winner = check_winner_ttt(board)
    if winner == bot_color:
        return 10 - depth
    if winner == opp_color:
        return depth - 10
    if winner == "DRAW":
        return 0
        
    empty_indices = [i for i, cell in enumerate(board) if cell is None]
    
    if is_max:
        best = -1000
        for move in empty_indices:
            board[move] = bot_color
            val = minimax(board, depth + 1, False, bot_color, opp_color)
            board[move] = None
            best = max(best, val)
        return best
    else:
        best = 1000
        for move in empty_indices:
            board[move] = opp_color
            val = minimax(board, depth + 1, True, bot_color, opp_color)
            board[move] = None
            best = min(best, val)
        return best
