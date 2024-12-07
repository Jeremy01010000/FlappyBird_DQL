import os, constants
import pygame as pg
from core.game import Bird, Pipe

class VisualManager:
    def __init__(self, assets_path:str):
        pg.init()
        self.assets_path = assets_path
        self.window = pg.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
        pg.display.set_caption("Flappy Bird")
        self.clock:pg.time.Clock = pg.time.Clock()
        self.font:pg.font.Font = pg.font.Font(f"{self.assets_path}/fonts/retro.ttf", 32)
        self.assets:dict[str,pg.Surface] = {}
        self.load_assets()
        self.format_assets()

    def load_assets(self) -> None:
        """Loading Assets into Dictionary"""
        for file in os.listdir(f"{self.assets_path}/images/"):
            if file.startswith("."):
                continue
            self.assets[file.split(".")[0]] = pg.image.load(f"{self.assets_path}/images/{file}").convert_alpha()

    def format_assets(self) -> None:
        """Format All Assets to their Desired Sizes"""
        self.assets["Forest"] = pg.transform.scale(self.assets["Forest"], (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
        self.assets["Pipe"] = pg.transform.scale(self.assets["Pipe"], tuple(constants.PIPE_SIZE.values()))
        self.assets["Pipe2"] = pg.transform.scale(self.assets["Pipe2"], tuple(constants.PIPE_SIZE.values()))
        self.assets["Flappy"] = pg.transform.scale(self.assets["Flappy"], tuple(constants.BIRD_SIZE.values()))

    def draw_landscape(self, iterations:int) -> None:
        """Draws the Background; Using Two to Simulate Continuous Image"""
        self.window.blit(self.assets["Forest"], (0 - iterations % constants.WINDOW_WIDTH, 0))
        self.window.blit(self.assets["Forest"], (constants.WINDOW_WIDTH - iterations % constants.WINDOW_WIDTH, 0))

    def draw_objects(self, bird:Bird, pipes:list[Pipe]) -> None:
        """Draw Images onto Window"""
        self.window.blit(self.assets["Flappy"], (bird.x, bird.y))
        for pipe in pipes:
            self.window.blit(self.assets["Pipe"], (pipe.x, pipe.y - 500 - constants.PIPE_GAP))
            self.window.blit(self.assets["Pipe2"], (pipe.x, pipe.y + constants.PIPE_GAP))

    def display_score(self, score:int, reward:int) -> None:
        """Display Score onto Screen"""
        score_text = self.font.render(f'Score: {score}', True, (0, 0, 0))
        self.window.blit(score_text, (constants.WINDOW_WIDTH // 2 - 50, 25))
        reward_text = self.font.render(f'Reward: {reward}', True, (0, 0, 0))
        self.window.blit(reward_text, (constants.WINDOW_WIDTH // 2 - 50, 50))

    def display_score_zones(self, bird:Bird, pipe:Pipe) -> None:
        """Provides Ability to Display High Reward Zones"""
        transparent_surface = pg.Surface(self.window.get_size(), pg.SRCALPHA)
        # Green Zone ; High Reward For Bird
        high_reward_zone = pg.Rect(
            0, 
            (pipe.y - constants.PIPE_GAP * constants.CENTER_FOCUS) + constants.PIPE_GAP * constants.SHIFT_DOWN, 
            constants.WINDOW_WIDTH, 
            constants.PIPE_GAP * 2 * constants.CENTER_FOCUS
        )
        # Blue Line ; Bird's Considered Center in the Green Zone
        bird_hitbox_center = pg.Rect(
            0, 
            bird.y + constants.BIRD_SIZE["Y"] // 2 - 2, 
            constants.WINDOW_WIDTH, 
            4
        )

        # Draw onto the overlay surface
        pg.draw.rect(transparent_surface, (0,255,0,100), high_reward_zone)
        pg.draw.rect(transparent_surface, (0,0,255,100), bird_hitbox_center)
        # Overlay the transparent surface onto the game's surface to allow transparency
        self.window.blit(transparent_surface, (0, 0))
        pg.display.update()

    def draw_window(self, iterations:int, bird:Bird, pipes:list[Pipe], reward:int, score:int, fps:int=constants.FPS, show_reward_zone:bool=False) -> None:
        """Main Drawing Function Calling All Other Functions; Granular"""
        self.draw_landscape(iterations)
        self.draw_objects(bird, pipes)
        self.display_score(score, reward)
        if show_reward_zone:
            self.display_score_zones(bird, pipes[0])
        pg.display.update()
        self.clock.tick(fps)