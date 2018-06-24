# encoding=utf-8
#!/usr/bin/python
'''
This Rocks
'''

# Import Statements {{{
import wx
import time
import os
import sys
import ConfigParser
import glob
import re
# }}}

# Helper: Path Change {{{ 
relpath = os.path.dirname(sys.argv[0])
g_scriptpath = os.path.abspath(relpath)

def setpathscript():
    """
    Change path to script directory
    """
    os.chdir(g_scriptpath)
    return g_scriptpath

def setpathhome():
    """
    Change path to home directory
    """
    os.chdir(os.path.expanduser("~"))

# }}}

# Helper: TranslateKey {{{
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

def TranslateKey(evt):
    keycode = evt.GetKeyCode()
    keyname = keyMap.get(keycode, None)
    modifiers = u""
    for mod, ch in ((evt.ControlDown(), 'Ctrl+'),
                    (evt.AltDown(),     'Alt+'),
                    (evt.ShiftDown(),   'Shift+'),
                    (evt.MetaDown(),    'Meta+')):
        if mod:
            modifiers += ch

    if keyname is None:
        #print keycode
        if 27 < keycode < 256:
            keyname = chr(keycode).decode('latin_1')
        else:
            keyname = "(%s)unknown" % keycode
    return modifiers + keyname
# }}}

# Helper: Misc {{{

def AddColors(col1, col2):
    col = [0,0,0,0,0,0]
    for i in range(len(col1)):
        col[i] = col1[i] + col2[i]
    return col

def threechars(i):
    s = str(i)
    if len(s) == 1:
        return "00" + s
    elif len(s) == 2:
        return "0" + s
    else:
        return s

def SortTuples(items, num):
    l = items
    if num == 0:
        l = [[a,b] for a,b in items]
        l = sorted(l)
        l = [(a,b) for a,b in l]
    else:
        l = [[b,a] for a,b in items]
        l = sorted(l)
        l = [(b,a) for a,b in l]
    return l

# }}}

def TryTabCompletion(text, output): # {{{
    #text = text.strip()
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
    names = [i for i in names if not os.path.isdir(i)]

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
    checkdir = os.path.isdir
    for i in range(numfound):
        isdir = checkdir(names[i])
        if isdir:
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

        if isdir:
            names[i] += '/'

    if numfound > 0 and len(file) > 0:
        return (match, output, names, numfound, path + '/')
    elif len(file) == 0:
        return (path + '/', output, names, numfound, path + '/')
    else:
        return (text, output, names, numfound, path + '/')
# }}}

def Launch(cmd, filename): # {{{
    cmd = cmd.replace('$$$$$$', filename)
    cmd = cmd.replace('$$##$$', filename.replace('#', '%23'))
    cmd = cmd.replace('$$$$$/', os.path.dirname(filename))
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
# }}}

