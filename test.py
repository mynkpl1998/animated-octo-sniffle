import time
import random
from v2i import V2I

configFilePath = "/home/mayank/Documents/animated-octo-sniffle/experiments/localviewonly30m/sim-config.yml"
env = V2I.V2I(configFilePath)
for i in range(0, 10):
    env.reset(0.6)
    acts = ['acc', 'dec']
    for j in range(0, 100):
        done = env.step(random.choice(acts))

        if done:
            break
    print("------------")