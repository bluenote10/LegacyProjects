'''
multi_hotkey.py

A few simple methods which implement multiple hotkey support for emacs-like
hotkey sequences.

Feel free to use this code as you desire, though please cite the source.

Josiah carlson
http://come.to/josiah
'''

import wx
import time
import os
import sys
import ConfigParser
import glob




def setpathscript():#{{{
    """
    Change path to script directory
    """
    pathname = os.path.dirname(sys.argv[0])
    newpath = os.path.abspath(pathname)
    os.chdir(newpath)#}}}

def setpathhome():
    """
    Change path to home directory
    """
    os.chdir(os.path.expanduser("~"))

keyMap = {}

def gen_keymap():
    keys = ("BACK", "TAB", "RETURN", "ESCAPE", "SPACE", "DELETE", "START",
        "LBUTTON", "RBUTTON", "CANCEL", "MBUTTON", "CLEAR", "PAUSE",
        "CAPITAL", "PRIOR", "NEXT", "END", "HOME", "LEFT", "UP", "RIGHT",
        "DOWN", "SELECT", "PRINT", "EXECUTE", "SNAPSHOT", "INSERT", "HELP",
        "NUMPAD0", "NUMPAD1", "NUMPAD2", "NUMPAD3", "NUMPAD4", "NUMPAD5",
        "NUMPAD6", "NUMPAD7", "NUMPAD8", "NUMPAD9", "MULTIPLY", "ADD",
        "SEPARATOR", "SUBTRACT", "DECIMAL", "DIVIDE", "F1", "F2", "F3", "F4",
        "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14",
        "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24",
        "NUMLOCK", "SCROLL", "PAGEUP", "PAGEDOWN", "NUMPAD_SPACE",
        "NUMPAD_TAB", "NUMPAD_ENTER", "NUMPAD_F1", "NUMPAD_F2", "NUMPAD_F3",
        "NUMPAD_F4", "NUMPAD_HOME", "NUMPAD_LEFT", "NUMPAD_UP",
        "NUMPAD_RIGHT", "NUMPAD_DOWN", "NUMPAD_PRIOR", "NUMPAD_PAGEUP",
        "NUMPAD_NEXT", "NUMPAD_PAGEDOWN", "NUMPAD_END", "NUMPAD_BEGIN",
        "NUMPAD_INSERT", "NUMPAD_DELETE", "NUMPAD_EQUAL", "NUMPAD_MULTIPLY",
        "NUMPAD_ADD", "NUMPAD_SEPARATOR", "NUMPAD_SUBTRACT", "NUMPAD_DECIMAL",
        "NUMPAD_DIVIDE")

    for i in keys:
        keyMap[getattr(wx, "WXK_"+i)] = i
    for i in ("SHIFT", "ALT", "CONTROL", "MENU"):
        keyMap[getattr(wx, "WXK_"+i)] = ''

def GetKeyPress(evt):
    keycode = evt.GetKeyCode()
    keyname = keyMap.get(keycode, None)
    modifiers = ""
    for mod, ch in ((evt.ControlDown(), 'Ctrl+'),
                    (evt.AltDown(),     'Alt+'),
                    (evt.ShiftDown(),   'Shift+'),
                    (evt.MetaDown(),    'Meta+')):
        if mod:
            modifiers += ch

    if keyname is None:
        if 27 < keycode < 256:
            keyname = chr(keycode)
        else:
            keyname = "(%s)unknown" % keycode
    return modifiers + keyname

def _spl(st):
    if '\t' in st:
        return st.split('\t', 1)
    return st, ''

def AddColors(col1, col2):
    col = [0,0,0,0,0,0]
    for i in range(len(col1)):
        col[i] = col1[i] + col2[i]
    return col