class MainFrame(wx.Frame):                                  # {{{
    def __init__(self):                                     # {{{
        wx.Frame.__init__(self, None, -1, "Launcher")
        self.CreateStatusBar()
        wx.EVT_CLOSE(self, self.OnClose)


        # load settings
        self.builtins, self.hotkeys, self.commands, self.locations, self.path, self.editorname, self.lastpath = ConfigOpen()
        self.filelist = []
        self.fontsize = 10
        print self.hotkeys

        # create the UI elements ...
        self.output = wx.TextCtrl(self, 1, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)   # wx.WANTS_CHARS | wx.TE_RICH2
        self.input = wx.TextCtrl(self, 1, style = wx.TE_PROCESS_ENTER)
        self.input.Bind(wx.EVT_KEY_DOWN, self.KeyPressed, self.input)
        self.output.Bind(wx.EVT_LEFT_DOWN, self.MouseClick, self.output)
        #self.input.Bind(wx.EVT_TEXT, self.CmdLineChanged, self.input)

        # ... do the layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.output, 1, wx.EXPAND)
        self.vbox.Add(self.input, 0, wx.EXPAND)
        self.SetSizer(self.vbox)
        self.SetAutoLayout(1)

        # ... and adjust the window size
        self.SetSize((1200, 800))
        self.Centre()
        self.Show(True)

        # init prompt
        self.prompt = '>>> '
        self.input.WriteText(self.prompt)
        self.input.SetFocus()
        self.input.SetSelection(len(self.prompt), len(self.prompt))

        # init mode std
        self.mode = 'welcome'
        self.SwitchMode('welcome')
        self.MainScreen = True

        # finally print textctrl content
        self.SetFontSizeAndPrintText()
        self.Raise()

    # }}}
    def OnClose(self, event):                               # {{{
        ConfigSaveLastPath(self.lastpath)
        event.Skip()
    # }}}
    def CreateNewLocation(self, newname):                   # {{{
        if len(newname) > 0:
            print 'adding', newname, ' -> ', self.cmdlinebackup[len(self.prompt):]
            self.locations[newname] = self.cmdlinebackup[len(self.prompt):]
            ConfigSaveLocations(self.locations)
        self.SwitchMode('locations')
    # }}}
    def SwitchMode(self, name, initcmd = ''):               # {{{

        oldmode = self.mode
        self.mode = name

        if name == 'welcome':
            self.SetStatusText('Normal Mode (File Completion)')
            self.display = []

            self.display.append(u"Builtin Shortcuts:\n\n")
            for cmd, hotkey in SortTuples(self.builtins.items(), 0):
                self.display.append(u"%-30s -> %-30s\n" % (cmd, hotkey))

            self.display.append(u"\n\nLaunch Shortcuts:\n\n")
            for hotkey, cmd in SortTuples(self.hotkeys.items(), 1):
                self.display.append(u"%-30s -> %-30s\n" % (cmd[1], hotkey))

            self.input.Clear()
            self.input.WriteText(self.prompt)

            self.PrintText()

        elif name == 'std':
            self.SetStatusText('Normal Mode (File Completion)')

            self.input.Clear()
            self.input.WriteText(self.prompt + initcmd)

            # für std muss print text manuell aufgerufen werden (weil completion erwünscht)
            # die anderen machen das in List...
            #self.PrintText()

        elif name == 'displaykeys':
            self.SetStatusText('Display Key Codes (press <ESC> to return to Normal Mode)')
            self.display = []
            self.PrintText()
            self.input.Clear()
            self.input.WriteText(self.prompt)

        elif name == 'commands':
            self.SetStatusText('Command Mode (press <ESC> to return to Normal Mode)')
            if oldmode != 'question':
                self.cmdlinebackup = self.input.GetValue()
            self.input.Clear()
            self.input.WriteText(self.prompt)
            self.ListCommands()

        elif name == 'locations':
            self.SetStatusText('Location Mode (press <ESC> to return to Normal Mode)')
            if oldmode != 'question':
                self.cmdlinebackup = self.input.GetValue()
            self.input.Clear()
            self.input.WriteText(self.prompt)
            self.ListLocations()

        elif name == 'question':
            self.ModeBeforeQuestion = oldmode
            self.input.Clear()
            self.input.WriteText(self.prompt)

            # um display / printtext muss sich der aufrufer selbst kuemmern
            # da die frage ja unterschiedlich sein soll

        elif name == 'displaykeys':
            self.input.Clear()
            self.input.WriteText(self.prompt)

    # }}}
    def SetFontSizeAndPrintText(self):                      # {{{
        font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Monospace')
        #font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        self.output.SetFont(font)
        self.input.SetFont(font)
        self.PrintText()
        # vielleicht sollte man sich den Insertion Point merken?
        intxt = self.input.GetValue()
        self.input.Clear()
        self.input.WriteText(intxt)
        self.Layout()
    # }}}
    def PrintText(self):                                    # {{{
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
    # }}}
    def ListCommands(self):                         # {{{
        cmdline = self.input.GetValue()[len(self.prompt):]
        self.display = []
        self.display.append(u"Commands:\n\n")
        #allcmds = SortTuples(self.commands.items(), 0)
        #names = [a for a, b in allcmds]
        #entries = [b for a, b in allcmds]
        #commonpref = os.path.commonprefix(names + [cmdline])
        for name, (cmd, descr) in SortTuples(self.commands.items(), 0):
            if name.find(cmdline) == 0:
                self.display.append(u"%-30s -> %-30s\n" % (name, descr))

        self.PrintText()

    # }}}
    def ListLocations(self):                         # {{{
        cmdline = self.input.GetValue()[len(self.prompt):]
        self.display = []
        self.display.append(u"Locations:\n\n")
        for name, path in SortTuples(self.locations.items(), 0):
            if name.find(cmdline) == 0:
                self.display.append(u"%-30s -> %-30s\n" % (name, path))

        self.PrintText()

    # }}}
    def UpdateTabCompletion(self, completemode):            # {{{
        self.display = []
        oldline = self.input.GetValue()[len(self.prompt):]
        newline, self.display, self.filelist, numfound, path = TryTabCompletion(oldline, self.display)

        #print completemode
        #print "oldline", oldline
        #print "newline", newline
        #print "path", path

        if oldline != '' or completemode == 0:
            self.lastpath = path
        self.MainScreen = False
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
    # }}}
    def CmdLineChanged(self, evt):                          # {{{
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
    # }}}
    def KeyPressed(self, evt):                              # {{{
        keycode = evt.GetKeyCode()
        keyname = TranslateKey(evt)
        cmdline = self.input.GetValue()[len(self.prompt):]

        # print keyname
        if self.mode == 'displaykeys':
            self.KeyPressed_DisplayKeys(evt, keycode, keyname)
            return
        elif self.mode == 'question':
            self.KeyPressed_Question(evt, keycode, keyname)
            return

        docompletion = True
        completemode = 0
        global g_tolaunch
        global g_filename

        # key: esc
        if keycode == wx.WXK_ESCAPE:
            if self.mode == 'welcome':
                # restore the old path and complete
                self.SwitchMode('std', self.lastpath)
                docompletion = True

            elif self.mode == 'std':
                self.SwitchMode('welcome')
                docompletion = False

            elif self.mode == 'commands':
                if self.cmdlinebackup == self.prompt:
                    self.cmdlinebackup = self.prompt + self.lastpath
                self.SwitchMode('std', self.cmdlinebackup[len(self.prompt):])
                docompletion = True

            elif self.mode == 'locations':
                if self.cmdlinebackup == self.prompt:
                    self.cmdlinebackup = self.prompt + self.lastpath
                self.SwitchMode('std', self.cmdlinebackup[len(self.prompt):])
                docompletion = True
        elif keycode == wx.WXK_TAB:
            if self.mode == 'commands':
                matchlist = []
                for name, path in SortTuples(self.commands.items(), 0):
                    if name.find(cmdline) == 0:
                        matchlist.append(name)
                self.input.Clear()
                self.input.WriteText(self.prompt + os.path.commonprefix(matchlist))
            if self.mode == 'locations':
                matchlist = []
                for name, path in SortTuples(self.locations.items(), 0):
                    if name.find(cmdline) == 0:
                        matchlist.append(name)
                self.input.Clear()
                self.input.WriteText(self.prompt + os.path.commonprefix(matchlist))
        # key: left
        elif keycode == wx.WXK_LEFT:
            if self.input.GetInsertionPoint() == 4:
                return
            evt.Skip()
            docompletion = False
        # key: back
        elif keycode == wx.WXK_BACK:
            completemode = 1
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
        # key: home
        elif keycode == wx.WXK_HOME:
            self.input.SetInsertionPoint(4)
        # key: return
        elif keyname == 'Meta+RETURN':
            if self.mode == 'commands':
                None
            elif self.mode == 'locations':
                if self.locations.has_key(cmdline):
                    self.SwitchMode('std', self.locations[cmdline])
                    docompletion = True
        # detect a user hotkey
        elif self.hotkeys.has_key(keyname):
            g_tolaunch = self.hotkeys[keyname][0]
            g_filename = cmdline
            self.Close()
        # handle copy & paste
        elif keyname == "Ctrl+Meta+C":
            data = wx.TextDataObject()
            data.SetText(cmdline)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(data)
                wx.TheClipboard.Close()
        # capture non printing characters
        elif keyname == 'Meta+':
            docompletion = False
        else:
            # search the builtin commands for a matching key
            for cmd, hotkey in self.builtins.items():
                if keyname == hotkey:
                    print "Builtin Command detected:", cmd
                    if cmd == 'ZoomIn':
                        self.fontsize += 1
                        self.SetFontSizeAndPrintText()
                    elif cmd == 'ZoomOut':
                        self.fontsize -= 1
                        self.SetFontSizeAndPrintText()
                    elif cmd == 'DisplayKeycodes':
                        self.SwitchMode('displaykeys')
                        return
                    elif cmd == 'EditSettings':
                        g_tolaunch = self.editorname
                        g_filename = self.path + '/settings.cfg'
                        self.Close()
                    elif cmd == 'Commands':
                        self.SwitchMode('commands')
                    elif cmd == 'Locations':
                        if self.mode != 'locations':
                            self.SwitchMode('locations')
                        else:
                            self.OnQuestionDone = self.CreateNewLocation
                            self.SwitchMode('question')
                            self.display = [u'New Location:\n\n' + self.cmdlinebackup[len(self.prompt):] + '\n\nType a name...']
                            self.PrintText()

            evt.Skip()

        if docompletion == True:
            # first switch to std if in welcome
            if self.mode == 'welcome':
                self.SwitchMode('std')
            # call the approriate completions
            if self.mode == 'std':
                wx.CallAfter(self.UpdateTabCompletion, completemode)
            elif self.mode == 'commands':
                wx.CallAfter(self.ListCommands)
            elif self.mode == 'locations':
                wx.CallAfter(self.ListLocations)
    # }}}
    def KeyPressed_DisplayKeys(self, evt, keycode, keyname):# {{{
        self.output.WriteText(unicode(keyname) + u'\n')

        if keycode == wx.WXK_ESCAPE:
            self.SwitchMode('welcome')
            return
    # }}}
    def KeyPressed_Question(self, evt, keycode, keyname):   # {{{

        cmdline = self.input.GetValue()[len(self.prompt):]

        if keycode == wx.WXK_ESCAPE:
            self.SwitchMode(self.ModeBeforeQuestion)
            return
        # key: left
        elif keycode == wx.WXK_LEFT:
            if self.input.GetInsertionPoint() == len(self.prompt):
                return
            else:
                evt.Skip()
        # key: back
        elif keycode == wx.WXK_BACK:
            if self.input.GetInsertionPoint() == len(self.prompt):
                return
            else:
                evt.Skip()
        # key: home
        elif keycode == wx.WXK_HOME:
            self.input.SetInsertionPoint(4)
        # key: return
        elif keycode == wx.WXK_RETURN:
            self.OnQuestionDone(cmdline)
        else:
            evt.Skip()
    # }}}
    def MouseClick(self, evt):                              # {{{
        pos = evt.GetPosition()
        a, x, y = self.output.HitTest(pos)
        evt.Skip()
        wx.CallAfter(self.MouseClickAfter, y, self.input.GetValue())
    # }}}
    def MouseClickAfter(self, row, oldcmdline):             # {{{
        self.input.SetFocus()
        row -= 3
        if row >= 0 and row < len(self.filelist):
            self.input.Clear()
            self.input.WriteText(self.prompt + self.filelist[row])
            self.UpdateTabCompletion(0)
        else:
            self.input.Clear()
            self.input.WriteText(oldcmdline)

    # }}}
