#!/usr/bin/env python3
#
# This file is part of LUNA.
#

from nmigen import Signal, Elaboratable, Module
from nmigen.lib.cdc import FFSynchronizer

from luna.gateware.platform import *
from luna.gateware.interface.spi import SPIDeviceInterface


class DebugSPIExample(Elaboratable):
    """ Hardware meant to demonstrate use of the Debug Controller's SPI interface. """


    def __init__(self):

        # Base ourselves around an SPI command interface.
        self.interface = SPIDeviceInterface(clock_phase=1)


    def elaborate(self, platform):
        m = Module()
        board_spi = platform.request("debug_spi")

        # Use our command interface.
        m.submodules.interface = self.interface

        sck = Signal()
        sdi = Signal()
        sdo = Signal()
        cs  = Signal()

        #
        # Synchronize each of our I/O SPI signals, where necessary.
        #
        m.submodules += FFSynchronizer(board_spi.sck, sck)
        m.submodules += FFSynchronizer(board_spi.sdi, sdi)
        m.submodules += FFSynchronizer(board_spi.cs,  cs)
        m.d.comb     += board_spi.sdo.eq(sdo)

        # Connect our command interface to our board SPI.
        m.d.comb += [
            self.interface.sck.eq(sck),
            self.interface.sdi.eq(sdi),
            sdo.eq(self.interface.sdo),
            self.interface.cs .eq(cs)
        ]

        # Turn on a single LED, just to show something's running.
        led = platform.request('led', 0)
        m.d.comb += led.eq(1)

        # Echo back the last received data.
        m.d.comb += self.interface.word_out.eq(self.interface.word_in)

        return m


if __name__ == "__main__":
    platform = LUNAPlatformR01()
    platform.build(DebugSPIExample(), do_program=True)
