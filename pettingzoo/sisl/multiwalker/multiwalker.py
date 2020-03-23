from .multiwalker_base import MultiWalkerEnv as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = list(range(self.num_agents))
        self.agent_selection = 0
        self.agent_order = self.agents[:]
        self._agent_selector_object = agent_selector(self.agent_order)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.04

        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))
        self.observations = self.env.get_last_obs()

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        observation = self.env.reset()
        self.steps = 0
        self._agent_selector_object.reinit(self.agent_order)
        self.agent_selection = self._agent_selector_object.next()
        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))
        if observe:
            return self.env.observe(0)

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render()

    def observe(self, agent):
        return self.env.observe(agent)

    def step(self, action, observe=True):
        agent = self.agent_selection
        action = np.array(action, dtype=np.float32)
        if any(np.isnan(action)):
            action = [0 for _ in action]
        elif not self.action_spaces[agent].contains(action):
            raise Exception('Action for agent {} must be in {}. It is currently {}'.format(
                agent, self.action_spaces[agent], action))

        self.env.step(action, agent, self._agent_selector_object.is_last())
        self.rewards = self.env.get_last_rewards()
        self.dones = self.env.get_last_dones()
        self.agent_selection = self._agent_selector_object.next()

        if self.env.frames >= self.env.max_frames:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))

        self.steps += 1
        if observe:
            return self.observe(self.agent_selection)
