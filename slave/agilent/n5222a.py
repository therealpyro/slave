#  -*- coding: utf-8 -*-

"""The n5222a module implements an interface for the Agilent N5222A Vector
Network Analyzer.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import collections

from slave.driver import Command, Driver
from slave.iec60488 import IEC60488
from slave.types import Boolean, Enum, Float, Integer, Mapping, \
                        Register, Set, String

# -------------------------------------------------------------------
# The Calculate command subsystem.
# -------------------------------------------------------------------
class Calculate(Driver):
    """Implements the calculate subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(Calculate, self).__init__(transport, protocol)

class CalculateParameter(Driver):
    """Implements the calculate parameter subsystem."""
    def __init__(self, transport, protocol):
        super(CalculateParameter, self).__init__(transport, protocol)
        self.catalog = Command(
            'CALC:PAR:CAT:EXT?',
            String
        )
        
    def define(self, name, param):
        """Create a measurement but does NOT display it.

        :param name: The name of the new measurement.
        :param param: Measurement parameter. Right now, only S-parameters
        are supported.
        """
        name = '"{0}"'.format(name)
        self._write('CALC:PAR:EXT', 
                    [String, Set('S11', 'S12', 'S21', 'S22')],
                    name, param)

    def select(self, name, fast=True):
        """Set the selected measurement.

        :param name: The name of the measurement.
        :param fast: If fast is set to True, the display will not be
            updated.
        """
        name = '"{0}"'.format(name)
        self._write('CALC:PAR:SEL', 
                    [String, Mapping({True: 'fast', False: '')],
                    name, fast)


class N5222A(IEC60488):
    """Represents an Agilent N5222A Vector Network Analyzer."""

    def __init__(self, transport):
        super(N5222A, self).__init__(transport)
        self.calculate = Calculate(self._transport, self._protocol)

