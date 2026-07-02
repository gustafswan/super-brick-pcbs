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

from circuitpythonutilities import bit_list_to_bytes, bytes_to_bit_list, int_to_bit_list
import board
import digitalio
import busio
import time
from adafruit_bus_device.spi_device import SPIDevice



### AD5781 constants
# Table 8. Decoding the Input Shift Register
DAC_REGISTER = [0,0,1]
CONTROL_REGISTER = [0,1,0]
CLEARCODE_REGISTER = [0,1,1]
SOFTWARE_CONTROL_REGISTER = [1,0,0]
IDX_R1W0 = (0,1)
IDX_REGISTER = (1,4)
IDX_DAC_DATA = (4,22)
# Control register bits
IDX_LINCOMP = (14,18)
IDX_SDO_DISABLE = (18,19)
IDX_2S_COMPLEMENT = (19,20)
IDX_DAC_TRISTATE = (20,21)
IDX_GROUND_CLAMP = (21,22)
IDX_RBUF = (22,23)



class AD5781:
    def __init__(self,
                 clk_speed,
                 out_en,
                 sclk,
                 sdin,
                 sdo,
                 cs):
            
        self.relay = digitalio.DigitalInOut(out_en)
        self.relay.direction = digitalio.Direction.OUTPUT
        self.relay.value = False
        # Create the SPI device
        spi_bus = busio.SPI(sclk, sdin, sdo)
        self.spi = SPIDevice(spi_bus, digitalio.DigitalInOut(cs), cs_active_value = False,
                             baudrate = clk_speed, phase = 0, polarity = 1)
        # Setup the DAC to work properly in the gain-of-two configuration
        self.write_control_register(lincomp_20v = True, sdo_disable = False, binary_coding = True, dac_tristate = False, ground_clamp = False, rbuf = False)
        self.set_dac_voltage(0)


    def write_with_cs(self, bit_list):
        """ Writes a series of bits to the SPI device """ 
        # Convert the bit string to bytes
        write_bytes = bit_list_to_bytes(bit_list)
        # Write the bytes to the SPI device, dropping the CS line low before and
        with self.spi as spi:
            spi.write(write_bytes)


    def query_with_cs(self, bit_list):
        """ Writes a series of bits to the SPI device and then performs a read
        operation, returning the bits in the read response """ 
        # Convert the bit string to bytes
        write_bytes = bit_list_to_bytes(bit_list)
        # Write the bytes to the SPI device, dropping the CS line low before and high after
        with self.spi as spi:
            spi.write(write_bytes)
        # Read the response from the SPI device and convert it to a bit list
        result = bytearray(4)
        with self.spi as spi:
            spi.readinto(result)
        result_bit_list = bytes_to_bit_list(result)
        return result_bit_list


    def read_control_register(self):
        bit_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        bit_list[IDX_R1W0[0]:IDX_R1W0[1]] = [1]
        bit_list[IDX_REGISTER[0]:IDX_REGISTER[1]] = CONTROL_REGISTER
        read_bits = self.query_with_cs(bit_list)
        return read_bits


    def write_control_register(self, lincomp_20v = True, sdo_disable = False, binary_coding = True, dac_tristate = False, ground_clamp = False, rbuf = False):
        bit_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        bit_list[IDX_R1W0[0]:IDX_R1W0[1]] = [0]
        bit_list[IDX_REGISTER[0]:IDX_REGISTER[1]] = CONTROL_REGISTER
        if lincomp_20v is True:
            bit_list[IDX_LINCOMP[0]:IDX_LINCOMP[1]] = [1,1,0,0]
        else:
            bit_list[IDX_LINCOMP[0]:IDX_LINCOMP[1]] = [0,0,0,0]
        bit_list[IDX_SDO_DISABLE[0]:IDX_SDO_DISABLE[1]] = [int(sdo_disable)]
        bit_list[IDX_2S_COMPLEMENT[0]:IDX_2S_COMPLEMENT[1]] = [int(binary_coding)]
        bit_list[IDX_DAC_TRISTATE[0]:IDX_DAC_TRISTATE[1]] = [int(dac_tristate)]
        bit_list[IDX_GROUND_CLAMP[0]:IDX_GROUND_CLAMP[1]] = [int(ground_clamp)]
        bit_list[IDX_RBUF[0]:IDX_RBUF[1]] = [int(rbuf)]
        return self.query_with_cs(bit_list)


    def read_dac_register(self):
        bit_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        bit_list[IDX_R1W0[0]:IDX_R1W0[1]] = [1]
        bit_list[IDX_REGISTER[0]:IDX_REGISTER[1]] = DAC_REGISTER
        read_bits = self.query_with_cs(bit_list)
        return read_bits


    def write_dac_register(self, dac_bits):
        bit_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        bit_list[IDX_R1W0[0]:IDX_R1W0[1]] = [0]
        bit_list[IDX_REGISTER[0]:IDX_REGISTER[1]] = DAC_REGISTER
        bit_list[IDX_DAC_DATA[0]:IDX_DAC_DATA[1]] = dac_bits
        read_bits = self.query_with_cs(bit_list)
        return read_bits


    def set_dac_voltage(self, v):
        if v > 10 or v < -10:
            raise ValueError("Voltage must be between -10 and 10 V")
        dac_code = int(round((v+10)/20*(2**18-1)))
        dac_bits = int_to_bit_list(dac_code, 18)
        self.write_dac_register(dac_bits)

    def read_dac_code_as_voltage(self):
        read_bits = self.read_dac_register()
        dac_code = int(''.join(map(str, read_bits[IDX_DAC_DATA[0]:IDX_DAC_DATA[1]])), 2)
        voltage = 20*dac_code/(2**18-1) - 10
        return voltage

    def set_relay_state(self, connected):
        if connected == True:
            self.relay.value = True
        else:
            self.relay.value = False

    def get_relay_state(self):
        return self.relay.value


if __name__ == "__main__":
    # Example usage

    vs = AD5781(
        clk_speed = 1000000,
        out_en = board.GP11,
        sclk =  board.GP2,
        sdin =  board.GP3,
        sdo =  board.GP0,
        cs =  board.GP1)

    print(vs.read_control_register())
    result = vs.write_control_register(lincomp_20v = True, sdo_disable = False, binary_coding = True, dac_tristate = False, ground_clamp = False, rbuf = False)
    # print(result)

    v = -3.5
    print(f'Setting DAC voltage: to {v}')
    vs.set_dac_voltage(v)
    print('Reading DAC voltage:', vs.read_dac_code_as_voltage())
