import chess
import pygame
import sys
import os.path
from pygame import color
from pygame.event import event_name
from pygame.image import save
from pygame.math import Vector2
from pygame.time import Clock
from pathlib import Path
import chess.engine
import sqlite3
import ctypes


class INPUTBOX():
    def __init__(self, x, y, w, h, text=''):
        x = int(x*scale_x)
        y = int(y*scale_y)
        w = int(w*scale_x)
        h = int(h*scale_y)
        self.cinactive = pygame.Color('Black')
        self.cactive = pygame.Color('Grey')
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('Black')
        self.text = text
        self.input = ''
        self.txt_surface = game_font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            if self.active:
                self.color = self.cactive
            else:
                self.color = self.cinactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.input = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text = self.text + event.unicode
                self.txt_surface = game_font.render(
                    self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def return_input(self):
        return self.input


class BUTTON:
    def __init__(self, x, y, width, height, text='', dis=True):
        self.color = pygame.Color('Grey')
        self.x = int(x*scale_x)
        self.y = int(y*scale_y)
        self.width = int(width*scale_x)
        self.height = int(height*scale_y)
        self.text = text
        self.dis = dis
        self.colorog = self.color

    def isOver(self, posx, posy):
        if posx > self.x and posx < self.x + self.width:
            if posy > self.y and posy < self.y + self.height:
                return True
        return False

    def draw(self):
        x, y = pygame.mouse.get_pos()
        if(self.isOver(x, y) and self.dis):
            self.color = pygame.Color(85, 85, 85)
        else:
            self.color = self.colorog
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.width, self.height), 0)
        if self.text != '':
            text_rect = game_font.render(
                self.text, True, pygame.Color('Black'))
            screen.blit(text_rect, (self.x+(self.width/2-text_rect.get_width()/2),
                        self.y + (self.height/2 - text_rect.get_height()/2)))


