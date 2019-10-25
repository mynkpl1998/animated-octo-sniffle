import os
import sys
import gym
import numpy as np

class V2I(gym.Env):

    def __init__(self, config):

        # Parse config file and return the handle
        