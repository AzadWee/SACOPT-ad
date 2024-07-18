import matplotlib.pyplot as plt
import pandas as pd


# 读取CSV文件
df1 = pd.read_csv('log_diffusion-Jul16-125908.csv')
df2 = pd.read_csv('log_sac-Jul16-205017.csv')
df3 = pd.read_csv('log_dqnJul18-115235.csv')




df1.set_index('Step', inplace=True)

# 绘制折线图
#plt.figure(figsize=(10, 6))
plt.plot(df1.index, df1['Value'], linestyle='-', label='diffusion')
plt.plot(df2['Step'], df2['Value'], linestyle='-', label='sac')
plt.plot(df3['Step'], df3['Value'], linestyle='-', label='dqn')
plt.legend()
plt.title('result')
plt.xlabel('step')
plt.ylabel('reward')
plt.grid(True)
plt.show()