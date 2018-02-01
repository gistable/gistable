import os
import random
import gym


class Hanamichi():

    def __init__(self):
        self.actions = [2, 3]  # up and down
        self.fun = []

    def start(self, observation):
        self.fun = []
        return self.act(observation, 0)
    
    def act(self, observation, last_reward):
        if len(self.fun) == 0:
            print("\nFUN", end="")
            fun_length = random.randint(5, 15)
            self.actions = self.actions[::-1]
            self.fun = sum([[a] * fun_length for a in self.actions], [])
        elif self.fun[0] == self.actions[0]:
            print(">" if self.fun[0] == 2 else "<", end="")

        action = self.fun.pop(-1)

        if last_reward > 0:  # lose
            print("TENSAI!!!!!")
            self.fun = [0] * 5  # stop a while to shout

        return action
    
    def end(self, last_reward):
        print("")


def main(game_count=1):
    record = os.path.join(os.path.dirname(__file__), "funfun")
    env = gym.make("Pong-v0")
    hanamichi = Hanamichi()

    env.monitor.start(record)
    for i in range(game_count):
        playing = True
        observation = env.reset()
        reward = -1
        action = -1

        while playing:
            env.render()
            if action < 0:
                action = hanamichi.start(observation)
            else:
                action = hanamichi.act(observation, reward)
            observation, reward, done, info = env.step(action)
            playing = not done
            if done:
                hanamichi.end(reward)

    env.monitor.close()


if __name__ == "__main__":
    main()
