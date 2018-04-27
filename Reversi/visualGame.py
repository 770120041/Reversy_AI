import sys
import pygame
from board import Board
import timeit
import traceback
import time


class VisualGame:
    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        self.window_size = (self.window_width, self.window_height)
        self.caption = "Reversi"
        self.board_x = 100
        self.board_y = 100
        self.grid_size = 50
        self.boarder_width = 5
        self.emphasize_size = 40
        self.emphasize_length = 5
        self.bg_color = (180, 230, 180)
        self.board_color = (36, 40, 41)
        self.player_color = {-1: (0, 0, 0), 1: (255, 255, 255), 0: (230, 80, 80)}
        self.engines_name = {-1: 'simple', 1: 'simple'}
        self.engines = {-1: None, 1: None}
        for i in [-1, 1]:
            engine_name = self.engines_name[i]
            self.engines[i] = __import__('engines.' + engine_name).__dict__[engine_name].__dict__['engine']()
        self.one_step_mode = True
        self.continuable = True
        self.board = None
        self.total_time = None
        self.use_time = None
        self.has_game = False

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(self.caption)
        self.repaint()

        self.run_game()

        # wait for quit
        while True:
            self.repaint()

    def repaint(self):
        self.handle_event()

        self.screen.fill(self.bg_color)
        # draw board
        for i in range(0, 9):
            p1 = (self.board_x + i * self.grid_size, self.board_y)
            p2 = (self.board_x + i * self.grid_size, self.board_y + 8 * self.grid_size)
            pygame.draw.line(self.screen, self.board_color, p1, p2, self.boarder_width)
            p1 = (self.board_x, self.board_y + i * self.grid_size)
            p2 = (self.board_x + 8 * self.grid_size, self.board_y + i * self.grid_size)
            pygame.draw.line(self.screen, self.board_color, p1, p2, self.boarder_width)
            if i > 0:
                self.draw_text(chr(64 + i), self.board_x + i * self.grid_size - self.grid_size / 2,
                               self.board_y - self.grid_size)
                self.draw_text(str(i), self.board_x - self.grid_size,
                               self.board_y + i * self.grid_size - self.grid_size / 2)
        if self.has_game:
            # draw chess
            for i in range(0, 8):
                for j in range(0, 8):
                    if self.board[i][j] is not 0:
                        pygame.draw.circle(self.screen, self.player_color[self.board[i][j]],
                                           [self.board_x + i * self.grid_size + self.grid_size / 2,
                                            self.board_y + j * self.grid_size + self.grid_size / 2],
                                           self.grid_size / 3, 0)
            # emphasize last move
            if self.current_move is not None:
                x = self.current_move[0]
                y = self.current_move[1]
                for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    point_center = [self.board_x + x * self.grid_size + self.grid_size / 2,
                                    self.board_y + y * self.grid_size + self.grid_size / 2]
                    point_angle = [point_center[0] + direction[0] * self.emphasize_size / 2,
                                   point_center[1] + direction[1] * self.emphasize_size / 2]
                    p1 = [point_angle[0], point_angle[1] - direction[1] * self.emphasize_length]
                    p2 = [point_angle[0] - direction[0] * self.emphasize_length, point_angle[1]]
                    pygame.draw.line(self.screen, self.player_color[0], point_angle, p1, 3)
                    pygame.draw.line(self.screen, self.player_color[0], point_angle, p2, 3)
            # draw score
            pygame.draw.circle(self.screen, self.player_color[-1],
                               [self.window_width / 4 + self.board_x * 3 / 2 + self.grid_size * 6, self.grid_size],
                               self.grid_size / 2, 0)
            pygame.draw.circle(self.screen, self.player_color[1],
                               [self.window_width * 3 / 4 + self.board_x / 2 + self.grid_size * 2, self.grid_size],
                               self.grid_size / 2, 0)
            self.draw_text(str(self.board.count(-1)), self.window_width / 4 + self.board_x * 3 / 2 + self.grid_size * 6,
                           self.grid_size * 2)
            self.draw_text(str(self.board.count(1)), self.window_width * 3 / 4 + self.board_x / 2 + self.grid_size * 2,
                           self.grid_size * 2)
            # draw time
            self.draw_text(str(self.total_time[-1]), self.window_width / 4 + self.board_x * 3 / 2 + self.grid_size * 6,
                           self.grid_size * 3)
            self.draw_text(str(self.total_time[1]), self.window_width * 3 / 4 + self.board_x / 2 + self.grid_size * 2,
                           self.grid_size * 3)
            self.draw_text(str(self.use_time[-1]), self.window_width / 4 + self.board_x * 3 / 2 + self.grid_size * 6,
                           self.grid_size * 4)
            self.draw_text(str(self.use_time[1]), self.window_width * 3 / 4 + self.board_x / 2 + self.grid_size * 2,
                           self.grid_size * 4)
        pygame.display.flip()

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.continuable = True
                elif event.key == pygame.K_SPACE:
                    self.one_step_mode = not self.one_step_mode

    def get_move(self, move_num, color):
        legal_moves = self.board.get_legal_moves(color)

        if not legal_moves:
            return None
        else:
            try:
                move = self.engines[color].get_move(self.board, color, move_num, self.total_time[color])
            except Exception as e:
                print(traceback.format_exc())
                raise SystemError(color)

            if move not in legal_moves:
                raise LookupError(color)

            return move

    def draw_text(self, text, posx, posy, text_height=30, font_color=(0, 0, 0), background_color=None):
        if background_color is None:
            background_color = self.bg_color
        font_obj = pygame.font.Font('Arial.ttf', text_height)
        text_surface_obj = font_obj.render(text, True, font_color, background_color)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = (posx, posy)
        self.screen.blit(text_surface_obj, text_rect_obj)

    def run_game(self):
        # run a game
        self.board = Board()
        self.total_time = {-1: 1800, 1: 1800}
        self.use_time = {-1: 0, 1: 0}
        self.has_game = True
        # do rounds
        try:
            for move_num in range(0, 35):
                one_has_move = False
                for self.current_color in [-1, 1]:
                    self.continuable = False
                    start_time = timeit.default_timer()
                    self.current_move = self.get_move(move_num, self.current_color)
                    end_time = timeit.default_timer()
                    self.use_time[self.current_color] = use_time = round(end_time - start_time, 1)
                    self.total_time[self.current_color] -= use_time
                    if self.total_time[self.current_color] < 0:
                        raise RuntimeError(self.current_color)
                    if self.current_move is not None:
                        self.board.execute_move(self.current_move, self.current_color)
                        one_has_move = True
                    self.repaint()
                    while self.one_step_mode and not self.continuable:
                        self.handle_event()
                        time.sleep(0.1)
                        pass
                if not one_has_move:
                    break
        except RuntimeError as err:
            pass
        except LookupError as err:
            pass
        except SystemError as err:
            pass


VisualGame()
