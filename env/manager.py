import numpy as np

from .config import *
from .vehicle import Vehicle
from .RSU import RSU


class Manager:
    def __init__(self):
        self._n_vehicle = GOOD_VEHICLE_NUMBER + BED_VEHICLE_NUMBER
        self._n_rsu = RSU_NUMBER
        self._good_vehicles = [Vehicle(vid, 0, 0) for vid in range(GOOD_VEHICLE_NUMBER)]
        self._bad_vehicles = [Vehicle(vid, 1, 0) for vid in range(GOOD_VEHICLE_NUMBER, self._n_vehicle)]
        self._rsu = [RSU(rid) for rid in range(RSU_NUMBER)]
        for r in self._rsu:
            for v in self._good_vehicles:
                if v.rid == r.rid:
                    r.add_vehicle(v)
            for v in self._bad_vehicles:
                if v.rid == r.rid:
                    r.add_vehicle(v)

        self.best_reward = 0
        self.global_step = 0

    @property
    def good_vehicles(self):
        return self._good_vehicles

    @property
    def bad_vehicles(self):
        return self._bad_vehicles

    @property
    def rsu(self):
        return self._rsu

    # def step(self, action):
    #     fov = action[0]
    #     for r in self._rsu:
    #         r.rsu_set_fov(r.vehicles[fov])
    #     block_size = action[1]
    #     for r in self._rsu:
    #         r.set_block_size(block_size)
    #     block_interval = action[2]
    #     for r in self._rsu:
    #         r.set_block_interval(block_interval)
    #
    #     for r in self._rsu:
    #         lantacy = r.rsu_generate_transaction()
    #         if lantacy:
    #             r.generate_block()

    @property
    def space_vector(self):
        '''状态空间为车辆处理能力+传输时延+平均事务大小'''
        vec = [v.vector for v in self._good_vehicles]
        vec += [r.vector for r in self._rsu]
        return np.hstack(vec)
    
    def capacity_change(self):
        indices = {capacity: i for i, capacity in enumerate(CAPACITY)}

        for v in self._good_vehicles:
            current_capacity = v.capacity
            current_index = indices[current_capacity]
            new_capacity = np.random.choice(CAPACITY, p=TRANSITION_MATRIX_1[current_index])
            v.change_capacity(new_capacity)
        for v in self._bad_vehicles:
            current_capacity = v.capacity
            current_index = indices[current_capacity]
            new_capacity = np.random.choice(CAPACITY, p=TRANSITION_MATRIX_1[current_index])
            v.change_capacity(new_capacity)

    def transrate_change(self):
        indices = {rate: i for i, rate in enumerate(TRANS_RATE)}
        for v in self._good_vehicles:
            current_rate = v.transrate
            current_index = indices[current_rate]
            new_rate = np.random.choice(TRANS_RATE, p=TRANSITION_MATRIX_2[current_index])
            v.change_transrate(new_rate)
        for v in self._bad_vehicles:
            current_rate = v.transrate
            current_index = indices[current_rate]
            new_rate = np.random.choice(TRANS_RATE, p=TRANSITION_MATRIX_2[current_index])
            v.change_transrate(new_rate)

    def set(self, action, global_step):
        '''action包括头车选择，区块大小，区块间隔'''
        # action一维为fov，二维为区块大小，三维为区块间隔
        fov_id = action // (BLOCK_SIZE_RANGE * BLOCK_INTERVAL_RANGE)
        block_size = (action // BLOCK_INTERVAL_RANGE) % BLOCK_SIZE_RANGE + MIN_BLOCK_SIZE
        block_interval = action % BLOCK_INTERVAL_RANGE + MIN_BLOCK_INTERVAL

        # print("action:{},{},{}".format(fov_id, block_size, block_interval))

        assert fov_id < self._n_vehicle, \
            "FOV id should be less than the number of vehicles"
        assert MIN_BLOCK_SIZE <= block_size <= MAX_BLOCK_SIZE, \
            "Block size should be in the range of [{}, {}]".format(MIN_BLOCK_SIZE, MAX_BLOCK_SIZE)
        assert MIN_BLOCK_INTERVAL <= block_interval <= MAX_BLOCK_INTERVAL, \
            "Block interval should be in the range of [{}, {}]".format(MIN_BLOCK_INTERVAL, MAX_BLOCK_INTERVAL)

        

        fov = None
        # 找到fovID对应的vehicle
        for v in self._good_vehicles:
            if v.vid == fov_id:
                fov = v
                break
        # if not fov:
        #     for v in self._bad_vehicles:
        #         if v.vid == fov_id:
        #             fov = v
        #             break
        # reward = 0
        # for r in self._rsu:
        #     reward += r.operate(fov)
        reward = self._rsu[0].operate(fov, block_size, block_interval)

        self.global_step += 1

        if self.global_step % 2 == 0:
            self.transrate_change()
            self.capacity_change()
        
        # c=[]
        # for v in self.good_vehicles:
        #     c += [v.capacity]
        # print(c)

        return reward

    def reset(self):
        for v in self._good_vehicles:
            v.reset()
        for v in self._bad_vehicles:
            v.reset()
        for r in self._rsu:
            r.reset()
        self.global_step = 0
        return self.space_vector

