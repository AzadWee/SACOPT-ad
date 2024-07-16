import os
import argparse
import pprint
from datetime import datetime

import numpy as np
import torch
from torch.utils.tensorboard import SummaryWriter

from tianshou.data import Collector, VectorReplayBuffer
from tianshou.utils import TensorboardLogger
from tianshou.trainer import offpolicy_trainer


from env import OPTEnv, make_env
from policy import DiffusionSAC
from diffusion import Diffusion
from diffusion.model import MLP, DoubleCritic

from args import *

# manager = Manager()
# for v in manager.good_vehicles:
#     print(v.capacity)
# print("--------------------------")
# for i in range(10):
#     manager.capacity_change()
#     for v in manager.good_vehicles:
#         print(v.capacity)
#     print("--------------------------")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', type=str, default='cpu')

    args = parser.parse_known_args()[0]
    return args


def main(args=get_args()):
    env, train_envs, test_envs = make_env(TRAINING_NUM, TEST_NUM)
    state_shape = env.observation_space.shape[0]
    action_shape = env.action_space.n
    print(f'Shape of Observation Space: {state_shape}')
    print(f'Shape of Action Space: {action_shape}')

    # 设置seed
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    train_envs.seed(SEED)
    test_envs.seed(SEED)

    # 创建actor
    actor_net = MLP(
        state_dim=state_shape,
        action_dim=action_shape,
    )

    actor = Diffusion(
        state_dim=state_shape,
        action_dim=action_shape,
        model=actor_net,
        max_action=MAX_ACTION,
        min_action=MIN_ACTION,
        n_timesteps=TIME_STEPS
    ).to(args.device)
    actor_optim = torch.optim.Adam(
        actor.parameters(),
        lr=ACTOR_LR,
        weight_decay=WEIGHT_DECAY
    )

    # 创建critic
    critic = DoubleCritic(
        state_dim=state_shape,
        action_dim=action_shape
    ).to(args.device)
    critic_optim = torch.optim.Adam(
        critic.parameters(),
        lr=CRITIC_LR,
        weight_decay=WEIGHT_DECAY
    )

    # 创建log
    time_now = datetime.now().strftime('%b%d-%H%M%S')
    log_path = os.path.join(
       "./log", time_now)
    writer = SummaryWriter(log_path)
    writer.add_text("args", str(args))
    # visualize model graphs
    # dummy_input = torch.randn(1, args.state_shape, device=args.device)
    # writer.add_graph(actor, dummy_input)
    # writer.add_graph(critic, dummy_input)
    logger = TensorboardLogger(writer)

    policy = DiffusionSAC(
        actor,
        actor_optim,
        action_shape,
        critic,
        critic_optim,
        torch.distributions.Categorical,
        tau=TAU,
        alpha=ALPHA,
        gamma=GAMMA,
        estimation_step=N_STEP,
        pg_coef=PG_COEF,
        action_space=env.action_space,
        device=args.device
    )

    # buffer
    buffer = VectorReplayBuffer(
        BUFFER_SIZE,
        buffer_num=len(train_envs)
    )

    # collector
    train_collector = Collector(policy, train_envs, buffer)
    test_collector = Collector(policy, test_envs)

    # trainer
    result = offpolicy_trainer(
        policy,
        train_collector,
        test_collector,
        EPOCH,
        STEP_PER_EPOCH,
        STEP_PER_COLLECT,
        TEST_NUM,
        BATCH_SIZE,
        logger=logger,
        test_in_train=False
    )
    pprint.pprint(result)

    if __name__ == '__main__':
        np.random.seed(SEED)
        env, _, _ = make_env()
        policy.eval()
        collector = Collector(policy, env)
        result = collector.collect(n_episode=10, render=0.1)
        rews, lens = result["rews"], result["lens"]
        print(f'Mean Reward: {rews.mean}, Mean Length: {lens.mean}')


if __name__ == '__main__':
    main(get_args())
