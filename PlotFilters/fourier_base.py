from pylab import *
import math
import cmath
import sys

PI = math.pi

def pha(z):
    return 180 * math.atan2(z.imag, z.real) / PI

def gauss(x, mu, sigma):
    return 1. / (math.sqrt(2*PI)*float(sigma)) * exp(-(x-float(mu))**2 / (2*(float(sigma)**2)))

def multlist(list, factor):
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

def GenerateSampleDamped(numSamples, w):
    data = [cmath.exp(1j*w*t).imag for t in range(numSamples)]
    for i in range(len(data)):
        data[i] *= gauss(i, 0, numSamples/4)
    return data

def MirrorSample(sample, even, faktor):
    if even == True:
        toappend = list(reversed(sample[1:-1]))
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


origsample = [0]*16 + GenerateSample(16, math.pi / 2) + [0]*16
#origsample = [0.5, -0.5]
#origsample = [-1,2,6,2,-1]

#origsample = GenerateSampleDamped(33, PI/4)

#origsample = [0]*10 + [1]*4 + [0]*10                  # box band pass
#origsample = [1]*3 + [0]*10                           # box tief pass
#origsample = imaglist(GenerateGaussSample(20, 4, 1))
#origsample = imaglist(GenerateGaussSample(10, 4, 0.1))


# Fill or Mirror?
#origsample = MirrorSample(origsample, True, -1)
#origsample += [0]*len(origsample)





#transsample = FourierSample(origsample, -1)
#transfilter = FourierSample(filtersam, 1)
#transsample = [(transsample[i] * filtersam[i]) for i in range(N)]
#invtrsample = FourierSample(origsample, +1)
#transsample = [abs(x) for x in transsample]
#orig2sample = FourierSample(transsample, +1)