# }}}

# Config File Handling {{{

def ConfigSort():
    cfgfile = open('settings.cfg', 'r')
    text = cfgfile.read()
    cfgfile.close()

    p = re.compile('^\[', flags=re.MULTILINE)
    s = sorted(re.split(p, text))
    for i in range(len(s)):
        if s[i] != '':
            lines = s[i].split('\n')
            lines = filter(lambda x: x != '', lines)
            lines = [lines[0], ''] + sorted(lines[1:]) + ['', '', '']
            s[i] = "\n".join(lines)

    text = "[".join(s)
    cfgfile = open('settings.cfg', 'wb')
    cfgfile.write(text)
    cfgfile.close()


def ConfigSaveLastPath(lastpath):
    path = setpathscript()

    config = ConfigParser.RawConfigParser()
    config.read('settings.cfg')

    if not config.has_section('Misc'):
        config.add_section('Misc')

    config.set('Misc', 'lastpath', lastpath)

    cfgfile = open('settings.cfg', 'wb')
    config.write(cfgfile)
    cfgfile.close()

    ConfigSort()


def ConfigSaveLocations(locations):
    path = setpathscript()

    config = ConfigParser.RawConfigParser()
    config.read('settings.cfg')

    if not config.has_section('Locations'):
        config.add_section('Locations')

    i = 0
    for name, path in SortTuples(locations.items(), 0):
        print 'saving location', name, 'with path', path
        config.set('Locations', threechars(i) + '_name', name)
        config.set('Locations', threechars(i) + '_path', path)
        i += 1


    cfgfile = open('settings.cfg', 'wb')
    config.write(cfgfile)
    cfgfile.close()

    ConfigSort()


