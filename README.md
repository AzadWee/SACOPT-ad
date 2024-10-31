# 使用DiffusionSAC算法进行优化
diffusionSAC算法的改进，主要改进车联网区块链环境，优化了训练效果

环境中有10个车辆，1个RSU

环境：在车辆编队中应用区块链进行信息管理 IoVB

状态空间：[(车辆处理能力，车辆RSU通信速率)，事务大小，车辆数]

行为空间：[头车，区块大小，区块间隔]

```
env 环境文件

diffusion 实现扩散模型

policy 调用diffusion包实现diffusionSAC策略
```