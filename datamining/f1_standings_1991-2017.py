import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from f1_wdc_standings import *

for year in range(1991,2018):
    print(year)

    drstd = scrape_wiki_f1_standings(year)

    if len(drstd.rounds) > 0:
        fig, ax = plt.subplots(figsize=(15,10))
        races = np.arange(len(drstd.rounds))
        for i, (pts, driver) in enumerate(zip(map(np.cumsum, drstd.points), drstd.drivers)):
            ax.plot(races, pts, label=driver)
            # if i >= (25-1):
            #     break
        
        plt.xticks(races, drstd.rounds)
        ax.set_xlim(races[0], races[-1])
        ax.set_xlabel('Round')
        ax.set_ylabel('Points')
        ax.set_title('{} FIA Formula One World Drivers\'s Championship standings'.format(year))
        ax.legend(loc='upper left', ncol=2)

        if not os.path.exists('f1standings'):
            os.makedirs('f1standings')

        plt.savefig(os.path.join('f1standings', 'f1{}.pdf'.format(year)))
    else:
        print('No data found')
