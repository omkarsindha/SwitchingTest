import os
import wx
import wx.adv
import socket
import time


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
        self.radio_type.Bind(wx.EVT_RADIOBOX, self.on_type)
        self.radio_type.SetSelection(int(self.config.Read('/type', defaultVal="0")))

        script_choices = ['SRC-X and SRC-Y to DST Z', 'SRC-X and SRC-Y to DST 1-Z']
        self.radio_script = wx.RadioBox(self, label='Script', choices=script_choices)
        self.radio_script.Bind(wx.EVT_RADIOBOX, self.on_script)
        self.radio_script.SetSelection(int(self.config.Read('/script', defaultVal="0")))

        self.switch = wx.Button(self, label="Start switching")
        self.switch.Bind(wx.EVT_BUTTON, self.on_start)
        self.hBox1.Add(self.radio_type, flag=wx.ALL, border=10)
        self.hBox1.Add(self.radio_script, flag=wx.ALL, border=10)
        self.hBox1.Add(self.switch, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self.route_label = wx.StaticText(self, label="Destination:")
        self.route_input = wx.TextCtrl(self, size=(20, -1), value=self.config.Read('/route', defaultVal=""))

        self.magnum_label = wx.StaticText(self, label="Magnum IP:")
        self.magnum_input = wx.TextCtrl(self, value=self.config.Read('/magnumIP', defaultVal=""))

        self.port_label = wx.StaticText(self, label="Interface Port #:")
        self.port_input = wx.TextCtrl(self, size=(50, -1), value=self.config.Read('/port', defaultVal=""))

        self.delay_label = wx.StaticText(self, label="Delay per route:")
        self.delay_input = wx.TextCtrl(self, size=(30, -1), value=self.config.Read('/delay', defaultVal=""))
        self.delay_label_post = wx.StaticText(self, label="seconds")
        self.grid = wx.GridBagSizer(4, 4)

        self.grid.Add(self.magnum_label, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.grid.Add(self.magnum_input, pos=(0, 1), flag=wx.TOP, border=10)

        self.grid.Add(self.port_label, pos=(0, 2), flag=wx.LEFT | wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.grid.Add(self.port_input, pos=(0, 3), span=(1, 2), flag=wx.TOP, border=10)

        self.grid.Add(self.route_label, pos=(1, 0), flag=wx.LEFT | wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.grid.Add(self.route_input, pos=(1, 1), flag=wx.TOP, border=10)

        self.grid.Add(self.delay_label, pos=(1, 2), flag=wx.LEFT | wx.TOP | wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL, border=10)
        self.grid.Add(self.delay_input, pos=(1, 3), flag=wx.TOP, border=10)
        self.grid.Add(self.delay_label_post, pos=(1, 4), flag= wx.TOP | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, border=10)

        self.scrolled_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)

        self.main_vbox.Add(self.hBox1, flag=wx.Right)
        self.main_vbox.Add(self.grid, flag=wx.RIGHT)
        self.main_vbox.Add(self.scrolled_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.CreateStatusBar(number=2, style=wx.STB_DEFAULT_STYLE)
        self.SetStatusWidths([-1, 100])
        self.SetStatusText("This is the status bar", 0)

        self.SetSizer(self.main_vbox)

    def on_start(self, event):
        # saving to configuration
        self.config.Write("/magnumIP", self.magnum_input.GetValue())
        self.config.Write("/port", self.port_input.GetValue())
        self.config.Write("/route", self.route_input.GetValue())
        self.config.Write("/delay", self.delay_input.GetValue())
        self.config.Write("/type", self.radio_type.GetSelection())
        self.config.Write("/script", self.radio_script.GetSelection())

        MAGNUM_ADDR = self.magnum_input.GetValue()
        INTERFACE_PORT = self.port_input.GetValue()

        # eport1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # eport1.connect((MAGNUM_ADDR, INTERFACE_PORT))
        # eport1.settimeout(3)
        # print('CONNECTED TO MAGNUM INTERFACE')
        #
        # n = 1
        # error = 1
        # x = 1
        # input = 1  # BI starts from 1-8, IPG25 starts from 9-24, A9 starts from 25-33, 670IPG starts from 34-49
        # output = 1  # BI starts from 1-8, IPG25 starts from 9-24, A9 starts from 25-33, 670IPG starts from 34-49
        #
        # while True:
        #     print("********")
        #     print("Route %d" % n)
        #     print("********")
        #     cmd1 = '.SVABCDEFGHIJKLMNOPQRS%03d,%03d\r' % (output, input)
        #     print(cmd1)
        #     eport1.send(cmd1)
        #     print(eport1.recv(200))
        #
        #     time.sleep(0.3)  # Change the ms to achieve more or less routes
        #     output = output + 1
        #     if output == 33:
        #         output = 1
        #         input = input + 1
        #         if input == 3:
        #             input = 1
        #     n = n + 1  # for route counter
        # eport1.close()

    def on_type(self, event):
        if self.radio_type.GetStringSelection() == "SDI":
            self.delay_input.SetValue("0.1")
        if self.radio_type.GetStringSelection() == "IP":
            self.delay_input.SetValue("0.3")

    def on_script(self, event):
        if self.radio_script.GetStringSelection() == "SRC-X and SRC-Y to DST Z":
            self.route_label.SetLabel("Destination:")
        if self.radio_script.GetStringSelection() == "SRC-X and SRC-Y to DST 1-Z":
            self.route_label.SetLabel("Output 1 to")

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
