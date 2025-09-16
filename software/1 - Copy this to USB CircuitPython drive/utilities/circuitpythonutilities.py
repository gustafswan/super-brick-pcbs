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

import sys, supervisor, usb_cdc

def bit_list_to_bytes(bit_list):
    if len(bit_list) % 8 != 0:
        raise ValueError("The list length must be a multiple of 8 bits")
    # Convert the list of bits to a single integer
    bit_string = ''.join(map(str, bit_list))
    bit_value = int(bit_string, 2)
    # Calculate the number of bytes
    num_bytes = len(bit_list) // 8
    # Pack the integer into the corresponding number of bytes
    return bit_value.to_bytes(num_bytes, 'big')


def bytes_to_bit_list(byte_list):
    bit_list = []
    for byte in byte_list:
        # Convert each byte to its binary representation and remove the '0b' prefix
        bits = bin(byte)[2:]
        # Manually pad the binary representation with leading zeros to ensure it is 8 bits long
        bits = '0' * (8 - len(bits)) + bits
        # Append each bit to the bit_list
        bit_list.extend(int(bit) for bit in bits)
    return bit_list

def int_to_bit_list(value, bit_length):
    # Convert the integer to a binary string and remove the '0b' prefix
    bit_string = bin(value)[2:]
    # Calculate the number of leading zeros needed
    leading_zeros = bit_length - len(bit_string)
    # Manually pad the binary string with leading zeros
    bit_string = '0' * leading_zeros + bit_string
    # Convert the binary string to a list of integers
    bit_list = [int(bit) for bit in bit_string]
    
    return bit_list


class USBSerialInterface:
    def __init__(self, console_or_data = 'console', echo = False):
        self.s = ''
        self.echo = echo
        if console_or_data == 'console':
            self.serial_bytes_available = lambda: supervisor.runtime.serial_bytes_available
            self.serial_read = lambda num_bytes: sys.stdin.read(num_bytes)
            self.serial_write = lambda write_str:  sys.stdout.write(write_str)
        elif console_or_data == 'data':
            self.serial_bytes_available = lambda: usb_cdc.data.in_waiting
            self.serial_read = lambda num_bytes: usb_cdc.data.read(num_bytes).decode('utf-8')
            self.serial_write = lambda write_str: usb_cdc.data.write(write_str.encode())
            # self.serial_write = lambda write_str:  sys.stdout.write(write_str)
        else:
            raise ValueError("console_or_data must be either 'console' or 'data'")

    def read(self, n):
        s = self.serial_read(n)
        if self.echo: self.write(s)
        return s

    def write(self, write_str):
        self.serial_write(write_str)

    def readline(self):
        """ Read a line from USB Serial (ending with either \r or \n), from either
        the "console" serial port or the "data" serial port. Non-blocking, and
         returns None until a full line is read at which point the full line is returend. """
        n = self.serial_bytes_available()
        if n > 0:                    # we got bytes!
            s = self.read(n)    # actually read it in
            self.s = self.s + s      # keep building the string up
            # print(f'self.s = {self.s.encode()}')
            if s.endswith('\n') or s.endswith('\r'): # got our end_char!
                return_string = self.s.strip()   # save for return
                self.s = ''          # Reset str to beginning
                if len(return_string) > 0: # Only return if not an empty command
                    return_string = return_string + "\n"
                    return return_string
        return None                  # no end_char yet
