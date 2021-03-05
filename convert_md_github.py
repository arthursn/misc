#!/bin/env python3

"""
Converts equations in gitlab markdown files to github-compatible equations

A. Nishikawa 2020
"""

import os
import urllib.parse
import argparse


def translate_equations(ocl, ccl, new_ocl, new_ccl, fin, fout):
    """
    Translate LaTeX equations

    ocl: str
        Opening equation clause, e.g., $` or math```
    ccl: str
        Closing equation clause, e.g., `$ or ```
    new_ocl: str
        New opening clause
    new_ccl: str
        New closing clause
    fin: TextIOWrapper
        Input file stream
    fout: TextIOWrapper
        Output file stream
    """
    len_ocl, len_ccl = len(ocl),  len(ccl)
    expr_open = False
    expr = ''
    for line in fin:
        while line:
            if not expr_open:
                if (m := line.find(ocl)) >= 0:
                    fout.write(line[:m])
                    line = line[m+len_ocl:]
                    expr_open = True
                else:
                    fout.write(line)
                    break
            else:
                if (m := line.find(ccl)) >= 0:
                    expr += line[:m]
                    fout.write(new_ocl + urllib.parse.quote(expr.strip('\n')) + new_ccl)
                    line = line[m+len_ccl:]
                    expr_open = False
                    expr = ''
                else:
                    expr += line
                    break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='+', help='input markdown files')
    parser.add_argument('-s', '--suffix', default='_github_compatible',
                        help='suffix of output file')
    parser.add_argument('-e', '--extension', default='md',
                        help='extension of output file')
    args = parser.parse_args()

    render_url = 'https://render.githubusercontent.com/render/math?math='

    for fname in args.filenames:
        fnametmp = fname + '.tmp'
        fnameout = os.path.splitext(fname)[0] + args.suffix + "." + args.extension

        print(f'{fname} -> {fnameout}')

        # Convert inline equations. Result goes in temp file
        with open(fname, 'r') as fin, open(fnametmp, 'w') as fout:
            translate_equations('$`', '`$',
                                '<img src="' + render_url,
                                '" style="display: inline; margin-top: 0;"/>',
                                fin, fout)

        # Convert block equations
        with open(fnametmp, 'r') as fin, open(fnameout, 'w') as fout:
            translate_equations('```math', '```',
                                '<p align="center"><img src="' + render_url,
                                '"/></p>',
                                fin, fout)

        # Delete temp file
        os.remove(fnametmp)
