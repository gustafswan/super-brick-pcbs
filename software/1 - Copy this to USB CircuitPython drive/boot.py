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

# Disable showing CIRCUITPY drive when the board is connected to the computer
# If you want to see the CIRCUITPY drive, use the "DEBUG" command
import storage
import supervisor
# storage.disable_usb_drive()
# supervisor.runtime.autoreload = False
supervisor.set_usb_identification(manufacturer = 'McCaughan', 
                                  product = 'BrickVS', 
                                  vid = 0xD1C9, 
                                  pid = 0x5000)




# import usb_cdc
# usb_cdc.enable(console=True, data=True)