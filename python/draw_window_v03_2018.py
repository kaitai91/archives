
import sys
import copy
import tkinter as tk
from tkinter.ttk import Frame, Style
from tkinter import StringVar, IntVar
from tkinter import Radiobutton, Entry

import bt_threading_v03 as bt

WINDOW = None
BLUE = None
SYNC = False
NAME = "RoboMapper"
VERSION = "0.02a"

#min height and width
HEIGHT = 800
WIDTH = 1280
DELAY = 50
SYMBOLS = [""]
#SYMBOLS = [0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0]

class MainWindow(tk.Tk):
    '''
    UI and the base elements for the content.

    '''

    def __init__(self, *args,**kwargs):
        '''
        Creates an GUI instance and setup for it.

        '''
        self.i = 0

        tk.Tk.__init__(self,*args,**kwargs)

        #title
        tk.Tk.wm_title(self, NAME+" - v."+VERSION)     
        tk.Tk.minsize(self,width=WIDTH, height=HEIGHT)


        #WINDOW GEOMETRY

        #Background style
        Style().configure("TFrame", background="#999")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)         
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)


        #CANVAS
        self.canv=RoboCanvas(self)
        self.canv.grid_rowconfigure(0,weight=1)
        self.canv.grid_columnconfigure(0,weight=1)
        self.canv.grid(row=0,column=0, sticky="nsew")

        #BUTTON(S) FOR DEBUG
        self.create_debug_buttons()
        #self.create_control_panel()

        self.panel = PanelFrame(self)
        self.panel.grid(row=1,column=0, sticky="nsew")
        
        #initial call
        self.canv.read_input()

    def create_button(self,title,cmd,cmd_args=None, *args,**kwargs):
        '''
        Creates a button with given command.
        '''
        if cmd_args != None:
            return tk.Button(self,text=title,justify="left",
                          command=lambda:cmd(*cmd_args))
        else:
            return tk.Button(self,text=title,justify="left",
                          command=cmd)

    def create_debug_buttons(self):
        '''Creates buttons to imitate "arbitrary" incoming BlueTooth signal.
           (Requires that BLUE is defined as global BlueReader object.) 
        '''
        NAMES_ARGS = [("CREATE INPUT1",[[0,0,1,0,0,2,0,0,0],]),\
                      ("CREATE INPUT2",[[0,0,2,0,0,2,0,0],]),\
                      ("FORWARD",[[0,],]),\
                      ("TURN RIGHT",[[2,0],]),\
                      ("TURN LEFT",[[1,0],])]
        
        for b in range(len(NAMES_ARGS)):
            self.create_button(NAMES_ARGS[b][0],BLUE.add_symbols, \
                               cmd_args=NAMES_ARGS[b][1]) \
                               .grid(row=b+1,column=1, sticky="nsew")
        #b1 = self.create_button("CREATE INPUT1",BLUE.add_symbols, cmd_args=[[0,0,1,0,0,2,0,0,0],])
        #b1.grid(row=1,column=1, sticky="nsew")



