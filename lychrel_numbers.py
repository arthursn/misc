"""
https://www.youtube.com/watch?v=bN8PE3eljdA
"""


def reverse(n):
    r = str(n)[::-1]
    return int(r, base=10)


def ispalindrome(n):
    if n == reverse(n):
        return True
    else:
        return False


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    n_list = []
    it_list = []
    sum_list = []
    itmax = 1000

    for n in range(10000):
        it = 0
        sum_rev = n
        while not ispalindrome(sum_rev):
            it += 1
            sum_rev += reverse(sum_rev)
            if it > itmax:
                print("n={} itmax was reached".format(n))
                break

        if ispalindrome(sum_rev):
            n_list.append(n)
            it_list.append(it)
            sum_list.append(sum_rev)
            print("n={} sum={} it={}".format(n, sum_rev, it))

    fig, ax = plt.subplots()
    ax.plot(n_list, it_list, "k.")
    plt.show()
