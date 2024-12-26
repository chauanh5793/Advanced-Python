import pygame
from Piece import Pawn, Rook, Knight, Bishop, Queen, King


WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
class Board:

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
        self.move_history = []
        self.redo_stack = []

    def draw_board(self, window, square_size, flipped=False):
        colors = [WHITE, GRAY]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                if flipped:
                    pygame.draw.rect(window, color, ((7 - col) * square_size, (7 - row) * square_size, square_size, square_size))
                else:
                    pygame.draw.rect(window, color, (col * square_size, row * square_size, square_size, square_size))

    def draw_pieces(self, window, IMAGES, square_size, flipped=False):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    piece_name = f"{piece.color}_{piece.__class__.__name__.lower()}"
                    if flipped:
                        window.blit(IMAGES[piece_name], ((7 - col) * square_size, (7 - row) * square_size))
                    else:
                        window.blit(IMAGES[piece_name], (col * square_size, row * square_size))
    
    def promotion_pieces(self, window, IMAGES, square_size, color, option, col, row, flipped=False):
        image = pygame.transform.scale(IMAGES[f"{color}_{option['name']}"], (square_size, square_size))
        if (color == 'black' and not flipped) or (color == 'white' and flipped):
            pygame.draw.rect(window, (203, 203, 203),
                             (col * square_size, (7 - row) * square_size, square_size, square_size))
            window.blit(image, (col * square_size, (7 - row) * square_size))
            option['properties'] = (7 - row, col)
        else:
            pygame.draw.rect(window, (203, 203, 203),
                             (col * square_size, row * square_size, square_size, square_size))
            window.blit(image, (col * square_size, row * square_size))
            option['properties'] = (row, col)

    def setup_pieces(self):
        # Add pawns
        for i in range(8):
            self.board[1][i] = Pawn('black')
            self.board[6][i] = Pawn('white')
        
        # Add other pieces (rooks, knights, bishops, etc.)
        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece in enumerate(placements):
            self.board[0][i] = piece('black')
            self.board[7][i] = piece('white')

    def move_piece(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        target_piece = self.board[end_pos[0]][end_pos[1]]

        # Move the piece
        self.board[end_pos[0]][end_pos[1]] = piece
        self.board[start_pos[0]][start_pos[1]] = None
        piece.has_moved = True

        self.redo_stack.clear()

        piece_moved_before = piece.has_moved

        return piece, start_pos, end_pos, target_piece, piece_moved_before

    def undo_move(self):
        if not self.move_history:
            return
        last_move = self.move_history.pop()

        if len(last_move) == 8 and last_move[4] == "castle":
            # undo castling
            piece, start_pos, end_pos, _, _, rook, rook_start_pos, rook_end_pos = last_move
            self.board[start_pos[0]][start_pos[1]] = piece
            self.board[end_pos[0]][end_pos[1]] = None
            self.board[rook_start_pos[0]][rook_start_pos[1]] = rook
            self.board[rook_end_pos[0]][rook_end_pos[1]] = None

            piece.has_moved = False
            rook.has_moved = False

            self.redo_stack.append((
                piece,  #King
                (start_pos),
                (end_pos),
                None,
                "castle",
                Rook(piece.color),
                rook_start_pos,
                rook_end_pos
            ))
        elif len(last_move) == 7 and last_move[5] == "en_passant":

            piece, start_pos, end_pos, target_piece, piece_moved_before, _, en_passant_captured_pos = last_move
            self.board[start_pos[0]][start_pos[1]] = piece
            self.board[end_pos[0]][end_pos[1]] = None
            piece.has_moved = piece_moved_before
            
            captured_pawn_row, captured_pawn_col = en_passant_captured_pos
            color = None
            if piece.color == 'white':
                color = 'black'
            else:
                color = 'white'
            self.board[captured_pawn_row][captured_pawn_col] = Pawn(color)

            self.redo_stack.append((piece, start_pos, end_pos, target_piece, piece_moved_before, "en_passant", en_passant_captured_pos))
        elif len(last_move) == 5:
            # undo move
            piece, start_pos, end_pos, target_piece, piece_moved_before = last_move
            self.board[start_pos[0]][start_pos[1]] = piece
            self.board[end_pos[0]][end_pos[1]] = target_piece
            if isinstance(piece, King):
                piece.has_moved = False
            else:
                piece.has_moved = piece_moved_before
            self.redo_stack.append((piece, start_pos, end_pos, target_piece, piece_moved_before))      


    def redo_move(self):
        if self.redo_stack:
       
            move = self.redo_stack.pop()

            if len(move) == 8 and move[4] == "castle":
                piece, start_pos, end_pos, target_piece, _, rook, rook_start_pos, rook_end_pos = move
                
                # Move the king
                self.board[start_pos[0]][start_pos[1]] = None
                self.board[end_pos[0]][end_pos[1]] = piece
                piece.has_moved = True

                # Move the rook
                self.board[rook_start_pos[0]][rook_start_pos[1]] = None
                self.board[rook_end_pos[0]][rook_end_pos[1]] = rook
                rook.has_moved = True

                self.move_history.append((
                    piece,
                    (start_pos),
                    (end_pos),
                    None,
                    "castle",
                    Rook(piece.color),
                    rook_start_pos,
                    rook_end_pos
                ))

            elif len(move) == 7 and move[5] == "en_passant":
                # Handle en passant
                piece, start_pos, end_pos, target_piece, piece_moved_before,  _, en_passant_captured_pos = move
                
                # Move the pawn that performed en passant
                self.board[start_pos[0]][start_pos[1]] = None
                self.board[end_pos[0]][end_pos[1]] = piece
                piece.has_moved = piece_moved_before

                # Restore the captured pawn
                captured_row, captured_col = en_passant_captured_pos
                self.board[captured_row][captured_col] = target_piece

                self.move_history.append(move)

            else:
                piece, start_pos, end_pos, target_piece, piece_moved_before = move
                self.board[start_pos[0]][start_pos[1]] = None
                if isinstance(piece, Pawn) and piece.color == 'white' and end_pos[0] == 0 or isinstance(piece, Pawn) and piece.color == 'black' and end_pos[0] == 7:
                    self.board[end_pos[0]][end_pos[1]] = piece.promotion
                else:
                    self.board[end_pos[0]][end_pos[1]] = piece
                piece.has_moved = piece_moved_before

                self.move_history.append((piece, start_pos, end_pos, target_piece, True))
        
        
        
