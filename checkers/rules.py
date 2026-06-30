def get_next_turn_checkers(current_color: str) -> str:
    return "RED" if current_color == "BLACK" else "BLACK"

def get_valid_moves(board: list, color: str) -> list:
    """Returns list of (from_pos, to_pos) tuples for all valid moves for the given color."""
    moves = []
    captures = []
    
    own_pieces = ["RED", "RED_KING"] if color == "RED" else ["BLACK", "BLACK_KING"]
    opp_pieces = ["BLACK", "BLACK_KING"] if color == "RED" else ["RED", "RED_KING"]
    
    for pos in range(64):
        piece = board[pos]
        if piece not in own_pieces:
            continue
            
        row, col = pos // 8, pos % 8
        is_king = piece.endswith("_KING")
        
        # Determine forward directions
        if is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif color == "RED":
            directions = [(1, -1), (1, 1)]  # Red moves down
        else:
            directions = [(-1, -1), (-1, 1)]  # Black moves up
        
        for dr, dc in directions:
            # Simple move
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                npos = nr * 8 + nc
                if board[npos] is None:
                    moves.append((pos, npos))
            
            # Capture move
            jr, jc = row + 2 * dr, col + 2 * dc
            mr, mc = row + dr, col + dc
            if 0 <= jr < 8 and 0 <= jc < 8 and 0 <= mr < 8 and 0 <= mc < 8:
                mid_pos = mr * 8 + mc
                jump_pos = jr * 8 + jc
                if board[mid_pos] in opp_pieces and board[jump_pos] is None:
                    captures.append((pos, jump_pos))
    
    # If captures available, must capture (forced capture rule)
    if captures:
        return captures
    return moves

def check_winner_checkers(board_state: dict) -> str:
    """A player wins when their opponent has no pieces left or no valid moves."""
    board = board_state.get("board", [])
    if not board:
        return None
        
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
    
    # Check if current player has any valid moves
    # If RED has no moves, BLACK wins and vice versa
    red_moves = get_valid_moves(board, "RED")
    black_moves = get_valid_moves(board, "BLACK")
    
    if not red_moves:
        return "BLACK"
    if not black_moves:
        return "RED"
        
    return None
