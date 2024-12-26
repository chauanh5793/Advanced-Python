import pygame
import os
from ChessGame import ChessGame
from Piece import *
from config import FLIP_BOARD, INITIAL_TIME

# Initialize pygame
pygame.init()

# Set up the window
BOARD_WIDTH, BOARD_HEIGHT = 640, 640
INFO_WIDTH = 200
WINDOW_WIDTH = BOARD_WIDTH + INFO_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chess")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Size of the squares
SQUARE_SIZE = BOARD_WIDTH // 8

# Load piece images
def load_images():
    pieces = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
    colors = ['white', 'black']
    images = {}
    for color in colors:
        for piece in pieces:
            image_path = os.path.join("images", f"{color}_{piece}.png")
            images[f"{color}_{piece}"] = pygame.transform.scale(
                pygame.image.load(image_path), (SQUARE_SIZE, SQUARE_SIZE))
    return images
def pieces_captured_images():
    pieces = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
    colors = ['white', 'black']
    images = {}
    for color in colors:
        for piece in pieces:
            image_path = os.path.join("images", f"{color}_{piece}.png")
            images[f"{color}_{piece}"] = pygame.transform.scale(
                pygame.image.load(image_path), (SQUARE_SIZE/3, SQUARE_SIZE/3))
    return images

IMAGES = load_images()
PIECES_CAPTURED_IMAGES = pieces_captured_images()
def get_board_coords(pos, flipped=False):
    x, y = pos
    row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
    if flipped:
        return 7 - row, 7 - col
    return row, col

