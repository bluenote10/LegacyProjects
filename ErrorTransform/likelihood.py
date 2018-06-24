import sympy
import matplotlib
import pylab
import math
import scipy.stats
import numpy

PI = math.pi
def plot(subplot, f, x):
    pylab.subplot(subplot)
    xx = pylab.arange(-2, 5, 0.1)
    yy = [float(f.subs(x, i)) for i in xx]
    pylab.plot(xx,yy)

x = sympy.Symbol('x')
mu = sympy.Symbol('mu')
ga = sympy.Symbol('gamma')

f = sympy.log(1.0/PI * (ga / ((x-mu)**2 + ga**2)))
sympy.pprint(f)
#f = f.subs(mu, 2)
f = f.subs(ga, 1)

sample = [numpy.random.standard_cauchy()+2 for i in range(500)]
L = sum([f.subs(x,xi) for xi in sample])
#sympy.pprint(L)


#abl = L.diff(mu)
#sympy.pprint(abl)
#sympy.solve(abl,mu)
plot(211, L, mu)
#plot(212, f.diff(x) , x)
pylab.show()


