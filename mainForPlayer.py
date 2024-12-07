import pygame as pg
import os
from managers.Visuals import VisualManager
from managers.Audio import AudioManager
from utils.Plotting import Plotter
from constants import *
from core.game import *

class FlappyBird:
    def __init__(self):
        self.project_path:str = os.path.dirname(os.path.abspath(__file__)) + "/assets"

        # Initialize Pygame Elements
        self.init_pygame()

        self.plotter = Plotter()

    def init_pygame(self) -> None:
        # Initialize managers
        self.audio_manager:AudioManager = AudioManager(self.project_path)
        self.visual_manager:VisualManager = VisualManager(self.project_path)

        self.fps:int = FPS
        self.play:bool = SOUND_ENABLED
        self.show:bool = True


    def handle_event(self, event:pg.event.Event) -> bool:
        if event.type == pg.QUIT:
            exit(0)
            return False
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            return True

    def game_loop(self) -> None:
        while True:
            game:Environment = Environment()
            while game.run:
                for event in pg.event.get():
                    if self.handle_event(event):
                        game.bird.flap()
                        self.audio_manager.play_sound("sfx_wing", (self.play and FLAP_SOUND_ENABLED))

                if game.frames % (WINDOW_WIDTH // GAME_X_SPEED) == 0:
                    game.pipes.append(Pipe())

#################################### Game ####################################
                game.update_variables()
                game.detect_collision()
                reward:int = None

                if self.show:
                    self.visual_manager.draw_window(game.frames, game.bird, game.pipes, reward, game.score, self.fps)

                if game.pipe_cleared():
                    self.audio_manager.play_sound("sfx_point", (self.play and POINT_SOUND_ENABLED))
##############################################################################

            self.plotter.add_game(game.score)

if __name__ == "__main__":
    game = FlappyBird()
    game.game_loop()
