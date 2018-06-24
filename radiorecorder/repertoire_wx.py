#!/usr/bin/python
# -*- encoding=utf-8
'''
This Rocks
'''

# Imports
import wx
import time
import os
import sys
import ConfigParser
import glob
import re
import pickle
import locale
locale.setlocale(locale.LC_ALL,"")

def labels2str(labels):
    return ';;'.join(['->'.join(l) for l in labels])

def labelstr2list(s):
    labels = s.split(';;')
    ret = []
    for s in labels:
        s = s.lstrip('"').rstrip('"')
        l = s.split('"->"')
        ret.append(l)
    return ret
   
def cmp_label_list(tocheck, must):
    for i in range(len(must)):
        if i >= len(tocheck):
            return False
        else:
            if must[i] != tocheck[i]:
                return False    
    return True

class Label():
    def __init__(self, name, parent):
        self.name = name
        self.sublabels = []
        if parent == None:
            self.parent = self
        else:
            self.parent = parent

    def makelist(self):
        return [self.fullname()] + reduce(list.__add__, [sub.makelist() for sub in self.sublabels], [])
            
    def fullname(self):
        if self.parent != self:
            return self.parent.fullname() + [self.name]
        else:
            return [self.name]
        
    def has_label(self, searchfor):
        sl_names = [sl.name for sl in self.sublabels]
        try:
            ret = sl_names.index(searchfor)
            return ret
        except:
            return -1

    def add_sublabel(self, name):
        if not name in set([l.name for l in self.sublabels]):
            self.sublabels.append(Label(name, self))
        return self.sublabels[-1]
    
    def add_sublabel_recursive(self, names, newname):
        
        curlabel = self
        for name in names:
            label_index = curlabel.has_label(name)
            if label_index != -1:
                curlabel = curlabel.sublabels[label_index]
                # print curlabel.name.encode('utf-8')
            else:
                print 'error - could not add sublabel: %s is not a children of %s' % (name, curlabel.name)
                return
        curlabel.add_sublabel(newname)

    def delete(self, name):
        label_index = self.has_label(name)
        if label_index != -1:
            del self.sublabels[label_index]
        else:
            print 'error - could not delete sublabel: %s is not a children of %s' % (name, root.name)
            return

    def delete_recursive(self, todelete):
        root = self
        for name in todelete:
            label_index = root.has_label(name)
            if label_index != -1:
                root = root.sublabels[label_index]
                # print root.name.encode('utf-8')
            else:
                print 'error - could not delete sublabel: %s is not a children of %s' % (name, root.name)
                return
        root.parent.delete(todelete[-1])

    def parent(self):
        return self.parent

    def child(self, name):
        subs = [i.name for i in self.sublabels]
        try:
            index = subs.index(name)
            return self.sublabels[index]
        except:
            return self
    
    def fill_tree_ctrl(self, root, tree):
        # print 'sorted:', [x.name for x in sorted(self.sublabels, cmp=lambda x,y: locale.strcoll(x.name, y.name))]
        for sub in sorted(self.sublabels, cmp=lambda x,y: locale.strcoll(x.name, y.name)):
            # print sub.name.encode('utf-8')
            newroot = tree.AppendItem(root, sub.name)
            sub.fill_tree_ctrl(newroot, tree)

    def SaveLabels(self):
        print 'Saving Labels...'
        output = self.makelist()
        output = [x[1:] for x in output if len(x)>1]
        pickle.dump(output, open('labels.dat', 'w'))
    
    def LoadLabels(self):
        print 'Loading Labels...'
        input = pickle.load(open('labels.dat', 'r'))
        for label in input:
            for i in range(len(label)):
                self.add_sublabel_recursive(label[0:i], label[i])

# Helper: TranslateKey
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


