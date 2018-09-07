"""
https://en.wikipedia.org/wiki/6174_(number)
"""


def kaprekar_routine(n, ndigits=4, nlist=[]):
    """
    One iteration of the Kaprekar routine
    """
    while n not in nlist[:-1]:
        # fill with zeros
        n = '{:0{:}d}'.format(n, ndigits)
        # sort digits
        n = sorted(n)
        # join digits to form a number; reverse digits
        # to form another number. Subtract the former
        # from the later.
        n = int(''.join(n[::-1])) - int(''.join(n))

        # repeat until n appears again on the list. i.e.,
        # the cycle has closed
        nlist = kaprekar_routine(n, ndigits, nlist+[n])

    return nlist


if __name__ == '__main__':
    ndigits = 4  # number of digits

    for n in range(1001):
        nlist = kaprekar_routine(n, ndigits, [n])

        print(nlist)
