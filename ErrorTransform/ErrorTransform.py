import sympy
import matplotlib
import pylab


def plot(subplot, f, x):
    pylab.subplot(subplot)
    xx = pylab.arange(0.1, 2, 0.1)
    yy = [float(f.subs(x, i)) for i in xx]
    pylab.plot(xx,yy)

x = sympy.Symbol('x')
f = x**2

plot(211, f, x)
plot(212, f.diff(x) , x)
pylab.show()


