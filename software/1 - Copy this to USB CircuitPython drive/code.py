# This file is part of BrickVS by Adam McCaughan.
#
# BrickVS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BrickVS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BrickVS.  If not, see <https://www.gnu.org/licenses/>.


from ad5781 import AD5781
from circuitpythonutilities import USBSerialInterface
import board
import time
import microcontroller
from commandhandler import CommandHandler

__version__ = '1.0.0'
__date__ = 'Oct 2024'

usb_interface = USBSerialInterface(console_or_data = 'console', echo = False)


handler = CommandHandler()
vs = AD5781(
    spi_clock_speed = 1000000,
    relay_pin = board.GP14,
    spi_clock_pin =  board.GP2,
    spi_mosi_pin =  board.GP3,
    spi_miso_pin =  board.GP0,
    spi_cs_pin =  board.GP1)





@handler.register_command('*IDN?', "Returns the device identification string")
def identify():
    return f"BrickVS module by Adam McCaughan, version {__version__} ({__date__})"


@handler.register_command('*RST', "Resets the voltage to 0V and disables the output")
def reset():
    vs.set_dac_voltage(0)
    vs.set_relay_state(False)
    return "Reset complete"


@handler.register_command('VOLT', 
""" Sets the voltage from -10V to 10V. Example: 'VOLT 2.7' or 'VOLT -1.5e-2' """)
def set_voltage(v):
    vs.set_dac_voltage(float(v))
    return float(v)

@handler.register_command('VOLT?', "Reads back the current voltage setting")
def get_voltage():
    return vs.read_dac_code_as_voltage()

@handler.register_command('OUTPUT', 
""" Enables (1) or disables (0) the output. When the output is \
disabled, a relay is opened and the output is disconnected \
from the voltage source. Example: 'OUTPUT 1' or 'OUTPUT 0' """)
def set_relay(v):
    if v == '1':
        vs.set_relay_state(True)
    elif v == '0':
        vs.set_relay_state(False)
    else:
        raise ValueError("OUTPUT must be in the form 'OUTPUT 1' or 'OUTPUT 0'")
    return v

@handler.register_command('OUTPUT?', 
""" Reads back the current output state. """)
def get_relay():
    return int(vs.get_relay_state())

@handler.register_command('DEBUG', 
""" Enters debug mode, giving access to the file system and preventing \
code from automatically running. """)
def enter_debug():
    microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
    microcontroller.reset()


while True:
     # Non-blocking read, returns None if line not complete
    command = usb_interface.readline()
    # print(usb_interface.s)
    if command is not None:
        try:
            response = handler.handle_command(command)
            usb_interface.write(str(response) + "\n")
        except Exception as e:
            # print(f'Error: {e}\n')
            usb_interface.write(f'Error: {e}\n')
    time.sleep(0.0001)  # do something time critical