def TryTabCompletion(text, output):
    text = text.strip()
    setpathhome()

    if text == "":
        path = os.path.abspath("")
        file = ""
    elif text == "/":
        path = ""
        file = ""
    elif text == ".":
        path = os.path.abspath("")
        file = "."
    else:
        if text[-1] == "/":
            text = os.path.abspath(text) + "/"
        elif text[-2:] == "/.":
            test = os.path.abspath(text) + "/."
        else:
            text = os.path.abspath(text)
        path = os.path.dirname(text)
        file = os.path.basename(text)

        if path == "/":
            path = ""

    #print "path", path
    #print "file", file

    s = path + "/" + file + "*"
    #print s
    names = glob.glob(s)
    names = sorted(names, lambda a, b: cmp(a.lower(), b.lower()))
    names = [i for i in names if os.path.isdir(i)] + [i for i in names if not os.path.isdir(i)]

    numfound = len(names)
    match = os.path.commonprefix(names)
    if len(file) == 0:
        match = path + '/'
    elif numfound == 1 and os.path.isdir(match):
        output = []
        return TryTabCompletion(match + "/", output)

    output.append([20,20,20,255,255,255])
    output.append(u"Matching:\n")
    output.append([0,20,150,255,255,255])
    output.append(u"%-80s [%d found]\n\n" % (s, len(names)))
    for i in range(numfound):
        if os.path.isdir(names[i]):
            colFG = [0,180,0,0,0,0]
        else:
            colFG = [0,0,0,0,0,0]

        colBG = [0, 0, 0, 255-((i%2)*15), 255-((i%2)*15), 255]
        colHL = [0, 0, 0, 255, 200, 200]

        index = len(match)
        if index < len(names[i]):
            output.append(AddColors(colFG, colBG))
            output.append(unicode(names[i][:index]))
            output.append(AddColors(colFG, colHL))
            output.append(unicode(names[i][index]))
            output.append(AddColors(colFG, colBG))
            output.append(unicode(names[i][index+1:]) + u"\n")
        else:
            output.append(AddColors(colFG, colBG))
            output.append(unicode(names[i]) + u"\n")

    if numfound > 0 and len(file) > 0:
        return (match, output, numfound)
    else:
        return (text, output, numfound)


def Launch(cmd, filename): # {{{
    filename2 = filename.replace('#', '%23')
    cmd = cmd.replace('$$$$$$', filename)
    cmd = cmd.replace('$$##$$', filename2)
    cmd = cmd.replace('""', '')
    cmd = cmd.strip()
    print "Launching: '" + cmd + "'"
    os.system(cmd)

    """
    pid = os.fork()
    if pid == 0:
        # child
        print "Child " + str(pid) + ": done"
        sys.exit(0)
        #os._exit(0)
    else:
        # parent
        print "Parent " + str(pid) + ": launching '" + cmd + "'"
        os.system(cmd)
        print "Parent: done"
    """
#}}}


