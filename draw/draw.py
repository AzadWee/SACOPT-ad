# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd

fig, ax = plt.subplots()
# 读取CSV文件
df1 = pd.read_csv('log_diffusion-Jul16-125908.csv')
df2 = pd.read_csv('log_diffusion-Jul19-122852.csv')
df3 = pd.read_csv('log_diffusion-Jul19-134023.csv')

mean1 = df1['Value'].mean()
mean2 = df2['Value'].mean()
mean3 = df3['Value'].mean()
y1 = [mean1, mean2, mean3]
y1 = [round(i, 2) for i in y1]

best1 = df1['Value'].max()
best2 = df2['Value'].max()
best3 = df3['Value'].max()
y2 = [best1, best2, best3]
y2 = [round(i, 2) for i in y2]

x1 = "10,15,60-100,1 "
x2 = "10,15,20-100,2"
x3 = "10,15,40-100,1"
x = [x1, x2, x3]

# df1.set_index('Step', inplace=True)
#
# # 绘制折线图
# #plt.figure(figsize=(10, 6))
# plt.plot(df1.index, df1['Value'], linestyle='-', label='SEED=0')
# plt.plot(df2['Step'], df2['Value'], linestyle='-', label='SEED=222')
# plt.plot(df3['Step'], df3['Value'], linestyle='-', label='SEED=111')
# plt.legend()
# plt.title('result')
# plt.xlabel('step')
# plt.ylabel('reward')

# 绘制柱状图
ax.bar(x, y1, color='steelblue', width=0.5, label='mean reward')
# for a, b in zip(x, y1):
#     plt.text(a, b, b, ha='center', va='top', fontsize=10)
ax.plot(x, y2, 'r-', marker='o', label='best reward')
for a, b in zip(x, y2):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=10)
plt.xlabel('state [Vehicle_number,Transaction_size,Vehicular_capacity,Variance]')
plt.ylabel('throughput')
plt.ylim(0, 200)
plt.legend(loc='upper left')

ax2 = plt.twinx()
epoch = [300, 770, 440]
ax2.plot(x, epoch, 'y', marker='s', label='convergence epoch')
for a, b in zip(x, epoch):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=10)
plt.legend(loc='upper right')
plt.ylabel('epoch')
plt.ylim(200, 1000)

# plt.grid(True)
plt.show()

fig.savefig('bar.eps', format='eps', dpi=600)
