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

import binascii

def encode_message(destination_id, command):
    """ Encondes a command as
      <2 bytes destination_id hex>
      <8 bytes CRC hex>
      <N bytes message>
      <1 byte newline termination character> 
    """
    # Convert the destination_id to hex bytes
    destination_id_hex_bytes = binascii.hexlify((destination_id+128).to_bytes(1,'big'))
    command_bytes = command.encode('utf-8')
    # Calculate the CRC of both the destination_id and the command
    crc = binascii.crc32(destination_id_hex_bytes)
    crc = binascii.crc32(command_bytes, crc)
    # Convert CRC to hex bytes
    crc_hex_bytes = binascii.hexlify((crc).to_bytes(4,'big'))
    # print(f'Sending: destination_id={destination_id}, crc={crc}')
    return [destination_id_hex_bytes, crc_hex_bytes, command_bytes, b'\n']


def decode_message(message_bytes):
    """ Parse a message from a string to a dictionary. """
    # message = message_bytes.decode('utf-8')
    # Check that the message ends properly with the termination character
    if message_bytes[-1] != 10: # 10 == b'\n'
        raise ValueError(f'message incomplete; did not end with {b'\n'}; got {message_bytes[-1]}')
    # Split the message into its components
    destination_id_hex_bytes = message_bytes[0:2]
    crc_hex_bytes = message_bytes[2:10]
    command_bytes = message_bytes[10:-1]
    # Decode each component
    destination_id = int.from_bytes(binascii.unhexlify(destination_id_hex_bytes), 'big') - 128
    received_crc = int.from_bytes(binascii.unhexlify(crc_hex_bytes), 'big')
    command = command_bytes.decode('utf-8')
    # Compare the received CRC data to the locally-calculated CRC
    crc = binascii.crc32(destination_id_hex_bytes)
    crc = binascii.crc32(command_bytes, crc)
    if crc != received_crc:
        raise ValueError(f'Command CRC32 checksum failed, received CRC32 of {received_crc} but calculated CRC32 of {crc}')
    return destination_id, command

# # Function to concatenate bytes
# def concatenate_bytes(*args):
#     return b''.join(args)

# x = encode_message(destination_id = 4, command = 'abc')
# message_bytes = concatenate_bytes(*x)
# decode_message(message_bytes)