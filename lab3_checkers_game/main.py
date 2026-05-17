import pygame
import sys
import os
from app.consts import cfg
from app.renderer import Renderer
from app.audio import AudioManager
from app.records import RecordManager
from app.menu import MainMenu, PauseMenu, GameOverMenu, SettingsMenu, HelpMenu, NameInputMenu, LeaderboardMenu
from core.board import Board
from core.enums import Color, PlayerMode
from app.game import GameController


def create_screen():
    """Создает окно. Если полноэкранный режим, использует родное разрешение монитора."""
    if cfg.FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
    cfg.update_sizes(screen.get_width(), screen.get_height())
    return screen


def main():
    pygame.init()
    screen = create_screen()
    pygame.display.set_caption("Шашки")

    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        icon_img = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_img)

    clock = pygame.time.Clock()

    records = RecordManager()
    audio = AudioManager()
    audio.play_bg_music()

    main_menu = MainMenu(screen)
    pause_menu = PauseMenu(screen)
    game_over_menu = GameOverMenu(screen)
    settings_menu = SettingsMenu(screen)
    help_menu = HelpMenu(screen)
    name_input_menu = NameInputMenu(screen)
    leaderboard_menu = LeaderboardMenu(screen, records)
    renderer = Renderer(screen)

    state = "MENU"
    board = None
    controller = None
    winner = None

    player_names = {Color.WHITE: "Игрок 1", Color.BLACK: "Игрок 2"}

    running = True
    while running:
        clock.tick(cfg.FPS)

        if state == "MENU":
            main_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = main_menu.handle_click(pygame.mouse.get_pos())

                    if action == PlayerMode.SINGLE:
                        board = Board()
                        controller = GameController(board, action)
                        state = "GAME"

                    elif action == PlayerMode.VERSUS:
                        name_input_menu.white_name = ""
                        name_input_menu.black_name = ""
                        name_input_menu.active_field = 0
                        state = "INPUT_NAMES"

                    elif action == "LEADERBOARD":
                        state = "LEADERBOARD"
                    elif action == "SETTINGS":
                        state = "SETTINGS"
                    elif action == "HELP":
                        state = "HELP"
                    elif action == "QUIT":
                        running = False

        elif state == "INPUT_NAMES":
            name_input_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = name_input_menu.handle_click(pygame.mouse.get_pos())
                    if action == "BACK":
                        state = "MENU"
                    elif action == "START":
                        player_names[Color.WHITE] = name_input_menu.white_name.strip() or "Игрок 1 (Белые)"
                        player_names[Color.BLACK] = name_input_menu.black_name.strip() or "Игрок 2 (Черные)"

                        board = Board()
                        controller = GameController(board, PlayerMode.VERSUS)
                        state = "GAME"

                if event.type == pygame.KEYDOWN:
                    name_input_menu.handle_keydown(event)

        elif state == "LEADERBOARD":
            leaderboard_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if leaderboard_menu.handle_click(pygame.mouse.get_pos()) == "BACK":
                        state = "MENU"

        elif state == "SETTINGS":
            settings_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = settings_menu.handle_click(pygame.mouse.get_pos())

                    changed = False
                    if action == "RES_1":
                        cfg.data["WINDOW_WIDTH"] = 800
                        cfg.data["WINDOW_HEIGHT"] = 880
                        changed = True
                    elif action == "RES_2":
                        cfg.data["WINDOW_WIDTH"] = 1000
                        cfg.data["WINDOW_HEIGHT"] = 1080
                        changed = True
                    elif action == "TOGGLE_FS":
                        cfg.data["FULLSCREEN"] = not cfg.data["FULLSCREEN"]
                        changed = True
                    elif action == "BACK":
                        state = "MENU"

                    if changed:
                        cfg.save()
                        cfg.update_sizes()
                        screen = create_screen()

                        renderer.screen = screen
                        main_menu.screen = screen
                        pause_menu.screen = screen
                        game_over_menu.screen = screen
                        settings_menu.screen = screen

                        main_menu.update_buttons()
                        pause_menu.update_buttons()
                        game_over_menu.update_buttons()
                        settings_menu.update_buttons()

        elif state == "HELP":
            help_menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if help_menu.handle_click(pygame.mouse.get_pos()) == "BACK":
                        state = "MENU"

        elif state == "GAME":
            flip_board = (controller.mode == PlayerMode.VERSUS and controller.turn == Color.BLACK)

            winner = board.winner()
            if winner:
                if controller.mode == PlayerMode.VERSUS:
                    win_color = winner
                    lose_color = Color.BLACK if win_color == Color.WHITE else Color.WHITE

                    win_name = player_names[win_color]
                    lose_name = player_names[lose_color]

                    win_score = 100
                    for r in range(8):
                        for c in range(8):
                            p = board.get_piece(r, c)
                            if p and p.color == win_color:
                                win_score += 20 if p.is_king else 10

                    records.update_record(win_name, win_score)
                    records.update_record(lose_name, -100)

                state = "GAME_OVER"
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if cfg.PAUSE_BTN_RECT.collidepoint(pos):
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
                        if controller.mode == PlayerMode.VERSUS:
                            name_input_menu.white_name = ""
                            name_input_menu.black_name = ""
                            name_input_menu.active_field = 0
                            state = "INPUT_NAMES"
                        else:
                            board = Board()
                            controller = GameController(board, controller.mode)
                            state = "GAME"
                    elif action == "MENU":
                        state = "MENU"

        elif state == "GAME_OVER":
            flip_board = (controller.mode == PlayerMode.VERSUS and controller.turn == Color.BLACK)
            renderer.draw_board(board, controller, flip_board)
            game_over_menu.draw(winner)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = game_over_menu.handle_click(pygame.mouse.get_pos())
                    if action == "RESTART":
                        if controller.mode == PlayerMode.VERSUS:
                            name_input_menu.white_name = ""
                            name_input_menu.black_name = ""
                            name_input_menu.active_field = 0
                            state = "INPUT_NAMES"
                        else:
                            board = Board()
                            controller = GameController(board, controller.mode)
                            state = "GAME"
                    elif action == "MENU":
                        state = "MENU"

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()