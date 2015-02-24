#  -*- coding: utf-8 -*-

"""The n5222a module implements an interface for the Agilent N5222A Vector
Network Analyzer.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import future
from future.builtins import *
import itertools
import struct

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from slave.driver import Command, Driver
from slave.iec60488 import IEC60488
from slave.types import Boolean, Enum, Float, Integer, Mapping, \
                        Register, Set, String

class BlockDataCommand(Command):
    """ This command receives block data from the VNA.

    This command can receive values as ASCII characters or as REAL,32 or
    REAL,64 data. Use REAL,32 for measurement data and REAL,64 for
    frequency data.

    The block data format is specified as follows::

        #<num_digits><byte_count><data bytes><NL><End>

    where

    - `'#'` marks the beginning of the block.
    - `num_digits` specifies how many digits are contained in
      `byte_count`.
    - `byte_count` specifies number of bytes in the `data bytes` section.
    - `data_bytes` represents the actual data.
    - `<NL><End>` is always send at the end of the transmission.
    """
    def __init__(self, query=None, protocol=None, format='ascii'):
        super(BlockDataCommand, self).__init__(protocol=protocol)
        self.protocol = protocol
        self._query = query
        if not format in ('REAL,32', 'REAL,64', 'ASC,0'):
            raise ValueError("Unknown format: {0}".format(format))
        self.format = format


    def query(self, transport, protocol):
        from slave.driver import _dump
        if self.protocol:
            self.protocol = protocol

        # set format first
        protocol.write(transport, 'FORM:DATA', self.format)

        if self.format == 'ASC,0':
            # If the format is ASCII we retrieve everything until the <NL>
            # character and convert it to floats.
            data = protocol.query(transport, self._query)
            data = map(float, data)
        else:
            protocol.write(transport, self._query)
            # If the format is REAL,32 or REAL,64 we have to receive the
            # header first.  It consists of a "#" sign and the number of
            # digits.
            with transport:
                logger.debug("BlockDataCommand query: %s", self._query)
                transport.write(self._query)

                data = transport.read_until(0x0A)
                if data[0] != ord('#'):
                    raise ValueError("Unknown header for block data.")
                digits = int(chr(data[1]))
                logger.debug("BlockDataCommand digits: %d", digits)

                # Read number of bytes of the actual data. This number is 
                # ASCII encoded with `digits` as number of digits.
                headerlength = 2+digits
                byte_count = int((data[2:headerlength]).decode('ascii'))
                logger.debug("BlockDataCommand byte_count: %s", byte_count)

                # Now read the actual data.
                data = data[headerlength:headerlength+byte_count]
                print(len(data))

                # Convert data to floats again. First build format string,
                # then use struct.unpack to unpack data from big-endian
                # format.
                if self.format == 'REAL,32':
                    fmtchar = 'f'
                    size = 4
                else:
                    fmtchar = 'd'
                    size = 8
                num_vars = int(byte_count / size)
                # struct.unpack requries a string, not a unicode string and also
                # not a future.types.newstr.newstr!
                fmt = future.utils.native_str('>' + fmtchar*num_vars)
                data = list(struct.unpack(fmt, data))

        return data

    def __repr__(self):
        """The BlockDataCommands representation."""
        return '<BlockDataCommand({0},{1},{2})>'.format(self._query,
                self.format, self.protocol)

# -------------------------------------------------------------------
# The Calculate command subsystem.
# -------------------------------------------------------------------
class Calculate(Driver):
    """Implements the calculate subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(Calculate, self).__init__(transport, protocol)
        self.parameter = CalculateParameter(self._transport, self._protocol)
        self.format = Command(
            'CALC:FORM?',
            'CALC:FORM',
            Mapping({'mlinear': 'MLIN', 'mlogarithmic': 'MLOG',
                     'phase': 'PHAS', 'uphase': 'UPH',
                     'imaginery': 'IMAG', 'real': 'REAL', 'polar': 'POL',
                     'smith': 'SMIT', 'sadmittance': 'SADM', 'swr': 'SWR',
                     'group_delay': 'GDEL', 'kelvin': 'KELV',
                     'fahrenheit': 'FAHR', 'celsius': 'CELS'
                    })
        )
        self.fdata = BlockDataCommand('CALC:DATA? FDATA', format='REAL,32')
        self.x = BlockDataCommand('CALC:X?', format='REAL,64')

