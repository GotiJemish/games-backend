import chess
from typing import Dict, Any, Tuple

def initialize_board(difficulty: str = "medium") -> dict:
    """
    Initializes chess board state.
    """
    return {
        "fen": chess.STARTING_FEN,
        "history": [],
        "difficulty": difficulty
    }

def make_move(board_state: dict, move_uci: str) -> Tuple[dict, bool, str]:
    """
    Simulates or executes a move on the chess board.
    move_uci is coordinate notation (e.g. 'e2e4', 'e7e8q').
    Returns (new_board_state, success, move_desc).
    """
    fen = board_state.get("fen", chess.STARTING_FEN)
    board = chess.Board(fen)
    
    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError:
        return board_state, False, f"Invalid move format: {move_uci}"
        
    if move not in board.legal_moves:
        # Check if it was a pawn promotion that was sent without the promotion piece suffix (e.g., e7e8 instead of e7e8q)
        pawn_promotion_move = None
        for legal_move in board.legal_moves:
            if legal_move.from_square == move.from_square and legal_move.to_square == move.to_square and legal_move.promotion:
                # If a promotion is possible, default to Queen promotion if not specified
                pawn_promotion_move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
                break
        
        if pawn_promotion_move and pawn_promotion_move in board.legal_moves:
            move = pawn_promotion_move
        else:
            return board_state, False, f"Illegal move: {move_uci}"
            
    # Keep track of moving piece details for the description
    piece = board.piece_at(move.from_square)
    piece_name = piece.symbol().upper() if piece else "Piece"
    from_name = chess.square_name(move.from_square)
    to_name = chess.square_name(move.to_square)
    
    # Execute the move
    board.push(move)
    
    new_history = list(board_state.get("history", []))
    new_history.append(move.uci())
    
    new_board_state = {
        **board_state,
        "fen": board.fen(),
        "history": new_history
    }
    
    move_desc = f"{piece_name} moved from {from_name} to {to_name}."
    if board.is_checkmate():
        move_desc += " Checkmate!"
    elif board.is_check():
        move_desc += " Check!"
        
    return new_board_state, True, move_desc
