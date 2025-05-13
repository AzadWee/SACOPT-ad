VEHICLE_NUMBER = 15  # 15
RSU_NUMBER = 3  # 3
CAPACITY = [60, 80, 100, 120, 140]
TRANSITION_MATRIX_1 = [[0.1, 0.2, 0.5, 0.1, 0.1],
                        [0.2, 0.1, 0.3, 0.2, 0.2],
                        [0.4, 0.1, 0.1, 0.2, 0.2],
                        [0.3, 0.2, 0.1, 0.1, 0.3],
                        [0.2, 0.3, 0.2, 0.2, 0.1]]
TRANS_RATE = [10, 20, 30, 45, 60]
TRANSITION_MATRIX_2 = [[0.1, 0.3, 0.3, 0.2, 0.1],
                        [0.5, 0.1, 0.2, 0.1, 0.1],
                        [0.2, 0.1, 0.3, 0.2, 0.2],
                        [0.2, 0.2, 0.1, 0.3, 0.2],
                        [0.1, 0.2, 0.1, 0.2, 0.4]]

RSU_TRANS_RATE = 100


# environment
MEAN_TRANSACTION_NUM = 3 # 每个step产生的事务数，正态均值，默认10

MEAN_TRANSACTION_SIZE = 12
TRANSACTION_LAMMA = 0.7
MAX_TRANSACTION_SIZE = 20
MIN_TRANSACTION_SIZE = 10
MAX_BLOCK_SIZE = 250
MIN_BLOCK_SIZE = 200
BLOCK_SIZE_RANGE = MAX_BLOCK_SIZE - MIN_BLOCK_SIZE + 1
MAX_BLOCK_INTERVAL = 7
MIN_BLOCK_INTERVAL = 2
BLOCK_INTERVAL_RANGE = MAX_BLOCK_INTERVAL - MIN_BLOCK_INTERVAL + 1

INTERVAL_FACTOR = 1.5  # 区块间隔系数, 调节区块间隔和时延关系,7
THROUGHPUT_COEF = 0.8  # 事务吞吐量系数 1
LATENCY_COEF = 0.2  # 时延系数 0.5
PLENTLY_COEF = 1

ACTION_SPACE = VEHICLE_NUMBER//RSU_NUMBER * (MAX_BLOCK_SIZE - MIN_BLOCK_SIZE + 1) * (MAX_BLOCK_INTERVAL - MIN_BLOCK_INTERVAL + 1)
MAX_STEP = 100  # 1000

SEED = 0
