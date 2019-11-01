import time
import random
from v2i import V2I

configFilePath = "/home/mayank/Documents/animated-octo-sniffle/experiments/localviewonly30m/sim-config.yml"
env = V2I.V2I(configFilePath)
for i in range(0, 10):
    env.reset(0.8)
    acts = ['acc', 'dec', 'do-nothing']
    for j in range(0, 1000):
        act = 'acc'
        if j >= 10:
            act = 'do-nothing'
        done = env.step(act)
        if done:
            print("Done")
            break
    print("------------")