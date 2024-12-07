import pygame as pg
from random import randint
import os
from agent import QLearningAgent
from managers.Visuals import VisualManager
from managers.Audio import AudioManager
import torch
from utils.Plotting import Plotter
import constants, time, shutil
from core.game import Environment as Env


class FlappyBird:
    def __init__(self):
        self.assets_path:str = os.path.dirname(os.path.abspath(__file__)) + "/assets"
        self.init_pygame()          # PyGame Objects
        self.plotter = Plotter()    # MatPlotLib Plotting

        # Agent Creation
        self.agent = QLearningAgent(
            state_size=constants.INPUT, 
            action_size=constants.OUTPUT, 
            assets_path=self.assets_path,
            save_interval=constants.SAVE_INTERVAL,
            memory_size=constants.MEMORY_SIZE
        )
        if constants.LOAD_MODEL:
            self.agent.load_model()

    def init_pygame(self) -> None:
        """Initializes the PyGame Managers and Variables"""
        self.audio_manager = AudioManager(self.assets_path)
        self.visual_manager = VisualManager(self.assets_path)

        self.fps:int = constants.FPS
        self.play:bool = constants.SOUND_ENABLED
        self.show:bool = constants.SHOW_GAME
        self.show_reward_zone:bool = True

    def get_state(self, game:Env) -> torch.Tensor:
        """Get Necessary states from Game to Train AI"""
        return torch.tensor(
            [
                float((game.bird.y + constants.BIRD_SIZE["Y"]//2) - game.pipes[0].y),      # First Pipe
                float(game.bird.velocity),                                                 # Bird's Y Velocity
            ],
            dtype=torch.float32
        )

    def handle_event(self, event:pg.event.Event) -> None:
        """Handling All User Inputs"""
        if event.type == pg.QUIT:
            if constants.SAVE_MODEL:
                self.save_as_model()
            exit(0)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                # self.play = not self.play # Playing Sounds
                self.show_reward_zone = not self.show_reward_zone
            elif event.button == 3: # Right Click
                self.show = not self.show
            elif event.button == 4: # Scroll Up
                self.fps += 5
            elif event.button == 5: # Scroll Down
                self.fps -= 5

    def save_as_model(self) -> None:
        """Once Game is Over or Max Number of Training Games are Done, Save the Snapshot of the Used Model"""
        folder_name = f"Model{time.strftime('%Y%b%d-%H:%M:%S')}"
        path = f"{self.assets_path}/models/{folder_name}"
        os.mkdir(path)

        for file in constants.SAVE_FILES:
            shutil.copyfile(f"{os.path.dirname(os.path.abspath(__file__))}/{file}.py", f"{path}/{file}.py")
        self.plotter.save_graph(f"{path}")
        self.agent.save_model(f"{path}")

    def game_loop(self) -> None:
        while True:
            game:Env = Env()
            if self.agent.num_games == constants.TRAIN_X_ITER:
                if self.agent.top_score > constants.SAVE_IF_SCORE:
                    self.save_as_model()
                game.run = False
                return
            while game.run:
                for event in pg.event.get():
                    self.handle_event(event)
                        
                game.create_pipe()

                state = self.get_state(game)
                action = self.agent.act(state)
                if action == 1:
                    game.bird.flap()
                    self.audio_manager.play_sound("sfx_wing", (self.play and constants.FLAP_SOUND_ENABLED))

#################################### Env ####################################
                game.update_variables()
                game.detect_collision()
                reward:int = game.reward(action)

                if self.show:
                    self.visual_manager.draw_window(game.frames, game.bird, game.pipes, reward, game.score, self.fps, self.show_reward_zone)

                if game.pipe_cleared():
                    self.audio_manager.play_sound("sfx_point", (self.play and constants.POINT_SOUND_ENABLED))
##############################################################################
                
                next_state = self.get_state(game)
                self.agent.update_agent(game, state, action, reward, next_state)

            self.agent.update_game_record(game)
            self.plotter.add_game(game.score, (self.agent.all_scores/self.agent.num_games))

if __name__ == "__main__":
    game = FlappyBird()
    game.game_loop()
