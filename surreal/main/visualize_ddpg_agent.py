import gym
from tabulate import tabulate

from surreal.agent.base import AgentMode
from surreal.agent.ddpg_agent import DDPGAgent
from surreal.env import *
from surreal.replay import *
from surreal.session import *
from surreal.main.halfcheetah_configs import *

import time

env = gym.make('HalfCheetah-v1')
# env._max_episode_steps = 100
env = GymAdapter(env)
env = EpisodeMonitor(env, filename=None)

ddpg_agent = DDPGAgent(
    learn_config=halfcheetah_learn_config,
    env_config=halfcheetah_env_config,
    session_config=halfcheetah_session_config,
    agent_mode=AgentMode.training
)

info_print = PeriodicTracker(1)

ddpg_agent.pull_parameters()

obs, _ = env.reset()
for T in itertools.count():

    action = ddpg_agent.act(U.to_float_tensor(obs))
    obs, reward, done, info = env.step(action)
    env.render()

    if done:
        obs, _ = env.reset()
        if info_print.track_increment():
            # book-keeping, TODO should be done in Evaluator
            info_table = []
            avg_reward = np.mean(env.get_episode_rewards()[-10:])
            info_table.append(['Last 10 rewards', U.fformat(avg_reward, 3)])
            avg_speed = 1 / (float(np.mean(env.get_episode_times()[-10:])) + 1e-6)
            info_table.append(['Speed iter/s', U.fformat(avg_speed, 1)])
            info_table.append(['Total steps', env.get_total_steps()])
            info_table.append(['Episodes', len(env.get_episode_rewards())])
            print(tabulate(info_table, tablefmt='fancy_grid'))