#    @property
#    def fdata(self):


class CalculateParameter(Driver):
    """Implements the calculate parameter subsystem."""
    def __init__(self, transport, protocol):
        super(CalculateParameter, self).__init__(transport, protocol)
        self.catalog = Command(
            ('CALC:PAR:CAT:EXT?', itertools.repeat([String, String]))
        )
        self.selected = Command(
            ('CALC:PAR:SEL?', String)
        )

    def define(self, name, param):
        """Create a measurement but does NOT display it.

        :param name: The name of the new measurement.
        :param param: Measurement parameter. Right now, only S-parameters
        are supported.
        """
        name = '"{0}"'.format(name)
        self._write(('CALC:PAR:EXT',
                    [String, Set('S11', 'S12', 'S21', 'S22')]),
                    name, param)

    def select(self, name, fast=True):
        """Set the selected measurement.

        :param name: The name of the measurement.
        :param fast: If fast is set to True, the display will not be
            updated.
        """
        argument = '"{0}"'.format(name)
        if fast:
            argument += ',fast'
        self._write(('CALC:PAR:SEL', String), argument)

# -------------------------------------------------------------------
# The CalSet command subsystem.
# -------------------------------------------------------------------
class CalSet(Driver):
    """Implements the calset subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(CalSet, self).__init__(transport, protocol)
        self.catalog = Command(
            ('CSET:CAT?', itertools.repeat(String))
        )

# -------------------------------------------------------------------
# The Sense command subsystem.
# -------------------------------------------------------------------
class Sense(Driver):
    """Implements the sense subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(Sense, self).__init__(transport, protocol)
        self.average = SenseAverage(self._transport, self._protocol)
        self.correction = SenseCorrection(self._transport, self._protocol)
        self.frequency = SenseFrequency(self._transport, self._protocol)
        self.sweep = SenseSweep(self._transport, self._protocol)
        self.if_bandwidth = Command(
            'SENS:BWID?',
            'SENS:BWID',
            Float
        )

class SenseAverage(Driver):
    """Implements the sense average subsystem. """
    def __init__(self, transport, protocol):
        super(SenseAverage, self).__init__(transport, protocol)
        self.state = Command(
            'SENS:AVER:STAT?',
            'SENS:AVER:STAT',
            Boolean
        )
        self.mode = Command(
            'SENS:AVER:MODE?',
            'SENS:AVER:MODE',
            Mapping({'point': 'POINT', 'sweep': 'SWEEP'})
        )
        self.count = Command(
            'SENS:AVER:COUN?',
            'SENS:AVER:COUN',
            Integer(min=1, max=65536)
        )

class SenseCorrection(Driver):
    """Implements the sense correction subsystem. """
    def __init__(self, transport, protocol):
        super(SenseCorrection, self).__init__(transport, protocol)
        self.calset = SenseCorrectionCalSet(self._transport,
                                            self._protocol)

class SenseCorrectionCalSet(Driver):
    """Implements the sense correction calset subsystem. """
    def __init__(self, transport, protocol):
        super(SenseCorrectionCalSet, self).__init__(transport, protocol)
        self.active = Command(
            ('SENS:CORR:CSET:ACT?', [String, Boolean])
        )

    def activate(self, calset, stimulus=True):
        calset = '"{0}"'.format(calset)
        self._write(('SENS:CORR:CSET:ACT', [String, Boolean]),
                     calset, stimulus)

