#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import requests
# Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup


def scrape_xkcd(issue, save=True):
    meta = {}
    issue = str(issue)
    url = 'https://m.xkcd.com/' + issue

    sys.stdout.write('Fetching comic #{}... '.format(issue))
    sys.stdout.flush()
    r = requests.get(url)
    if r.status_code == 200:  # success!
        try:
            soup = BeautifulSoup(r.content, "html.parser")

            img = soup.find("img", {"id": "comic"})
            alt_text = img.get('title')
            img_src = img.get('src')
            if 'http' not in img_src:
                img_src = 'https:' + img_src

            title = soup.find("h1", {"id": "title"}).string

            local_file = None
            if save:
                r_img = requests.get(img_src)
                if r_img.status_code == 200:  # success!
                    extension = os.path.splitext(img_src)[-1]
                    local_file = issue + extension
                    open(local_file, 'wb').write(r_img.content)

            meta = {'title': title, 'alt_text': alt_text,
                    'img_src': img_src, 'local_file': local_file}

            sys.stdout.write('done!\n')
        except:
            sys.stdout.write('failed!\n')
    else:
        sys.stdout.write('not found!\n')
    sys.stdout.flush()

    return meta


if __name__ == '__main__':
    import json
    args = sys.argv[1:]
    issues = []

    save = False
    openimg = False
    for arg in args:
        if arg == '-s':
            save = True
        elif arg == '-o':
            openimg = True
        else:
            issues.append(arg)

    for issue in issues:
        meta = scrape_xkcd(issue, save)
        print(json.dumps(meta, indent=2))

        if openimg:
            try:
                os.system('eog {}'.format(meta['img_src']))
            except:
                pass
