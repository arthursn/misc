import datetime

import matplotlib.pyplot as plt
import numpy as np
from f1_wdc_standings import scrape_wiki_f1_standings


def main():
    now = datetime.datetime.now()

    for year in range(1991, now.year + 1):
        print(year)

        dr_std = scrape_wiki_f1_standings(year)

        if len(dr_std.races) > 0:
            fig, ax = plt.subplots(figsize=(12, 8))
            rounds = np.arange(len(dr_std.races))
            pts_leader = None

            for driver, std in dr_std.drivers.items():
                cum_pts = np.cumsum(std.points)
                sel = slice(0, dr_std.next_round)
                ax.plot(rounds[sel], cum_pts[sel], label=driver, lw=1)
                next_round = rounds[sel][-1]
                curr_pts = cum_pts[sel][-1]
                if pts_leader is None:
                    pts_leader = curr_pts

                driver_abbr = driver.split(" ")[1][:3]
                ax.text(
                    next_round,
                    curr_pts,
                    f"{driver_abbr} {cum_pts[sel][-1]:g} pts",
                    ha="center",
                    va="bottom",
                    size=10 * (curr_pts / pts_leader) ** 0.1,
                )

            ax.set_xticks(rounds, dr_std.races)
            ax.set_xlabel("Round")
            ax.set_ylabel("Points")
            ax.set_title(
                "{} FIA Formula One World Drivers's Championship standings".format(year)
            )
            ax.legend(loc="upper left", ncol=2)

            fig.tight_layout()
            fig.savefig("f1_{}.png".format(year))
            plt.close(fig)
        else:
            print("No data found")


if __name__ == "__main__":
    main()