class PanelFrame(tk.Frame):
    def __init__(self, parent):

        tk.Frame.__init__(self,parent)
        self.parent = parent
        
        CTRL_BUTTONS =["TOGGLE BT","SET PORT", "DELAY (seconds)"]
        #use radiobuttons to set one thing at once? -toggle bt starts the run...
        ENTRIES = ["",str(use_Reader(1)),str(use_Reader(3))]

        for i in range(3):
            print(ENTRIES[i])

        buttons = []
        self.entries = []
        self.e_vars = []
        self.var = IntVar()
        #self.colconfigure(0, weight=1)
        #self.colconfigure(1, weight=0)
        self.prev = 0
        self.active = 0
        self.var.set(0)
        
        
        for i in range(len(CTRL_BUTTONS)):
            el = self.create_button_frame(CTRL_BUTTONS[i],ENTRIES[i],i)
            buttons.append(el)
            e_var = StringVar()
            #print(ENTRIES[i])#debug
            e_var.set(ENTRIES[i])
            e = Entry(self, textvariable=e_var)

            self.entries.append(e)
            self.e_vars.append(e_var)

            #self.rowconfigure(1, weight=1)
            el.grid(row=0,column=i, sticky="nsew")
            e.grid(row=1,column=i, sticky="nsew")

            
        self.prev_vars = []
        for ev in self.e_vars:
            self.prev_vars.append(ev.get())

        #disable useless entry under "toggle BT"
        self.entries[0].config(state=tk.DISABLED)

        self.activate_entries()
        self.var.trace("w", self.activate_entries)
        

    def create_button_frame(self,b_name,entry_text,index):

        button = Radiobutton(self, text=b_name,indicatoron=False,\
                        variable=self.var, value=index)

        return button

    def activate_entries(self,*args):


        #CTRL_BUTTONS =["TOGGLE BT","SET PORT", "DELAY (seconds)"]
        
        self.active = self.var.get()
        for i in range(1,len(self.e_vars)):
            if i == self.active:
                #self.entries[i].enable()
                self.prev_vars[i] = self.e_vars[i].get()
                self.entries[i].config(state=tk.NORMAL)

            else:
                #copy the old values (just debug)
                self.prev_vars[i] = self.e_vars[i].get()
                #self.e_vars[i].set(self.prev_vars[self.active])
                #self.entries[i].disable()
                self.entries[i].config(state=tk.DISABLED)

        if self.active == 0:
            manage_Reader(1)#connect

        else:
            manage_Reader(2)#disconnect

        if self.active == 1: #set port
            #print(self.e_vars[1].get())#debug
            if (self.e_vars[1].get().isalnum()):
                setup_Reader(2,self.e_vars[1].get())

        elif self.prev == 2: #set delay
            #print(self.e_vars[2].get())#debug
            if (self.e_vars[2].get().isdigit() and self.e_vars[2].get().isalnum()):
                setup_Reader(4,int(self.e_vars[2].get()))

        #if self.prev == self.active:
         #   self.var.set(len(self.e_vars))
        self.prev = self.active
          
    
class RoboCanvas(tk.Canvas):
    '''Canvas Class for mapping the robot movement'''
    def __init__(self, parent):

        tk.Canvas.__init__(self,parent)
        self.parent = parent
        self.prev = (WIDTH/2,HEIGHT/2)
        self.current = (WIDTH/2,HEIGHT/2)
        self.dest = (WIDTH/2,HEIGHT/2)
        self.direction = "up"
        self.step = 10
        self.create_oval((self.current[0]-5,self.current[1]-5,self.current[0]+5,self.current[1]+5),fill="black")


    def turn_left(self):
        '''Changes the direction to the left related to the current heading.'''
        if self.direction=="up":
            self.direction="left"
        elif self.direction=="left":
            self.direction="down"
        elif self.direction=="right":
            self.direction="up"
        elif self.direction=="down":
            self.direction="right"


    def turn_right(self):
        '''Changes the direction to the right related to the current heading.'''
        if self.direction=="up":
            self.direction="right"
        elif self.direction=="left":
            self.direction="up"
        elif self.direction=="right":
            self.direction="down"
        elif self.direction=="down":
            self.direction="left"


    def fwd(self):
        '''Sets the destination in front of the robot'''
        if self.direction=="up":
            self.dest = (self.current[0],self.current[1]+self.step)
        elif self.direction=="left":
            self.dest = (self.current[0]-self.step,self.current[1])
        elif self.direction=="right":
            self.dest = (self.current[0]+self.step,self.current[1])
        elif self.direction=="down":
            self.dest = (self.current[0],self.current[1]-self.step)


    def update_location(self):
        '''Moves the robot to the current location on the map (Canvas).'''
        self.create_line((self.prev, self.current),width=5, fill="black",joinstyle=tk.MITER, cap=tk.ROUND)
        self.create_line((self.current, self.dest),width=5, fill="black",joinstyle=tk.MITER, cap=tk.ROUND)
        avg = ((self.dest[0]+self.current[0])/2+1,(self.dest[1]+self.current[1])/2)
        self.create_line((avg, self.dest),width=2, fill="red",joinstyle=tk.BEVEL, cap = tk.ROUND)
        self.create_oval((self.dest[0]-2,self.dest[1]-2,self.dest[0]+2,self.dest[1]+2),fill="red",outline="")


    def check_directions(self,item):
        '''Checks what robot is doing based on input'''
        if item==0: #fwd
            self.fwd() 

        elif item==2: #left
            self.turn_left()
            

        elif item==1: #right
            self.turn_right()


    def update_buffer_and_delay(self,buffer):
        '''Updates the input buffer and adjusts the delay in certain conditions.'''
        global DELAY
        global SYNC
        if len(buffer) == 0:
                DELAY = min(max(1000,DELAY * 2), 5000)#minimum wait time 1s, max wait time 10s
                print("BlueTooth buffer is empty. Retrying in "+str(DELAY/1000)+" seconds.")

        elif len(SYMBOLS) == 1:
            DELAY = 1000
            #DEFAULT: lets assume the signal is send to BlueTooth device once per second.
            #         this is done to remove unnecessary messages about buffer being empty.
            SYNC = True
            
        elif len(SYMBOLS) > 1:
            #If the signal is sent more often than expected (less than 10 times a second),
            #try to catch up.
            #This (also) happens, if DELAY is set longer than BT signal is reseived
            DELAY = 100
            SYNC = False
            
             
    def read_input(self):
        '''Reads one symbol from input buffer and acts depending on what the input is.
           
           If the input buffer is empty, tries to read more data from global BlueReader object "BLUE".
           If there is (are) symbols to read, maps the robot motion on canvas to illustrate its movement
           on its environment.
        '''

        global SYMBOLS

        if 0<len(SYMBOLS):
            self.check_directions(SYMBOLS.pop(0))
            self.update_location()
            
            self.prev = copy.deepcopy(self.current)
            self.current = copy.deepcopy(self.dest)

        else:
            SYMBOLS = BLUE.get_symbols()
            self.update_buffer_and_delay(SYMBOLS)

        #loop call
        self.parent.after(DELAY, self.read_input)


