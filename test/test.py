# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

class MyHash:
    def __init__(self):
        self.cur = 0x42

    def add_byte(self, val):
        combine = self.cur ^ val
        mix = ((combine << 4) | (combine >> 4)) & 0xFF
        self.cur = combine ^ mix


async def verify_one_byte(dut, expected, byte):
    if isinstance(byte, str):
        assert len(byte) == 1
        byte = ord(byte)

    dut.ui_in.value = int(byte)
    expected.add_byte(int(byte))
    await ClockCycles(dut.clk, 2)
    assert dut.uo_out.value == expected.cur

async def verify_one_byte_nochange(dut, expected, byte):
    if isinstance(byte, str):
        assert len(byte) == 1
        byte = ord(byte)

    dut.ui_in.value = int(byte)
    await ClockCycles(dut.clk, 2)
    assert dut.uo_out.value == expected.cur


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    assert dut.uo_out.value == 0x42

    dut._log.info("Test project behavior")

    expected = MyHash()

    dut.uio_in.value = 0x01 # Enable accum
    await verify_one_byte(dut, expected, 'h')
    await verify_one_byte(dut, expected, 'e')
    await verify_one_byte(dut, expected, 'l')
    await verify_one_byte(dut, expected, 'l')
    await verify_one_byte(dut, expected, 'o')

    dut.uio_in.value = 0x0 # Disable accum
    await verify_one_byte_nochange(dut, expected, 'w')
    await verify_one_byte_nochange(dut, expected, 'o')
    await verify_one_byte_nochange(dut, expected, 'r')
    dut.uio_in.value = 0x1 # Enable accum
    await verify_one_byte(dut, expected, 'l')
    await verify_one_byte(dut, expected, 'd')

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
