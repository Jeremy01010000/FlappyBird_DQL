import constants
from random import randint

class Bird:
    def __init__(self):
        self.x = constants.BIRD_INIT["X"]
        self.y = constants.BIRD_INIT["Y"]
        self.velocity:float = 0.0

    def flap(self) -> None:
        """Increases Bird's Velocity"""
        self.velocity -= constants.FLAP_CONST

    def update(self, gravity:float) -> None:
        """Update Velocity"""
        self.velocity += gravity
        self.y += int(self.velocity)

class Pipe:
    def __init__(self):
        self.x:int = constants.WINDOW_WIDTH + 50
        self.y:int = randint(constants.PIPE_MIN_MAX_OFFSET, constants.WINDOW_HEIGHT - constants.PIPE_MIN_MAX_OFFSET)
        self.gap:int = constants.PIPE_GAP
        self.cleared:bool = False

    def update(self) -> bool:
        """Update Pipe's X"""
        self.x -= constants.GAME_X_SPEED
        return self.x > -constants.PIPE_SIZE["X"]

class Environment:
    def __init__(self):
        self.run:bool           = True
        self.gravity:float      = constants.GRAVITY
        self.score:int          = 0
        self.frames:int         = 0
        self.bird:Bird          = Bird()
        self.pipes:list[Pipe]   = list()
        self.ceil:int           = 0
        self.floor:int          = constants.WINDOW_HEIGHT

    def update_variables(self) -> None:
        """Update variables for next frame"""
        self.pipes = [pipe for pipe in self.pipes if pipe.update()]
        self.bird.velocity = max(-constants.MAX_VEL, min(constants.MAX_VEL, self.bird.velocity))
        self.bird.update(self.gravity)
        self.frames += 1

    def create_pipe(self):
        """Create New Pipes"""
        if constants.WINDOW_WIDTH < 500:
            if self.frames % (constants.WINDOW_WIDTH // constants.GAME_X_SPEED) == 0:
                self.pipes.append(Pipe())
        else:
            if self.frames % 100 == 0:
                self.pipes.append(Pipe())

    def pipe_cleared(self):
        """Verifies if pipe passed for first time"""
        if self.pipes and self.bird.x > self.pipes[0].x and not self.pipes[0].cleared:
            self.score += 1
            self.pipes[0].cleared = True
            return True
        return False

    def detect_collision(self) -> None:
        """True: Continue - False: Stop"""
        # Check for floor collisions
        if self.bird.y <= self.ceil or self.bird.y >= self.floor - constants.BIRD_SIZE["Y"]:
            self.run = False
            return
        # Check for pipe collisions
        for pipe in self.pipes:
            if (self.bird.x + constants.BIRD_SIZE["X"] > pipe.x and self.bird.x < pipe.x + constants.PIPE_SIZE["X"]):
                if (self.bird.y < pipe.y - constants.PIPE_GAP or self.bird.y + constants.BIRD_SIZE["Y"] > pipe.y + constants.PIPE_GAP):
                    self.run = False
                    return
        self.run = True
    
    def reward(self, action:int) -> float:
        """Rewarding System"""
        reward = 0.5 # Surviving
        if self.run:
            # In Increased Reward Zone ; Green Zone when Visuals.display_score_zones() is turned on
            if abs((self.pipes[0].y + constants.PIPE_GAP * constants.SHIFT_DOWN) - (self.bird.y + constants.BIRD_SIZE["Y"]//2)) < constants.PIPE_GAP * constants.CENTER_FOCUS:
                reward = 20 + 0.01 * self.score
            # If the Bird is higher than pipes and flaps, moves towards death, therefore big reward deduction
            if self.bird.y + constants.BIRD_SIZE["Y"] < self.pipes[0].y - constants.PIPE_GAP and action == 1:
                reward -= 20
            # If the Bird is lower than pipes and doesn't flaps, moves towards death, therefore big reward deduction
            if self.bird.y  > self.pipes[0].y + constants.PIPE_GAP and action == 0:
                reward -= 20
        else:
            reward = -100 # Collision
        return reward