def manage_Reader(identifier, reader=BLUE):
    ''' Wrapper used to call different functions for an instance
        BlueReader class.

        identifier: Identifies the function to be called.
        0 : BLUE.start
        1 : BLUE.connect
        2 : BLUE.disconnect
        3 : BLUE.restart
        4 : BLUE.shutdown

    '''

    COMMANDS = [BLUE.start, BLUE.connect, BLUE.disconnect, \
                BLUE.restart, BLUE.shutdown] 

    if identifier not in range(len(COMMANDS)):
        print("Varning! Invalid function identifier.")
        return
    print(COMMANDS[identifier])
    COMMANDS[identifier]()

def setup_Reader(identifier, value, reader=BLUE):
    ''' Wrapper used to call different functions for an instance
        BlueReader class.

        identifier: Identifies the function to be called.
        0 : BLUE.reset_symbols
        1 : BLUE.add_symbols
        2 : BLUE.set_port
        3 : BLUE.set_BRate
        4 : BLUE.set_delay

    '''
    
    COMMANDS = [BLUE.reset_symbols, BLUE.add_symbols, BLUE.set_port, BLUE.set_BRate, \
                BLUE.set_delay] 

    if identifier not in range(len(COMMANDS)):
        print("Varning! Invalid function identifier.")
        return
    print(COMMANDS[identifier])
    COMMANDS[identifier](value)

def use_Reader(identifier, reader=BLUE):
    ''' Wrapper used to call different functions for an instance
        BlueReader class.

        identifier: Identifies the function to be called.
        0 : BLUE.get_symbols
        1 : BLUE.get_port
        2 : BLUE.get_BRate
        3 : BLUE.get_delay

    '''
    
    COMMANDS = [BLUE.get_symbols, BLUE.get_port, BLUE.get_BRate, \
                BLUE.get_delay] 

    if identifier not in range(len(COMMANDS)):
        print("Varning! Invalid function identifier.")
        return
    print(COMMANDS[identifier])
    return COMMANDS[identifier]()


def main():
    
    
    global WINDOW
    global BLUE
    BLUE = bt.BlueReader() #define BLUE before window
    WINDOW = MainWindow()
    BLUE.start()
    WINDOW.mainloop()
    BLUE.shutdown()
    BLUE.join()

    print("\nThanks For Using Our Program.")

if __name__ == "__main__":
    main()
