import os
import wx
import wx.adv
import socket
import time
import threading
from datetime import datetime

class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

        self.config = wx.Config()
        self.Center()
        self.SetMinSize((600, 700))

        menubar = wx.MenuBar()
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "&About")
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.SetMenuBar(menubar)

        self.main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.hBox1 = wx.BoxSizer(wx.HORIZONTAL)

        type_choices = ['IP', 'SDI']
        self.radio_type = wx.RadioBox(self, label='Type', choices=type_choices)
        self.radio_type.Bind(wx.EVT_RADIOBOX, self.set_configuration)
        self.radio_type.SetSelection(int(self.config.Read('/type', defaultVal="0")))

        script_choices = ['SRC-X and SRC-Y to DST Z', 'SRC-X and SRC-Y to DST 1-Z']
        self.radio_script = wx.RadioBox(self, label='Script', choices=script_choices)
        self.radio_script.Bind(wx.EVT_RADIOBOX, self.set_configuration)
        self.radio_script.SetSelection(int(self.config.Read('/script', defaultVal="0")))

        self.choices = ['570 A9', '570 X-19', 'evIPG-12G', 'evIPG-3G']
        self.choice = wx.Choice(self, choices=self.choices)
        self.choice.Bind(wx.EVT_CHOICE, self.set_configuration)
        self.choice.SetStringSelection(self.config.Read("/device", defaultVal="570 A9"))


        self.start_button = wx.Button(self, label="Start")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start)

        self.pause_button = wx.Button(self, label="Pause")
        self.pause_button.Disable()
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)

        self.hBox1.Add(self.radio_type, flag=wx.ALL, border=10)
        self.hBox1.Add(self.radio_script, flag=wx.ALL, border=10)
        self.hBox1.Add(self.choice, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self.route_label = wx.StaticText(self, label="Destination:")

        if self.radio_script.GetSelection() == 1:
            self.route_label.SetLabel("Output 1 to")

        self.route_input = wx.TextCtrl(self, size=(30, -1), value=self.config.Read('/route', defaultVal=""))

        self.magnum_label = wx.StaticText(self, label="Magnum IP:")
        self.magnum_input = wx.TextCtrl(self, value=self.config.Read('/magnumIP', defaultVal=""))

        self.port_label = wx.StaticText(self, label="Interface Port #:")
        self.port_input = wx.TextCtrl(self, size=(50, -1), value=self.config.Read('/port', defaultVal=""))

        self.delay_label = wx.StaticText(self, label="Delay per route:")
        self.delay_input = wx.TextCtrl(self, size=(30, -1), value=self.config.Read('/delay', defaultVal=""))
        self.delay_label_post = wx.StaticText(self, label="seconds")
        self.grid = wx.GridBagSizer(4, 4)

        self.grid.Add(self.magnum_label, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        self.grid.Add(self.magnum_input, pos=(0, 1), flag=wx.TOP, border=10)

        self.grid.Add(self.port_label, pos=(0, 2), flag=wx.LEFT | wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        self.grid.Add(self.port_input, pos=(0, 3), span=(1, 2), flag=wx.TOP, border=10)

        self.grid.Add(self.start_button, pos=(0, 5), flag=wx.TOP | wx.LEFT, border=10)

        self.grid.Add(self.route_label, pos=(1, 0), flag=wx.LEFT | wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        self.grid.Add(self.route_input, pos=(1, 1), flag=wx.TOP, border=10)

        self.grid.Add(self.delay_label, pos=(1, 2), flag=wx.LEFT | wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        self.grid.Add(self.delay_input, pos=(1, 3), flag=wx.TOP, border=10)
        self.grid.Add(self.delay_label_post, pos=(1, 4), flag=wx.TOP | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL,
                      border=10)
        self.grid.Add(self.pause_button, pos=(1, 5), flag=wx.TOP | wx.LEFT, border=10)

        self.scrolled_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)

        self.main_vbox.Add(self.hBox1, flag=wx.Right)
        self.main_vbox.Add(self.grid, flag=wx.RIGHT)
        self.main_vbox.Add(self.scrolled_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.CreateStatusBar(number=2, style=wx.STB_DEFAULT_STYLE)
        self.SetStatusWidths([-1, 100])
        self.SetStatusText("This is the status bar", 0)

        self.SetSizer(self.main_vbox)

        self.isStart = False
        self.isResume = False

    def on_start(self, event):
        # saving to configuration
        self.config.Write("/magnumIP", self.magnum_input.GetValue())
        self.config.Write("/port", self.port_input.GetValue())
        self.config.Write("/route", self.route_input.GetValue())
        self.config.Write("/delay", self.delay_input.GetValue())
        self.config.Write("/type", str(self.radio_type.GetSelection()))
        self.config.Write("/script", str(self.radio_script.GetSelection()))

        # Checking if script is already running
        if self.start_button.GetLabel() == "Stop":
            self.isResume = False
            self.isStart = False
            self.start_button.SetLabel("Start")
            self.pause_button.SetLabel("Pause")
            self.pause_button.Disable()
            self.SetStatusText("Stopped switching")
            return
        else:
            self.start_button.SetLabel("Stop")
            start_thread = threading.Thread(target=self.on_start_thread)
            self.pause_button.Enable()
            self.isStart = True
            self.isResume = True
            self.scrolled_text.Clear()
            self.SetStatusText("Switching.....")
            start_thread.start()

    def on_pause(self, event):
        if self.pause_button.GetLabel() == "Pause":
            self.SetStatusText("Paused")
            self.pause_button.SetLabel("Resume")
        elif self.pause_button.GetLabel() == "Resume":
            self.SetStatusText("Switching.....")
            self.pause_button.SetLabel("Pause")
        self.isResume = not self.isResume

    def on_start_thread(self):
        # Getting the UI configuration
        MAGNUM_ADDR = self.magnum_input.GetValue()
        INTERFACE_PORT = self.port_input.GetValue()
        DELAY = self.delay_input.GetValue()
        ROUTE = int(self.route_input.GetValue())
        SCRIPT = self.radio_script.GetSelection()

        eport1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        eport1.connect((MAGNUM_ADDR, int(INTERFACE_PORT)))
        eport1.settimeout(3)
        self.scrolled_text.write('CONNECTED TO MAGNUM INTERFACE\n\n')

        n = 1
        input = 1
        output = 1

        while self.isStart:
            while self.isResume:
                if SCRIPT == 0:  # 0 means the selection is x,y to z
                    cmd1 = '.SVABCDEFGHIJKLMNOPQRS%03d,%03d\r' % (ROUTE, input)
                    eport1.send(cmd1.encode())
                    time.sleep(float(DELAY))

                    self.scrolled_text.write("Route %d\n" % n)
                    self.scrolled_text.write(f"Routing Source {input} to Destination {ROUTE}\n")
                    self.scrolled_text.write(f"Time {datetime.now().strftime('%Y-%m-%d %H:%M %Ss')}\n")
                    self.scrolled_text.write("********\n\n\n")

                    input += 1
                    if input == 3:
                        input = 1
                    n = n + 1  # calculates the route number

                if SCRIPT == 1:  # 1 means the selection is x,y to all
                    cmd1 = '.SVABCDEFGHIJKLMNOPQRS%03d,%03d\r' % (output, input)
                    eport1.send(cmd1.encode())
                    time.sleep(float(DELAY))

                    self.scrolled_text.write("Route %d\n" % n)
                    self.scrolled_text.write(f"Routing Source {input} to Destination {output}\n")
                    self.scrolled_text.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M %Ss')}\n")
                    self.scrolled_text.write("********************\n\n\n")

                    output += 1
                    if output == ROUTE + 1:  # Route + 1 is non-existent since route is the last IO entered by user
                        output = 1
                        input += 1
                        if input == 3:
                            input = 1
                    n = n + 1  # calculates the route number
        eport1.close()

    def set_configuration(self, event):
        if self.radio_type.GetStringSelection() == "SDI":
            self.delay_input.SetValue("0.1")
        if self.radio_type.GetStringSelection() == "IP":
            self.delay_input.SetValue("0.3")
        if self.radio_script.GetStringSelection() == "SRC-X and SRC-Y to DST Z":
            self.route_label.SetLabel("Destination:")
        if self.radio_script.GetStringSelection() == "SRC-X and SRC-Y to DST 1-Z":
            self.route_label.SetLabel("Output 1 to")
            if (self.choice.GetSelection() == 0) or (self.choice.GetSelection() == 1):
                self.route_input.SetValue("18")
            elif self.choice.GetSelection() == 2:
                self.route_input.SetValue("16")
            elif self.choice.GetSelection() == 3:
                self.route_input.SetValue("32")

    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName('Switching UI')
        info.SetDescription(
            "Python version 3.11.7\n" +
            "Powered by wxPython %s\n" % (wx.version()) +
            "Running on %s\n\n" % (wx.GetOsDescription()) +
            "Process ID = %s\n" % (os.getpid()))
        info.SetWebSite("www.evertz.com", "Evertz")
        info.AddDeveloper("Omkarsinh Sindha")
        wx.adv.AboutBox(info)



if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame(None, title="Switching UI", size=(600, 700))
    frame.Show()
    app.MainLoop()
