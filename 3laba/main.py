import pygame
import asyncio
from tetris_game import TetrisGame
from game_state import GameState
from tetromino import Tetromino

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048)  # Моно

async def main():
    game = TetrisGame()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.sound_manager.stop_background()
                pygame.quit()
                return
            elif game.mode == "menu":
                if selected_difficulty := game.menu.handle_input(event):
                    game.state = GameState(selected_difficulty)
                    game.mode = "game"
                    game.sound_manager.play_background()
            elif game.mode == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game.state.paused = not game.state.paused
                        if game.state.paused:
                            game.sound_manager.stop_background()
                        else:
                            game.sound_manager.play_background()
                    elif event.key == pygame.K_q:
                        game.sound_manager.stop_background()
                        pygame.quit()
                        return
                    elif not game.state.paused and not game.state.game_over:
                        if event.key == pygame.K_LEFT and not game.state.check_collision(dx=-1):
                            game.state.current_tetromino.move(-1, 0)
                            game.sound_manager.play('move')
                        elif event.key == pygame.K_RIGHT and not game.state.check_collision(dx=1):
                            game.state.current_tetromino.move(1, 0)
                            game.sound_manager.play('move')
                        elif event.key == pygame.K_DOWN and not game.state.check_collision(dy=1):
                            game.state.current_tetromino.move(0, 1)
                            game.sound_manager.play('move')
                        elif event.key == pygame.K_UP:
                            original_shape = game.state.current_tetromino.shape
                            game.state.current_tetromino.rotate()
                            if game.state.check_collision():
                                game.state.current_tetromino.shape = original_shape
                            else:
                                game.sound_manager.play('rotate')
                        elif event.key == pygame.K_SPACE:
                            while not game.state.check_collision(dy=1):
                                game.state.current_tetromino.move(0, 1)
                            game.sound_manager.play('drop')
                            game.state.merge()
                            if game.state.clear_lines() > 0:
                                game.sound_manager.play('line_clear')
                            game.state.current_tetromino = game.state.next_tetromino
                            game.state.next_tetromino = Tetromino()
                            if game.state.check_collision():
                                game.state.game_over = True
                                game.sound_manager.play('game_over')
                    elif game.state.game_over and event.key == pygame.K_r:
                        game.mode = "menu"
                        game.sound_manager.play_background()

        if game.mode == "menu":
            game.menu.draw(game.screen)
        elif game.mode == "game" and game.state:
            cleared_lines = game.state.update()
            if cleared_lines > 0:
                game.sound_manager.play('line_clear')
            game.draw_game()

        pygame.display.flip()
        game.clock.tick(game.fps)
        await asyncio.sleep(1.0 / game.fps)

if __name__ == "__main__":
    asyncio.run(main())
