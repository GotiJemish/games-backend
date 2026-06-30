import random
from checkers.rules import get_valid_moves, check_winner_checkers


def get_bot_move(board_state: dict, bot_color: str, difficulty: str = "medium") -> tuple:
    """
    Returns (from_pos, to_pos) for the bot's move.
    Returns None if no moves available.
    """
    board = board_state.get("board", [])
    valid_moves = get_valid_moves(board, bot_color)
    
    if not valid_moves:
        return None
    
    difficulty = difficulty.lower()
    
    if difficulty == "easy":
        return random.choice(valid_moves)
    
    opp_color = "RED" if bot_color == "BLACK" else "BLACK"
    
    if difficulty == "medium":
        # Prefer captures, then center moves, else random
        captures = [(f, t) for f, t in valid_moves if abs(f // 8 - t // 8) == 2]
        if captures:
            return random.choice(captures)
        
        # Prefer center moves
        center_moves = [(f, t) for f, t in valid_moves if 2 <= (t % 8) <= 5 and 2 <= (t // 8) <= 5]
        if center_moves:
            return random.choice(center_moves)
            
        return random.choice(valid_moves)
    
    # Hard mode: minimax with alpha-beta pruning
    best_score = float('-inf')
    best_move = valid_moves[0]
    
    for move in valid_moves:
        board_copy = list(board)
        score = evaluate_move(board_copy, move, bot_color, opp_color, depth=4)
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move


def evaluate_move(board: list, move: tuple, bot_color: str, opp_color: str, depth: int) -> float:
    """Simulate a move and run minimax."""
    board_copy = list(board)
    from_pos, to_pos = move
    
    # Apply the move
    apply_move(board_copy, from_pos, to_pos)
    
    return minimax(board_copy, depth - 1, False, bot_color, opp_color, float('-inf'), float('inf'))


def apply_move(board: list, from_pos: int, to_pos: int):
    """Apply a move directly to the board list (mutates board)."""
    piece = board[from_pos]
    from_row = from_pos // 8
    to_row = to_pos // 8
    
    board[from_pos] = None
    
    # Check for capture
    if abs(from_row - to_row) == 2:
        mid_row = (from_row + to_row) // 2
        from_col = from_pos % 8
        to_col = to_pos % 8
        mid_col = (from_col + to_col) // 2
        mid_pos = mid_row * 8 + mid_col
        board[mid_pos] = None
    
    # King promotion
    if piece == "RED" and to_row == 7:
        board[to_pos] = "RED_KING"
    elif piece == "BLACK" and to_row == 0:
        board[to_pos] = "BLACK_KING"
    else:
        board[to_pos] = piece


def evaluate_board(board: list, bot_color: str, opp_color: str) -> float:
    """Evaluate the board state for the bot."""
    score = 0.0
    
    bot_pieces = ["RED", "RED_KING"] if bot_color == "RED" else ["BLACK", "BLACK_KING"]
    opp_pieces = ["RED", "RED_KING"] if opp_color == "RED" else ["BLACK", "BLACK_KING"]
    
    for pos in range(64):
        piece = board[pos]
        if piece is None:
            continue
            
        row, col = pos // 8, pos % 8
        
        if piece in bot_pieces:
            # Base value
            if piece.endswith("_KING"):
                score += 5.0
            else:
                score += 3.0
            
            # Center control bonus
            if 2 <= row <= 5 and 2 <= col <= 5:
                score += 0.5
                
            # Advancement bonus (closer to promotion)
            if bot_color == "RED":
                score += row * 0.1
            else:
                score += (7 - row) * 0.1
                
        elif piece in opp_pieces:
            if piece.endswith("_KING"):
                score -= 5.0
            else:
                score -= 3.0
            
            if 2 <= row <= 5 and 2 <= col <= 5:
                score -= 0.5
    
    return score


def minimax(board: list, depth: int, is_maximizing: bool, 
            bot_color: str, opp_color: str, alpha: float, beta: float) -> float:
    """Minimax with alpha-beta pruning."""
    # Check terminal states
    winner = check_winner_from_board(board)
    if winner == bot_color:
        return 100 + depth
    elif winner == opp_color:
        return -100 - depth
    
    if depth <= 0:
        return evaluate_board(board, bot_color, opp_color)
    
    current_color = bot_color if is_maximizing else opp_color
    moves = get_valid_moves(board, current_color)
    
    if not moves:
        return -100 if is_maximizing else 100
    
    if is_maximizing:
        max_eval = float('-inf')
        for move in moves:
            board_copy = list(board)
            apply_move(board_copy, move[0], move[1])
            eval_score = minimax(board_copy, depth - 1, False, bot_color, opp_color, alpha, beta)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board_copy = list(board)
            apply_move(board_copy, move[0], move[1])
            eval_score = minimax(board_copy, depth - 1, True, bot_color, opp_color, alpha, beta)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def check_winner_from_board(board: list) -> str:
    """Check winner directly from board array without wrapping in dict."""
    red_count = 0
    black_count = 0
    
    for cell in board:
        if cell in ["RED", "RED_KING"]:
            red_count += 1
        elif cell in ["BLACK", "BLACK_KING"]:
            black_count += 1
            
    if red_count == 0:
        return "BLACK"
    if black_count == 0:
        return "RED"
    
    red_moves = get_valid_moves(board, "RED")
    black_moves = get_valid_moves(board, "BLACK")
    
    if not red_moves:
        return "BLACK"
    if not black_moves:
        return "RED"
        
    return None
