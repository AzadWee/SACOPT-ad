GOOD_VEHICLE_NUMBER = 5
BED_VEHICLE_NUMBER = 0
RSU_NUMBER = 1
CAPACITY = [10, 30, 40, 60, 100]
TRANSITION_MATRIX_1 = [[0.1, 0.5, 0.2, 0.1, 0.1],
                        [0.2, 0.1, 0.3, 0.2, 0.2],
                        [0.2, 0.1, 0.1, 0.4, 0.2],
                        [0.3, 0.2, 0.1, 0.1, 0.3],
                        [0.2, 0.3, 0.2, 0.2, 0.1]]
TRANS_RATE = [20, 30, 40, 50, 60]
TRANSITION_MATRIX_2 = [[0.1, 0.4, 0.2, 0.2, 0.1],
                        [0.5, 0.1, 0.2, 0.1, 0.1],
                        [0.2, 0.1, 0.3, 0.2, 0.2],
                        [0.1, 0.1, 0.1, 0.5, 0.2],
                        [0.3, 0.2, 0.1, 0.2, 0.2]]

MAX_TRANSACTION_SIZE = 20
MIN_TRANSACTION_SIZE = 10
MAX_BLOCK_SIZE = 100
MIN_BLOCK_SIZE = 50
MAX_BLOCK_INTERVAL = 10
MIN_BLOCK_INTERVAL = 30

THROUGHPUT_COEF = 1   # 事务吞吐量系数
LATENCY_COEF = 2  # 时延系数

ACTION_SPACE = 3
MAX_STEP = 20

SEED = 0