class SenseFrequency(Driver):
    """Implements the sense frequency subsystem. """
    def __init__(self, transport, protocol):
        super(SenseFrequency, self).__init__(transport, protocol)
        self.center = Command(
            'SENS:FREQ:CENT?',
            'SENS:FREQ:CENT',
            Integer
        )
        self.fixed = Command(
            'SENS:FREQ:FIX?',
            'SENS:FREQ:FIX',
            Integer
        )
        self.start = Command(
            'SENS:FREQ:STAR?',
            'SENS:FREQ:STAR',
            Integer
        )
        self.stop = Command(
            'SENS:FREQ:STOP?',
            'SENS:FREQ:STOP',
            Integer
        )


class SenseSweep(Driver):
    """Implements the sense sweep subsystem. """
    def __init__(self, transport, protocol):
        super(SenseSweep, self).__init__(transport, protocol)
        self.type = Command(
            'SENS:SWE:TYPE?',
            'SENS:SWE:TYPE',
            Mapping({'linear': 'LIN', 'logarithmic': 'LOG',
                     'power': 'POW', 'continuous': 'CW',
                     'segment': 'SEGM', 'phase': 'PHAS'})
        )
        self.dwell = Command(
            'SENS:SWE:DWEL?',
            'SENS:SWE:DWEL',
            Float(min=0)
        )
        self.generation = Command(
            'SENS:SWE:GEN?',
            'SENS:SWE:GEN',
            Mapping({'stepped': 'STEP', 'analog': 'ANAL'})
        )
        self.points = Command(
            'SENS:SWE:POIN?',
            'SENS:SWE:POIN',
            Integer(min=1)
        )


# -------------------------------------------------------------------
# The Source command subsystem.
# -------------------------------------------------------------------
class Source(Driver):
    """Implements the Source subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(Source, self).__init__(transport, protocol)
        self.power = SourcePower(self._transport, self._protocol)

class SourcePower(Driver):
    """Implements the source power subsystem. """
    def __init__(self, transport, protocol):
        super(SourcePower, self).__init__(transport, protocol)
        self.level = Command(
            'SOUR:POW?',
            'SOUR:POW',
            Integer
        )
        self.coupling = Command(
            'SOUR:POW:COUP?',
            'SOUR:POW:COUP',
            Boolean
        )
        self.mode = Command(
            'SOUR:POW:MODE?',
            'SOUR:POW:MODE',
            Mapping({'auto': 'AUTO', 'on': 'ON', 'off': 'OFF'})
        )

# -------------------------------------------------------------------
# The System command subsystem.
# -------------------------------------------------------------------
class System(Driver):
    """Implements the system subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(System, self).__init__(transport, protocol)

    def preset(self):
        """Performs a standard preset, deletes default trace, measurement
        and window.
        """
        self._write('SYST:FPR')

# -------------------------------------------------------------------
# The Trigger command subsystem.
# -------------------------------------------------------------------
class Trigger(Driver):
    """Implements the trigger subsystem of the Agilent N5222 VNA."""
    def __init__(self, transport, protocol):
        super(Trigger, self).__init__(transport, protocol)
        self.source = Command(
            'TRIG:SOUR?',
            'TRIG:SOUR',
            Mapping({'manual': 'MAN', 'external': 'EXT',
                     'immediate': 'IMM'})
        )


class N5222A(IEC60488):
    """Represents an Agilent N5222A Vector Network Analyzer."""

    def __init__(self, transport):
        super(N5222A, self).__init__(transport)
        self.calculate = Calculate(self._transport, self._protocol)
        self.calset = CalSet(self._transport, self._protocol)
        self.sense = Sense(self._transport, self._protocol)
        self.system = System(self._transport, self._protocol)
        self.source = Source(self._transport, self._protocol)
        self.trigger = Trigger(self._transport, self._protocol)

    def initiate(self):
        self._write('INIT')

