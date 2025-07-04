import numpy as np
from .config import *
from .block import Block


class Transaction:
    def __init__(self, vid:int, input:list, is_fake=0, size=1):
        self.vid = vid
        self.is_fake = is_fake
        self.size = size
        self.input = input


class Vehicle:
    def __init__(self, vid, rid):
        self.vid = vid
        if rid >= RSU_NUMBER:
            self.rid = RSU_NUMBER - 1
        else:
            self.rid = rid  # 车辆所属rsu
        self.is_fov = False    # 是否是头车
        self.capacity = 10  # 计算能力
        self.transrate = 20  # 到rsu传输速率

        # 能耗相关
        self.genEnergyConsumption = 0
        self.upEnergyConsumption = 0
        self.sendEnergyConsumption = 0

        # 安全相关
        self.reputation = 0  # 信誉
        self.MH = 0  # 累计恶意历史得分
        

        self.block_chain = []
        
        # 安全相关
        self.is_bad = False
        
        # 共识相关
        self.messages = {}
        self.view_id = 0
    
    @property
    def norm_capacity(self):
        return self.capacity / CAPACITY[-1]
    
    @property
    def norm_transrate(self):
        return self.transrate / TRANS_RATE[-1]
    
    @property
    def vector(self):
        return np.hstack([self.norm_capacity, self.norm_transrate])
    
    
    def set_energy(self, energy):
        self.energy = energy
    
    def set_fov(self, is_fov):
        self.is_fov = is_fov
    
    def set_bad(self, is_bad):
        self.is_bad = is_bad

    def change_capacity(self, capacity):
        self.capacity = capacity

    def change_transrate(self, transrate):
        self.transrate = transrate
    
    def eneragy_consumption(self, size, factor, purpose):
        # 计算能耗
        if purpose == 'gen':
            self.genEnergyConsumption += size * factor
        elif purpose == 'up':
            self.upEnergyConsumption += size * factor
        elif purpose == 'send':
            self.sendEnergyConsumption += size * factor
        else:
            raise ValueError("Invalid purpose for energy consumption calculation")
        return size * factor
    
    def generate_transaction(self,t_size, t_lamma, min_size, max_size, isCrossShard=False, input=None):
        
        # 正态分布随机生成事务大小
        random_number = np.random.normal(t_size, t_lamma)
        size = int(np.clip(random_number, min_size, max_size))
        is_fake = False
        if self.is_bad:
            # 一半概率生成虚假事务
            is_fake = np.random.rand() < 0.5
        if isCrossShard:
            trans = Transaction(vid=self.vid, input=input, is_fake=is_fake, size=size)
        else:
            trans = Transaction(vid=self.vid, input=[self.rid], is_fake=is_fake, size=size)

        return trans
    
    def generate_block(self, block: Block):
        lantacy = block.size / self.capacity
        # 计算能耗
        self.eneragy_consumption(block.size, 0.3, 'gen')
        return lantacy

    def upload_block(self, block: Block, cblock: Block):
        lantacy = (block.size + cblock.size) / self.transrate
        # 计算能耗
        self.eneragy_consumption(block.size + cblock.size, 0.1, 'up')
        return lantacy
    
    # 共识相关
    def send_message(self, message, nodes):
        """向其他节点广播消息"""
        for node in nodes:
            node.receive_message(message)
            self.eneragy_consumption(10, 1, 'send')
        
    def receive_message(self, message):
        if message['view_id'] > self.view_id:
            self.view_id = message['view_id']
        if message['view_id'] not in self.messages:
            self.messages[message['view_id']] = [message]
        else:
            self.messages[message['view_id']].append(message)
    
    def pre_prepare(self, nodes):
        self.view_id += 1
        message = {'type': 'pre_prepare', 'view_id': self.view_id}
        self.send_message(message, nodes)
        
    def prepare(self, nodes, view_id):
        for mess in self.messages[view_id]:
            if mess['type'] == 'pre_prepare':
                message = {'type': 'prepare', 'view_id': view_id}
                self.send_message(message, nodes)
                break
                
    def commit(self, nodes, view_id):
        for mess in self.messages[view_id]:
            if mess['type'] == 'prepare':
                message = {'type': 'commit', 'view_id': view_id}
                self.send_message(message, nodes)
                break
    
    def check_consensus(self, view_id, fault):
        # 检查是否达成共识
        prepare_count = 0
        commit_count = 0
        for mess in self.messages[view_id]:
            if mess['type'] == 'prepare':
                prepare_count += 1
            if mess['type'] == 'commit':
                commit_count += 1
        if prepare_count > 2 * fault and commit_count > 2 * fault:
            return True
        else:
            return False
    
    # 对区块中交易进行投票
    def check_transaction(self, block: Block):
        votes = []
        # 恶意车辆会有0.8概率相反投票,正常车辆有0.1到概率相反投票
        if self.is_bad:
            pro = 0.6
        else:
            pro = 0.1
        for t in block.transactions:
            rand = np.random.rand()
            if rand < pro:
                votes.append(1 if t.is_fake else -1)
            else:
                votes.append(1 if not t.is_fake else -1)

        return votes

    def reset(self):
        self.is_fov = False
        self.block_chain.clear()
        self.capacity = np.random.choice(CAPACITY)  # 计算能力
        self.transrate = np.random.choice(TRANS_RATE)  # 到rsu传输速率

        self.reputation = 0 # 声誉

        # 能耗
        self.genEnergyConsumption = 0
        self.upEnergyConsumption = 0
        self.sendEnergyConsumption = 0
        
        self.messages.clear()
        self.view_id = 0