class MainFrame(wx.Frame):#{{{1
    def __init__(self):#{{{2
        wx.Frame.__init__(self, None, -1, "Launcher")
        self.CreateStatusBar()
        #ctrl = self.ctrl = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.WANTS_CHARS|wx.TE_RICH2)
        #ctrl.SetFocus()


        self.prompt = '>>> '

        self.output = wx.TextCtrl(self, 1, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        self.input = wx.TextCtrl(self, 1, style=wx.TE_PROCESS_ENTER)
        self.input.Bind(wx.EVT_KEY_DOWN, self.KeyPressed, self.input)
        #self.input.Bind(wx.EVT_TEXT, self.CmdLineChanged, self.input)

        # layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.output, 1, wx.EXPAND)
        self.vbox.Add(self.input, 0, wx.EXPAND)
        self.SetSizer(self.vbox)
        self.SetAutoLayout(1)
        self.Show()

        # events
        #self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        #self.input.Bind(wx.EVT_KEY_DOWN, self.OnChar)
        self.input.WriteText(self.prompt)

        # misc
        self.input.SetFocus()
        self.input.SetSelection(4,4)

        self.SetSize((800, 600))
        self.Centre()

        self.builtins, self.commands = OpenConfigFile()
        self.mode = 'std'

        self.display = [u"Hallo", [0,0,250,255,255,255], u"\ndu"]
        self.fontsize = 10
        self.SetFontSize()

        self.Show(True)
#}}}2
    def SetFontSize(self):
        font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        self.output.SetFont(font)
        self.input.SetFont(font)
        self.PrintText()
        intxt = self.input.GetValue()
        self.input.Clear()
        self.input.WriteText(intxt)

    def PrintText(self):
        #print self.display
        self.output.Clear()
        for i in self.display:
            if type(i) == type(u""):
                self.output.WriteText(i)
            else:
                col1 = wx.Colour(i[0], i[1], i[2])
                col2 = wx.Colour(i[3], i[4], i[5])
                dastyle = wx.TextAttr()
                dastyle.SetTextColour(col1)
                dastyle.SetBackgroundColour(col2)
                self.output.SetDefaultStyle(dastyle)
        self.output.ShowPosition(0)

    def UpdateTabCompletion(self, completemode):
        self.display = []
        oldline = self.input.GetValue()[len(self.prompt):]
        print "trying to complete", oldline
        newline, self.display, numfound = TryTabCompletion(oldline, self.display)
        print "                ->", newline
        self.PrintText()

        if completemode == 0:
            newline = self.prompt + newline
        elif completemode >= 1:
            newline = self.prompt + oldline
        """
        elif completemode == 2:
            search = oldline
            oldnum = numfound
            print numfound
            newline = oldline
            while len(search) > 0 and oldnum == numfound:
                print "seaching:", search
                search = search[:-1]
                self.display = []
                newline, self.display, numfound = TryTabCompletion(search, self.display)
                print numfound, oldnum
            self.PrintText()
            newline = self.prompt + newline
        """
        #print newline
        #print len(newline)
        #self.input.ChangeValue(newline)
        #self.input.SetInsertionPointEnd()
        self.input.Clear()
        self.input.WriteText(newline)

        """
        if newline != cmdline:
            pos = len(self.input.GetValue()) - self.input.GetInsertionPoint()
            #print "old pos", pos
            newline = self.prompt + newline

            self.input.ChangeValue(newline)
            self.input.SetInsertionPoint(len(newline))
            #print "newlinelength", len(newline)
            #print "num found", numfound

        if numfound > 0:
            self.input.SetInsertionPoint(len(newline) - 1)
        else:
            if pos <= len(self.prompt):
                self.input.SetInsertionPoint(len(self.prompt) + 1)
            else:
                self.input.SetInsertionPoint(len(newline) - pos)
        """

    def CmdLineChanged(self, evt):
        cmdline = self.input.GetValue()
        cmdline = cmdline[len(self.prompt):]
        #if len(cmdline) <= len(self.prompt):
        #    cmdline = ''
        #else:
        #    cmdline = cmdline[len(self.prompt):len(cmdline)]
        print "ungestrippt:    '" + self.input.GetValue() + "'"
        print "calling update: '" + cmdline + "'"
        print len(self.prompt)
        print len(self.input.GetValue())
        #self.UpdateTabCompletion(cmdline)

    def KeyPressed(self, evt):
        key = GetKeyPress(evt)
        keycode = evt.GetKeyCode()
        print key
        self.SetStatusText(key)
        cmdline = self.input.GetValue()[len(self.prompt):]
        #print cmdline

        completemode = 0

        if keycode == wx.WXK_ESCAPE:
            self.input.Clear()
            self.input.WriteText(self.prompt)
        elif keycode == wx.WXK_TAB:
            None
        elif keycode == wx.WXK_LEFT:
            if self.input.GetInsertionPoint() == 4:
                return
        elif keycode == wx.WXK_BACK:
            if len(cmdline) > 0 and cmdline[-1] == '/':
                index = cmdline[:-1].rfind('/')
                if index >= 0:
                    self.input.Clear()
                    cmdline = cmdline[:index] + '/'
                    self.input.WriteText(self.prompt + cmdline)
                else:
                    evt.Skip()
                completemode = 1
            elif self.input.GetInsertionPoint() > 4:
                evt.Skip()
                completemode = 2
        elif keycode == wx.WXK_HOME:
            self.input.SetInsertionPoint(4)
        elif self.commands.has_key(key):
            global g_tolaunch
            global g_filename
            g_tolaunch = self.commands[key]
            g_filename = cmdline
            self.Close()
        else:
            for cmd, hotkey in self.builtins.items():
                if key == hotkey:
                    if cmd == 'ZoomIn':
                        self.fontsize += 1
                        self.SetFontSize()
                    if cmd == 'ZoomOut':
                        self.fontsize -= 1
                        self.SetFontSize()

            evt.Skip()

        wx.CallAfter(self.UpdateTabCompletion, completemode)

#}}}1
def threechars(i):
    s = str(i)
    if len(s) == 1:
        return "00" + s
    elif len(s) == 2:
        return "0" + s
    else:
        return s

def SaveConfigFile(builtins, commands):
    newcfg = ConfigParser.RawConfigParser()

    newcfg.add_section('TopLevel')
    i = 0
    for key, cmd in commands.items():
        num = threechars(i)
        newcfg.set('TopLevel', num + '_key', key)
        newcfg.set('TopLevel', num + '_cmd', cmd)
        i += 1

    newcfg.add_section('TopLevelBuiltinCmds')
    for cmd, key in builtins.items():
        newcfg.set('TopLevelBuiltinCmds', cmd, key)

    cfgfile = open('settings.cfg', 'wb')
    newcfg.write(cfgfile)
    cfgfile.close()


def OpenConfigFile():
    setpathscript()

    builtins = {}
    commands = {}

    builtins['EditTopLevel'] = 'Alt+Meta+E'
    builtins['EditDirectories'] = 'Alt+Meta+D'
    builtins['ZoomIn'] = 'Ctrl+Meta+NUMPAD_ADD'
    builtins['ZoomOut'] = 'Ctrl+Meta+NUMPAD_SUBTRACT'
    commands['Ctrl+Alt+Meta+A'] = 'audacious -e -p "$$##$$"'
    commands['Ctrl+Alt+Meta+G'] = 'gvim "$$$$$$"'

    if not os.path.exists('settings.cfg'):
        SaveConfigFile(builtins, commands)

    config = ConfigParser.RawConfigParser()
    config.read('settings.cfg')

    if config.has_section('TopLevel'):
        i = 0
        while config.has_option('TopLevel', threechars(i) + "_key"):
            key = config.get('TopLevel', threechars(i) + "_key")
            cmd = config.get('TopLevel', threechars(i) + "_cmd")
            commands[key] = cmd
            i += 1

    if config.has_section('TopLevelBuiltinCmds'):
        for key in builtins.keys():
            if config.has_option('TopLevelBuiltinCmds', key):
                builtins[key] = config.get('TopLevelBuiltinCmds', key)

    SaveConfigFile(builtins, commands)

    print commands
    print builtins

    return (builtins, commands)


g_tolaunch = ''
g_filename = ''

if __name__ == '__main__':
    gen_keymap()
    app = wx.PySimpleApp()
    frame = MainFrame()
    app.MainLoop()
    if g_tolaunch != '':
        Launch(g_tolaunch, g_filename)





"""
Good to know:
    decorte - sort - undercorate is much faster than a manual search of the string with the shortest lenght

files = [pair[1] for pair in sorted((len(fi), fi) for fi in files)]
"""

"""sp = text.split("/")
path = ''

print "split:", sp

if len(text) == 0:
    return ''
    #path += '~/'
elif sp[0] == '':
    path += '/'
    sp = sp[1:]
elif sp[0] == '~':
    path += '~/'
    sp = sp[1:]
else:
    path += '~/'

if len(text) > 0 and sp[-1] == '':
    if len(sp) > 1:
        path += '/'.join(sp[:-1]) + '/'
    searchname = ''
else:
    if len(sp) > 1:
        path += '/'.join(sp[:-1]) + '/'
    searchname = sp[-1]

print "Search Path:", path
print "Search Name:", searchname
print " ->", path + searchname

if len(searchname) > 0 and searchname[0] == ".":
    lsopt = "A"
else:
    lsopt = ""

output.Clear()
output.WriteText("Matching: " + path + searchname + "\n")
put, get = os.popen4('ls -l' + lsopt + ' --group-directories-first --quoting-style=c "' + path + '"')
matchlist = []
for lines in get.readlines():
    cols = lines.split('"')
    if len(cols) >= 3:
        filename = unicode(cols[1], errors='replace')
        if filename.find(searchname) == 0:
            matchlist.append(filename)
            output.WriteText(str(lines))

longestmatch = os.path.commonprefix(matchlist)
print longestmatch

if len(matchlist) == 1 and os.path.isdir(path + longestmatch):
    longestmatch += '/'
    return TryTabCompletion(path + longestmatch, output)
elif len(matchlist) == 0:
    return text
else:
    return path + longestmatch
"""

