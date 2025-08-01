import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('2011_Canadian_GP_lap_times.csv', sep='\t', index_col=0)
cumtimes = df.cumsum(axis=1)
order = np.argsort(cumtimes.iloc[:,-1].values)

fig, ax = plt.subplots()
for idx, row in cumtimes.iloc[order].iterrows():
    ax.plot(cumtimes.loc['Jenson Button'] - row, label=idx)
ax.legend(loc='center left')
ax.set_title('2011 Canadian GP: Delta to Button')
ax.set_xlabel('Lap')
ax.set_ylabel('Delta to Button (s)')

plt.show()
