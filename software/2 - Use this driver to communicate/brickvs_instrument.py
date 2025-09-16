#%%
import serial

class BrickVS(object):
    """Python class for the BrickVS isolated voltage source,
    written by Adam McCaughan"""
    def __init__(self, port, timeout=0.5):
        baudrate=115200
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
    
    def read(self):
        return self.serial.readline().decode().strip()
    
    def write(self, string):
        string = string+"\n"
        self.serial.write(string.encode())  # Write string to serial port

    def query(self, string):
        self.write(string)
        return self.read()

    def close(self):
        self.serial.close()
        
    def reset(self):
        self.write('*RST')

    def help(self):
        self.write('HELP')
        print(self.serial.readlines())

    def debug(self):
        self.write('DEBUG')
    
    def identify(self):
        return self.query('*IDN?')
    
    def set_voltage(self, voltage):
        self.query(f'VOLT {voltage}')

    def get_voltage(self):
        return float(self.query('VOLT?'))
    
    def set_output(self, enabled = True):
        if enabled is True:
            self.query('OUTPUT 1')
        else:
            self.query('OUTPUT 0')

    def get_output(self):
        return int(self.query('OUTPUT?')) == 1

# vs = BrickVS('COM10')
# print(vs.get_voltage())
# print(vs.set_voltage(3.54))
# print(vs.get_output())
# vs.serial.write('test\r'.encode())
# print(vs.identify())
