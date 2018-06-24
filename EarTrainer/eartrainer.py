
# test code for PyPortMidi
# a port of a subset of test.c provided with PortMidi
# John Harrison
# harrison [at] media [dot] mit [dot] edu

# March 15, 2005: accommodate for SysEx messages and preferred list formats
#                 SysEx test code contributed by Markus Pfaff 
# February 27, 2005: initial release

import pypm
import array
import time
import random
import curses


NUM_MSGS = 100 # number of MIDI messages for input before closing

INPUT = 0
OUTPUT = 1

def PrintDevices(InOrOut):
    for loop in range(pypm.CountDevices()):
        interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
        if ((InOrOut == INPUT) & (inp == 1) |
            (InOrOut == OUTPUT) & (outp ==1)):
            print loop, name," ",
            if (inp == 1): print "(input) ",
            else: print "(output) ",
            if (opened == 1): print "(opened)"
            else: print "(unopened)"
    print


def ProgramChange(prog):
    MidiOut.Write([[[0xc0,0,0],pypm.Time()]])

def NoteOn(note):
    #MidiOut.Write([[[0x90, note, 100], pypm.Time()]])
    MidiOut.WriteShort(0x90, note, 100)

def NoteOff(note):
    #MidiOut.Write([[[0x90, note, 0], pypm.Time()]])
    MidiOut.WriteShort(0x90, note, 0)

def PlayChord(chord, bpm):
    ChordList = []
    MidiTime = pypm.Time()
    wait = 60.0 / bpm * 1000
    print wait
    for i in range(len(chord)):
        ChordList.append([[0x90,chord[i],100], MidiTime + wait * i])
    MidiOut.Write(ChordList)
    while pypm.Time() < MidiTime + wait + len(chord) * wait : pass
    ChordList = []
    # seems a little odd that they don't update MidiTime here...
    for i in range(len(chord)):
        ChordList.append([[0x90,chord[i],0], MidiTime + wait * i])
    MidiOut.Write(ChordList)


def PlayScale(tones, bpm):
    wait = 60.0 / bpm
    for i in tones:
        NoteOn(i)
        time.sleep(wait)
        NoteOff(i)

def PrintTone(tone, key):
    t = tone - 60
    okt = t / 12
    t = t % 12

    flats = [2, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0]
    names = [ ["C","Cis","D","Dis","E","Eis","Fis","G","Gis","A","Ais","H"],
              ["C","Des","D","Es", "E","F","Ges","G","As", "A","B","Ces"],
              ["C","Cis","D","Dis","E","F","Fis","G","Gis","A","Ais","H"] ]

    name = names[flats[key]][t]
    stdscr.addstr("Octave: " + str(okt+2) + "    Note: " + name + "\n")
    stdscr.refresh()

def PrintTones(tones, key):
    for i in tones:
        PrintTone(i, key)

def DiatonicMelody():

    keynames = ["C","Des (Cis)", "D", "Es", "E", "F", "Ges/Fis", "G", "As", "A", "Bb", "H (Ces)"]

    shapeoffsets = [7, 9, 12, 14, 16]
    shapenames = [7, 2, 3, 5, 6]

    sh = [ [[0,1,3],[0,1,3],[0,2,3],[0,2,3],[1,3],[0,1,3]],
           [[1,3,4],[1,3],[0,1,3],[0,1,3],[1,3,4],[1,3,4]],
           [[0,1,3],[0,2,3],[0,2,3],[0,2],[0,1,3],[0,1,3]],
           [[1,3],[0,1,3],[0,1,3],[0,2,3],[1,3,4],[1,3]],
           [[1,3,4],[1,3,4],[1,3],[0,1,3],[1,2,4],[1,3,4]] ]

    stringadd = [0, 5, 10, 15, 19, 24]

    done = False
    while 1:
        key = random.randint(0, 11)
        shape = random.randint(0, 4)

        base = shapeoffsets[shape] + key
        while base > 12:
            base -= 12

        tones = []
        lowE = 40
        for s in range(6):
            for i in range(len(sh[shape][s])):
                tones.append(sh[shape][s][i] + base + lowE + stringadd[s])

        stdscr.clear()

        randtone = tones[random.randint(0, len(tones)-1)]
        stdscr.addstr("Start: ")
        PrintTone(randtone, key)

        stdscr.refresh()
        time.sleep(5)

        #stdscr.addstr("Shape: " + str(shapenames[shape]) + "\n")
        stdscr.addstr("Key:   " + str(keynames[key]) + "\n")

        stdscr.addstr("\nAll Notes\n")
        PrintTones(tones, key)

        stdscr.addstr("Playing Scale\n")
        stdscr.refresh()
        PlayScale(tones, 600)

        stdscr.addstr("repeat? (ENTER -> Next, ESC -> quit)\n")
        stdscr.refresh()
        while 1:
            c = stdscr.getch()
            #stdscr.addstr("'" + str(c) + "'")
            #stdscr.refresh()
            if c == 27:
                done = True
                break
            if c == 10:
                break
            else:
                PlayScale(tones, 600)

        if done == True:
            break

def RandomKey():

    keynames = ["C","Des (Cis)", "D", "Es", "E", "F", "Ges/Fis", "G", "As", "A", "Bb", "H (Ces)"]
    lastkey = -999

    while 1:
        key = 0
        """
        while 1:
            new = random.randint(0, 11)
            if abs(new - lastkey) > 2:
                key = new
                break
        """

        key = random.randint(0, 11)

        stdscr.clear()
        stdscr.addstr("Key:   " + str(keynames[key]) + "\n")
        stdscr.refresh()

        c = stdscr.getch()
        if c == 27:
            break

        lastkey = key

def Repeat(func):
    while 1:
        func()
        stdscr.addstr("\nagain? (ESC to quit)\n")
        stdscr.refresh()
        c = stdscr.getch()
        if c == 27: break


def Choose(list):
    while 1:
        stdscr.clear()
        for i in range(len(list)):
            stdscr.addstr(str(i+1) + ". " + list[i][0] + "\n")
        stdscr.refresh()
        c = stdscr.getch()
        num = c - 49
        stdscr.addstr("'" + str(num) + "'")
        stdscr.refresh()
        if c == 27:
            break
        if num >= 0 and num <= 9:
            list[num][1]()

    stdscr.addstr("\ndone\n")
    stdscr.refresh()


# init pyportmide
pypm.Initialize()

# init curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

# open midi out
PrintDevices(OUTPUT)
#dev = int(raw_input("Type output number: "))
dev = 8
#print "Using Device:", dev
MidiOut = pypm.Output(dev, 100)

# call choose
Choose([ ["Diatonic Melody", DiatonicMelody],
         ["Random Key", RandomKey] ])
DiatonicMelody()

# uninit curses
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()

# uninit pyportmidi
del MidiOut
pypm.Terminate()














#dummy = raw_input("ready to chord-on/chord-off... (type RETURN):")
#chord = [60, 67, 76, 83, 90]
#PlayScale(chord, 240)



