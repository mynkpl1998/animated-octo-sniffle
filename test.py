import time
import random
from v2i import V2I

configFilePath = "/home/mayank/Documents/animated-octo-sniffle/experiments/localviewonly30m/sim-config.yml"
env = V2I.V2I(configFilePath)
for i in range(0, 10):
    env.reset(.1)
    acts = ['acc', 'dec', 'do-nothing']
    for j in range(0, 1000):
        act = acts[0]
        if j >= 50:
            act = acts[1]
        done = env.step(act)
        if done:
            print("Done")
            break
    print("------------")