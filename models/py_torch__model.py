import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as functional
import os

from logger import self_logger


class Linear_QNet(nn.Module):
    def __init__(
        self,
        input_layer_size,
        hidden_layer_1_size,
        hidden_layer_2_size,
        output_layer_size,
        *,
        file_name='model.pth',
    ):
        super().__init__()
        self._file_name = file_name

        self.linear1 = nn.Linear(input_layer_size, hidden_layer_1_size)
        self.linear2 = nn.Linear(hidden_layer_1_size, hidden_layer_2_size)
        self.linear3 = nn.Linear(hidden_layer_2_size, output_layer_size)

    def forward(self, x):
        x = functional.relu(self.linear1(x))
        x = self.linear2(x)
        x = self.linear3(x)
        return x

    @property
    def file_name(self):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        return os.path.join(model_folder_path, self._file_name)

    def save(self):
        torch.save(self.state_dict(), self.file_name)

    def load(self):
        try:
            self.load_state_dict(torch.load(self.file_name))
        except FileNotFoundError:
            self_logger.warning('File not found. New model will be created.')
        else:
            self.eval()
            self_logger.warning('Model was loaded successfully.')


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
