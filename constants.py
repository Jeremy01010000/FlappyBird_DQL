## PyGame Constants
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 600
FPS = 90

## Environment Constants
# Game
GRAVITY = 0.5
GAME_X_SPEED = 4
MAX_VEL = 8                             # Bird's Max Velocity & The Flap Maxes it Maxed, hence 2 * MAX_VEL
FLAP_CONST = MAX_VEL * 2
# Bird
BIRD_SIZE = {"X": 50, "Y": 40}
BIRD_INIT = {"X": 25, "Y": WINDOW_HEIGHT / 2}
# Pipes
PIPE_SIZE = {"X": 80, "Y": 500}
PIPE_GAP = 150 // 2
PIPE_MIN_MAX_OFFSET = PIPE_GAP + 25     # Pipes Can't Spawn PIPE_MIN_MAX_OFFSET 25 pixels from Floor/Ceil
# Rewards
CENTER_FOCUS = 0.4                      # Give greater rewards if bird's center is within 40% zone of pipe gap
SHIFT_DOWN = 0.1                        # Offset the center focus zone 10% lower

# Agent
HL_NODES = 64
BATCH_SIZE = 32
INPUT, OUTPUT = 2, 2
AGENT_GAMMA = 0.9
AGENT_EPSILON = 0.25
AGENT_EPSILON_MIN = 0.00001
AGENT_EPSILON_EXP_DECAY = 0.9
ITERATIONS = 25
AGENT_EPSILON_LINEAR_DECAY = (AGENT_EPSILON - AGENT_EPSILON_MIN) / ITERATIONS
AGENT_LEARNING_RATE = 0.01
AGENT_INIT_LEARNING_RATE = 0.01
AGENT_MIN_LEARNING_RATE = 0.005
AGENT_LEARNING_RATE_ITERATIONS = 100
SAVE_IF_SCORE = 0
SAVE_INTERVAL = 500
MEMORY_SIZE = 1000
SAVE_FILES = ["agent", "constants", "main"]
UPDATE_MODEL_DICT_EVERY = 1


## Model Iterations
STOP_NEW_LEARNING_AFTER_SCORE = 70
TRAIN_X_ITER = 500


## Enables/Disables
# Sounds
SOUND_ENABLED = False
FLAP_SOUND_ENABLED = False
POINT_SOUND_ENABLED = True
# Model
LOAD_MODEL = False
SAVE_MODEL = True
MODEL_NAME = {"folder": "Model2024Nov27-10:19:40", "file": "flappy_model"}  # Load models from models folder
# PyGame
SHOW_GAME = False