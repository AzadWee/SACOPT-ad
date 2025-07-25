import numpy as np

from .block import Block
from .vehicle import Vehicle
from .config import *


class RSU:
    def __init__(self, rid):
        self.rid = rid
        self._block_interval = 1
        self._block_size = 100
        self._block_count = 0
        self.local_chain = []
        self._data_size = 0
        self.vehicles = []
        self.fov = None

        self.transactions = []
        self.crossShardTransactions = []
        
        self.transaction_mean_size = MIN_TRANSACTION_SIZE  # rsu计算得到的事务平均大小，用于构建状态向量
        
        # 常量定义
        self._mean_transaction_size = MEAN_TRANSACTION_SIZE
        self._transaction_lamma = TRANSACTION_LAMMA
        self._min_transaction_size = MIN_TRANSACTION_SIZE
        self._max_transaction_size = MAX_TRANSACTION_SIZE
        self._mean_transaction_num = MEAN_TRANSACTION_NUM
        

    @property
    def block_interval(self):
        return self._block_interval

    @property
    def block_size(self):
        return self._block_size

    @property
    def norm_transaction_size(self):
        return self.transaction_mean_size / self._max_transaction_size
    
    @property
    def vector(self):
        return np.hstack([self.norm_transaction_size, len(self.vehicles)])
    
    @property
    def data_size(self):
        return self._data_size
    
    def set_block_size(self, block_size):
        self._block_size = block_size

    def set_block_interval(self, block_interval):
        self._block_interval = block_interval

    def add_vehicle(self, vehicle: Vehicle):
        if not self.fov:
            self.fov = vehicle
        self.vehicles.append(vehicle)

    def rsu_set_fov(self, fov_id:int):
        if self.fov:
            self.fov.set_fov(False)
        self.fov = self.vehicles[fov_id]
        self.fov.set_fov(True)
    
    # 统计区块链总大小
    def total_block_size(self):
        return sum(block.size for block in self.local_chain)
    
    def rsu_generate_transaction(self, is_generate_vehicle):
        if not self.fov:
            raise ValueError("FOV not set")
        for vehicle in self.vehicles:
            if is_generate_vehicle[vehicle.vid]:
                transaction_num = np.random.randint(1, 10)
                for _ in range(transaction_num):
                    # 0.1概率生成跨分片事务
                    if np.random.rand() < 0.1:
                        randomRid = np.random.randint(0, RSU_NUMBER)
                        # while randomRid == self.rid: 一个RSU时会出现死循环
                        randomRid = np.random.randint(0, RSU_NUMBER)
                        input = [vehicle.rid, randomRid]
                        t = vehicle.generate_transaction(self._mean_transaction_size, self._transaction_lamma,
                                                            self._min_transaction_size, self._max_transaction_size, True, input)
                        # gen_latency += t.size / self.fov.capacity
                        self.crossShardTransactions.append(t)
                    # 0.9概率生成本分片事务
                    else:
                        t = vehicle.generate_transaction(self._mean_transaction_size, self._transaction_lamma,
                                                            self._min_transaction_size, self._max_transaction_size)
                        # gen_latency += t.size / self.fov.capacity
                        self.transactions.append(t)
                        # if gen_latency > self._block_interval:
                        #     break
        # self.reputation_control(trans)
        # self.transactions.append(trans)
    
    def generate_block(self):
        size = 5
        gen_latency = 0
        new_block = Block()
       
        # 头车打包事物形成区块
        while size < self._block_size:
            if not self.transactions:
                break
            t = self.transactions.pop(0)
            size += t.size
            new_block.add_transaction(t)
        new_block.set_size(size)
        gen_latency = self.fov.generate_block(new_block)
        # 返回生成和发送区块时延
        return new_block, gen_latency
    
    def generateCrossShardBlock(self):
        size = 0
        gen_latency = 0
        new_block = Block()
       
        # 头车打包事物形成区块
        while size < self._block_size:
            if not self.crossShardTransactions:
                break
            t = self.crossShardTransactions.pop(0)
            size += t.size
            new_block.add_transaction(t)
        new_block.set_size(size)
        gen_latency = size / self.fov.capacity
        # 返回生成和发送区块时延
        return new_block, gen_latency
    

    # fov向RSU发送区块,返回值为共识时延
    def consensus_block(self, block: Block, cblock: Block):
        # 返回最长发送时延
        latency = 0
        for vehicle in self.vehicles:
            if vehicle == self.fov:
                continue
            latency = max(latency, vehicle.upload_block(block, cblock))
        return latency
    
    def pbft(self, block: Block, cblock: Block):
        self.fov.pre_prepare(self.vehicles)
        
        for vehicle in self.vehicles:

            if vehicle != self.fov:
                vehicle.prepare(self.vehicles, self.fov.view_id)
        
        for vehicle in self.vehicles:
            vehicle.commit(self.vehicles, self.fov.view_id)
        latency = 0
        for vehicle in self.vehicles:
            if vehicle.check_consensus(self.fov.view_id, (len(self.vehicles)-1) // 3):
                latency = self.consensus_block(block, cblock)
                self.local_chain.append(block)
                self._block_count += 1
                if cblock.size > 0:
                    self.local_chain.append(cblock)
                    self._block_count += 1
                break
        return latency
    
    def check_votes(self, block):
        votes = []
        for vehicle in self.vehicles:
            vote = vehicle.check_transaction(block)
            # votes长度与block中事务数相同，否则抛出异常
            if len(vote) != len(block.transactions):
                raise ValueError("Votes length does not match block transactions length")
            votes.append(vote)
        # 有最多相似的投票为结果投票
        result = max(votes, key=votes.count)

        # 将每辆车的投票与result的余弦相似度作为该车的信誉分数
        for i, vote in enumerate(votes):
            # 计算余弦相似度
            cos_sim = np.dot(vote, result) / (np.linalg.norm(vote) * np.linalg.norm(result))
            # 计算信誉分数
            vehicle = self.vehicles[i]
            #vehicle.reputation += cos_sim
            # 对车辆MH进行衰减
            vehicle.MH = vehicle.MH * cigema_M
            # 当r（t）< r_crit,对车辆MH进行累加
            if cos_sim < r_crit:
                vehicle.MH = vehicle.MH + c_M * np.abs(cos_sim) 

            if cos_sim >= 0:
                # todo 根据车辆历史作恶行为，对alpha进行衰减，但还没启用
                alpha = 0.05 / (1 + k_H * vehicle.MH)
                vehicle.reputation = vehicle.reputation + alpha * cos_sim  * (100 - vehicle.reputation)
            else:
                vehicle.reputation = vehicle.reputation + 0.5 * cos_sim * (vehicle.reputation + 100)

        
                
        


    def calculate_reward(self, block, gen_latency, send_latency, plently):
        # throughput = len(block.transactions) / (gen_latency + send_latency)
        throughput = len(block.transactions) / self._block_interval
        # print("{},{},{},{}".format(throughput, plently, gen_latency, send_latency))
        reward = throughput * THROUGHPUT_COEF - (gen_latency + send_latency) * LATENCY_COEF - plently
        # print("reward:", reward, "throughput:", throughput, "latency:", gen_latency+send_latency)

        return reward

    def operate(self, fov_id:int, block_size:int, block_interval:int, is_generate_vehicle):
        assert fov_id < len(self.vehicles), \
            "FOV id should be less than the number of vehicles"
        
        self.rsu_set_fov(fov_id)
        self.set_block_size(block_size)
        self.set_block_interval(block_interval)

        # 车辆产生交易进入交易池
        self.rsu_generate_transaction(is_generate_vehicle)

        # 头车生成新的区块
        # gen_latency为生成区块时延，send_latency为区块内共识时延
        if self.transactions or self.crossShardTransactions:
            block, gen_latency = self.generate_block()
            # 头车生成新的跨分片区块
            cblock, cgen_latency = self.generateCrossShardBlock()
            

            # fov将区块上传到RSU开始共识过程，delivery_latency为上传时延
            delivery_latency = self.fov.upload_block(block, cblock)

            # 区块共识
            consensus_latency = self.pbft(block, cblock)
            assert consensus_latency >= 0, "Consensus Failed"

            # 计算每个车辆信誉
            self.check_votes(block)
        else:
            block = None
            cblock = None
            gen_latency = 0
            cgen_latency = 0
            delivery_latency = 0
            consensus_latency = 0
        
        if block and block.transactions:
            self.transaction_mean_size = block.size / len(block.transactions)
            self._data_size += block.size
         # 当区块未容纳所有事务时，奖励为0
        plently = 0
        if self.transactions:
            plently = len(self.transactions)
            self.transactions.clear()
        # reward = self.calculate_reward(block, gen_latency, delivery_latency, plently)
        delay = gen_latency + cgen_latency + delivery_latency + consensus_latency
        # return block, delay, plently
        return block, cblock, delay, plently

    def reset(self):
        self._block_count = 0
        self._data_size = 0
        self.local_chain.clear()
        self.fov = self.rsu_set_fov(np.random.choice(range(len(self.vehicles))))
        self.transaction_mean_size = self._min_transaction_size

