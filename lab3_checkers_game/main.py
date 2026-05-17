import pygame
import sys
import os
from app.consts import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, PAUSE_BTN_RECT
from app.renderer import Renderer
from app.menu import Menu, PauseMenu, GameOverMenu
from core.board import Board
from core.enums import Color, PlayerMode
from app.game import GameController
from app.audio import AudioManager



def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Шашки")

    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        icon_img = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_img)
    else:
        print(f"Ошибка: Файл иконки '{icon_path}' не найден.")

    clock = pygame.time.Clock()
    main_menu = Menu(screen)
    pause_menu = PauseMenu(screen)
    game_over_menu = GameOverMenu(screen)
    renderer = Renderer(screen)
    audio = AudioManager()

    state = "MENU"
    board = None
    controller = None
    winner = None

    running = True
    while running:
        clock.tick(FPS)

        if state == "MENU":
            main_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_mode = main_menu.handle_click(pygame.mouse.get_pos())
                    if selected_mode:
                        board = Board()
                        controller = GameController(board, selected_mode)
                        state = "GAME"

        elif state == "GAME":
            flip_board = (controller.mode == PlayerMode.VERSUS and controller.turn == Color.BLACK)

            winner = board.winner()
            if winner:
                state = "GAME_OVER"
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if PAUSE_BTN_RECT.collidepoint(pos):
                        state = "PAUSE"
                    else:
                        row, col = controller.get_row_col_from_mouse(pos, flip_board)
                        controller.select(row, col, renderer, flip_board, clock, audio)


            if state == "GAME":
                renderer.draw_board(board, controller, flip_board)

        elif state == "PAUSE":
            pause_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = pause_menu.handle_click(pygame.mouse.get_pos())
                    if action == "RESUME":
                        state = "GAME"
                    elif action == "RESTART":
                        board = Board()
                        controller = GameController(board, controller.mode)
                        state = "GAME"
                    elif action == "MENU":
                        state = "MENU"

        elif state == "GAME_OVER":
            game_over_menu.draw(winner)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = game_over_menu.handle_click(pygame.mouse.get_pos())
                    if action == "RESTART":
                        board = Board()
                        controller = GameController(board, controller.mode)
                        state = "GAME"
                    elif action == "MENU":
                        state = "MENU"
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()