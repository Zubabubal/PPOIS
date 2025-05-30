import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.set_num_channels(16)
        self.sounds = {}
        sound_path = "sounds"
        try:
            self.sounds = {
                'rotate': pygame.mixer.Sound(os.path.join(sound_path, 'rotate.wav')),
                'move': pygame.mixer.Sound(os.path.join(sound_path, 'move.wav')),
                'drop': pygame.mixer.Sound(os.path.join(sound_path, 'drop.wav')),
                'line_clear': pygame.mixer.Sound(os.path.join(sound_path, 'line_clear.wav')),
                'game_over': pygame.mixer.Sound(os.path.join(sound_path, 'game_over.wav')),
                'background': pygame.mixer.Sound(os.path.join(sound_path, 'background.wav'))
            }
            self.sounds['rotate'].set_volume(1.0)
            self.sounds['move'].set_volume(1.0)
            self.sounds['drop'].set_volume(1.0)
            self.sounds['line_clear'].set_volume(1.0)
            self.sounds['game_over'].set_volume(1.0)
            self.sounds['background'].set_volume(0.5)
        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")
            self.sounds = {
                'rotate': None,
                'move': None,
                'drop': None,
                'line_clear': None,
                'game_over': None,
                'background': None
            }
        self.background_playing = False

    def play(self, sound_name, loops=0):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play(loops=loops)
            except Exception as e:
                print(f"Ошибка воспроизведения звука {sound_name}: {e}")

    def stop(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].stop()
            except Exception as e:
                print(f"Ошибка остановки звука {sound_name}: {e}")

    def play_background(self):
        if not self.background_playing and self.sounds.get('background'):
            try:
                self.sounds['background'].play(loops=-1)
                self.background_playing = True
            except Exception as e:
                print(f"Ошибка воспроизведения фоновой музыки: {e}")

    def stop_background(self):
        if self.background_playing and self.sounds.get('background'):
            try:
                self.sounds['background'].stop()
                self.background_playing = False
            except Exception as e:
                print(f"Ошибка остановки фоновой музыки: {e}")
