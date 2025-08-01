"""
Script that searches for grafting numbers

http://math.wikia.com/wiki/Grafting_number
"""


def isgrafiting(n):
    # 18 points decimal representation of square root of n
    sqrt = '%.18f' % (n**.5)
    # n as string
    n = str(n)
    # decimal separator position
    pos = sqrt.find('.')
    # sqrt(n) without decimal separator
    sqrt_nosep = sqrt.replace('.', '')
    match = sqrt_nosep.find(n)

    if match >= 0:
        if match <= pos:
            beg = match
            end = beg + len(n)

            if beg >= pos:
                beg += 1
            if end > pos:
                end += 1

            # formatting match
            sqrt_fmt = sqrt[:beg] + '\033[31;1m' + \
                sqrt[beg:end] + '\033[0m' + sqrt[end:]

            print(n, sqrt_fmt)

            return True

    return False


if __name__ == '__main__':
    for n in range(1000000):
        isgrafiting(n)
