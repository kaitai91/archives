

from threading import Thread
import sys
import serial
import time

class BlueReader(Thread):
    '''Class defined to read signal from serial port. Implemented for a BlueTooth signal reading, may be used for other serial input as well.'''
    def __init__(self, name="BlueReader", s_port ='COM5', b_rate = 38400, delay = 0.01, symbols = [], disconnect = True):
        super(BlueReader,self).__init__()

        #items needed for connection
        self.name= name
        self.__s_port = s_port
        self.__b_rate = b_rate
        self.__delay = delay #how often the signal is read (every X seconds)
        
        #items needed for drawing
        self.__symbols = symbols
        self.__disconnect = disconnect
        self._end = False

    def run(self):

        while not self._end:
            if not self.__disconnect:
                try:
                    ser = serial.Serial(
                            port=self.__s_port,\
                            baudrate=self.__b_rate,\
                            parity=serial.PARITY_NONE,\
                            stopbits=serial.STOPBITS_ONE,\
                            bytesize=serial.EIGHTBITS,\
                                timeout=0)
                except serial.SerialException:
                    print("Error: Could not access port \""+self.__s_port+"\".",file=sys.stderr)
                    self.__disconnect = True
                

                if not self.__disconnect:
                    print("Connected to: " + ser.portstr + ".")

                while(not self.__disconnect): #read input once every second (time.sleep(1))
                    symbol = read_input(ser)
                    #print(symbol) #for debugging
                    if symbol.isdigit() and symbol.isalnum(): #to make sure we have a (non-negative) integer
                        self.__symbols.append(int(symbol))
                    
                    time.sleep(self.__delay)

                if "ser" in locals():
                    ser.close()
                    print("Disconnected from: " + ser.portstr + ".")
                    del(ser)

            #else:
                #we are not connecting /reading data

        print("Thread: "+self.name+" has shutdown.")

    def shutdown(self):
        '''Shutdowns the thread.'''
        self.disconnect()
        self._end = True

    def stop(self):
        '''Deprecated - Use shutdown instead.'''
        self.shutdown()
    
    def disconnect(self):
        '''Disconnects from current.'''
        self.__disconnect = True

    def connect(self):
        '''(Re)connects to a serial.'''
        self.__disconnect = False
        
    def reset_symbols(self):
        '''Resets the symbol buffer.'''
        self.__symbols = []

    #BLUE.add_symbols([0,0,1,0,0,2,0,0,0])
    def add_symbols(self,new_symbols):
        '''Appends an array of symbols to symbol list.

        (Use this for debugging only.)
        '''
        self.__symbols += new_symbols
    def restart(self):
        '''Resets the connection and the symbol buffer and reconnects.'''
        if not self.__disconnect:
            self.disconnect()
            time.sleep(self.__delay)

        reset_symbols()
        
    
    def get_symbols(self):
        '''Returns the contents of symbol buffer and empties it.'''

        #done with queue to remove chances for simultaneous read and write
        #(consider single write and read only)
        helper = []
        if 0 < len(self.__symbols):
            for i in range(len(self.__symbols)):
                helper.append(self.__symbols.pop(0))

        return helper

    def set_port(self,new_port):
        '''Set port for connetion (such as 'COM1')'''
        self.__s_port = new_port

    def get_port(self):
        '''Returns connection port.'''
        return self.__s_port

    def set_BRate(self,new_rate):
        '''Specifies the bitrate to be used.'''
        self.__b_rate = new_rate

    def get_BRate(self):
        '''Returns bitrate.'''
        return self.__b_rate

    def set_delay(self,new_delay):
        '''Defines the frequency for signal reading (in seconds).'''
        self.__delay = new_delay

    def get_delay(self):
        '''Returns the signal reading frequency (in seconds).'''
        return self.__delay

def read_input(serial):
    '''Reads line from serial.'''
    line = serial.readline()
    symbol = line.decode('utf-8')
    symbol = symbol.strip()
    return symbol


def main():
    b = BlueReader()
    b.start()
    time.sleep(min(max(2,10*b.get_delay()),10))
    print("Shutting down..")
    b.shutdown()
    b.join()
    print("All Clear.")

if __name__ == "__main__": 
    main()
