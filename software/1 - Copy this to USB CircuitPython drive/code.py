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
__date__ = 'Jul 2026'

usb_interface = USBSerialInterface(console_or_data = 'console', echo = False)

out_en = board.GP1 # Note in this design, all of the output channels share the same out_en signal
sclk   = board.GP2
sdin   = board.GP3
sdo    = board.GP0

handler = CommandHandler()
vs1_1 = AD5781(cs=board.GP29, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs1_2 = AD5781(cs=board.GP23, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs1_3 = AD5781(cs=board.GP4 , clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs1_4 = AD5781(cs=board.GP10, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs2_1 = AD5781(cs=board.GP28, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs2_2 = AD5781(cs=board.GP22, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs2_3 = AD5781(cs=board.GP5 , clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs2_4 = AD5781(cs=board.GP11, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs3_1 = AD5781(cs=board.GP27, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs3_2 = AD5781(cs=board.GP22, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs3_3 = AD5781(cs=board.GP6 , clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs3_4 = AD5781(cs=board.GP12, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs4_1 = AD5781(cs=board.GP26, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs4_2 = AD5781(cs=board.GP20, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs4_3 = AD5781(cs=board.GP7 , clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs4_4 = AD5781(cs=board.GP13, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs5_1 = AD5781(cs=board.GP25, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs5_2 = AD5781(cs=board.GP19, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs5_3 = AD5781(cs=board.GP8 , clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
vs5_4 = AD5781(cs=board.GP14, clk_speed=1e6, out_en=out_en, sclk=sclk, sdin=sdin, sdo=sdo)
  

""" vs_list is indexed by the dsub connector pin number. """
vs_list = {
    1  : vs1_1, 
    2  : vs1_2, 
    #3 : GND
    4  : vs1_3, 
    5  : vs1_4,
    6  : vs2_1,
    7  : vs2_2,
    #8 : GND
    9  : vs2_3,
    10 : vs2_4,
    11 : vs3_1,
    12 : vs3_2,
    #13: Not connected
    14 : vs3_3,
    15 : vs3_4,
    16 : vs4_1,
    17 : vs4_2,
    #18: GND
    19 : vs4_3,
    20 : vs4_4,
    21 : vs5_1,
    22 : vs5_2,
    #23: GND
    24 : vs5_3,
    25 : vs5_4}


@handler.register_command('*IDN?', "Returns the device identification string")
def identify():
    """ Note, when connecting to multiple bricks, it is much easier to identify the brick by their unique
    serial number to establish a connection. This is beacuse the com number and a Visa ASRL number do not
    always match. """
    return f"TODO, REPLACE WITH SERIAL NUMBER"



@handler.register_command('CRED?', "Returns the string crediting Adam for his desing")
def identify():
    f"Super-Brick module by Adam McCaughan, Gus Swansen, version {__version__} ({__date__})"


@handler.register_command('*RST', "Resets the voltage to 0V and disables the output")
def reset():
    for vs in vs_list.values():
        vs.set_dac_voltage(0)
        vs.set_relay_state(False)
    return "Reset complete"


@handler.register_command('VOLT', 
""" Sets the voltage from -10V to 10V. Example: 'VOLT 2.7' or 'VOLT -1.5e-2' """)
def set_voltage(v, channel):
    vs = vs_list[channel]
    vs.set_dac_voltage(float(v))
    return float(v)

@handler.register_command('VOLT?', "Reads back the current voltage setting")
def get_voltage(channel):
    vs = vs_list[channel]
    return vs.read_dac_code_as_voltage()

@handler.register_command('OUTPUT', 
""" Enables (1) or disables (0) the output. When the output is \
disabled, a relay is opened and the output is disconnected \
from the voltage source. Example: 'OUTPUT 1' or 'OUTPUT 0' """)
def set_relay(v, channel):
    vs = vs_list[channel]
    if v == '1':
        vs.set_relay_state(True)
    elif v == '0':
        vs.set_relay_state(False)
    else:
        raise ValueError("OUTPUT must be in the form 'OUTPUT 1' or 'OUTPUT 0'")
    return v

@handler.register_command('OUTPUT?', 
""" Reads back the current output state. """)
def get_relay(channel):
    vs = vs_list[channel]
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
