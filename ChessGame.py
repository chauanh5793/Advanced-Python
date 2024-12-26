from Piece import *
from Board import *

class ChessGame:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'
        self.en_passant_target = None

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def is_in_bounds(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def parse_position(self, pos):
        try:
            col = ord(pos[0].lower()) - ord('a')
            row = 8 - int(pos[1])
            return (row, col)
        except (IndexError, ValueError):
            return None
        
    def to_algebraic_notation(self, row, col):
        row_notation = 8 - row
        col_notation = chr(col + ord('a'))
        return f"{col_notation}{row_notation}"

    def is_threefold_repetition(self, move_history):
        positions = {}
        for move in move_history:
            if len(move) == 8 and move[4] == "castle":
                _, start_pos, end_pos, _, _, _, rook_start_pos, rook_end_pos = move
                board_state = (start_pos, end_pos, rook_start_pos, rook_end_pos)
            elif len(move) == 6 and move[5] == "en_passant":
                _, start_pos, end_pos, _, en_passant_captured_pos, _ = move
                board_state = (start_pos, end_pos, en_passant_captured_pos)
            elif len(move) == 5:
                _, start_pos, end_pos, _, _ = move
                board_state = (start_pos, end_pos) 
            if board_state in positions:
                positions[board_state] += 1
                if positions[board_state] == 3:
                    return True
            else:
                positions[board_state] = 1
        return False

    def is_fifty_move_rule(self, move_history):
        count = 0
        for move in reversed(move_history):
            if len(move) == 8 and move[4] == "castle":
                piece, _, _, _, _, _, _, _ = move
            elif len(move) == 6 and move[5] == "en_passant":
                piece, _, _, _, _, _ = move
            elif len(move) == 5:
                piece, _, _, target_piece, _ = move
                if isinstance(piece, Pawn) or target_piece is not None:
                    break
            count += 1
            if count >= 50:
                return True
        return False
    
    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None
    
    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        #print(f"King's position {color}: {king_pos}")

        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece and piece.color != color:
                    if piece.is_valid_move((row, col), king_pos, self.board.board):
                        #print(f"The piece at {(row, col)} can attack the king at {king_pos}")
                        return True
        return False
    
    def get_valid_moves(self,piece, start_pos, board, en_passant_target=None, flipped=False):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                end_pos = (row, col)
                if flipped:
                    end_pos = (7 - row, 7 - col)

                if isinstance(piece, Pawn):
                    if piece.is_valid_move(start_pos, end_pos, board, en_passant_target):
                        valid_moves.append(end_pos)
                else:
                    if piece.is_valid_move(start_pos, end_pos, board):
                        valid_moves.append(end_pos)
        return valid_moves
    
    def has_legal_moves(self, color):
        original_turn = self.current_turn
        self.current_turn = color  # Change the turn to the color being checked

        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece and piece.color == color:
                    for r in range(8):
                        for c in range(8):
                            if self.is_valid_move((row, col), (r, c), simulate=True):
                                
                                original_piece = self.board.board[r][c]

                                self.board.move_piece((row, col), (r, c))
                                # Check if the king is still in check
                                in_check = self.is_in_check(color)

                                # Undo the move
                                self.board.move_piece((r, c), (row, col))
                                self.board.board[r][c] = original_piece
                                piece.has_moved = False
                                
                                # If there is any legal move, return True
                                if not in_check:
                                    self.current_turn = original_turn
                                    return True
        self.current_turn = original_turn
        return False
    
    def is_checkmate(self, color):
        if self.is_in_check(color):
            if not self.has_legal_moves(color):
                print(f"Checkmate. {color.capitalize()} loses.")
                return True
        return False
    
    def is_stalemate(self, color):
        if not self.is_in_check(color):
            if not self.has_legal_moves(color):
                print(f"Stalemate. Draw.")
                return True
        return False
    
    def is_square_attacked(self, position, color):
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece and piece.color != color:
                    if self.is_valid_move((row, col), position, simulate=True):
                        return True
        return False
    
    def is_valid_move(self, start_pos, end_pos, en_passant_target=None, simulate=False):
        piece = self.board.board[start_pos[0]][start_pos[1]]
        #target_piece = self.board.board[end_pos[0]][end_pos[1]]

        if start_pos == end_pos or piece is None or (not simulate and piece.color != self.current_turn):
            return False

        if isinstance(piece, King) and abs(start_pos[1] - end_pos[1]) == 2:

            if piece.has_moved:
                return False

            rook_col = 0 if end_pos[1] < start_pos[1] else 7
            rook = self.board.board[start_pos[0]][rook_col]
            
            if not isinstance(rook, Rook) or rook.has_moved:
                return False

            # Check for empty squares between the king and the rook
            step = 1 if end_pos[1] > start_pos[1] else -1
            for col in range(start_pos[1] + step, end_pos[1], step):
                if self.board.board[start_pos[0]][col] is not None:
                    return False
            
            # Check if the king is in check in any square between the king and the rook
            if self.is_in_check(self.current_turn):
                return False
            for col in range(start_pos[1], end_pos[1] + step, step):
                if self.is_square_attacked((start_pos[0], col), self.current_turn):
                    return False
            
            return True

        # Check if the move is valid according to the piece's logic
        if isinstance(piece, Pawn):
            is_valid = piece.is_valid_move(start_pos, end_pos, self.board.board, en_passant_target)
        else:
            is_valid = piece.is_valid_move(start_pos, end_pos, self.board.board)

        if is_valid:
            if simulate:
                piece.has_moved = False
            return True

        return False
