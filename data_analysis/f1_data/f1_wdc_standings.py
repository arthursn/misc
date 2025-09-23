import argparse
import datetime
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import List

import bs4
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4.element import Tag


def is_int(s):
    try:
        int(s)
    except Exception:
        return False
    return True


def parse_html_tables(table: Tag) -> List[str]:
    """
    Parse html table to list
    """
    rows = []
    for trow in table.find_all("tr"):
        row = []
        for tcell in trow.find_all(["th", "td"]):  # type: ignore
            strings = []
            for item in tcell.strings:  # type: ignore
                item = item.strip(" \n\t\xa0")
                if len(item) > 0:
                    strings.append(item)
            row.append(strings)
        rows.append(row)
    return rows


@dataclass
class DriverWDCClassification:
    name: str  # Driver name
    positions: list  # Race classification per round
    points: list  # Points per round


class DriversStandings:
    def __init__(self, year):
        self.year = year

        self.drivers = OrderedDict()  # Standings for each driver
        self.races = []  # Races
        self.next_round = 0

        if self.year >= 2022:
            self._sprint_position_to_points = {
                1: 8,
                2: 7,
                3: 6,
                4: 5,
                5: 4,
                6: 3,
                7: 2,
                8: 1,
            }
        elif self.year >= 2021:
            self._sprint_position_to_points = {1: 3, 2: 2, 3: 1}
        else:
            self._sprint_position_to_points = {}

        if self.year >= 2010:
            self._position_to_points = {
                1: 25,
                2: 18,
                3: 15,
                4: 12,
                5: 10,
                6: 8,
                7: 6,
                8: 4,
                9: 2,
                10: 1,
            }
        elif self.year >= 2003:
            self._position_to_points = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
        elif self.year >= 1991:
            self._position_to_points = {1: 10, 2: 6, 3: 4, 4: 3, 5: 2, 6: 1}
        else:
            raise RuntimeError("Not supported for championships held before 1991")

    def position_to_points(self, p, round, fastest_lap=False, p_sprint=None):
        # Race points
        pts = self._position_to_points.get(p, 0)

        if self.year == 2014 and round == "ABU":
            pts *= 2.0
        if self.year == 1991 and round == "AUS":
            pts *= 0.5
        if self.year == 2009 and round == "MAL":
            pts *= 0.5
        if self.year == 2021 and round == "BEL":
            pts *= 0.5
            fastest_lap = False

        if self.year >= 2019:
            if p <= 10 and fastest_lap:
                pts += 1

        # Sprint points
        if p_sprint is not None:
            pts += self._sprint_position_to_points.get(p_sprint, 0)

        return pts


def scrape_wiki_f1_standings(year):
    """
    Given a F1 season, scrapes the corresponding wikipedia page
    for the drivers standings
    """

    response = requests.get(
        url=f"https://en.wikipedia.org/wiki/{year:d}_FIA_Formula_One_World_Championship",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        },
        allow_redirects=True,
    )

    dr_std = DriversStandings(year)

    if response.status_code == 200:  # success!
        soup = bs4.BeautifulSoup(response.content, "html.parser")

        lookfor = [
            "Drivers' standings",
            "Drivers' Championship standings",
            "Drivers Championship standings",
            "World Drivers' Championship final standings",
            "{year:d} Drivers' Championship final standings",
            "World Drivers' Championship standings",
            "Drivers' Championship",
            "Drivers",
        ]

        for sectionname in lookfor:
            regex = re.compile((sectionname), re.IGNORECASE)
            dr_std_sect = [
                h3tag
                for h3tag in soup.find_all("h3")
                if h3tag.find(string=regex)  # type: ignore
            ]

            if len(dr_std_sect) > 0:
                dr_std_sect = dr_std_sect[0]
                # Next two tables are for the point system and drivers' points
                tables = dr_std_sect.find_all_next("table")[:2]
                rows = parse_html_tables(tables[0])  # type: ignore

                if len(rows) == 2:
                    posdr_table = tables[1]
                else:
                    posdr_table = tables[0]

                tab = posdr_table.find("table")  # type: ignore
                if tab:
                    posdr_table = tab

                rows = parse_html_tables(posdr_table)  # type: ignore
                dr_std.races = [r[0] for r in rows[0][2:-1]]

                next_round = 0

                # Loop through each row (driver)
                for row in rows[1:-1]:
                    try:
                        if row[1][0].lower() == "driver":
                            continue
                    except Exception:
                        continue

                    driver = row[1][0]
                    pos = []
                    pts = []

                    # Loop through each column (round)
                    for rnd, p_raw in zip(dr_std.races, row[2:-1]):
                        p = None
                        pt = 0
                        if len(p_raw) >= 1:
                            try:
                                p = int("".join(filter(is_int, p_raw[0])))
                            except ValueError:
                                p = -1  # DNS, RET, ...
                            fastest_lap = False
                            p_sprint = None
                            if len(p_raw) >= 2:
                                try:
                                    rest = "".join(p_raw[1:])
                                    fastest_lap = "F" in rest
                                    p_sprint = int("".join(filter(is_int, rest)))
                                except ValueError:
                                    pass
                            pt = dr_std.position_to_points(
                                p, rnd, fastest_lap, p_sprint
                            )
                        pos.append(p)
                        pts.append(pt)

                    try:
                        next_round = max(next_round, pos.index(None))
                    except ValueError:
                        next_round = len(dr_std.races)

                    dr_std.drivers[driver] = DriverWDCClassification(driver, pos, pts)

                dr_std.next_round = next_round

                break

    return dr_std


def main():
    now = datetime.datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument("years", nargs="*", type=int, default=[now.year])
    parser.add_argument(
        "-s", "--save", action="store_true", help="if true, saves into file [year].png"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="if true, does not show plot in interactive window",
    )

    args = parser.parse_args()

    for year in args.years:
        if year <= 0:
            year += now.year

        dr_std = scrape_wiki_f1_standings(year)

        if len(dr_std.races) > 0:
            fig, ax = plt.subplots(figsize=(15, 10))
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

            ax.set_xticks(rounds)
            ax.set_xticklabels(dr_std.races)
            ax.set_xlabel("Round")
            ax.set_ylabel("Points")
            ax.set_title(
                f"{year} FIA Formula One World Drivers's Championship standings"
            )
            ax.legend(loc="upper left", ncol=2)

            if args.save:
                fig.savefig(f"f1_{year}.png")

            if not args.quiet:
                plt.show()
        else:
            print("No data found")


if __name__ == "__main__":
    main()
