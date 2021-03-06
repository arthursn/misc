#!/bin/env python3

"""
Converts equations in gitlab markdown files to github-compatible equations

A. Nishikawa 2020
"""

import os
import urllib.parse
import argparse


def translate_equations(ocl, ccl, new_ocl, new_ccl, lines, encode_url=True):
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
    new_lines = []
    len_ocl, len_ccl = len(ocl),  len(ccl)
    expr_open = False
    expr = ''
    for line in lines:
        while line:
            if not expr_open:
                # Search for opening clause
                if (m := line.find(ocl)) >= 0:
                    new_lines.append(line[:m])
                    line = line[m+len_ocl:]
                    expr_open = True
                else:
                    new_lines.append(line)
                    break
            else:
                # Search for closing clause
                if (m := line.find(ccl)) >= 0:
                    expr += line[:m]
                    expr = expr.strip(' \n')
                    if encode_url:
                        expr = urllib.parse.quote(expr)
                    new_lines.append(new_ocl + expr + new_ccl)
                    line = line[m+len_ccl:]
                    expr_open = False
                    expr = ''
                else:
                    expr += line
                    break
    return new_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='+', help='input markdown files')
    parser.add_argument('-s', '--suffix', default='_github_compatible',
                        help='suffix of output file')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='overwrite file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='activate debug mode')
    args = parser.parse_args()

    if args.debug:
        import sys

    render_url = 'https://render.githubusercontent.com/render/math?math='

    for fname in args.filenames:
        lines = []
        with open(fname, 'r') as f:
            for line in f:
                lines.append(line)

        if args.debug:
            # Convert inline equations. Result goes in temp file
            lines = translate_equations('$`', '`$', '\033[1;31m', '\033[0m', lines, False)
            # Convert block equations
            lines = translate_equations('```math', '```', '\033[1;32m', '\033[0m', lines, False)

            for line in lines:
                sys.stdout.write(line)
        else:
            # Convert inline equations. Result goes in temp file
            lines = translate_equations('$`', '`$',
                                        '<img src="' + render_url,
                                        '" style="display: inline; margin-top: 0;"/>',
                                        lines)
            # Convert block equations
            lines = translate_equations('```math', '```',
                                        '<p align="center"><img src="' + render_url, '"/></p>',
                                        lines)

            if args.overwrite:
                fnameout = fname
                print(f'Overwriting {fname}')
            else:
                basename, ext = os.path.splitext(fname)
                fnameout = basename + args.suffix + ext
                print(f'{fname} -> {fnameout}')

            with open(fnameout, 'w') as f:
                for line in lines:
                    f.write(line)
