#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import os, subprocess, sys
from subprocess import PIPE, STDOUT, Popen
from getpass import getuser
from time import sleep
import threading

# dependency check
os.system("pip install --upgrade pip")
for pkg in ['psutil', 'gputil', 'psutil', 'WMI', 'pywin32']:
    os.system(f'pip install {pkg}')

# import installed modules
import wmi
import psutil
import GPUtil as GPU


__version__ = 1.0
_path = os.path.dirname(os.path.realpath(__file__))
print('Pgnite location path:', _path)


class pipe(threading.Thread):

    def __init__(self, function, wait, *args):
        self.wait = wait
        threading.Thread.__init__(self)
        self.func = function
        self.args = args
        self.stoprequest = threading.Event()

    def run(self):

        print('start {}-pipe...'.format(self.func.__name__))

        while not self.stoprequest.isSet():
            
            try: # important during init, otherwise crash
                self.func(*self.args)
                
                # listen frequently during waiting
                for i in range(int(10*self.wait)):
                    if self.stoprequest.isSet():
                        break
                    sleep(.1)
            
            except:
                pass

    def stop(self, timeout = None):
        print('stop updater')
        self.stoprequest.set()
        super(pipe, self).join(timeout)

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(rowspan=20, columnspan=20)
        self.setup()
        self.build()
        self.updater = pipe(self.update, 0.5)
        self.updater.start()
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        self.mainloop()

    def applyInput(self):
        # validate inputs
        if len(self.walletField.get()) != 42:
            self.infoVariable.set("Not a valid wallet!")
            return False
        elif len(self.poolField.get()) < 4:
            self.infoVariable.set("Not a valid pool port!")
            return False
        elif len(self.workerVariable.get()) == 0 or ' ' in self.workerVariable.get():
            self.infoVariable.set("Worker name needs at least 1 symbol & no spacing.")
            return False

        # apply the input
        self.infoVariable.set('Ignite Phoenix Miner ...')
        print(os.getcwd())
        with open(f'{_path}/PhoenixMiner/config.txt', 'w+') as f:
            f.write(f'-pool eu1.ethermine.org:{self.poolVariable.get()} -pool2 us1.ethermine.org:{self.poolVariable.get()} -wal {self.walletVariable.get()}.{self.workerVariable.get()} -log 2 -logdir {_path}/PhoenixMiner/log/ -logfile log.txt -gpow {self.gpuUsageVariable.get()}')
        return True

    def build(self):
        # ---- build gui ----
        # parameters
        bg="#0d0d0d"
        font=('Calibri', 10) # font size
        fontColor="#fff"
        warnColor="#ffdd00"
        eggWhite="#ddd"
        activeColor="#bf396d"

        # add logo seal
        self.master.iconbitmap(f'{_path}/static/logo.ico')

        # build general shape
        self.master.geometry('400x400')
        self.master.title(f'Pgnite {__version__} ETH UI')
        self.master.resizable(0, 0)
        self.master.configure(background=bg)
        for i in [0,1]:
            self.master.columnconfigure(i, weight=0)
            self.master.rowconfigure(i, weight=0)
        self.leftUpperFrame = tk.Frame(self.master, height=450, width=400, background=bg)
        self.leftUpperFrame.grid_propagate(0)
        self.leftUpperFrame.grid(row=0, column=0, columnspan=10, rowspan=20, sticky="NW")
        self.rightUpperFrame = tk.Frame(self.master, height=400, width=400, background=bg)
        self.rightUpperFrame.grid_propagate(0)
        self.rightUpperFrame.grid(row=0, column=1)
        self.leftLowerFrame = tk.Frame(self.master, height=50, width=400, background=bg)
        self.leftLowerFrame.grid_propagate(0)
        self.leftLowerFrame.grid(row=1, column=0)
        self.rightLowerFrame = tk.Frame(self.master, height=250, width=400, background=bg)
        self.rightLowerFrame.grid_propagate(0)
        self.rightLowerFrame.grid(row=1, column=1)

        # left upper (general info)
        self.workerLabel = tk.Label(self.leftUpperFrame, text="Worker Name", height=1, fg=fontColor, bg=bg)
        self.workerLabel.grid(row=0, column=0, padx=5)
        self.workerVariable = tk.StringVar()
        self.workerVariable.set(f'{getuser()}_donating_to_Pgnite')
        self.workerField = tk.Entry(self.leftUpperFrame, width=30, textvariable=self.workerVariable)
        self.workerField.grid(row=0, column=1, columnspan=8, sticky="W", pady=(5,0))

        self.walletLabel = tk.Label(self.leftUpperFrame, text="Wallet Address", height=1, fg=fontColor, bg=bg)
        self.walletLabel.grid(row=1, column=0, padx=5)
        self.walletVariable = tk.StringVar()
        self.walletVariable.set('0xC146f17afc36089ae030A5FB23420C6eBD0c4DF0')
        self.walletField = tk.Entry(self.leftUpperFrame, width=30, textvariable=self.walletVariable)
        self.walletField.grid(row=1, column=1, columnspan=8, sticky="W", pady=(5,0))

        self.poolLabel = tk.Label(self.leftUpperFrame, text="Pool Port", height=1, fg=fontColor, bg=bg)
        self.poolLabel.grid(row=2, column=0, padx=5)
        self.poolVariable = tk.StringVar()
        self.poolVariable.set('5555')
        self.poolField = tk.Entry(self.leftUpperFrame, width=5, textvariable=self.poolVariable)
        self.poolField.grid_propagate(0)
        self.poolField.grid(row=2, column=1, columnspan=8, sticky="W", pady=(5,0))

        self.skuLabel = tk.Label(self.leftUpperFrame, text="Card", height=1, fg=fontColor, bg=bg)
        self.skuLabel.grid(row=3, column=0, padx=5)
        self.skuVariable = tk.StringVar()
        self.skuLabel = tk.Label(self.leftUpperFrame, textvariable=self.skuVariable, bg=bg, fg=fontColor)
        self.skuLabel.grid_propagate(0)
        self.skuLabel.grid(row=3, column=1, columnspan=8, sticky="W", pady=10)
        self.skuVariable.set('No suitable card found.')
        for name in self.sys.Win32_VideoController(): # load the gpu name
            if 'nvidia' in name.Name.lower() or 'amd' in name.Name.lower() or 'intel' in name.Name.lower():
                self.skuVariable.set(name.Name) 

        self.gpuUsageLabel = tk.Label(self.leftUpperFrame, text="GPU Usage", height=2, fg=fontColor, bg=bg)
        self.gpuUsageLabel.grid(row=4, column=0, padx=5)
        self.gpuUsageVariable = tk.IntVar(0)
        self.gpuUsageScale = tk.Scale(self.leftUpperFrame, from_=10, to=100, orient=tk.HORIZONTAL, resolution=1, bg=bg, fg=fontColor, variable=self.gpuUsageVariable)
        self.gpuUsageScale.grid_propagate(0)
        self.gpuUsageScale.grid(row=4, column=1, columnspan=8, sticky="W")

        self.gpuStatusLabel = tk.Label(self.leftUpperFrame, text="GPU", height=1, fg=warnColor, bg=bg)
        self.gpuStatusLabel.grid(row=5, column=0, padx=5)
        self.gpuStatusVariable = tk.StringVar()
        self.gpuStatusVariable.set('-')
        self.gpuStatusLabel = tk.Label(self.leftUpperFrame, textvariable=self.gpuStatusVariable, bg=bg, fg=fontColor)
        self.gpuStatusLabel.grid_propagate(0)
        self.gpuStatusLabel.grid(row=5, column=1, columnspan=8, sticky="W")

        self.tempLabel = tk.Label(self.leftUpperFrame, text="Temperature", height=1, fg=fontColor, bg=bg)
        self.tempLabel.grid(row=6, column=0, padx=5)
        self.tempVariable = tk.StringVar()
        self.tempVariable.set('-')
        self.tempLabel = tk.Label(self.leftUpperFrame, textvariable=self.tempVariable, bg=bg, fg=fontColor)
        self.tempLabel.grid_propagate(0)
        self.tempLabel.grid(row=6, column=1, columnspan=8, sticky="W")

        self.memLabel = tk.Label(self.leftUpperFrame, text="Memory", height=1, fg=fontColor, bg=bg)
        self.memLabel.grid(row=7, column=0, padx=5)
        self.memVariable = tk.StringVar()
        self.memVariable.set('-')
        self.memLabel = tk.Label(self.leftUpperFrame, textvariable=self.memVariable, bg=bg, fg=fontColor)
        self.memLabel.grid_propagate(0)
        self.memLabel.grid(row=7, column=1, columnspan=8, sticky="W")

        self.infoVariable = tk.StringVar()
        self.infoVariable.set(f'Pgnite Version {__version__}')
        self.infoLabel = tk.Label(self.leftUpperFrame, textvariable=self.infoVariable, fg=warnColor, bg=bg)
        self.infoLabel.grid(row=8, column=0, columnspan=8, sticky="W", padx=20, pady=10)


        # left lower (general info)
        self.startButton = tk.Button(self.leftUpperFrame, text='mine', fg=bg, bg=eggWhite, width=20, command=self.buttonAction)
        self.startButton.grid_propagate(0)
        self.startButton.grid(row=9, column=1, padx=20, sticky="W")


        # right upper (general info)
        self.terminalPayload = ['Welcome']
        self.terminal = tk.Text(self.rightUpperFrame, width=70, bg=bg, fg=eggWhite, font=("Calibri", 7), highlightthickness=0, relief='flat')
        self.terminal.grid(row=0, column=0, sticky="nsew", pady=5, padx=20)

        # create a Scrollbar and associate it with terminal
        scrollb = ttk.Scrollbar(self, command=self.terminal.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.terminal['yscrollcommand'] = scrollb.set
    
    def buttonAction(self):
        if self.minerActive:
            self.master.geometry('400x400')
            self.startButton.configure(text='mine', bg="#ddd", fg="#0d0d0d")
            self.minerActive=False
            self.workerField.config(state='normal')
            self.walletField.config(state='normal')
            self.poolField.config(state='normal')
            self.gpuUsageScale.config(state='normal')
            self.infoVariable.set('')
            self.terminal.delete('1.0', tk.END)
            self.killMinerSubprocess()
        else:
            if self.applyInput():
                self.master.geometry('800x400')
                self.startButton.configure(text='stop', bg="#bf396d", fg="#ddd")
                self.minerActive=True
                self.workerField.config(state='disabled')
                self.walletField.config(state='disabled')
                self.poolField.config(state='disabled')
                self.gpuUsageScale.config(state='disabled')

                # ---- trigger miner ----
                self.invokeMinerSubprocess()

    def invokeMinerSubprocess(self):
        print('invoke')
        cmd = f'{_path}/PhoenixMiner/PhoenixMiner.exe -config {_path}/PhoenixMiner/config.txt'
        #self.process = Popen(['C:\\Windows\\System32\\runas.exe', '/noprofile', '/user:Administrator', "PhoenixMiner\\PhoenixMiner.exe"], stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf8', shell=True)
        self.process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf8', bufsize=1)

    def killMinerSubprocess(self):
        self.process.kill()
        self.process = None

    def nvidiaDetected(self):
        if self.targetGPU != None:
            return True
        return False
    
    def refreshUtilization(self):
        # when called will refresh the util
        self.targetGPU = GPU.getGPUs()[self.GPUid]
        self.tempVariable.set(f'{getattr(self.targetGPU,"temperature")} °C')
        self.gpuStatusVariable.set(f'{getattr(self.targetGPU,"load")} %')
        self.memVariable.set(f'{int(getattr(self.targetGPU, "memoryUtil"))} %')

    def setup(self):
        # setup all global objects
        self.sys = wmi.WMI()
        self.GPUid = None
        self.targetGPU = None
        self.minerActive = False
        self.process = None
        self.processHistory = []

        # find correct GPU (only NVIDIA is targeted)
        try:
            GPUs = GPU.getGPUs()
            for gpu in GPUs:
                try:
                    if 'geforce' in gpu.name.lower() or 'gtx' in gpu.name.lower():
                        print('GPU found:', gpu.name)
                        self.GPUid = GPUs.index(gpu)
                        print('index', self.GPUid)
                        self.targetGPU = gpu
                        break
                except Exception as e:
                    print(e)
        except:
            tk.messagebox.showerror(message="Setup Error: System has no valid GPU.")
    
    def quit(self):
        # stop loop
        self.master.destroy()
        self.updater.stop()

    def update(self):
        # many services are only available for NVIDIA cards
        if self.nvidiaDetected():
            self.refreshUtilization()

        # update process stdout
        if self.process != None:

            # read out the last 10 lines maybe from the log Path
            linesize = 10
            logPath = _path + '/PhoenixMiner/log/log.txt'
            with open(logPath, 'r') as f:
                stdout = f.read().split('\n')[-linesize:-1]
                stdout.remove('')
                print(stdout)
                if self.terminalPayload[-1] != stdout[-1]:
                    print('log change')
                    self.terminalPayload = stdout
                    self.terminal.insert(tk.INSERT, '\n'.join(self.terminalPayload))
                    self.terminal.see("end")

if __name__ == '__main__':
    Application(tk.Tk())