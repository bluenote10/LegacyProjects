import sympy
import matplotlib
import pylab
import math
import scipy.stats
import numpy

PI = math.pi
def plot(subplot, f, x):
    pylab.subplot(subplot)
    xx = pylab.arange(0.8, 1.2, 0.005)
    yy = [float(f.subs(x, i)) for i in xx]
    pylab.plot(xx,yy)

x = sympy.Symbol('x')
mu = sympy.Symbol('mu')
si = sympy.Symbol('sigma')

#f = sympy.log(1.0/PI * (ga / ((x-mu)**2 + ga**2)))
f = 1.0 / (sympy.sqrt(2*PI) * si) * sympy.exp(- (x - mu)**2 / (2 * si**2))
sympy.pprint(f)
f = f.subs(mu, 2)
#f = f.subs(ga, 1)

sample = [numpy.random.standard_normal()+2 for i in range(100)]
L = sum([sympy.log(f.subs(x,xi)) for xi in sample])

print "Likelihood"
#sympy.pprint(L)

abl1 = L.diff(si)
print "Likelihood - 1. Derivative"
#sympy.pprint(abl1)

abl2 = L.diff(si, 2)
print "Likelihood - 2. Derivative"
#sympy.pprint(abl2)

#sympy.solve(abl,mu)
plot(311, L, si)
plot(312, abl1 , si)
plot(313, abl2 , si)
pylab.show()


