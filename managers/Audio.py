import os
import pygame as pg

class AudioManager:
    def __init__(self, assets_path:str):
        pg.mixer.init()
        self.assets_path = assets_path
        self.sounds: dict[str,pg.mixer.Sound] = {}
        self.load_sounds()

    def load_sounds(self) -> None:
        """Load Sounds into Dictionary"""
        for file in os.listdir(f"{self.assets_path}/sounds"):
            self.sounds[file.split(".")[0]] = pg.mixer.Sound(f"{self.assets_path}/sounds/{file}")

    def play_sound(self, sound_name:str, play_sound:bool) -> None:
        """Play Sounds if True"""
        if play_sound and sound_name in self.sounds:
            self.sounds[sound_name].play()        