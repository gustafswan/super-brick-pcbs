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

from brick2brick import Brick2Brick
from circuitpythonutilities import USBSerialInterface
import board
import time
import microcontroller
from commandhandler import CommandHandler
from message import decode_message

__version__ = '1.0.0'
__date__ = 'Oct 2024'

class Brick:
    def __init__(self,
                 tx_pin,
                 rx_pin,
                 timeout,
                 baudrate,
                 location_id,
                 tx_oe_pin = None):
        self.usb_interface = USBSerialInterface(console_or_data = 'console', echo = False)
        self.handler = CommandHandler()
        self.b2b = Brick2Brick(tx_pin = tx_pin, rx_pin = rx_pin, timeout = timeout,
                               baudrate = baudrate, location_id = location_id,
                               tx_oe_pin = tx_oe_pin)

    def parent_event_loop(self):
                
        while True:
            # Non-blocking read, returns None if line not complete
            command_bytes = self.usb_interface.readline()
            # print(usb_interface.s)
            if command_bytes is not None:
                destination_id, command = decode_message(command_bytes)
                if destination_id == 0:
                    try:
                        response = self.handler.handle_command(command)
                        self.usb_interface.write(str(response) + "\n")
                    except Exception as e:
                        # print(f'Error: {e}\n')
                        self.usb_interface.write(f'Error: {e}\n')
                else:
                    self.b2b.send(command, destination_id = destination_id)
                    response = self.b2b.receive(force_read = True)
                    self.usb_interface.write(str(response) + "\n")
            time.sleep(0.0001)  # do something time critical

    def child_event_loop(self):
        # Wait for a command from the parent
        while True: 
            try:
                command = self.b2b.receive()
                if command is not None:
                    print(f'Command received: {command}, sending response')
                    response = self.handler.handle_command(command)
                    self.b2b.send(response, destination_id = 0)
            except ValueError as e:
                print(f'Error: {e}')
                command = None
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                break

