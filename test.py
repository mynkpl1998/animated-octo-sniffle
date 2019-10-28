import time

from v2i import V2I

configFilePath = "/home/mayank/Documents/animated-octo-sniffle/experiments/localviewonly30m/sim-config.yml"
env = V2I.V2I(configFilePath)
for i in range(0, 1):
    env.reset(0.3)
    for j in range(0, 1):
        env.step()
    #time.sleep(100)
    print("------------")