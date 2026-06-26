import chess

def get_next_turn_chess(current: str) -> str:
    """
    Alternates between WHITE and BLACK.
    """
    return "BLACK" if current == "WHITE" else "WHITE"

def is_game_over(fen: str) -> tuple[bool, str | None]:
    """
    Checks if the game is over. Returns (is_over, winner_color).
    winner_color can be 'WHITE', 'BLACK', 'DRAW', or None if not over.
    """
    board = chess.Board(fen)
    if board.is_game_over():
        if board.is_checkmate():
            # If it is checkmate, the player whose turn it is lost.
            # So the opponent won.
            winner = "BLACK" if board.turn == chess.WHITE else "WHITE"
            return True, winner
        else:
            return True, "DRAW"
    return False, None
