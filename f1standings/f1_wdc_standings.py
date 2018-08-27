# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString

def isint(s):
    try:
        int(s)
    except:
        return False
    return True

def htmltable2list(table):
    rows = []
    for trow in table.find_all('tr'):
        row = []
        for tcell in trow.find_all(['th', 'td']):
            string = [string for string in tcell.strings if len(string.strip(' \n\t\xa0')) > 0]
            string = string[0] if len(string) > 0 else ''
            row.append(string)
        rows.append(row)
    return rows

class DriversStandings(object):
    def __init__(self, year):
        if int(year) <= 1990:
            raise Exception('Not supported for championships held before 1991')

        self.year = int(year)

        self.rounds = []
        self.drivers = []
        self.positions = []
        self.points = []
        
        self._p2points = {}

        self.set_p2points()

    def set_p2points(self):
        if self.year >= 2010:
            p2points = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}
        elif self.year >= 2003:
            p2points = {1:10, 2:8, 3:6, 4:5, 5:4, 6:3, 7:2, 8:1}
        elif self.year >= 1991:
            p2points = {1:10, 2:6, 3:4, 4:3, 5:2, 6:1}
        self._p2points = p2points

    def p2points(self, p, round):
        try:
            pts = self._p2points[p]
        except KeyError:
            pts = 0.
        if self.year == 2014 and round == 'ABU':
            pts *= 2.
        if self.year == 2009 and round == 'MAL':
            pts *= .5
        return pts


def scrape_wiki_f1_standings(year):
    url = 'https://en.wikipedia.org/wiki/{}_FIA_Formula_One_World_Championship'.format(year)
    r = requests.get(url)

    drstd = DriversStandings(year)

    if r.status_code == 200: # success!
        soup = BeautifulSoup(r.content, 'html.parser')
        
        lookfor = ['Drivers\' standings', 'Drivers\' Championship standings', 'World Drivers\' Championship final standings', 
                   '{} Drivers\' Championship final standings'.format(year),
                   'World Drivers\' Championship standings', 'Drivers\' Championship', 'Drivers', ]

        for sectionname in lookfor:
            drstd_sect = [h3tag for h3tag in soup.find_all(['h2', 'h3']) if h3tag.find(text=sectionname)]

            if len(drstd_sect) > 0:
                drstd_sect = drstd_sect[0]
                tables = drstd_sect.find_all_next('table')[:2]  # Next two tables are for the point system and drivers' points
                
                rows = htmltable2list(tables[0])
                if len(rows) == 2:
                    posdr_table = tables[1]
                else:
                    posdr_table = tables[0]

                tab = posdr_table.find('table')
                if tab:
                    posdr_table = tab

                rows = htmltable2list(posdr_table)
                drstd.rounds = rows[0][2:-1]
                for row in rows[1:-1]:
                    drstd.drivers.append(row[1])
                    pos = []
                    pts = []
                    for rnd, p in zip(drstd.rounds, row[2:-1]):
                        p = ''.join(filter(isint, p))
                        try:
                            p = int(p)
                            pos.append(p)
                            pts.append(drstd.p2points(p, rnd))
                        except ValueError:
                            pos.append(None)
                            pts.append(0)
                    drstd.positions.append(pos)
                    drstd.points.append(pts)

                break

    return drstd

if __name__ == '__main__':
    import sys
    import os
    import numpy as np
    import matplotlib.pyplot as plt

    if len(sys.argv) > 1:
        year = sys.argv[1]
        drstd = scrape_wiki_f1_standings(year)

        if len(drstd.rounds) > 0:
            fig, ax = plt.subplots(figsize=(15,10))
            races = np.arange(len(drstd.rounds))
            for i, (pts, driver) in enumerate(zip(map(np.cumsum, drstd.points), drstd.drivers)):
                ax.plot(races, pts, label=driver)
            
            plt.xticks(races, drstd.rounds)
            ax.set_xlim(races[0], races[-1])
            ax.set_xlabel('Round')
            ax.set_ylabel('Points')
            ax.set_title('{} FIA Formula One World Drivers\'s Championship standings'.format(year))
            ax.legend(loc='upper left', ncol=2)

            fig.savefig('f1{}.pdf'.format(year))
            plt.show()
        else:
            print('No data found')