def ConfigGenerate(builtins):
    newcfg = ConfigParser.RawConfigParser()

    newcfg.add_section('Builtin')
    for cmd, key in builtins.items():
        newcfg.set('Builtin', cmd, key)

    newcfg.add_section('Hotkeys')
    newcfg.set('Hotkeys', '000_key', 'Ctrl+Alt+Meta+A')
    newcfg.set('Hotkeys', '000_cmd', 'audacious -e -p "$$##$$"')
    newcfg.set('Hotkeys', '000_descr', 'Audacious (enqueue)')

    newcfg.add_section('Commands')
    newcfg.set('Commands', '000_name', 'm')
    newcfg.set('Commands', '000_cmd', 'mplayer -loop 0 "$$$$$$"')
    newcfg.set('Commands', '000_descr', 'mplayer (looped)')

    newcfg.add_section('Locations')
    newcfg.set('Locations', '000_name', 'h')
    newcfg.set('Locations', '000_path', '/home/')

    newcfg.add_section('Misc')
    newcfg.set('Misc', 'editorname', 'gvim "$$$$$$"')

    cfgfile = open('settings.cfg', 'wb')
    newcfg.write(cfgfile)
    cfgfile.close()

    ConfigSort()


def ConfigOpen():
    scriptpath = setpathscript()

    builtins = {}
    hotkeys = {}
    commands = {}
    locations = {}

    # set the (minimum) default values
    builtins['Commands'] = 'Alt+Meta+C'
    builtins['Locations'] = 'Alt+Meta+D'
    builtins['ZoomIn'] = 'Ctrl+Meta+NUMPAD_ADD'
    builtins['ZoomOut'] = 'Ctrl+Meta+NUMPAD_SUBTRACT'
    builtins['DisplayKeycodes'] = 'Ctrl+Meta+F12'
    builtins['EditSettings'] = 'Alt+Meta+RETURN'
    editorname = 'gvim "$$$$$$"'
    lastpath = ''

    # and initialize a config file if there isn't any
    if not os.path.exists('settings.cfg'):
        ConfigGenerate(builtins)

    # now there must be a config, so we can load it
    config = ConfigParser.RawConfigParser()
    config.read('settings.cfg')

    # and replace the default keys by the values in the config
    if config.has_section('Builtin'):
        for key in builtins.keys():
            if config.has_option('Builtin', key):
                builtins[key] = config.get('Builtin', key)

    # now the user defined stuff

    if config.has_section('Hotkeys'):
        i = 0
        while (config.has_option('Hotkeys', threechars(i) + "_key") and
               config.has_option('Hotkeys', threechars(i) + "_cmd") and
               config.has_option('Hotkeys', threechars(i) + "_descr")):
            key = config.get('Hotkeys', threechars(i) + "_key")
            cmd = config.get('Hotkeys', threechars(i) + "_cmd")
            descr = config.get('Hotkeys', threechars(i) + "_descr")
            hotkeys[unicode(key.decode('utf-8'))] = (unicode(cmd), unicode(descr))
            i += 1

    if config.has_section('Commands'):
        i = 0
        while (config.has_option('Commands', threechars(i) + "_name") and
               config.has_option('Commands', threechars(i) + "_cmd") and
               config.has_option('Commands', threechars(i) + "_descr")):
            name = config.get('Commands', threechars(i) + "_name")
            cmd = config.get('Commands', threechars(i) + "_cmd")
            descr = config.get('Commands', threechars(i) + "_descr")
            commands[name] = (cmd, descr)
            i += 1

    if config.has_section('Locations'):
        i = 0
        while (config.has_option('Locations', threechars(i) + "_name") and
               config.has_option('Locations', threechars(i) + "_path")):
            name = config.get('Locations', threechars(i) + "_name")
            path = config.get('Locations', threechars(i) + "_path")
            locations[name] = path
            i += 1

    if config.has_section('Misc'):
        if config.has_option('Misc', 'editorname'):
            editorname = config.get('Misc', 'editorname')
        if config.has_option('Misc', 'lastpath'):
            lastpath = config.get('Misc', 'lastpath')

    #print builtins
    #print hotkeys
    #print commands
    #print locations

    return (builtins, hotkeys, commands, locations, scriptpath, editorname, lastpath)
# }}}

g_tolaunch = ''
g_filename = ''


if __name__ == '__main__':
    gen_keymap()
    app = wx.PySimpleApp()
    frame = MainFrame()
    app.MainLoop()
    if g_tolaunch != '':
        Launch(g_tolaunch, g_filename)

# Old Code {{{

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

# }}}
