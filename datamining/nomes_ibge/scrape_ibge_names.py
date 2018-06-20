# -*- coding: utf-8 -*-

import requests
import json
import numpy as np
import matplotlib.pyplot as plt


def scrape_names(names):
    metalist = []

    for name in names:
        name = name.title()
        txt = None

        try:
            f = open('json/{}.json'.format(name))
            txt = f.read()
        except:
            url = 'https://servicodados.ibge.gov.br/api/v2/censos/nomes/' + name
            r = requests.get(url)
            if r.status_code == 200:  # success!
                txt = r.content.decode()  # bits to str
                f = open('json/{}.json'.format(name), 'w')
                f.write(txt)
                f.close()

        metadict = {'nome_busca': name}
        if txt:
            dlist = json.loads(txt)  # parse json
            if len(dlist) > 0:
                for metaitem in dlist:
                    metadict.update(metaitem)
                    metalist.append(MetadataIBGE(metadict))
            else:
                metalist.append(MetadataIBGE(metadict))
        else:
            metalist.append(MetadataIBGE(metadict))

    return metalist


class MetadataIBGE(object):
    def __init__(self, metadict={}, name_display=None):
        self.name = ''
        self.name_search = ''
        self.name_display = ''
        self.location = ''
        self.frequency = []
        self.cum_frequency = []
        self.period = []
        self.year_lb = []  # year lower bound
        self.year_ub = []  # year upper bound

        if len(metadict) > 0:
            self.parse_dict_meta(metadict)
            self.set_name_display(name_display)

    def set_name_display(self, name_display=None):
        if name_display:
            self.name_display = name_display
        else:
            self.name_display = self.name_search.split(',')[0].title()

    def split_period(self, period):
        period = period.split(',')
        year_lb = None
        year_ub = None
        if len(period) == 2:
            year_lb = int(period[0].strip('[]'))
            year_ub = int(period[1].strip('[]'))
        elif len(period) == 1:
            year_ub = int(period[0].strip('[]'))
        return year_lb, year_ub

    def parse_dict_meta(self, metadict):
        try:
            self.name = metadict['nome']
        except:
            pass

        try:
            self.name_search = metadict['nome_busca']
        except:
            pass

        try:
            self.location = metadict['localidade']
        except:
            pass

        try:
            res = metadict['res']
        except:
            pass
        else:
            self.frequency = []
            self.period = []
            for item in res:
                self.frequency.append(item['frequencia'])
                self.period.append(item['periodo'])
                # split period into year_lb and year_ub
                year_lb, year_ub = self.split_period(item['periodo'])
                self.year_lb.append(year_lb)
                self.year_ub.append(year_ub)
            self.cum_frequency = list(np.cumsum(self.frequency))

    def plot_frequency(self, ax=None, cum=False, *args, **kwargs):
        if not ax:
            fig, ax = plt.subplots()

        kwargs['label'] = kwargs.get('label', self.name_display)
        if cum:
            line, = ax.plot(self.year_ub, self.cum_frequency, *args, **kwargs)
        else:
            line, = ax.plot(self.year_ub, self.frequency, *args, **kwargs)

        return line


def merge_metadata_group_names(metalist, name_display=None):
    location = []
    name = []
    name_search = []
    frequency = []
    period = []

    for meta in metalist:
        location += [meta.location]
        name += [meta.name]
        name_search += [meta.name_search]
        frequency += meta.frequency
        period += meta.period

    frequency = np.array(frequency)
    period = np.array(period)

    newmeta = MetadataIBGE()
    newmeta.location = ','.join(location)
    newmeta.name = ','.join(name)
    newmeta.name_search = ','.join(name_search)
    newmeta.set_name_display(name_display)

    set_period = sorted(set(period))
    for per in set_period:
        sel = per == period

        newmeta.frequency.append(frequency[sel].sum())
        newmeta.period.append(per)

        year_lb, year_ub = newmeta.split_period(per)
        newmeta.year_lb.append(year_lb)
        newmeta.year_ub.append(year_ub)

    return newmeta


def get_option(args, option):
    hasit = False
    try:
        idx = args.index(option)
    except:
        pass
    else:
        hasit = True
        args.pop(idx)
    return args, hasit


if __name__ == '__main__':
    import sys

    args = sys.argv[1:]

    args, cum = get_option(args, '-c')
    args, sort = get_option(args, '-s')
    args, log = get_option(args, '-l')

    if len(args) > 0:
        metalist = scrape_names(args)

        fig, ax = plt.subplots()

        order = range(len(metalist))
        if sort:
            criteria = []
            for meta in metalist:
                criteria.append(meta.cum_frequency[-1])
            order = np.argsort(criteria)[::-1]

        for i in order:
            metalist[i].plot_frequency(ax=ax, cum=cum, marker='o')

        ax.set_xlabel('Ano censo')

        if cum:
            ax.set_ylabel(u'Número total de pessoas')
        else:
            ax.set_ylabel(u'Variação em relação à década anterior')

        if log:
            ax.set_yscale('log')
            ax.set_ylim(1, )

        plt.legend(loc='lower left')

        plt.show()
