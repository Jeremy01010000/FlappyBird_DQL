import constants, os, torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
from core.game import Environment

class QNetwork(nn.Module):
    def __init__(self, state_size: int, action_size: int):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, constants.HL_NODES)
        self.fc2 = nn.Linear(constants.HL_NODES, constants.HL_NODES)
        self.fc3 = nn.Linear(constants.HL_NODES, constants.HL_NODES)
        self.fc4 = nn.Linear(constants.HL_NODES, constants.HL_NODES)
        self.fc5 = nn.Linear(constants.HL_NODES, action_size)

    def forward(self, x) -> nn.Linear:
        """Feed Forward"""
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        y = self.fc5(x)
        return y


class QLearningAgent:
    def __init__(self, state_size:int, action_size:int, assets_path:str, save_interval:int=500, memory_size:int=1000):
        ## Paths
        self.assets_path:str = assets_path
        self.models_path:str = f"{self.assets_path}/models"

        ## Parameters
        self.state_size                     = state_size
        self.action_size                    = action_size
        self.memory:deque                   = deque(maxlen=memory_size)
        ## HyperParameters
        self.gamma:float                    = constants.AGENT_GAMMA
        self.epsilon:float                  = constants.AGENT_EPSILON
        self.epsilon_min:float              = constants.AGENT_EPSILON_MIN
        self.epsilon_decay:float            = constants.AGENT_EPSILON_EXP_DECAY
        self.epsilon_linear:float           = constants.AGENT_EPSILON_LINEAR_DECAY
        self.initial_learning_rate:float    = constants.AGENT_INIT_LEARNING_RATE
        self.min_learning_rate:float        = constants.AGENT_MIN_LEARNING_RATE
        self.decay_iterations:float         = constants.AGENT_LEARNING_RATE_ITERATIONS

        self.model = QNetwork(state_size, action_size)
        self.target_model = QNetwork(state_size, action_size)
        self.target_model.load_state_dict(self.model.state_dict())

        self.optimizer = optim.RMSprop(self.model.parameters(), lr=self.initial_learning_rate)
        self.criterion = nn.MSELoss()
        self.save_interval:int = save_interval

        ## Game Related Values
        self.num_games:int = 1
        self.top_score:int = 0
        self.last_score:int = 0
        self.all_scores: int = 0

        self.update_model = True

    def act(self, state:torch.Tensor) -> None:
        """Flap or Don't Flap"""
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.model(state_tensor)
            return torch.argmax(q_values).item()

    def remember(self, state:torch.Tensor, action:int, reward:float, next_state:torch.Tensor, done:bool) -> None:
        """Add frame to memory"""
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size:int=64) -> None:
        """Learning"""
        if len(self.memory) < batch_size:
            return

        batch = [self.memory[idx] for idx in np.random.choice(len(self.memory), batch_size)]

        states, actions, rewards, next_states, dones = zip(*batch)

        states_tensor = torch.FloatTensor(np.array(states))
        actions_tensor = torch.LongTensor(actions).unsqueeze(1)
        rewards_tensor = torch.FloatTensor(rewards).unsqueeze(1)
        next_states_tensor = torch.FloatTensor(np.array(next_states))
        dones_tensor = torch.BoolTensor(dones).unsqueeze(1)

        q_values = self.model(states_tensor).gather(1, actions_tensor)

        with torch.no_grad():
            next_action = torch.argmax(self.model(next_states_tensor), dim=1, keepdim=True)
            next_q_values = self.target_model(next_states_tensor).gather(1, next_action)
            target_q_values = rewards_tensor + (1 - dones_tensor.float()) * self.gamma * next_q_values

        loss = self.criterion(q_values, target_q_values)

        self.update_learning_rate()

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

        if self.num_games % constants.UPDATE_MODEL_DICT_EVERY == 0:
            self.target_model.load_state_dict(self.model.state_dict())

    def update_learning_rate(self) -> None:
        """Dynamic Changing of Learning Rate"""
        current_learning_rate = max(
            self.min_learning_rate,
            self.initial_learning_rate * np.exp(-self.num_games / self.decay_iterations)
        )
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = current_learning_rate

    def update_agent(self, game:Environment, state: torch.Tensor, action: int, reward: int, next_state: torch.Tensor) -> None:
        """Update Agent's Memory ; Remembers / Learns Experience"""
        self.remember(state, action, reward, next_state, not game.run)
        if self.top_score < constants.STOP_NEW_LEARNING_AFTER_SCORE:
            self.replay(batch_size=constants.BATCH_SIZE)

    def update_scores(self, current_score:int) -> None:
        """Update both Last/Top Scores for Further Usage"""
        self.last_score = current_score
        if current_score > self.top_score:
            self.top_score = current_score

    def update_game_record(self, game:Environment) -> None:
        """After each game, reset/update all variables"""
        self.last_score = game.score
        self.all_scores += game.score
        self.top_score = max(self.top_score, game.score)
        self.num_games += 1
        # Testing with both Exponential/Linear Decay
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        # self.epsilon = max(self.epsilon_min, self.epsilon - self.epsilon_linear)
        self.print_scores_and_info()
        self.update_model = True

    def print_scores_and_info(self) -> None:
        """Terminal Information; Centralized to Add/Remove Desired Info"""
        print(
            f"Iteration: {self.num_games} ; " +
            f"Top Score: {self.top_score} ; " +
            f"Last Score: {self.last_score} ; " +
            f"Epsilon: {self.epsilon:.6f} ; " +
            f"Memory size: {len(self.memory)}"
        )

    def save_model(self, location:str) -> None:
        """Save Model to later Re-use"""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'memory': self.memory,
                'num_games': self.num_games,
                'top_score': self.top_score,
                'epsilon': self.epsilon,
            }, f'{location}/{constants.MODEL_NAME["file"]}.pth')
            print("Model saved!")
        except:
            print(f"Can't Save Model, Folder {location} does not exist.")

    def load_model(self) -> None:
        """Load Previous Model if it Exists"""
        try:
            if os.path.exists(f'{self.models_path}/{constants.MODEL_NAME["folder"]}/'):
                checkpoint = torch.load(f'{self.models_path}/{constants.MODEL_NAME["folder"]}/{constants.MODEL_NAME["file"]}.pth')
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                self.memory = checkpoint['memory']
                self.num_games = checkpoint['num_games']
                self.top_score = checkpoint['top_score']
                self.epsilon = checkpoint['epsilon']
                print("Model loaded!")
            else:
                print("Path does not Exist")
        except:
            print(f"Failed to Load Model")