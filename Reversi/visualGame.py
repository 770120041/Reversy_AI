import sys
import pygame
from board import Board
import timeit
import traceback
import time


class VisualGame:
    def __init__(self):
        self.engines_name = {-1: 'human', 1: 'simple'}

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
        self.hint_size = 40
        self.hint_length = 5
        self.bg_color = (231, 233, 210)
        self.board_color = (36, 40, 41)
        self.player_color = {-1: (0, 0, 0), 1: (255, 255, 255)}
        self.emphasize_color = (230, 80, 80)
        self.hint_color = (6, 156, 130)
        self.current_turn = -1
        self.hint_turn = -1
        self.engines = {-1: None, 1: None}
        for i in [-1, 1]:
            engine_name = self.engines_name[i]
            self.engines[i] = __import__('engines.' + engine_name).__dict__[engine_name].__dict__['engine']()
        self.has_human_player = 'human' in self.engines_name[-1]
        self.one_step_mode = self.switch_to_one_step_mode(True)
        self.continuable = True
        self.board = None
        self.total_time = None
        self.use_time = None
        self.has_game = False
        self.current_move = None
        self.waiting_for_player = False
        self.move_player_choose = None

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(self.caption)
        self.repaint()

        self.run_game()

        # wait for quit
        while True:
            self.handle_event()

    def repaint(self):
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
                                           self.pos_transform_index_to_pixel(i, j),
                                           self.grid_size / 3, 0)
            # emphasize last move
            if self.current_move is not None:
                x = self.current_move[0]
                y = self.current_move[1]
                for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    point_center = self.pos_transform_index_to_pixel(x, y)
                    point_angle = [point_center[0] + direction[0] * self.emphasize_size / 2,
                                   point_center[1] + direction[1] * self.emphasize_size / 2]
                    p1 = [point_angle[0], point_angle[1] - direction[1] * self.emphasize_length]
                    p2 = [point_angle[0] - direction[0] * self.emphasize_length, point_angle[1]]
                    pygame.draw.line(self.screen, self.emphasize_color, point_angle, p1, 3)
                    pygame.draw.line(self.screen, self.emphasize_color, point_angle, p2, 3)
            # draw possible move
            possible_moves = self.board.get_legal_moves(self.hint_turn)
            for possible_move in possible_moves:
                x = possible_move[0]
                y = possible_move[1]
                for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    point_center = self.pos_transform_index_to_pixel(x, y)
                    point_angle = [point_center[0] + direction[0] * self.hint_size / 2,
                                   point_center[1] + direction[1] * self.hint_size / 2]
                    p1 = [point_angle[0], point_angle[1] - direction[1] * self.hint_length]
                    p2 = [point_angle[0] - direction[0] * self.hint_length, point_angle[1]]
                    pygame.draw.line(self.screen, self.hint_color, point_angle, p1, 3)
                    pygame.draw.line(self.screen, self.hint_color, point_angle, p2, 3)
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
                    self.one_step_mode = self.switch_to_one_step_mode(not self.one_step_mode)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.waiting_for_player:
                    mouse_pos = pygame.mouse.get_pos()
                    grid_chosen = self.pos_transform_pixel_to_index(mouse_pos[0], mouse_pos[1])
                    possible_moves = self.board.get_legal_moves(self.current_turn)
                    for possible_move in possible_moves:
                        if grid_chosen[0] == possible_move[0] and grid_chosen[1] == possible_move[1]:
                            self.move_player_choose = grid_chosen
                            self.waiting_for_player = False
                            break

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
                for self.current_turn in [-1, 1]:
                    self.hint_turn = self.current_turn
                    self.repaint()
                    self.continuable = False
                    start_time = timeit.default_timer()
                    if self.engines_name[self.current_turn] is not 'human':
                        self.current_move = self.get_move(move_num, self.current_turn)
                    else:
                        self.current_move = self.wait_for_player()
                    end_time = timeit.default_timer()
                    self.use_time[self.current_turn] = use_time = round(end_time - start_time, 1)
                    self.total_time[self.current_turn] -= use_time
                    if self.total_time[self.current_turn] < 0:
                        raise RuntimeError(self.current_turn)
                    if self.current_move is not None:
                        self.board.execute_move(self.current_move, self.current_turn)
                        one_has_move = True
                        self.hint_turn = -self.hint_turn
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

    def wait_for_player(self):
        possible_moves = self.board.get_legal_moves(self.current_turn)
        if possible_moves:
            self.waiting_for_player = True
            while self.waiting_for_player:
                self.handle_event()
                time.sleep(0.5)
            return self.move_player_choose
        else:
            return None

    def pos_transform_index_to_pixel(self, x, y):
        return [self.board_x + x * self.grid_size + self.grid_size / 2,
                self.board_y + y * self.grid_size + self.grid_size / 2]

    def pos_transform_pixel_to_index(self, x, y):
        return [(x - self.board_x) / self.grid_size, (y - self.board_y) / self.grid_size]

    def switch_to_one_step_mode(self, flag):
        if self.has_human_player:
            return False
        else:
            return flag


VisualGame()
