from pylab import *
import math
import cmath
import sys
import os

PI = math.pi

pathname = os.path.dirname(sys.argv[0])
print 'sys.argv[0] =', sys.argv[0]
print 'path        =', pathname
print 'full path   =', os.path.abspath(pathname)
print 'current     =', os.getcwd()
os.chdir(os.path.abspath(pathname))
print 'new current =', os.getcwd()

def pha(z):
    return 180 * math.atan2(z.imag, z.real) / PI

def gauss(x, mu, sigma):
    return (exp(- ((float(x)-float(mu))**2.0) / (2*(float(sigma)**2.0))))

def multlist(list, factor):
    #print factor
    for i in range(len(list)):
        list[i] *= factor
    return list

def imaglist(list):
    for i in range(len(list)):
        list[i] *= 1j
    return list

def GenerateGaussSample(n, mu, sigma):
    data = []
    for i in range(n):
        data.append(gauss(i, mu, sigma))
    return data

def GenerateSample(numSamples, w):
    return [cmath.exp(1j*w*t).imag for t in range(numSamples)]

def GenerateSampleDamped(numSamples, w, sym):
    if sym == True:
        def val(x):
            #print x
            return x.imag
    else:
        def val(x):
            #print x
            return x.real
    data = [val(cmath.exp(1j*w*t)) for t in range(numSamples)]
    #print data
    for i in range(len(data)):
        data[i] *= gauss(i, 0, float(numSamples) / 4)
    return data

def MirrorSample(sample, even, faktor):
    if even == True:
        toappend = list(reversed(sample))
    else:
        toappend = list(reversed(sample[1:]))
    for i in range(len(toappend)):
        toappend[i] *= faktor
    return sample + toappend

def PlotSample(sampleX, sampleY):
    plot(sampleX, sampleY, linewidth=1.0)
    xlabel('time (s)')
    ylabel('voltage (mV)')
    title('About as simple as it gets, folks')
    grid(True)
    show()

def PlotComplex(sampleX, sampleY, plotopt, plotwindows):
    yReal = [x.real for x in sampleY]
    yImag = [x.imag for x in sampleY]
    yAbs  = [abs(x) for x in sampleY]
    yPha  = [pha(x) for x in sampleY]

    subplot(plotwindows[0])
    plot(sampleX, yReal, plotopt, linewidth=1.0)
    grid(True)

    subplot(plotwindows[1])
    plot(sampleX, yImag, plotopt, linewidth=1.0)
    grid(True)

    subplot(plotwindows[2])
    plot(sampleX, yAbs, plotopt, linewidth=1.0)
    grid(True)

    subplot(plotwindows[3])
    plot(sampleX, yPha, plotopt, linewidth=1.0)
    grid(True)

    #xlabel('time (s)')
    #ylabel('voltage (mV)')
    #title('About as simple as it gets, folks')
    #show()

def Fourier(j, sample, sign):
    def add(x,y):
        return x+y;
    N = len(sample)
    sum = [sample[k] * cmath.exp(sign*1j*k*2*PI/N*j) for k in range(N)]
    return reduce(add, sum) / math.sqrt(N)

def FourierSample(sample, sign, plotwindows):
    N = len(sample)
    fourierX_cont = arange(0, N, 0.01)
    fourierX_disc = range(N)
    fourierY_cont = [Fourier(x, sample, sign) for x in fourierX_cont]
    fourierY_disc = [Fourier(x, sample, sign) for x in fourierX_disc]
    PlotComplex(fourierX_cont, fourierY_cont, '',  plotwindows)
    PlotComplex(fourierX_disc, fourierY_disc, 'o', plotwindows)
    return fourierY_disc

def FourierBoth(sample):
    N = len(sample)
    trans = FourierSample(sample, -1, [425,426,427,428])
    back = FourierSample(trans, +1, [421,422,423,424])
    print "Maximum diff after retransform:", max([abs(sample[i]-back[i]) for i in range(N)])
    #savefig('shifted_' + str(nr), dpi=300)
    #clf()
    show()
    return trans

def ApplyFilter(sample, fil):
    out = sample[:]
    half = int(len(fil) / 2)
    for i in range(len(out)):
        out[i] = 0
        #for k in range(len(fil)):
        #    out[i] += fil[k] * sample[i-k]
        for k in range(-half, half):
            out[i] += fil[k] * sample[i-k % len(sample)]
    #out = out[shift:] + out[:shift]
    return out

def shiftlist(list, i):
    return list[i:] + list[:i]
"""
fil1 = [0.5, 0.5]
fil2 = [0.5, -0.5]
"""

"""
fil1 = [-2,1,1]
fil2 = [1,-2,1]
"""

fil1 = [-1,2,-6,2,-1]
fil2 = [-6,2,-1,-1,2]

"""
fil1 = [-2,1,1]
fil2 = [-1,2,6,2,-1]
fil3 = [6,2,-1,-1,2]
"""

"""
filter1DFT = multlist(GenerateGaussSample(3, 1, 1), +1)
filter1DFT = [0] + MirrorSample(filter1DFT, True, +1)
filter1coef = FourierBoth(filter1DFT)

filter2DFT = multlist(GenerateGaussSample(3, 1, 1), -1j)
filter2DFT = [0] + MirrorSample(filter2DFT, True, -1)
filter2coef = FourierBoth(filter2DFT)

for i in range(len(filter1coef)):
    f1 = filter1coef[i]
    f2 = filter2coef[-i]
    print f1, f2, abs(f1)**2 + abs(f2)**2
"""

filter1 = GenerateSampleDamped(5, PI/2, True)
filter1 += multlist(list(reversed(filter1[1:])), -1)
print filter1
filter1FT = FourierBoth(filter1)

filter2 = GenerateSampleDamped(5, PI/2, False)
filter2 += multlist(list(reversed(filter2[1:])), +1)
print filter2
filter2FT = FourierBoth(filter2)

for i in range(len(filter1FT)):
    f1r = filter1FT[i].real
    f1i = filter1FT[i].imag
    f2r = filter2FT[i].real
    f2i = filter2FT[i].imag
    print "Filter1: %2.3f %f     Filter2: %f %f" % (f1r, f1i, f2r, f2i)

#for i in range(len(fil1)):
#    f = shiftlist(fil1, i)
#    FourierBoth(f)

#FourierBoth(fil2)
#FourierBoth(fil3)


