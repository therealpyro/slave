#  -*- coding: utf-8 -*-

"""
The n5182a module implements an interface for the Agilent N5182A MXG
Signal Generator.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import collections

from slave.driver import Command, Driver
from slave.iec60488 import IEC60488
from slave.types import Boolean, Enum, Float, Integer, Mapping, \
                        Register, Set, String

class AmplitudeModulation(Driver):
    """Implements the amplitude modulation subsystem of the N5182A signal
    generator.
    """
    def __init__(self, transport, protocol):
        super(AmplitudeModulation, self).__init__(transport, protocol)
        self.external_coupling = Command(
            ':SOUR:AM:EXT:COUP?',
            ':SOUR:AM:EXT:COUP',
            Mapping({'ac': 'AC', 'dc': 'DC'})
        )
        self.source = Command(
            ':SOUR:AM:SOUR?',
            ':SOUR:AM:SOUR',
            Mapping({'internal': 'INT', 'external': 'EXT'})
        )
        self.state = Command(
            ':SOUR:AM:STAT?',
            ':SOUR:AM:STAT',
            Boolean
        )
        self.type = Command(
            ':SOUR:AM:TYPE?',
            ':SOUR:AM:TYPE',
            Mapping({'linear': 'LIN', 'exponential': 'EXP'})
        )
        self.linear_depth = Command(
            ':SOUR:AM:DEPT:LIN?',
            ':SOUR:AM:DEPT:LIN?',
            # XXX: This takes a number with a unit again, e.g. '90%'.
            String
        )


class Frequency(Driver):
    """Implements the frequency subsystem of the N5182A signal generator.
    """
    def __init__(self, transport, protocol):
        super(Frequency, self).__init__(transport, protocol)
        self.center = Command(
            (':SOUR:FREQ:CENT?', Float, 
             Mapping({'maximum': 'MAX', 'minimum': 'MIN'})),
            # TODO: This can also contain a frequency suffix.
            (':SOUR:FREQ:CENT', Float)
        )
        self.cw = Command(
            ':SOUR:FREQ:CW?',
            ':SOUR:FREQ:CW',
            # XXX: This is a string since the device expects a unit after
            # the frequency, e.g. '0.5MHz'
            String
        )
        self.mode = Command(
            ':SOUR:FREQ:MODE?',
            ':SOUR:FREQ:MODE',
            Mapping({'cw': 'CW', 'fixed': 'FIX', 'list': 'LIST'})
        )
        self.multiplier = Command(
            ':SOUR:FREQ:MULT?',
            ':SOUR:FREQ:MULT',
            Integer
        )


class Output(Driver):
    """Implements the output subsystem of the N5182A signal generator.
    """
    def __init__(self, transport, protocol):
        super(Output, self).__init__(transport, protocol)
        self.modulation_state = Command(
            ':OUTP:MOD:STAT?',
            ':OUTP:MOD:STAT',
            Boolean
        )
        self.state = Command(
            ':OUTP:STAT?',
            ':OUTP:STAT',
            Boolean
        )


class N5182A(IEC60488):
    """Represents an Agilent N5182A MXG Signal Generator."""

    def __init__(self, transport):
        super(N5182A, self).__init__(transport)
        self.am = AmplitudeModulation(self._transport, self._protocol)
        self.frequency = Frequency(self._transport, self._protocol)
        self.output = Output(self._transport, self._protocol)