class MainFrame(wx.Frame):                                  # {{{
    def __init__(self):                                     # {{{
        wx.Frame.__init__(self, None, -1, "Launcher")
        wx.EVT_CLOSE(self, self.OnClose)

        # load settings
        self.fontsize = 8
        all_songs = sorted(config_songs.sections())
        all_songs = [n.decode('utf-8') for n in all_songs]
        
        labels = Label(u'All', None)
        labels.LoadLabels()
        self.songdict = LoadSongDictionary()
        #SaveSongDictionary(self.songdict)
        #SaveSongLabels(all_songs, all_songs_label)
        
        self.labels = labels

        # status bar
        self.sb = self.CreateStatusBar(2)
        self.sb.SetStatusWidths([600, -1]) # positiv = absolut, negativ = relativ mode
        
        # create the UI elements ...
        self.panel1 = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        self.panel2 = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
    
        self.list = wx.ListCtrl(self.panel2, 1, style = wx.LC_REPORT)
        self.list.InsertColumn(0, 'Name')
        self.list.InsertColumn(1, 'Labels')
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.On_Play)
        self.input = wx.TextCtrl(self, 1, style = wx.TE_PROCESS_ENTER)
        #self.input.Bind(wx.EVT_KEY_DOWN, self.KeyPressed, self.input)
        #self.list.Bind(wx.EVT_LEFT_DOWN, self.MouseClick, self.list)
        #self.input.Bind(wx.EVT_TEXT, self.CmdLineChanged, self.input)
        #self.tree = wx.TreeCtrl(self, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        #self.tree = wx.TreeCtrl(self.panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT)
        self.tree = wx.TreeCtrl(self.panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        self.UpdateLables()
        
        # buttons
        self.btn_AddLabel = wx.Button(self.panel1, wx.ID_ANY, label='Add Label')
        self.btn_AddLabel.Bind(wx.EVT_BUTTON, self.On_AddLabel)
        self.btn_DelLabel = wx.Button(self.panel1, wx.ID_ANY, label='Delete Label')
        self.btn_DelLabel.Bind(wx.EVT_BUTTON, self.On_DelLabel)
        self.btn_Play = wx.Button(self.panel2, wx.ID_ANY, label='Play')
        self.btn_Play.Bind(wx.EVT_BUTTON, self.On_Play)
        self.btn_TextFile = wx.Button(self.panel2, wx.ID_ANY, label='Text File')
        self.btn_TextFile.Bind(wx.EVT_BUTTON, self.On_TextFile)
        self.btn_Edit = wx.Button(self.panel2, wx.ID_ANY, label='Edit')
        #self.btn_Edit.Bind(wx.EVT_LEFT_DOWN, self.On_DelLabel)
        self.btn_ApplyLabel = wx.Button(self.panel2, wx.ID_ANY, label='Apply Label')
        self.btn_ApplyLabel.Bind(wx.EVT_BUTTON, self.On_ApplyLabel)

        # button bars
        self.buttonbar1 = wx.BoxSizer()
        self.buttonbar1.Add(self.btn_AddLabel, 1, wx.EXPAND)
        self.buttonbar1.Add(self.btn_DelLabel, 1, wx.EXPAND)
        self.buttonbar2 = wx.BoxSizer()
        self.buttonbar2.Add(self.btn_Play, 1, wx.EXPAND)
        self.buttonbar2.Add(self.btn_TextFile, 1, wx.EXPAND)
        self.buttonbar2.Add(self.btn_Edit, 1, wx.EXPAND)
        self.buttonbar2.Add(self.btn_ApplyLabel, 1, wx.EXPAND)
        
        # left vbox/panel
        self.vbox_left = wx.BoxSizer(wx.VERTICAL)
        self.vbox_left.Add(self.tree, 1, wx.EXPAND)
        self.vbox_left.Add(self.buttonbar1, 0, wx.EXPAND)
        self.panel1.SetSizer(self.vbox_left)

        # right vbox/panel
        self.vbox_right = wx.BoxSizer(wx.VERTICAL)
        self.vbox_right.Add(self.list, 1, wx.EXPAND)
        self.vbox_right.Add(self.buttonbar2, 0, wx.EXPAND)
        self.panel2.SetSizer(self.vbox_right)

        # combine left/right panels
        self.hbox = wx.BoxSizer()
        self.hbox.Add(self.panel1, 1, wx.EXPAND)
        self.hbox.Add(self.panel2, 2, wx.EXPAND)
        
        # add final bar
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox, 1, wx.EXPAND)
        self.vbox.Add(self.input, 0, wx.EXPAND)
        
        self.SetSizer(self.vbox)
        self.SetAutoLayout(1)

        self.SetFontSizeAndPrintText()
        
        # ... and adjust the window size
        self.SetSize((1200, 800))
        self.Centre()
        self.Show(True)

        self.UpdateSongs()

        # init prompt
        self.prompt = '>>> '
        self.input.WriteText(self.prompt)
        self.input.SetFocus()
        self.input.SetSelection(len(self.prompt), len(self.prompt))
       
        # init mode std
        self.Raise()

    def RemoveLabelFromSongs(self, todelete):
        allsongs = sorted(self.songdict.keys())
        print ' *** todelete:', todelete.encode('utf-8')
        for s in allsongs:
            labellist = self.songdict[s].get('labels', [])
            newlabellist = []
            for label in labellist:
                if cmp_label_list(label, todelete):
                    print 'label:', label.encode('utf-8'), 'has to be removed'
                else:
                    print 'label:', label.encode('utf-8'), 'stays'
                    newlabellist.append(label)
            self.songdict[s]['labels'] = newlabellist

    def FilterSongs(self):
        allsongs = sorted(self.songdict.keys())
        
        songs_labelfiltered = []
        for s in allsongs:
            labellist = [[]] + self.songdict[s].get('labels', [])
            addlabel = False
            for label in labellist:
                if cmp_label_list(label, self.curlabel[1:]):
                    addlabel = True
            if addlabel:
                songs_labelfiltered.append(s)
            
        self.songs = songs_labelfiltered
    
    def UpdateSongs(self):
        self.FilterSongs()
        self.list.DeleteAllItems()
        self.list.SetItemCount(len(self.songs))
        for i in range(len(self.songs)):
            songname = self.songs[i]
            labelstr = labels2str(self.songdict[songname].get('labels', []))
            if labelstr == '': labelstr = '-'
            self.list.InsertStringItem(i, songname)
            self.list.SetStringItem(i, 1, labelstr)
            item = self.list.GetItem(i)
            color = wx.Colour(0xF3, 0xF4, 0xFF) if i % 2 == 0 else wx.Colour(0xf8, 0xff, 0xf8)
            item.SetBackgroundColour(color)
            self.list.SetItem(item)
        
        #self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        #self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(0, 300)
        self.list.SetColumnWidth(1, 400)
        
        self.sb.SetStatusText(str(len(self.songs)) + ' songs', 1)

    def UpdateLables(self):
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot('All')
        self.labels.fill_tree_ctrl(root, self.tree)
        self.tree.ExpandAll()
        
        self.curlabel = ['All']
        self.curlabelstr = ' -> '.join(self.curlabel)
        self.sb.SetStatusText(self.curlabelstr)
        self.UpdateSongs()


    def OnSelChanged(self, event):
        item =  event.GetItem()
        rootitem = self.tree.GetRootItem()
        paritem = item
        parents = [self.tree.GetItemText(item)]
        while paritem != rootitem:
            paritem = self.tree.GetItemParent(item)
            parname = self.tree.GetItemText(paritem)
            item = paritem
            parents.append(parname)
        
        self.curlabel = list(reversed(parents))
        self.curlabelstr = ' -> '.join(self.curlabel)
        self.sb.SetStatusText(self.curlabelstr)
        self.UpdateSongs()
    
    def On_AddLabel(self, event):
        event.Skip()
        dlg = wx.TextEntryDialog(self, 'Create new label under:\n\n%s\n\nEnter new label name:\n' % self.curlabelstr, 'New Label')
        dlg.SetValue('')
        if dlg.ShowModal() == wx.ID_OK:
            value = dlg.GetValue()
            if value != '':
                self.labels.add_sublabel_recursive(self.curlabel[1:], value)    # das erste Label 'All' darf nicht mit drin sein
                self.labels.SaveLabels()
                self.UpdateLables()
            
        dlg.Destroy()

    def On_DelLabel(self, event):
        event.Skip()
        dlg = wx.MessageDialog(self, 'Really delete label with all its sublabels?\n%s' % self.curlabelstr, 'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.labels.delete_recursive(self.curlabel[1:])
            self.RemoveLabelFromSongs(self.curlabel[1:])
            #self.labels.SaveLabels()
            self.UpdateLables()
            
    def On_Play(self, event):
        event.Skip()
        selected = self.list.GetFocusedItem()
        selected = self.list.GetItemText(selected)
        options = self.songdict[selected]
        if options.has_key(u'play'):
            filename = options[u'play'] 
            execcmd = '~/coding/python/pyTranscribe/pyTranscribe.py ' + filename.encode('utf-8') + ' &'
            print 'executing:', execcmd
            os.system(execcmd)
    
    def On_TextFile(self, event):
        event.Skip()
        selected = self.list.GetFocusedItem()
        selected = self.list.GetItemText(selected)
        execcmd = 'gedit "./txt/' + selected.encode('utf-8') + '" &'
        print 'executing:', execcmd
        os.system(execcmd)
        
    def On_ApplyLabel(self, event):
        event.Skip()
        selected = self.list.GetFirstSelected()
        
        songs = []
        while selected != -1:
            name = self.list.GetItemText(selected)
            songs.append(name)
            selected = self.list.GetNextSelected(selected)

        labellist = self.labels.makelist()
        labellist_str = ['"' + '"->"'.join(l[1:]) + '"' for l in labellist[1:]]
        dlg = wx.SingleChoiceDialog(self, 'Add %d songs to label:' % len(songs), 'Select Label', labellist_str, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            toapply = labellist[dlg.GetSelection() + 1][1:]
            print 'to apply:', toapply.encode('utf-8')
            for s in songs:
                oldlabels = self.songdict[s].get('labels', [])
                self.songdict[s]['labels'] = oldlabels + [toapply]
            self.UpdateSongs()
            SaveSongDictionary(self.songdict)
        
        dlg.Destroy()
        
    def OnClose(self, event):
        #ConfigSaveLastPath(self.lastpath)
        event.Skip()
        
    def SetFontSizeAndPrintText(self):
        font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Monospace')
        #font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        self.list.SetFont(font)
        self.input.SetFont(font)
        self.tree.SetFont(font)
        self.sb.SetFont(font)
        # vielleicht sollte man sich den Insertion Point merken?
        intxt = self.input.GetValue()
        self.input.Clear()
        self.input.WriteText(intxt)

    def KeyPressed(self, evt):
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



# --------------------
# Config File Handling
# --------------------

# correct path
os.chdir(sys.path[0])

# open config files
if os.path.exists('songs.txt'):
    config_songs = ConfigParser.RawConfigParser()
    config_songs.read('songs.txt')
else:
    print 'config files not found'
    sys.exit()
    

def LoadSongDictionary():
    songdict = {}
    
    songnames = sorted(config_songs.sections())
    songnames = [n.decode('utf-8') for n in songnames]
    print 'Loading Songs...', len(songnames), 'songs imported'
    
    for song in songnames:
        #options = config_songs.options(song)
        #options = [n.decode('utf-8') for n in options]
        items = config_songs.items(song.encode('utf-8'))
        # print items
        items = [(n[0].decode('utf-8'), n[1].decode('utf-8')) for n in items]
        # print items
        valuedict = {}
        for key, val in items:
            if key != 'labels':
                valuedict[key] = val
            else:
                valuedict[key] = eval(val)
        songdict[song] = valuedict
        
    # print songdict
    return songdict

def SaveSongDictionary(songdict):
    print 'Saving Song Dictionary...'
    for song, songparams in songdict.iteritems():
        for key, val in songparams.iteritems():
            if key != 'labels':
                config_songs.set(song.encode('utf-8'), key.encode('utf-8'), val.encode('utf-8'))
            else:
                config_songs.set(song.encode('utf-8'), key.encode('utf-8'), repr(val))
    config_songs.write(open('songs.txt', 'w'))
        
if __name__ == '__main__':
    gen_keymap()
    app = wx.PySimpleApp()
    frame = MainFrame()
    app.MainLoop()






# obsolete?
"""

def ReadLabels(name, label):
    name_u = name.encode('utf-8')
    if config_label.has_section(name_u):
        if config_label.has_option(name_u, 'sub'):
            sub = config_label.get(name_u, 'sub').decode('utf-8')
            sub = [i.strip().strip('"') for i in sub.split(';;')]
            for i in sub:
                #print 'adding sublabel', i
                newsub = label.add_sublabel(i)
                ReadLabels(i, newsub)


def ReadSongLabels(songs):
    #songlabels = [[[]] for i in range(len(songs))]
    songlabels = {}
    for i in range(len(songs)):
        try:
            labelstring = config_songs.get(songs[i].encode('utf-8'), 'labels').decode('utf-8')
            if labelstring.strip() != '':
                newsonglabels = [[x.strip('"') for x in l.split('->')] for l in labelstring.split(';;')]
                songlabels[songs[i]] = newsonglabels
                print songs[i], 'has labels:', songlabels[songs[i]]
            else:
                songlabels[songs[i]] = []
            #songlabels[i] = [l.split('->') for l in labelstring.split(';;')]
            #songlabels[i] = [[x.strip('"') for x in l] for l in songlabels[i]]
            #print songs[i], 'has labels:', songlabels[i]
        except ConfigParser.NoOptionError:
            songlabels[songs[i]] = []
    print songlabels
    return songlabels

def SaveSongLabels(songs, songlabels):
    for s in songs:
        if songlabels.has_key(s):
            labels = songlabels[s]
            print labels
            stringified = u';;'.join([u'->'.join([u'"' + unquoted + u'"' for unquoted in l]) for l in labels])
            print 'string written for', s, ':', stringified
            config_songs.set(s.encode('utf-8'), 'labels', stringified.encode('utf-8'))
            config_songs.write(open('songs.txt', 'w'))

def ApplyLabels(songs, newlabel, songlabels):
    print newlabel
    labels = list(reversed(newlabel))[1:]
    print newlabel
    for song in songs:
        songlabels[song].append(labels)

    print songlabels
    SaveSongLabels(songs, songlabels)
"""



"""
def get_sublabels(self):
    shift = '  '
    par = list(reversed(self.parent_names()))
    par = [shift*i + par[i] for i in range(len(par))]
    self.npar = len(par)
    sub = sorted([shift*len(par) + i.name for i in self.sublabels])
    return par + [shift*len(par) + 'Unlabeled'] + sub

def select(self, i):
    i = i - (self.npar + 1)
    print i, self.npar
    if i >= 0:
        print 'selecting', self.sublabels[i].name
        return self.sublabels[i]
    elif i<=-2:
        print 'go up to', self.get_parent(-i-2).name
        return self.get_parent(-i-2)
    else:
        return self

def get_parent(self, num):
    if num > 0:
        return self.parent.get_parent(num - 1)
    else:
        return self

def parent_names(self):
    if self.parent != self:
        return [self.name] + self.parent.parent_names()
    else:
        return [self.parent.name]
"""