def draw_king_in_check(window, board, color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color and isinstance(piece, King):
                pygame.draw.rect(window, (255, 0, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
                break

def draw_valid_moves(window, valid_moves, flipped=False):
    for move in valid_moves:
        row, col = move
        if flipped:
            row, col = 7 - row, 7 - col
        pygame.draw.rect(window, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_last_move(window, start_pos, end_pos, flipped=False):
    if start_pos:
        start_row, start_col = start_pos
        if flipped:
            start_row, start_col = 7 - start_row, 7 - start_col
        pygame.draw.rect(window, (255, 255, 0), (start_col * SQUARE_SIZE, start_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
    if end_pos:
        end_row, end_col = end_pos
        if flipped:
            end_row, end_col = 7 - end_row, 7 - end_col
        pygame.draw.rect(window, (255, 255, 0), (end_col * SQUARE_SIZE, end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_turn(window, turn):
    pygame.draw.rect(window, WHITE, (BOARD_WIDTH, 10, INFO_WIDTH, WINDOW_HEIGHT - 10))
    font = pygame.font.Font(None, 36)
    text = font.render(f"Turn: {turn.capitalize()}", True, BLACK)
    window.blit(text, (BOARD_WIDTH + 10, 10))

def pieces_captured(window, board):
    pieces_category = {'pawn': 8, 'rook': 2, 'knight': 2, 'bishop': 2, 'queen': 1, 'king': 1}
    colors = ['white', 'black']

    start_line = 90
    for i, color in enumerate(colors):
        if i > 0:
            start_line = start_line +75
        list_captured = []
        pieces_on_the_board = []

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece:
                    obj = {
                        'name': piece.__class__.__name__.lower(),
                        'color': piece.color,
                    }
                    if piece.color == color:
                        pieces_on_the_board.append(obj)
        for pc in pieces_category.items():
            pieces_on = 0
            for pot in pieces_on_the_board:
                if pc[0] == pot['name']:
                    pieces_on = pieces_on + 1
            captured = pc[1] - pieces_on
            for w in range(captured):
                piece_name = f"{color}_{pc[0]}"
                list_captured.append(piece_name)
        marginTop = 0
        marginLeft = 0
        for index, value in enumerate(list_captured):
            marginLeft = marginLeft + 1
            if index % 7 == 0:
                marginTop = marginTop + 30
                marginLeft = 1
            window.blit(PIECES_CAPTURED_IMAGES[value], (BOARD_WIDTH + 10 + (marginLeft - 1) * 25, start_line + marginTop))

def choose_promotion_piece(window, color, game, end_row, end_col, flipped):
    font = pygame.font.Font(None, 36)
    options = [
        {'name': 'queen', 'properties': None},
        {'name': 'rook', 'properties': None},
        {'name': 'bishop', 'properties': None},
        {'name': 'knight', 'properties': None}
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_board_coords(pos, flipped)
                for i, option in enumerate(options):
                    row_pice, col_pice = option['properties']
                    if row == row_pice and col == col_pice:
                        if option['name'] == 'queen':
                            return Queen(color)
                        elif option['name'] == 'rook':
                            return Rook(color)
                        elif option['name'] == 'bishop':
                            return Bishop(color)
                        elif option['name'] == 'knight':
                            return Knight(color)
        game.board.draw_board(window, SQUARE_SIZE, flipped)
        game.board.draw_pieces(window, IMAGES, SQUARE_SIZE, flipped)
        for i, option in enumerate(options):
            game.board.promotion_pieces(window, IMAGES, SQUARE_SIZE,color,option,end_col,i, flipped)
        pygame.display.flip()

def draw_move_history(window, move_history, scroll_offset, game):
    font = pygame.font.Font(None, 24)
    subtitle_font = pygame.font.Font(None, 28)
    x, y = BOARD_WIDTH + 10, 300
    max_visible_moves = 10
    visible_moves = move_history[scroll_offset:scroll_offset + max_visible_moves]
    
    # Clear the area where the move history will be drawn
    pygame.draw.rect(window, WHITE, (BOARD_WIDTH, 130, INFO_WIDTH, WINDOW_HEIGHT - 300))

    subtitle_text = subtitle_font.render("Move History", True, BLACK)
    window.blit(subtitle_text, (x, y))
    y += 40  # Move down for the next move
    
    for i, move in enumerate(visible_moves):
        if len(move) == 8 and move[4] == "castle":
            piece, start_pos, end_pos, _, _, rook, rook_start_pos, rook_end_pos = move
            move_text = f"{scroll_offset + i + 1}. {piece.__class__.__name__[0]}{game.to_algebraic_notation(start_pos[0], start_pos[1])} -> {game.to_algebraic_notation(end_pos[0], end_pos[1])} (0-0)"
        elif len(move) == 7 and move[5] == "en_passant":
            piece, start_pos, end_pos, _, _, _, _ = move
            move_text = f"{scroll_offset + i + 1}. {piece.__class__.__name__[0]}{game.to_algebraic_notation(start_pos[0], start_pos[1])} -> {game.to_algebraic_notation(end_pos[0], end_pos[1])}"
        elif len(move) == 5:
            piece, start_pos, end_pos, target_piece, piece_moved_before = move
            move_text = f"{scroll_offset + i + 1}. {piece.__class__.__name__[0]}{game.to_algebraic_notation(start_pos[0], start_pos[1])} -> {game.to_algebraic_notation(end_pos[0], end_pos[1])}"

        text = font.render(move_text, True, BLACK)
        window.blit(text, (x, y))
        y += 20  # Move down for the next move

def draw_clock(window, white_time, black_time):

    pygame.draw.rect(window, WHITE, (BOARD_WIDTH + 10, 200, INFO_WIDTH - 20, 100))

    font = pygame.font.Font(None, 36)
    white_minutes = int(white_time // 60)
    white_seconds = int(white_time % 60)
    black_minutes = int(black_time // 60)
    black_seconds = int(black_time % 60)
    white_text = font.render(f"White: {white_minutes}:{white_seconds:02d}", True, BLACK)
    black_text = font.render(f"Black: {black_minutes}:{black_seconds:02d}", True, BLACK)
    window.blit(white_text, (BOARD_WIDTH + 10, 50))
    window.blit(black_text, (BOARD_WIDTH + 10, 80))

def main_menu():
    font = pygame.font.Font(None, 74)
    text = font.render("Play Chess", True, BLACK)
    text_rect = text.get_rect(center=((BOARD_WIDTH + INFO_WIDTH) // 2, BOARD_HEIGHT // 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

        WINDOW.fill(WHITE)
        WINDOW.blit(text, text_rect)
        pygame.display.flip()

def game_over(winner):
    font = pygame.font.Font(None, 74)
    text = font.render(f"{winner}", True, BLACK)
    text_rect = text.get_rect(center=((BOARD_WIDTH + INFO_WIDTH) // 2, BOARD_HEIGHT // 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

        WINDOW.fill(WHITE)
        WINDOW.blit(text, text_rect)
        pygame.display.flip()

# Main loop
def main():
    main_menu()
    game = ChessGame()
    clock = pygame.time.Clock()
    selected_piece = None
    running = True
    en_passant_target = None
    valid_moves = []

    dragging_piece = False
    dragging_piece_pos = None

    last_move_start = None
    last_move_end = None

    board_flipped = FLIP_BOARD
    if board_flipped:
        board_flipped = False

    white_time = INITIAL_TIME
    black_time = INITIAL_TIME
    last_time_update = pygame.time.get_ticks()

    scroll_offset = 0  # Scroll offset for move history

    while running:

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - last_time_update) / 1000
        last_time_update = current_time

        if game.current_turn == 'white':
            white_time -= elapsed_time
        else:
            black_time -= elapsed_time

        if white_time <= 0:
            game_over("Black Wins")
            running = False
        elif black_time <= 0:
            game_over("White Wins")
            running = False

        if game.is_threefold_repetition(game.board.move_history):
            game_over("DRAW")
            running = False
        elif game.is_fifty_move_rule(game.board.move_history):
            game_over("DRAW")
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  # Undo move
                    if game.board.move_history:
                        game.board.undo_move()
                        game.switch_turn()
                        if FLIP_BOARD:
                            board_flipped = not board_flipped
                elif event.key == pygame.K_RIGHT:  # Redo move
                    if game.board.redo_stack:
                        game.board.redo_move()
                        game.switch_turn()
                        if FLIP_BOARD:
                            board_flipped = not board_flipped
                elif event.key == pygame.K_UP:  # Scroll up
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.key == pygame.K_DOWN:  # Scroll down
                    scroll_offset = min(len(game.board.move_history) - 5, scroll_offset + 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_board_coords(pos, board_flipped)
                piece = game.board.board[row][col]
                if piece and piece.color == game.current_turn:
                    selected_piece = (row, col)
                    dragging_piece = True
                    dragging_piece_pos = pos
                    valid_moves = game.get_valid_moves(piece, selected_piece, game.board.board, en_passant_target, board_flipped)
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_piece:
                    pos = pygame.mouse.get_pos()
                    end_row, end_col = get_board_coords(pos, board_flipped)
                    if (end_row, end_col) in valid_moves and game.is_valid_move(selected_piece, (end_row, end_col), en_passant_target):
                        move = game.board.move_piece(selected_piece, (end_row, end_col))
                        last_move_start = selected_piece
                        last_move_end = (end_row, end_col)

                        if game.is_in_check(game.current_turn):
                            print(f"{game.current_turn.capitalize()} is in check. Invalid move.")
                            game.board.move_piece((end_row, end_col), selected_piece)
                            game.board.board[end_row][end_col] = move[3]
                            piece.has_moved = False
                        else:
                            # En passant capture, promotion, castling
                            if isinstance(piece, Pawn) and en_passant_target == (end_row, end_col):
                                captured_pawn_row = selected_piece[0]
                                captured_pawn_pos = (captured_pawn_row, end_col)
                                game.board.board[captured_pawn_row][end_col] = None
                                move += ("en_passant", captured_pawn_pos)
                            if isinstance(piece, Pawn) and piece.promote((end_row, end_col)):
                                promoted_piece = choose_promotion_piece(WINDOW, piece.color, game,end_row, end_col, board_flipped)
                                piece.promotion = promoted_piece
                                game.board.board[end_row][end_col] = promoted_piece
                            if isinstance(piece, King) and abs(selected_piece[1] - end_col) == 2:
                                rook_start_col = 0 if end_col < selected_piece[1] else 7
                                rook_end_col = 3 if end_col < selected_piece[1] else 5

                                rook_start_pos = (selected_piece[0], rook_start_col)
                                rook_end_pos = (selected_piece[0], rook_end_col)
                                game.board.move_piece(rook_start_pos, rook_end_pos)

                                game.board.move_history.append((
                                    piece,  # El rey
                                    (selected_piece[0], selected_piece[1]),
                                    (selected_piece[0], end_col),
                                    None,
                                    "castle",
                                    Rook(piece.color),
                                    rook_start_pos,
                                    rook_end_pos
                                ))
                            else:
                                game.board.move_history.append(move)

                            opponent_color = 'black' if game.current_turn == 'white' else 'white'
                            

                            # En passant update
                            if isinstance(piece, Pawn) and abs(selected_piece[0] - end_row) == 2:
                                en_passant_target = ((selected_piece[0] + end_row) // 2, end_col)
                            else:
                                en_passant_target = None

                            if game.is_stalemate(opponent_color):
                                game_over("DRAW")
                                running = False
                            if game.is_checkmate(opponent_color):
                                print(f"Checkmate. {opponent_color.capitalize()} loses.")
                                game_over(f"{opponent_color.capitalize()} loses")
                                running = False
                            elif game.is_in_check(opponent_color):
                                print(f"{opponent_color.capitalize()} is in check.")

                            # Turn change and flipp the board
                            game.switch_turn()
                            if FLIP_BOARD:
                                board_flipped = not board_flipped

                            

                    selected_piece = None
                    dragging_piece = False
                    valid_moves = []
            elif event.type == pygame.MOUSEMOTION:
                if dragging_piece:
                    dragging_piece_pos = event.pos

        game.board.draw_board(WINDOW, SQUARE_SIZE, board_flipped)
        draw_last_move(WINDOW, last_move_start, last_move_end, board_flipped)
        game.board.draw_pieces(WINDOW, IMAGES, SQUARE_SIZE, board_flipped)
        draw_valid_moves(WINDOW, valid_moves, flipped=board_flipped)
        draw_turn(WINDOW, game.current_turn)
        draw_move_history(WINDOW, game.board.move_history,scroll_offset, game)
        draw_clock(WINDOW, white_time, black_time)
        
        pieces_captured(WINDOW, game.board.board)
        if game.is_in_check(game.current_turn):
            draw_king_in_check(WINDOW, game.board.board, game.current_turn)
        if dragging_piece and selected_piece:
            piece = game.board.board[selected_piece[0]][selected_piece[1]]
            piece_name = f"{piece.color}_{piece.__class__.__name__.lower()}"
            WINDOW.blit(IMAGES[piece_name], (dragging_piece_pos[0] - SQUARE_SIZE // 2, dragging_piece_pos[1] - SQUARE_SIZE // 2))
        pygame.display.flip()
        clock.tick(60)


        if game.is_in_check(game.current_turn):
            draw_king_in_check(WINDOW, game.board.board, game.current_turn)
        if dragging_piece and selected_piece:
            piece = game.board.board[selected_piece[0]][selected_piece[1]]
            piece_name = f"{piece.color}_{piece.__class__.__name__.lower()}"
            WINDOW.blit(IMAGES[piece_name], (dragging_piece_pos[0] - SQUARE_SIZE // 2, dragging_piece_pos[1] - SQUARE_SIZE // 2))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
