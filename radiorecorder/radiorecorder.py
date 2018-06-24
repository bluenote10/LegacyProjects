#!/usr/bin/python
# -*- encoding=utf-8 -*-

import os, sys, datetime
import wx
import operator
import datetime

os.chdir(sys.path[0])

defaultfolder = '/tmp'
defaultadd = 15

"""
recordfolder = '/tmp/'

print "Url: ",
url = raw_input()

print "Startuhrzeit: ",
input = raw_input()
starttime = input

print "Recodername: ",
recname = raw_input()

print "Laenge: ",
duration = int(raw_input())


cmd = ('at %s << EOF\n' % starttime) + \
      ('mkdir -p %s\n' % recordfolder) + \
      ('cd "%s"\n' % recordfolder) + \
      ('streamripper %s -a %s_%%S_%%d -A -s -k 0 -l %d\n' % (url, recname, int(duration)*60)) + \
      ('EOF')
print cmd
os.system(cmd)
"""

class MainFrame(wx.Frame):                                  # {{{
    def __init__(self):                                     # {{{
        wx.Frame.__init__(self, None, -1, "Radio-Recorder", size=(700,170))

        # load settings
        self.fontsize = 8

        if os.path.exists('senderliste.txt'):
            f = open('senderliste.txt', 'r')
            self.senderliste = eval(f.read())
            self.senderliste = list(sorted(self.senderliste))
        else:
            self.senderliste = []

        now = datetime.datetime.now()

        # create the UI elements ...
    
        self.st_url = wx.StaticText(self, 1, 'Url:', style=wx.ALIGN_CENTRE)
        self.in_url = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.fill_combobox()
        #self.in_url = wx.TextCtrl(self, 1, style = wx.TE_PROCESS_ENTER)
        self.line1 = wx.BoxSizer()
        self.line1.Add(self.st_url, 70, wx.ALIGN_CENTER)
        self.line1.Add(self.in_url, 200, wx.EXPAND)

        self.st_time_start = wx.StaticText(self, 1, 'Beginn:', style=wx.ALIGN_CENTER)
        self.in_y1 = wx.TextCtrl(self, 1, str(now.year), style = wx.TE_PROCESS_ENTER)
        self.in_m1 = wx.TextCtrl(self, 1, '%02d' % now.month, style = wx.TE_PROCESS_ENTER)
        self.in_d1 = wx.TextCtrl(self, 1, '%02d' % now.day, style = wx.TE_PROCESS_ENTER)
        self.in_T1 = wx.TextCtrl(self, 1, '%02d:%02d' % (now.hour, now.minute), style = wx.TE_PROCESS_ENTER)
        self.line2 = wx.BoxSizer()
        self.line2.Add(self.st_time_start, 70, wx.ALIGN_CENTER)
        self.line2.Add(self.in_y1, 60, wx.EXPAND)
        self.line2.Add(self.in_m1, 40, wx.EXPAND)
        self.line2.Add(self.in_d1, 40, wx.EXPAND)
        self.line2.Add(self.in_T1, 60, wx.EXPAND)
        
        self.st_time_end = wx.StaticText(self, 1, 'Ende:', style=wx.ALIGN_CENTER)
        self.in_y2 = wx.TextCtrl(self, 1, str(now.year), style = wx.TE_PROCESS_ENTER)
        self.in_m2 = wx.TextCtrl(self, 1, '%02d' % now.month, style = wx.TE_PROCESS_ENTER)
        self.in_d2 = wx.TextCtrl(self, 1, '%02d' % now.day, style = wx.TE_PROCESS_ENTER)
        self.in_T2 = wx.TextCtrl(self, 1, '%02d:%02d' % (now.hour, now.minute), style = wx.TE_PROCESS_ENTER)
        self.line3 = wx.BoxSizer()
        self.line3.Add(self.st_time_end, 70, wx.ALIGN_CENTER)
        self.line3.Add(self.in_y2, 60, wx.EXPAND)
        self.line3.Add(self.in_m2, 40, wx.EXPAND)
        self.line3.Add(self.in_d2, 40, wx.EXPAND)
        self.line3.Add(self.in_T2, 60, wx.EXPAND)

        self.st_add = wx.StaticText(self, 1, 'Add [min]', style=wx.ALIGN_CENTRE)
        self.in_add = wx.TextCtrl(self, 1, str(defaultadd), style = wx.TE_PROCESS_ENTER)
        self.line4 = wx.BoxSizer()
        self.line4.Add(self.st_add, 70, wx.ALIGN_CENTER)
        self.line4.Add(self.in_add, 200, wx.EXPAND)

        self.st_dir = wx.StaticText(self, 1, 'Verzeichnis:', style=wx.ALIGN_CENTRE)
        self.in_dir = wx.TextCtrl(self, 1, defaultfolder, style = wx.TE_PROCESS_ENTER)
        self.line5 = wx.BoxSizer()
        self.line5.Add(self.st_dir, 70, wx.ALIGN_CENTER)
        self.line5.Add(self.in_dir, 200, wx.EXPAND)

        self.btn_start = wx.Button(self, wx.ID_ANY, label='Programmieren')
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start)
        self.btn_testsender = wx.Button(self, wx.ID_ANY, label='Testen')
        self.btn_testsender.Bind(wx.EVT_BUTTON, self.on_testsender)
        self.btn_recnow = wx.Button(self, wx.ID_ANY, label='Jetzt aufnehmen')
        self.btn_recnow.Bind(wx.EVT_BUTTON, self.on_recnow)
        self.btn_addsender = wx.Button(self, wx.ID_ANY, label='Sender hinzufügen')
        self.btn_addsender.Bind(wx.EVT_BUTTON, self.on_addsender)
        self.linebut = wx.BoxSizer()
        self.linebut.Add(self.btn_start, 100, wx.ALIGN_CENTER)
        self.linebut.Add(self.btn_testsender, 100, wx.ALIGN_CENTER)
        self.linebut.Add(self.btn_recnow, 100, wx.ALIGN_CENTER)
        self.linebut.Add(self.btn_addsender, 100, wx.ALIGN_CENTER)

        self.all_lines = wx.BoxSizer(wx.VERTICAL)
        self.all_lines.Add(self.line1, 1, wx.EXPAND)
        self.all_lines.Add(self.line2, 1, wx.EXPAND)
        self.all_lines.Add(self.line3, 1, wx.EXPAND)
        self.all_lines.Add(self.line4, 1, wx.EXPAND)
        self.all_lines.Add(self.line5, 1, wx.EXPAND)
        self.all_lines.Add(self.linebut, 1, wx.EXPAND)
        
        self.SetSizer(self.all_lines)
        
        self.SetFontSizeAndPrintText()
        self.Raise()

    def on_start(self, event):
        event.Skip()
        index = self.in_url.GetSelection()
        url = self.senderliste[index][1]
        
        try:
            delta = datetime.timedelta(minutes = int(self.in_add.GetValue()))

            hour = int(self.in_T1.GetValue().split(':')[0])
            min = int(self.in_T1.GetValue().split(':')[1])
            time_start = datetime.datetime(int(self.in_y1.GetValue()), int(self.in_m1.GetValue()), int(self.in_d1.GetValue()), hour, min) - delta

            hour = int(self.in_T2.GetValue().split(':')[0])
            min = int(self.in_T2.GetValue().split(':')[1])
            time_end = datetime.datetime(int(self.in_y2.GetValue()), int(self.in_m2.GetValue()), int(self.in_d2.GetValue()), hour, min) + delta
            
        except:
            print 'error in date strings'
            return
        print time_start
        print time_end
        # print 'starting %s @ %s' % (self.senderliste[index][0], self.senderliste[index][1])
        
        atstart = '%02d:%02d %02d.%02d.%04d' % (time_start.hour, time_start.minute, time_start.day, time_start.month, time_start.year)
        duration = (time_end - time_start).seconds

        recordfolder = self.in_dir.GetValue()
        recname = 'test'
        
        cmd = ('at %s << EOF\n' % atstart) + \
              ('mkdir -p %s\n' % recordfolder) + \
              ('cd "%s"\n' % recordfolder) + \
              ('streamripper %s -a %s_%%S_%%d -A -s -k 0 -l %d\n' % (url, recname, duration)) + \
              ('EOF')
        #print cmd
        os.system(cmd)

        dlg = wx.MessageDialog(self, u'Aufnahme wurde programmiert für:\n\nDatum: %s\nZeit: %s\nDauer: %s min\nSender: %s' % (time_start.strftime('%d.%m.%Y'), time_start.strftime('%H:%M'), duration/60, url), u'Love you, Schnübbi', wx.OK)
        if dlg.ShowModal() == wx.OK:
            pass
        dlg.Destroy()



    def on_testsender(self, event):
        event.Skip()
        index = self.in_url.GetSelection()
        os.system("gnome-terminal -e 'mplayer %s'" % (self.senderliste[index][1]))

    def on_recnow(self, event):
        event.Skip()
        index = self.in_url.GetSelection()
        url = self.senderliste[index][1]

        wave_only = False
        if wave_only:
            recordfolder = self.in_dir.GetValue()
            recname = 'test'
            recfilename_wav = '%s/%s_%s.wav' % (recordfolder, recname, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            
            scriptname = '%s/%s_%s.sh' % (recordfolder, recname, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) 
            f = open(scriptname, 'w')
            f.write('#!/bin/bash\n')
            f.write('echo -e " *** starting mplayer"\n')
            f.write('mplayer -vc null -vo null -ao pcm:fast:file=\'%s\' %s\n' % (recfilename_wav, url))
            f.write('echo -e " *** press [return] to close this window"\n')
            f.write('read\n')
            f.close()
        else:
            recordfolder = self.in_dir.GetValue()
            recname = 'test'
            recfilename_wav = '%s/%s_%s.wav' % (recordfolder, recname, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            recfilename_mp3 = recfilename_wav[:-4] + '.mp3'
            
            scriptname = '%s/%s_%s.sh' % (recordfolder, recname, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) 
            f = open(scriptname, 'w')
            f.write('#!/bin/bash\n')
            f.write('echo -e " *** creating fifo %s"\n' % recfilename_wav)
            f.write('mkfifo "%s"\n' % recfilename_wav)
            f.write('echo -e " *** starting lame"\n')
            f.write('lame - < "%s" > "%s" &\n' % (recfilename_wav, recfilename_mp3))
            f.write('echo -e " *** starting mplayer"\n')
            f.write('mplayer -noconsolecontrols -vc null -vo null -ao pcm:fast:file=\'%s\' %s\n' % (recfilename_wav, url))
            f.write('echo -e " *** lame compression results:"\n')
            f.write('wait\n')
            f.write('echo -e " *** deleting fifo %s"\n' % recfilename_wav)
            f.write('rm "%s"\n' % recfilename_wav)
            f.write('echo -e " *** press [return] to close this window"\n')
            f.write('read\n')
            f.close()
            
        os.system('chmod +x %s' % scriptname)
        os.system('cat %s' % scriptname)
        os.system('gnome-terminal -x bash -c "%s"' % (scriptname))
        os.system('rm %s' % (scriptname))

    def on_addsender(self, event):
        event.Skip()
        dlg = wx.TextEntryDialog(self, 'Url:', 'Neuer Sender')
        dlg.SetValue('')
        if dlg.ShowModal() == wx.ID_OK:
            value = dlg.GetValue()
            if value != '':
                newurl = value
        else:
            return
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, 'Name:', 'Neuer Sender')
        dlg.SetValue('')
        if dlg.ShowModal() == wx.ID_OK:
            value = dlg.GetValue()
            if value != '':
                newname = value
        else:
            return
        dlg.Destroy()
        
        self.senderliste.append([newname, newurl])
        self.senderliste = list(sorted(self.senderliste))
        f = open('senderliste.txt', 'w')
        f.write(repr(self.senderliste))
        f.close()
        
        self.fill_combobox()        
            
    def fill_combobox(self):
        self.in_url.Clear()
        for sender in self.senderliste:
            self.in_url.Append('%s  @  %s' % (sender[0], sender[1]))
    
    def SetFontSizeAndPrintText(self):
        font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Monospace')
        #font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        #self.in_url.SetFont(font)



if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainFrame()
    app.MainLoop()
