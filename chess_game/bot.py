import chess
import random

def evaluate_board(board: chess.Board) -> float:
    """
    Evaluates the board state. Positive score favors White, negative favors Black.
    """
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -99999.0  # Black wins
        else:
            return 99999.0   # White wins
    if board.is_game_over():
        return 0.0           # Draw
        
    piece_values = {
        chess.PAWN: 10.0,
        chess.KNIGHT: 30.0,
        chess.BISHOP: 30.0,
        chess.ROOK: 50.0,
        chess.QUEEN: 90.0,
        chess.KING: 9000.0
    }
    
    score = 0.0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = piece_values[piece.piece_type]
            
            # Positional bonuses: encourage center control
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            center_bonus = 0.0
            if rank in [3, 4] and file in [3, 4]:
                center_bonus = 2.0
            elif rank in [2, 5] and file in [2, 5]:
                center_bonus = 0.5
                
            val += center_bonus
            
            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val
    return score

def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> tuple[float, chess.Move | None]:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None
        
    best_move = None
    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves)  # Add variety for equal evaluations
    
    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

def get_bot_move(fen: str, difficulty: str = "medium") -> str:
    """
    Computes the best chess move for the current player using minimax search.
    """
    board = chess.Board(fen)
    if board.is_game_over():
        return ""
        
    depth = 2
    if difficulty == "easy":
        depth = 1
    elif difficulty == "medium":
        depth = 2
    elif difficulty == "hard":
        depth = 3
        
    # For Easy difficulty, make a random legal move 30% of the time
    if difficulty == "easy" and random.random() < 0.3:
        return str(random.choice(list(board.legal_moves)))
        
    is_maximizing = (board.turn == chess.WHITE)
    _, move = minimax(board, depth, -float('inf'), float('inf'), is_maximizing)
    
    if move:
        return str(move)
    return str(random.choice(list(board.legal_moves)))
