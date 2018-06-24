from pylab import *
import math
import cmath

PI = math.pi

def pha(z):
    return 180 * math.atan2(z.imag, z.real) / math.pi

def GenerateSample(numSamples, w):
    x = [t for t in range(numSamples)]
    y = [cmath.exp(1j*w*t).real for t in range(numSamples)]
    return (x, y)

def PlotSample(sampleX, sampleY):
    plot(sampleX, sampleY, linewidth=1.0)
    xlabel('time (s)')
    ylabel('voltage (mV)')
    title('About as simple as it gets, folks')
    grid(True)
    show()

def PlotComplex(sampleX, sampleY, plotopt = ''):
    yReal = [x.real for x in sampleY]
    yImag = [x.imag for x in sampleY]
    yAbs  = [abs(x) for x in sampleY]
    yPha  = [pha(x) for x in sampleY]

    subplot(221)
    plot(sampleX, yReal, plotopt, linewidth=1.0)
    grid(True)

    subplot(222)
    plot(sampleX, yImag, plotopt, linewidth=1.0)
    grid(True)

    subplot(223)
    plot(sampleX, yAbs, plotopt, linewidth=1.0)
    grid(True)

    subplot(224)
    plot(sampleX, yPha, plotopt, linewidth=1.0)
    grid(True)

    #xlabel('time (s)')
    #ylabel('voltage (mV)')
    #title('About as simple as it gets, folks')
    #show()

def Fourier1(w, sample):
    def add(x,y):
        return x+y;
    N = len(sample)
    sum = [sample[k] * cmath.exp(-1j*w*k) for k in range(N)]
    return reduce(add, sum)

def Fourier1Inv(w, sample):
    def add(x,y):
        return x+y;
    N = len(sample)
    sum = [sample[k] * cmath.exp(1j*w*k) for k in range(N)]
    return reduce(add, sum) / N

def Fourier1DiscPoints(N):
    p = [2*PI/N*j for j in range(N)]
    for i in range(len(p)):
        if p[i] > PI: p[i] -= 2*PI
    p = sort(p)
    print p
    return p


#sampleX, sampleY = GenerateSample(8, math.pi / 2)
#sampleY = [0.5, -0.5]
sampleY = [0]*20 + [1] + [0]*20
sampleX = range(len(sampleY))
PlotSample(sampleX, sampleY)

fourierX_cont = arange(-PI, PI, 0.01)
fourierY_cont = [Fourier1(x, sampleY) for x in fourierX_cont]
fourierX_disc = Fourier1DiscPoints(len(sampleY))
fourierY_disc = [Fourier1(x, sampleY) for x in fourierX_disc]
PlotComplex(fourierX_cont, fourierY_cont)
PlotComplex(fourierX_disc, fourierY_disc, 'o')
show()

fourierX_cont = arange(-PI, PI, 0.01)
fourierY_cont = [Fourier1(x, sampleY) for x in fourierX_cont]
fourierX_disc = Fourier1DiscPoints(len(sampleY))
fourierY_disc = [Fourier1(x, sampleY) for x in fourierX_disc]
PlotComplex(fourierX_cont, fourierY_cont)
PlotComplex(fourierX_disc, fourierY_disc, 'o')
show()


