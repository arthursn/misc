import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt


def collatz(n, it=0, nlist=[]):
    if n <= 1:
        return [n] + nlist[::-1]
    elif n % 2 == 0:
        return collatz(n//2, it+1, nlist + [n])
    else:
        return collatz(3*n+1, it+1, nlist + [n])


def collatz_graph(nmax):
    """
    Creates a Collatz graph of the 'nmax' first natural numbers
    """
    nodes = []
    edges = []
    for n in range(nmax, 0, -1):
        if n not in nodes:
            nlist = collatz(n)
            nodes += nlist
            edges += list(zip(nlist[1:], nlist[:-1]))
    return list(set(edges))


def collatz_reverse(vmax, stop='n', n=1, it=0, edges=[]):
    """
    Creates a Collatz graph by the bottom-up method

    vmax: int
        iteration stops when vmax is reached by either 'n'
        or 'it', depending on the value set to 'stop'
        variable (see below)
    stop: str (optional)
        'n' or 'it'
        if stop='n' iteration stops when n reaches vmax
        if stop='it' iteration stops when it reaches vmax
        default: 'n'
    """
    neven = 2*n
    if dict(n=neven, it=it)[stop] <= vmax:
        # n % 6 == equivalent to (n % 2 == 0 and (n-1) % 3 == 0)
        # n != 4 because of loop 4-1
        if n % 6 == 4 and n != 4:
            nodd = (n-1)//3
            return collatz_reverse(vmax, stop, neven, it+1, edges + [[neven, n]]) + collatz_reverse(vmax, stop, nodd, it+1, [[nodd, n]])
        else:
            return collatz_reverse(vmax, stop, neven, it+1, edges + [[neven, n]])
    else:
        return edges


def collatz_iter(n):
    it = 0
    nmax = n
    while n > 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3*n + 1
            nmax = max(nmax, n)
        it += 1
    return it, nmax


# fig, ax = plt.subplots()
# nmax = 1000
# G = nx.DiGraph(collatz_graph(nmax))
# nx.draw(G, pos=graphviz_layout(G, prog='dot'),
#         ax=ax, node_size=2, arrows=False)

# # fig.savefig('collatz_{:}.pdf'.format(nmax), bbox_inches='tight')
# # plt.close('all')
# # write_dot(G, 'collatz.dot')

# fig, ax = plt.subplots()
# nmax = 100
# G = nx.DiGraph(collatz_graph(nmax))
# nx.draw(G, pos=graphviz_layout(G, prog='dot'), ax=ax, with_labels=True)

# fig, ax = plt.subplots()
# nmax, itmax = 20000, 10
# # G = nx.DiGraph(collatz_reverse(itmax, 'n'))
# # nx.draw(G, pos=graphviz_layout(G, prog='dot'), ax=ax, with_labels=True)
# G = nx.DiGraph(collatz_reverse(nmax, 'n'))
# nx.draw(G, pos=graphviz_layout(G, prog='dot'),
#         ax=ax, node_size=2, arrows=False)


# fig.set_size_inches(10, 10)
# fig.savefig('collatz_reverse_{:}.pdf'.format(nmax), bbox_inches='tight')

################

def get_primes(n):
    numbers = set(range(n, 1, -1))
    primes = []
    while numbers:
        p = numbers.pop()
        primes.append(p)
        numbers.difference_update(set(range(p*2, n+1, p)))
    return primes
    
nmax = 100000
nlist = range(1, nmax+1)
itlist = []
maxlist = []
for n in nlist:
    it, nmax = collatz_iter(n)
    itlist.append(it)
    maxlist.append(nmax)

fig, ax = plt.subplots()
ax.plot(nlist, itlist, "ko", ms=1)
ax.set_xlabel("n")
ax.set_ylabel("Iterations")

plt.show()
