#!/usr/bin/env python3

import argparse
import gym
import gym_minigrid
import time
import numpy as np

import torch_ac
import utils

# Parse arguments

parser = argparse.ArgumentParser(description='PyTorch RL example')
parser.add_argument('--env', required=True,
                    help='name of the environment to be run')
parser.add_argument('--model', required=True,
                    help='name of the trained model')
parser.add_argument('--episodes', type=int, default=50,
                    help='number of episodes of evaluation (default: 50)')
parser.add_argument('--seed', type=int, default=1,
                    help='random seed (default: 1)')
args = parser.parse_args()

# Set numpy and pytorch seeds

torch_ac.seed(args.seed)

# Generate environment

env = gym.make(args.env)
env.seed(args.seed)

# Define actor-critic model

obs_space = utils.preprocess_obs_space(env.observation_space)
model_path = utils.get_model_path(args.model)
acmodel = utils.load_model(obs_space, env.action_space, model_path)

# Initialize logs

log = {"num_frames": [], "return": []}

# Run the agent

start_time = time.time()

for _ in range(args.episodes):
    obs = env.reset()
    done = False

    num_frames = 0
    returnn = 0

    while not(done):
        obs = utils.preprocess_obss([obs], volatile=True)
        action = acmodel.get_action(obs, deterministic=True).data[0,0]
        obs, reward, done, _ = env.step(action)
        
        num_frames += 1
        returnn += reward
    
    log["num_frames"].append(num_frames)
    log["return"].append(returnn)

end_time = time.time()

# Print logs

fps = np.sum(log["num_frames"])/(end_time - start_time)

print("FPS {:.0f} | R:x̄σmM {:.1f} {:.1f} {:.1f} {:.1f} | F:x̄σmM {:.1f} {:.1f} {:.1f} {:.1f}".
    format(fps,
           *utils.synthesize(log["return"]),
           *utils.synthesize(log["num_frames"])))