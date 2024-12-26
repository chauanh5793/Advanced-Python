class Piece:
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, start, end, board):
        pass

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
        self.promotion = None

    def is_valid_move(self, start, end, board, en_passant_target=None):
        direction = -1 if self.color == 'white' else 1
        start_row, start_col = start
        end_row, end_col = end

        # Move forward
        if start_col == end_col:
            # One step move
            if end_row == start_row + direction and board[end_row][end_col] is None:
                return True
            # Initial two-step move
            """ not self.has_moved """
            if  (start_row == 6 or start_row==1) and end_row == start_row + 2 * direction and board[end_row][end_col] is None and board[start_row + direction][end_col] is None:
                return True

        # Capture diagonally
        if abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if board[end_row][end_col] is not None and board[end_row][end_col].color != self.color:
                return True
            # En Passant
            if en_passant_target and en_passant_target == (end_row, end_col):
                captured_pawn_row = start_row
                captured_pawn = board[captured_pawn_row][end_col]
                if captured_pawn and captured_pawn.color != self.color and isinstance(captured_pawn, Pawn):
                    return True

        return False

    def promote(self, end):
        end_row, _ = end
        if (self.color == 'white' and end_row == 0) or (self.color == 'black' and end_row == 7):
            return True
        return False

class Rook(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
    
    def is_valid_move(self, start, end, board):
        # Straight line movement (horizontal or vertical)
        start_row, start_col = start
        end_row, end_col = end
        # Check that the movement is in a straight line
        if start_row == end_row or start_col == end_col:
            # Validate that there are no pieces in the way
            if self.clear_path(start, end, board):
                target_piece = board[end_row][end_col]
                # Ensure not moving to a square occupied by a piece of the same color
                if target_piece is None or target_piece.color != self.color:
                    return True
        return False

    def clear_path(self, start, end, board):
        # Check that the path is clear between start and end
        start_row, start_col = start
        end_row, end_col = end
        step_row = (end_row - start_row) // max(1, abs(end_row - start_row))
        step_col = (end_col - start_col) // max(1, abs(end_col - start_col))
        current_row, current_col = start_row + step_row, start_col + step_col

        while (current_row, current_col) != (end_row, end_col):
            if board[current_row][current_col] is not None:
                return False
            current_row += step_row
            current_col += step_col
        return True

class Knight(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Knight movement
        if (row_diff, col_diff) in [(2, 1), (1, 2)]:
            # Check that the target square is not occupied by a piece of the same color
            target_piece = board[end_row][end_col]
            if target_piece is not None and target_piece.color == board[start_row][start_col].color:
                return False
            return True
        
        return False

class Bishop(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end
        # Diagonal movement
        if abs(start_row - end_row) == abs(start_col - end_col):
            # Check that there are no pieces in the way
            if self.clear_path(start, end, board):
                # Check that the target square is not occupied by a piece of the same color
                target_piece = board[end_row][end_col]
                if target_piece is not None and target_piece.color == board[start_row][start_col].color:
                    return False
                return True
        
        return False

    def clear_path(self, start, end, board):
        step_row = 1 if end[0] > start[0] else -1
        step_col = 1 if end[1] > start[1] else -1
        current_row, current_col = start[0] + step_row, start[1] + step_col

        while (current_row, current_col) != (end[0], end[1]):
            if board[current_row][current_col] is not None:
                return False
            current_row += step_row
            current_col += step_col
        return True

class Queen(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def is_valid_move(self, start, end, board):
        # Combines rook and bishop movements
        return Rook(self.color).is_valid_move(start, end, board) or Bishop(self.color).is_valid_move(start, end, board)

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Normal king movement
        if row_diff <= 1 and col_diff <= 1:
            # Check that the target square is not occupied by a piece of the same color
            target_piece = board[end_row][end_col]
            if target_piece is not None and target_piece.color == board[start_row][start_col].color:
                return False
            return True
        # Castling
        if not self.has_moved and row_diff == 0 and col_diff == 2:
            rook_col = 0 if end_col < start_col else 7
            rook = board[start_row][rook_col]
            if isinstance(rook, Rook) and not rook.has_moved:
                step = 1 if end_col > start_col else -1
                for col in range(start_col + step, end_col, step):
                    if board[start_row][col] is not None:
                        return False
                return True

        return False