class BOARD:
    def __init__(self):
        # 'rnbqkbnr/1ppp1ppp/8/p3p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 4'
        self.Board = chess.Board()
        self.square_dark = pygame.image.load(
            'Assets/square_brown_dark.png').convert_alpha()
        self.square_light = pygame.image.load(
            'Assets/square_brown_light.png').convert_alpha()
        self.legal_move_image = pygame.image.load(
            'Assets/dot.png').convert_alpha()
        self.capture_move_image = pygame.image.load(
            'Assets/capture_ring.png').convert_alpha()
        self.check_image = pygame.image.load(
            'Assets/check_ring.png').convert_alpha()
        if scale_x < 1 or scale_y < 1:
            scale_image = (scale_x+scale_y)/2
            self.legal_move_image = pygame.transform.rotozoom(
                self.legal_move_image, 0, scale_image)
            self.capture_move_image = pygame.transform.rotozoom(
                self.capture_move_image, 0, scale_image)
            self.check_image = pygame.transform.rotozoom(
                self.check_image, 0, scale_image)

        self.chessTablePos = str(self.Board)
        self.chessTablePos = self.chessTablePos.replace(" ", "")
        self.chessTablePos = self.chessTablePos.split("\n")
        # print(self.chessTablePos)
        self.Pieces = {
            'b': 'bishop',
            'r': 'rook',
            'n': 'knight',
            'p': 'pawn',
            'q': 'queen',
            'r': 'rook',
            'k': 'king'
        }
        self.move_history_san_white = []
        self.move_history_san_black = []
        self.set = 0
        self.setaddonce = False

    def print_TablePos(self):
        print(self.chessTablePos)

    def get_pos_fromsquare(self, sq):
        # b1
        lets = 'abcdefgh'
        x = lets.index(sq[0])
        y = int(sq[1]) - 1
        return x, y

    def get_square_frompos(self, x, y):
        lets = 'abcdefgh'
        sq = lets[x] + str(y + 1)
        return sq

    def ispieceatpos(self, x, y):
        square = self.get_square_frompos(x, y)
        if (self.Board.piece_at(chess.parse_square(square))):
            return True
        else:
            return False

    def iscolorandpieceatpos(self, x, y):
        square = self.get_square_frompos(x, y)
        if self.Board.piece_at(chess.parse_square(square)) and self.Board.turn == self.Board.color_at(
                chess.parse_square(square)):
            return True
        else:
            return False

    def pieceatpos(self, x, y):
        square = self.get_square_frompos(x, y)
        return self.Board.piece_type_at(chess.parse_square(square))

    def draw_board(self):
        for row in range(square_number):
            if row % 2 == 0:
                for col in range(square_number):
                    if col % 2 == 0:
                        board_rect = pygame.Rect(
                            int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                        screen.blit(self.square_light, board_rect)
                    else:
                        board_rect = pygame.Rect(
                            int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                        screen.blit(self.square_dark, board_rect)
            else:
                for col in range(square_number):
                    if col % 2 == 0:
                        board_rect = pygame.Rect(
                            int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                        screen.blit(self.square_dark, board_rect)
                    else:
                        board_rect = pygame.Rect(
                            int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                        screen.blit(self.square_light, board_rect)

    def draw_pieces(self):
        path_default = 'Assets/'
        self.update_table()
        for row in range(square_number):
            for col in range(square_number):
                piece = self.chessTablePos[row][col]
                if piece != '.':
                    if piece.isupper():
                        colorPiece = True
                    else:
                        colorPiece = False
                    piece = piece.lower()
                    piece_rect = pygame.Rect(
                        int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                    if colorPiece:
                        piece_path = path_default + \
                            'w_' + self.Pieces[piece] + '.png'
                    else:
                        piece_path = path_default + \
                            'b_' + self.Pieces[piece] + '.png'
                    # print(path)
                    piece_path = Path(piece_path)

                    scale_image = (scale_x+scale_y)/2
                    if scale_x == 1:
                        scale_image = 1.5
                    piece_image = pygame.image.load(piece_path).convert_alpha()
                    piece_image = pygame.transform.rotozoom(
                        piece_image, 0, scale_image)
                    screen.blit(
                        piece_image, piece_rect)

    def update_table(self):
        self.chessTablePos = str(self.Board)
        self.chessTablePos = self.chessTablePos.replace(" ", "")
        self.chessTablePos = self.chessTablePos.split("\n")

    def push_ai(self, engine):
        result = engine.play(self.Board, chess.engine.Limit(time=0.1))
        if self.Board.turn:
            self.move_history_san_white.append(
                self.Board.san(self.Board.parse_uci(str(result.move))))
        else:
            self.move_history_san_black.append(
                self.Board.san(self.Board.parse_uci(str(result.move))))
        self.Board.push(result.move)

    def push_move(self, table_x, table_y, table_x2, table_y2):
        squarefrom = self.get_square_frompos(table_x, table_y)
        squareto = self.get_square_frompos(table_x2, table_y2)
        # print(squarefrom + squareto)
        legal_move = [move.uci() for move in self.Board.generate_legal_moves()]
        legal_captures = [move.uci()
                          for move in self.Board.generate_legal_captures()]
        legal_enpassant = [move.uci()
                           for move in self.Board.generate_legal_ep()]
        legal_promotion = [move[:-1] for move in legal_captures + legal_move]
        move = squarefrom + squareto
        x, y = self.get_pos_fromsquare(squarefrom)
        # print(x, y)
        # print(self.pieceatpos(x, y))
        # print(legal_promotion)
        if move in legal_move or move in legal_captures or move in legal_enpassant:

            if self.Board.turn:
                self.move_history_san_white.append(
                    self.Board.san(self.Board.parse_uci(move)))
            else:
                self.move_history_san_black.append(
                    self.Board.san(self.Board.parse_uci(move)))
            self.Board.push_uci(move)
            print('Moved')
            return True
        elif self.pieceatpos(x, y) == 1 and move in legal_promotion:
            piece = ''
            queen_rect = pygame.Rect(
                int(square_number * square_size*scale_x), int((square_number - 4) * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
            knight_rect = pygame.Rect(
                int(square_number * square_size*scale_x), int((square_number - 3) * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
            rook_rect = pygame.Rect(
                int(square_number * square_size*scale_x), int((square_number - 2) * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
            bishop_rect = pygame.Rect(
                int(square_number * square_size*scale_x), int((square_number - 1) * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
            con = True
            while con:
                if self.Board.turn:
                    path_default = 'Assets/'
                    queen_path = path_default + 'w_' + \
                        self.Pieces['q'] + '.png'
                    knight_path = path_default + \
                        'w_' + self.Pieces['n'] + '.png'
                    rook_path = path_default + 'w_' + self.Pieces['r'] + '.png'
                    bishop_path = path_default + \
                        'w_' + self.Pieces['b'] + '.png'
                    queen_path = Path(queen_path)
                    knight_path = Path(knight_path)
                    rook_path = Path(rook_path)
                    bishop_path = Path(bishop_path)
                    queen_image = pygame.image.load(queen_path).convert_alpha()
                    knight_image = pygame.image.load(
                        knight_path).convert_alpha()
                    rook_image = pygame.image.load(rook_path).convert_alpha()
                    bishop_image = pygame.image.load(
                        bishop_path).convert_alpha()
                    screen.blit(queen_image, queen_rect)
                    screen.blit(knight_image, knight_rect)
                    screen.blit(rook_image, rook_rect)
                    screen.blit(bishop_image, bishop_rect)
                else:
                    path_default = 'Assets/'
                    queen_path = path_default + \
                        'b_' + self.Pieces['q'] + '.png'
                    knight_path = path_default + \
                        'b_' + self.Pieces['n'] + '.png'
                    rook_path = path_default + \
                        'b_' + self.Pieces['r'] + '.png'
                    bishop_path = path_default + \
                        'b_' + self.Pieces['b'] + '.png'
                    queen_path = Path(queen_path)
                    knight_path = Path(knight_path)
                    rook_path = Path(rook_path)
                    bishop_path = Path(bishop_path)
                    queen_image = pygame.image.load(
                        queen_path).convert_alpha()
                    knight_image = pygame.image.load(
                        knight_path).convert_alpha()
                    rook_image = pygame.image.load(rook_path).convert_alpha()
                    bishop_image = pygame.image.load(
                        bishop_path).convert_alpha()
                    screen.blit(queen_image, queen_rect)
                    screen.blit(knight_image, knight_rect)
                    screen.blit(rook_image, rook_rect)
                    screen.blit(bishop_image, bishop_rect)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                        con = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        if x >= int(square_number * square_size*scale_x) and x <= int((square_number * square_size + square_size)*scale_x):
                            if y >= (square_number - 4) * square_size * scale_y and y <= ((square_number - 3) * square_size*scale_y):
                                piece = 'q'
                            elif y >= (square_number - 3) * square_size * scale_y and y <= ((square_number - 2) * square_size*scale_y):
                                piece = 'n'
                            elif y >= (square_number - 2) * square_size * scale_y and y <= ((square_number - 1) * square_size*scale_y):
                                piece = 'r'
                            elif y >= (square_number - 1) * square_size * scale_y and y <= (square_number * square_size*scale_y):
                                piece = 'b'
                            con = False

            move = move + piece
            if move in legal_move or move in legal_captures or move in legal_enpassant:
                if self.Board.turn:
                    self.move_history_san_white.append(
                        self.Board.san(self.Board.parse_uci(move)))
                else:
                    self.move_history_san_black.append(
                        self.Board.san(self.Board.parse_uci(move)))
                self.Board.push_uci(move)
                print('Moved')
                return True
        else:
            print('Illegal')
            return False
        # print('White' + str(self.move_history_san_white))
        # print('Black' + str(self.move_history_san_black))

    def draw_legalmoves_piece(self, x, y, table_x, table_y):
        legal_moves = [move.uci()
                       for move in self.Board.generate_legal_moves()]
        squarepiece = self.get_square_frompos(table_x, table_y)
        for lmove in legal_moves:
            if squarepiece in lmove:
                x_l, y_l = self.get_pos_fromsquare(lmove[2:])
                y_le = 7 - y_l
                # print(x_l, y_l, y_le)
                legal_rect = pygame.Rect(
                    int(x_l * (square_size*scale_x)), int(y_le * (square_size*scale_y)), int(square_size*scale_x), int(square_size*scale_y))
                if not self.pieceatpos(x_l, y_l):
                    screen.blit(self.legal_move_image, legal_rect)
                else:
                    screen.blit(self.capture_move_image, legal_rect)
                # print(self.get_pos_fromsquare(lmove[2:]))

    def draw_check(self):
        if self.Board.is_check():
            if self.Board.turn:
                for col in range(square_number):
                    for row in range(square_number):
                        if self.chessTablePos[row][col] == 'K':
                            check_rect = pygame.Rect(
                                int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                            screen.blit(self.check_image, check_rect)

            else:
                for col in range(square_number):
                    for row in range(square_number):
                        if self.chessTablePos[row][col] == 'k':
                            check_rect = pygame.Rect(
                                int(col * square_size*scale_x), int(row * square_size*scale_y), int(square_size*scale_x), int(square_size*scale_y))
                            screen.blit(self.check_image, check_rect)

    def draw_history(self):
        white_move_number = len(self.move_history_san_white)
        black_move_number = len(self.move_history_san_black)
        move_number = white_move_number
        if move_number % 5 == 0 and move_number != 0 and not self.setaddonce:
            self.set = self.set + 5
            self.setaddonce = True
        elif move_number % 5 != 0:
            self.setaddonce = False
        # print(move_number, self.set)
        if self.set == move_number and self.set:
            self.set = self.set-1
        if self.set > move_number:
            self.set = int(int(move_number/5)*5)
        else:
            if self.set == move_number and self.set:
                self.set = self.set-1
        for move in range(self.set, move_number):
            move_rect1 = pygame.Rect(
                int(square_number * square_size*scale_x)+40, int(((move-self.set)*0.39+1) * square_size*scale_y/1.5), int((square_size/2 + 2 * square_size)*scale_x), int(square_size*0.4*scale_y))
            turn_text = str(move+1) + '. '
            turn_text = turn_text + self.move_history_san_white[move] + ' '
            if move <= black_move_number-1:
                turn_text = turn_text + self.move_history_san_black[move]
            turn_rect = game_font.render(
                turn_text, True, pygame.Color('Black'))
            # pygame.draw.rect(screen, pygame.Color('Green'), move_rect1)
            # pygame.draw.rect(screen, pygame.Color('Blue'), move_rect2)
            # pygame.draw.rect(screen, pygame.Color('Red'), move_rect3)
            screen.blit(turn_rect, move_rect1)

    def end_menu(self):
        result_text = str(self.Board.outcome().termination)[12:]
        if self.Board.outcome().winner:
            color_result = "WHITE"
        else:
            color_result = "BLACK"
        result_number = self.Board.outcome().result()
        for text in range(0, 3):
            result_rect = pygame.Rect(int((square_number+0.5)*square_size*scale_x), int((text+5)
                                      * square_size/2*scale_y), int((square_size/2 + square_size)*scale_x), int((square_size*0.5)*scale_y))
            if text == 0:
                text_rect = game_font.render(
                    result_text, True, pygame.Color('Black'))
                screen.blit(text_rect, result_rect)
            if text == 1 and result_number != '1/2-1/2':
                text_rect = game_font.render(
                    color_result, True, pygame.Color('Black'))
                screen.blit(text_rect, result_rect)
            if text == 2:
                text_rect = game_font.render(
                    result_number, True, pygame.Color('Black'))
                screen.blit(text_rect, result_rect)

    def newgame(self):
        self.Board.reset()
        self.move_history_san_white = []
        self.move_history_san_black = []
        self.set = 0
        self.setaddonce = False

    def savegame(self):
        if not os.path.isfile('Games.txt'):
            f = open("Games.txt", "x")
            f.write('GAME START')
            f.write('\n')
            move_number = len(self.move_history_san_white)
            for move in range(0, move_number):
                if move < len(self.move_history_san_white):
                    f.write(str(move+1) + '. ' +
                            self.move_history_san_white[move])
                if move < len(self.move_history_san_black):
                    f.write(' ' + self.move_history_san_black[move])
                f.write('\n')
            f.close()
        else:
            f = open("Games.txt", "a")
            f.write('\n')
            f.write('GAME START')
            f.write('\n')
            move_number = len(self.move_history_san_white)
            for move in range(0, move_number):
                if move < len(self.move_history_san_white):
                    f.write(str(move+1) + '. ' +
                            self.move_history_san_white[move])
                if move < len(self.move_history_san_black):
                    f.write(' ' + self.move_history_san_black[move])
                f.write('\n')
            f.close()

    def newgamefromfen(self):
        if os.path.isfile("FEN.txt"):
            f = open("FEN.txt", "r")
            FEN = f.read()
            f.close()
            self.Board = chess.Board(FEN)
            self.move_history_san_white = []
            self.move_history_san_black = []
            self.set = 0
            self.setaddonce = False

    def placepieceatpos(self, table_x, table_y, piece_type, piece_color):
        square = chess.parse_square(self.get_square_frompos(table_x, table_y))
        piece = chess.Piece(piece_type, piece_color)
        self.Board.set_piece_at(square, piece)

    def removepieceatpos(self, table_x, table_y):
        square = chess.parse_square(self.get_square_frompos(table_x, table_y))
        self.Board.remove_piece_at(square)

    def clear_board(self):
        self.Board.clear()

    def save_board_fen(self):
        text = self.Board.fen()
        if not os.path.isfile("SavedFEN.txt"):
            f = open("SavedFEN.txt", 'x')
            f.write(text)
            f.write('\n')
        else:
            f = open("SavedFEN.txt", 'a')
            f.write(text)
            f.write('\n')

    def undo_move(self):
        if not self.Board.turn and len(self.move_history_san_white) > 0:
            self.move_history_san_white.pop()
            self.Board.pop()
        elif self.Board.turn and len(self.move_history_san_black) > 0:
            self.move_history_san_black.pop()
            self.Board.pop()

    def undo_moveAI(self):
        if len(self.move_history_san_white) > 0:
            self.move_history_san_white.pop()
            self.Board.pop()
        if len(self.move_history_san_black) > 0:
            self.move_history_san_black.pop()
            self.Board.pop()


class TABLE_EDITOR:
    def __init__(self):
        self.board = BOARD()
        self.selected = False
        self.x = 0
        self.y = 0
        self.quit = False
        self.board.Board.clear()
        self.piece = chess.PAWN
        self.color = chess.WHITE
        self.game_loop()

    def game_loop(self):
        while not self.quit:
            screen.fill((94, 93, 96))
            self.board.draw_board()
            self.board.draw_pieces()
            clear_button = BUTTON((square_number+0.5)*square_size, 9*square_size/2,
                                  square_size/2 + square_size, square_size*0.5, 'Clear Board')
            startfromboard_button = BUTTON((square_number+0.5)*square_size, 10*square_size/2,
                                           square_size/2 + square_size, square_size*0.5, 'Start game')
            savegame_button = BUTTON((square_number+0.5)*square_size, 11*square_size/2,
                                     square_size/2 + square_size, square_size*0.5, 'Save game')
            readfen_button = BUTTON((square_number+0.5)*square_size, 12*square_size/2,
                                    square_size/2 + square_size, square_size*0.5, 'Read from FEN')
            exit_button = BUTTON((square_number+0.5)*square_size, 13*square_size/2,
                                 square_size/2 + square_size, square_size*0.5, 'Exit')
            clear_button.draw()
            startfromboard_button.draw()
            savegame_button.draw()
            readfen_button.draw()
            exit_button.draw()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        self.piece = chess.PAWN
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        self.piece = chess.KNIGHT
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        self.piece = chess.BISHOP
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        self.piece = chess.ROOK
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        self.piece = chess.QUEEN
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        self.piece = chess.KING
                    if event.key == pygame.K_w:
                        self.board.Board.turn = chess.WHITE
                    if event.key == pygame.K_b:
                        self.board.Board.turn = chess.BLACK
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.x, self.y = pygame.mouse.get_pos()
                    self.x_table = int(self.x / (square_size*scale_x))
                    self.y_table = 7 - int(self.y / (square_size*scale_y))
                    if self.x_table >= 0 and self.x_table < square_number and self.y_table >= 0 and self.y_table < square_number:
                        if event.button == 2:
                            self.board.removepieceatpos(
                                self.x_table, self.y_table)
                        else:
                            if event.button == 1:
                                self.color = chess.WHITE
                            if event.button == 3:
                                self.color = chess.BLACK
                            self.board.placepieceatpos(
                                self.x_table, self.y_table, self.piece, self.color)
                    else:
                        if clear_button.isOver(self.x, self.y):
                            self.board.clear_board()
                        if startfromboard_button.isOver(self.x, self.y):
                            GAME_LOCAL(True,
                                       '', self.board.Board.fen())
                        if savegame_button.isOver(self.x, self.y):
                            self.board.save_board_fen()
                        if readfen_button.isOver(self.x, self.y):
                            self.board.newgamefromfen()
                        if exit_button.isOver(self.x, self.y):
                            self.quit = True
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            clock.tick(60)


class GAME_AI:
    def __init__(self, color, user):
        self.board = BOARD()
        self.selected = False
        self.x = 0
        self.y = 0
        self.quit = False
        self.startcolor = color
        self.added = False
        self.user = user
        self.engine = chess.engine.SimpleEngine.popen_uci("engine")
        self.game_loop()

    def game_loop(self):
        while not self.board.Board.is_game_over() and not self.quit:
            screen.fill((94, 93, 96))

            self.board.draw_board()
            self.board.draw_pieces()
            self.board.draw_history()
            undo_button = BUTTON((square_number+0.5)*square_size, 11*square_size/2,
                                 square_size/2 + square_size, square_size*0.5, 'Undo')
            exit_button = BUTTON((square_number+0.5)*square_size, 12*square_size/2,
                                 square_size/2 + square_size, square_size*0.5, 'Exit')
            undo_button.draw()
            exit_button.draw()
            if self.startcolor != self.board.Board.turn:
                self.board.push_ai(self.engine)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.engine.quit()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                    self.selected = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.x, self.y = pygame.mouse.get_pos()
                    if exit_button.isOver(self.x, self.y):
                        self.quit = True
                    if undo_button.isOver(self.x, self.y):
                        self.board.undo_moveAI()
                    if not self.selected:
                        self.x, self.y = pygame.mouse.get_pos()
                        self.x_table = int(self.x / (square_size*scale_x))
                        self.y_table = 7 - int(self.y / (square_size*scale_y))
                        self.x = int(self.x / square_size)
                        self.y = int(self.y / square_size)
                    if self.x_table >= 0 and self.x_table < square_number and self.y_table >= 0 and self.y_table < square_number:
                        if self.board.iscolorandpieceatpos(self.x_table, self.y_table) and not self.selected:
                            self.selected = True
                        elif self.selected:
                            x2, y2 = pygame.mouse.get_pos()
                            x2_table = int(x2 / (square_size*scale_x))
                            y2_table = 7 - int(y2 / (square_size*scale_y))
                            if x2_table >= 0 and x2_table < square_number and y2_table >= 0 and y2_table < square_number:
                                self.board.push_move(
                                    self.x_table, self.y_table, x2_table, y2_table)
                                self.selected = False

            if self.selected:
                self.board.draw_legalmoves_piece(
                    self.x, self.y, self.x_table, self.y_table)
            self.board.draw_history()
            self.board.draw_check()
            pygame.display.update()
            clock.tick(60)
            while self.board.Board.is_game_over() and not self.quit:
                if not self.added:
                    self.added = True
                    if self.startcolor == self.board.Board.outcome().winner:
                        ld.add_game(self.user)
                        ld.add_victory(self.user)
                        ld.add_rating(self.user, 1)
                    else:
                        ld.add_game(self.user)
                        ld.add_rating(self.user, -1)
                screen.fill((94, 93, 96))
                self.board.draw_board()
                self.board.draw_pieces()
                self.board.draw_history()
                self.x, self.y = pygame.mouse.get_pos()
                ng_button = BUTTON((square_number+0.5)*square_size, 9*square_size/2,
                                   square_size/2 + square_size, square_size*0.5, 'New Game')
                startfromfen_button = BUTTON((square_number+0.5)*square_size, 10*square_size/2,
                                             square_size/2 + square_size, square_size*0.5, 'Start from FEN')
                savegame_button = BUTTON((square_number+0.5)*square_size, 11*square_size/2,
                                         square_size/2 + square_size, square_size*0.5, 'Save game')
                exit_button = BUTTON((square_number+0.5)*square_size, 12*square_size/2,
                                     square_size/2 + square_size, square_size*0.5, 'Exit')
                ng_button.draw()
                exit_button.draw()
                startfromfen_button.draw()
                savegame_button.draw()
                self.board.end_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.engine.quit()
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if ng_button.isOver(self.x, self.y):
                            self.added = False
                            self.board.newgame()
                        if startfromfen_button.isOver(self.x, self.y):
                            self.added = False
                            self.board.newgamefromfen()
                        if savegame_button.isOver(self.x, self.y):
                            self.board.savegame()
                        if exit_button.isOver(self.x, self.y):
                            self.quit = True
                self.board.draw_history()
                self.board.draw_check()
                pygame.display.update()
                clock.tick(60)
        self.engine.quit()


class GAME_LOCAL:
    def __init__(self, color, user, boardFEN=None):
        self.board = BOARD()
        if boardFEN != None:
            self.board.Board = chess.Board(boardFEN)
        self.selected = False
        self.x = 0
        self.y = 0
        self.quit = False
        self.color = color
        self.added = False
        self.user = user
        self.game_loop()

    def game_loop(self):
        while not self.board.Board.is_game_over() and not self.quit:
            screen.fill((94, 93, 96))
            self.board.draw_board()
            self.board.draw_pieces()
            self.board.draw_history()
            undo_button = BUTTON((square_number+0.5)*square_size, 11*square_size/2,
                                 square_size/2 + square_size, square_size*0.5, 'Undo')
            exit_button = BUTTON((square_number+0.5)*square_size, 12*square_size/2,
                                 square_size/2 + square_size, square_size*0.5, 'Exit')
            undo_button.draw()
            exit_button.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                    self.selected = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.x, self.y = pygame.mouse.get_pos()
                    if exit_button.isOver(self.x, self.y):
                        self.quit = True
                    if undo_button.isOver(self.x, self.y):
                        self.board.undo_move()
                    if not self.selected:
                        self.x, self.y = pygame.mouse.get_pos()
                        self.x_table = int(self.x / (square_size*scale_x))
                        self.y_table = 7 - int(self.y / (square_size*scale_y))
                        self.x = int(self.x / (square_size*scale_x))
                        self.y = int(self.y / (square_size*scale_y))
                    if self.x_table >= 0 and self.x_table < square_number and self.y_table >= 0 and self.y_table < square_number:
                        print(self.board.iscolorandpieceatpos(
                            self.x_table, self.y_table))
                        if self.board.iscolorandpieceatpos(self.x_table, self.y_table) and not self.selected:
                            self.selected = True
                        elif self.selected:
                            x2, y2 = pygame.mouse.get_pos()
                            x2_table = int(x2 / (square_size*scale_x))
                            y2_table = 7 - int(y2 / (square_size*scale_y))
                            print(x2_table, y2_table)
                            if x2_table >= 0 and x2_table < square_number and y2_table >= 0 and y2_table < square_number:
                                self.board.push_move(
                                    self.x_table, self.y_table, x2_table, y2_table)
                                self.selected = False

            if self.selected:
                self.board.draw_legalmoves_piece(
                    self.x, self.y, self.x_table, self.y_table)
            self.board.draw_history()
            self.board.draw_check()
            pygame.display.update()
            clock.tick(60)
            while self.board.Board.is_game_over() and not self.quit:
                if not self.added:
                    self.added = True
                    if self.color == self.board.Board.outcome().winner:
                        ld.add_game(self.user)
                        ld.add_victory(self.user)
                        ld.add_rating(self.user, 1)
                    else:
                        ld.add_game(self.user)
                        ld.add_rating(self.user, -1)

                screen.fill((94, 93, 96))
                self.board.draw_board()
                self.board.draw_pieces()
                self.board.draw_history()
                self.x, self.y = pygame.mouse.get_pos()
                ng_button = BUTTON((square_number+0.5)*square_size, 9*square_size/2,
                                   square_size/2 + square_size, square_size*0.5, 'New Game')
                startfromfen_button = BUTTON((square_number+0.5)*square_size, 10*square_size/2,
                                             square_size/2 + square_size, square_size*0.5, 'Start from FEN')
                savegame_button = BUTTON((square_number+0.5)*square_size, 11*square_size/2,
                                         square_size/2 + square_size, square_size*0.5, 'Save game')
                exit_button = BUTTON((square_number+0.5)*square_size, 12*square_size/2,
                                     square_size/2 + square_size, square_size*0.5, 'Exit')
                ng_button.draw()
                exit_button.draw()
                startfromfen_button.draw()
                savegame_button.draw()
                self.board.end_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if ng_button.isOver(self.x, self.y):
                            self.added = False
                            self.board.newgame()
                        if startfromfen_button.isOver(self.x, self.y):
                            self.added = False
                            self.board.newgamefromfen()
                        if savegame_button.isOver(self.x, self.y):
                            self.board.savegame()
                        if exit_button.isOver(self.x, self.y):
                            self.quit = True
                self.board.draw_history()
                self.board.draw_check()
                pygame.display.update()
                clock.tick(60)
                # print(self.x, self.y, x2, y2)
            # print(self.x_table, self.y_table,
            #     x2_table, y2_table)
            # print(self.board.pieceatpos(
            #    self.x_table, self.y_table))
            # print(self.board.print_TablePos())
            # print('------')
            # print(self.selected)
            # print(self.selected)
            # print(x_table, y_table)
            # print(self.x, self.y)
            # print(self.board.get_square_frompos(
            #    x_table, y_table))
            # print(self.board.print_TablePos())
            # print(self.board.Board.is_check())
            # print(self.board.pieceatpos(0, 0))
            # print(self.board.chessTablePos[0][2])
            # print(self.board.get_square_frompos(4, 6))
            # Draw the pieces
            # Update the screen


class LEADERBOARD():
    def __init__(self, con, cur):
        self.con = con
        self.cur = cur
        self.cur.execute(
            '''CREATE TABLE if not exists users(Name text,Games INT, Victories INT, Rating INT)''')

    def init_user(self, user):
        if user != '':
            self.cur.execute(
                "SELECT * FROM users WHERE Name= :name", {'name': user})
            entry = list(self.cur.fetchall())
            if not entry:
                with self.con:
                    self.cur.execute(
                        "INSERT INTO users VALUES(:name,0,0,0)", {'name': user})

    def add_game(self, user):
        if user != '':
            self.cur.execute(
                "SELECT Games FROM users WHERE Name= :name", {'name': user})
            entry = self.cur.fetchall()
            number = int(entry[0][0]+1)
            if entry:
                with self.con:
                    self.cur.execute(
                        "UPDATE users set Games = :vic WHERE Name= :name", {'name': user, 'vic': number})

    def add_victory(self, user):
        if user != '':
            self.cur.execute(
                "SELECT Victories FROM users WHERE Name= :name", {'name': user})
            entry = self.cur.fetchall()
            number = int(entry[0][0]+1)
            if entry:
                with self.con:
                    self.cur.execute(
                        "UPDATE users set Victories = :vic WHERE Name= :name", {'name': user, 'vic': number})

    def add_rating(self, user, ratnum):
        if user != '':
            self.cur.execute(
                "SELECT Rating FROM users WHERE Name= :name", {'name': user})
            entry = self.cur.fetchall()
            number = int(entry[0][0]+ratnum)
            if entry:
                with self.con:
                    self.cur.execute(
                        "UPDATE users set Rating = :vic WHERE Name= :name", {'name': user, 'vic': number})

    def get_values_from_user(self, user):
        if user != '':
            self.cur.execute("SELECT Games,Victories,Rating FROM users WHERE Name= :name", {
                             'name': user})
            values = self.cur.fetchall()
            return values[0][0], values[0][1], values[0][2]

    def draw_leaderboardscreen(self, user):
        games, vic, rat = self.get_values_from_user(user)
        user_button = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                             square_size, square_size*3, square_size/2, ('User: ' + user), False)
        games_rect = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                            square_size*3, square_size*3, square_size/2, ('Games: ' + str(games)), False)
        vic_rect = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                          square_size*4, square_size*3, square_size/2,  ('Victories: ' + str(vic)), False)
        rat_rect = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                          square_size*5, square_size*3, square_size/2,  ('Rating: ' + str(rat)), False)
        user_button.draw()
        games_rect.draw()
        vic_rect.draw()
        rat_rect.draw()


class MENU:
    def __init__(self):
        self.title_font = pygame.font.Font('Assets/gamefont.ttf', 250)
        self.user = ''
        self.get_user()
        ld.init_user(self.user)
        self.menu_loop()

    def menu_loop(self):
        while True:
            screen.fill((94, 93, 96))
            Title_text = 'Chess'
            Titlepos_rect = pygame.Rect(
                int((square_size*(square_number+3)-square_size*3)/2*scale_x), int(square_size*scale_y), int(square_size*3*scale_x), int(square_size/2*scale_y))
            TitleText_rect = self.title_font.render(
                Title_text, True, pygame.Color('Black'))
            screen.blit(TitleText_rect, (Titlepos_rect.x+(Titlepos_rect.width/2 - TitleText_rect.get_width()/2),
                        Titlepos_rect.y+(Titlepos_rect.height/2 - TitleText_rect.get_height()/2)))
            startgame_button = BUTTON(((square_size*(square_number+3)-square_size*3)/2),
                                      square_size*3, square_size*3, square_size/2, 'Start Game')
            gameai_button = BUTTON(((square_size*(square_number+3)-square_size*3)/2),
                                   square_size*4, square_size*3, square_size/2, 'Game against your AI')
            tableeditor_button = BUTTON(((square_size*(square_number+3)-square_size*3)/2),
                                        square_size*5, square_size*3, square_size/2, 'Table Editor')
            leaderboard_button = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                                        square_size*6, square_size*3, square_size/2, 'Leaderboard')
            exit_button = BUTTON(((square_size*(square_number+3)-square_size*3)/2),
                                 square_size*7, square_size*3, square_size/2, 'Quit')
            startgame_button.draw()
            gameai_button.draw()
            tableeditor_button.draw()
            exit_button.draw()
            leaderboard_button.draw()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if startgame_button.isOver(x, y):
                        color_selected = False
                        backbut = False
                        while not color_selected and not backbut:
                            screen.fill((94, 93, 96))
                            white_button = BUTTON(square_size*2.5,
                                                  (square_size*square_number)/2, square_size*3, square_size/2, 'White')
                            black_button = BUTTON(square_size*6*scale_x,
                                                  (square_size*square_number)/2, square_size*3, square_size/2, 'Black')
                            back_button = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                                                 ((square_size*square_number)/2 + square_size*1.5), square_size*3, square_size/2, 'Back')
                            white_button.draw()
                            black_button.draw()
                            back_button.draw()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                    x, y = pygame.mouse.get_pos()
                                    if white_button.isOver(x, y):
                                        color = True
                                        color_selected = True
                                    if black_button.isOver(x, y):
                                        color = False
                                        color_selected = True
                                    if back_button.isOver(x, y):
                                        backbut = True
                            pygame.display.update()
                        if color_selected:
                            GAME_LOCAL(color, self.user)
                    x, y = pygame.mouse.get_pos()
                    if gameai_button.isOver(x, y) and os.path.isfile('engine.exe'):
                        color_selected = False
                        backbut = False
                        while not color_selected and not backbut:
                            screen.fill((94, 93, 96))
                            white_button = BUTTON(square_size*2.5,
                                                  (square_size*square_number)/2, square_size*3, square_size/2, 'White')
                            black_button = BUTTON(square_size*6,
                                                  (square_size*square_number)/2, square_size*3, square_size/2, 'Black')
                            back_button = BUTTON((square_size*(square_number+3)-square_size*3)/2,
                                                 ((square_size*square_number)/2 + square_size*1.5), square_size*3, square_size/2, 'Back')
                            white_button.draw()
                            black_button.draw()
                            back_button.draw()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                    x, y = pygame.mouse.get_pos()
                                    if white_button.isOver(x, y):
                                        color = True
                                        color_selected = True
                                    if black_button.isOver(x, y):
                                        color = False
                                        color_selected = True
                                    if back_button.isOver(x, y):
                                        backbut = True
                            pygame.display.update()
                        if color_selected:
                            GAME_AI(color, self.user)
                    if leaderboard_button.isOver(x, y) and self.user != '':
                        self.draw_leaderboard()
                    if tableeditor_button.isOver(x, y):
                        TABLE_EDITOR()
                    if exit_button.isOver(x, y):
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            clock.tick(60)

    def draw_leaderboard(self):
        quit = False
        quit_button = BUTTON(((square_size*(square_number+3)-square_size*3)/2),
                             square_size*6, square_size*3, square_size/2, 'Back')
        while not quit:
            screen.fill((94, 93, 96))
            ld.draw_leaderboardscreen(self.user)
            quit_button.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if quit_button.isOver(x, y):
                        quit = True
            pygame.display.update()
            clock.tick(60)

    def get_user(self):
        done = False
        Text = BUTTON(((square_size*(square_number+3)-square_size*3)/2), square_size,
                      square_size*3, square_size/2, 'Enter your username', False)
        Text2 = BUTTON(((square_size*(square_number+3)-square_size*3)/2), square_size*3,
                       square_size*3, square_size/2, 'When done press ENTER', False)
        input_box = INPUTBOX(((square_size*(square_number+3)-square_size*1.5)/2),
                             square_size*2, square_size*3, square_size/2,)
        while not done:
            screen.fill((94, 93, 96))
            Text.draw()
            Text2.draw()
            input_box.update()
            input_box.draw()
            for event in pygame.event.get():
                input_box.handle_event(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                        self.user = input_box.return_input()

            pygame.display.update()
            clock.tick(60)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Chess')
    icon = pygame.image.load('Assets/icon.png')
    pygame.display.set_icon(icon)
    square_size = 128
    square_number = 8
    game_font = pygame.font.Font('Assets/gamefont.ttf', 55)
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    scale_x = (screensize[0]/(square_size * (square_number + 3))-0.2)
    scale_y = (screensize[1] / (square_size*square_number)-0.2)
    if scale_x + 0.2 > 1 and scale_y + 0.2 > 1:
        scale_x = 1
        scale_y = 1
    print(scale_x, scale_y)
    screen = pygame.display.set_mode(
        (int(square_size * (square_number + 3)*scale_x), int(square_size * square_number*scale_y)))
    print(screen.get_height(), screen.get_width())
    clock = pygame.time.Clock()
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    ld = LEADERBOARD(con, cur)
    main_game = MENU()
    con.close()
