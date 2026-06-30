from checkers.rules import get_valid_moves


def initialize_board(difficulty: str = "medium") -> dict:
    board = [None] * 64
    
    # Rows 0, 1, 2 are Red pieces on dark cells (row + col % 2 == 1)
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row * 8 + col] = "RED"
                
    # Rows 5, 6, 7 are Black pieces on dark cells
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row * 8 + col] = "BLACK"
                
    return {
        "board": board,
        "difficulty": difficulty
    }


def make_move(board_state: dict, color: str, from_pos: int, to_pos: int) -> tuple:
    """
    Execute a checkers move. Returns (new_board_state, success, description).
    Supports simple moves, single captures, and validates ownership & direction.
    """
    board = list(board_state.get("board", []))
    if not board:
        return board_state, False, "Board is uninitialized."
        
    if from_pos < 0 or from_pos >= 64 or to_pos < 0 or to_pos >= 64:
        return board_state, False, "Coordinates out of bounds."
        
    piece = board[from_pos]
    if not piece:
        return board_state, False, "No piece exists at selected position."
    
    # Check ownership
    own_pieces = ["RED", "RED_KING"] if color == "RED" else ["BLACK", "BLACK_KING"]
    if piece not in own_pieces:
        return board_state, False, "You do not own the selected piece."
    
    # Validate the move is in the valid moves list
    valid_moves = get_valid_moves(board, color)
    if (from_pos, to_pos) not in valid_moves:
        # Check if captures are available but player tried a simple move
        opp_pieces = ["BLACK", "BLACK_KING"] if color == "RED" else ["RED", "RED_KING"]
        has_captures = any(abs(f // 8 - t // 8) == 2 for f, t in valid_moves)
        if has_captures and abs(from_pos // 8 - to_pos // 8) == 1:
            return board_state, False, "You must capture when a jump is available."
        return board_state, False, "Invalid move."
    
    to_row, to_col = to_pos // 8, to_pos % 8
    from_row, from_col = from_pos // 8, from_pos % 8
    row_diff = abs(to_row - from_row)
    
    is_capture = row_diff == 2
    desc = ""
    
    if is_capture:
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        mid_pos = mid_row * 8 + mid_col
        
        board[from_pos] = None
        board[mid_pos] = None  # Captured!
        
        # King promotion
        is_kinged = False
        if piece == "RED" and to_row == 7:
            board[to_pos] = "RED_KING"
            is_kinged = True
        elif piece == "BLACK" and to_row == 0:
            board[to_pos] = "BLACK_KING"
            is_kinged = True
        else:
            board[to_pos] = piece
            
        desc = f"Captured piece at cell {mid_pos}"
        if is_kinged:
            desc += " and promoted to KING!"
            
        # Check for chain jumps (multi-jump)
        new_piece = board[to_pos]
        can_chain = False
        if not is_kinged:  # No chain after kinging
            chain_moves = get_valid_moves(board, color)
            chain_captures = [(f, t) for f, t in chain_moves if f == to_pos and abs(f // 8 - t // 8) == 2]
            if chain_captures:
                can_chain = True
        
        new_state = {
            "board": board,
            "difficulty": board_state.get("difficulty", "medium")
        }
        
        if can_chain:
            new_state["chain_from"] = to_pos
            desc += " (chain jump available!)"
        else:
            new_state.pop("chain_from", None)
            
        return new_state, True, desc
    else:
        # Simple move
        board[from_pos] = None
        
        is_kinged = False
        if piece == "RED" and to_row == 7:
            board[to_pos] = "RED_KING"
            is_kinged = True
        elif piece == "BLACK" and to_row == 0:
            board[to_pos] = "BLACK_KING"
            is_kinged = True
        else:
            board[to_pos] = piece
            
        desc = f"Moved from cell {from_pos} to {to_pos}"
        if is_kinged:
            desc += " and promoted to KING!"
            
        new_state = {
            "board": board,
            "difficulty": board_state.get("difficulty", "medium")
        }
        return new_state, True, desc
