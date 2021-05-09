import datetime
import numpy as np
import matplotlib.pyplot as plt
from f1_wdc_standings import scrape_wiki_f1_standings

if __name__ == '__main__':
    now = datetime.datetime.now()

    for year in range(1991, now.year + 1):
        print(year)

        drstd = scrape_wiki_f1_standings(year)

        if len(drstd.rounds) > 0:
            fig, ax = plt.subplots(figsize=(15, 10))
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

            fig.savefig('f1_{}.png'.format(year), dpi=150)
            plt.close()
        else:
            print('No data found')
