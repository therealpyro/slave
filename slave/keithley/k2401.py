# -*- coding: utf-8 -*-
""" The k2401 module implements the GPIB interface for a Keithley K2401
Source Meter.
"""

from slave.driver import Command, Driver
from slave.iec60488 import IEC60488, Trigger, ObjectIdentification, \
                           StoredSetting

class K2401(IEC60488, Trigger, ObjectIdentification, StoredSetting):
    """The Keithley K2401 source meter.

    The programmable interface is grouped into several layers and builts a tree
    like structure.

    .. rubric: The sense command layer

    .. ivar sense: The sense command subgroup, an instance of
        :class:`~.Sense`.
    """

    def __init__(self, transport):
        super(K2401, self).__init__(self._transport, self._protocol)


class Arm(Driver):
    """The arm command subsystem.

    :ivar count: Set the arm count (1-2500).
    :ivar source: Set the arm source. Valid are 'immediate', 'tlink',
        'timer', 'manual', 'bus', 'nstest', 'pstest', 'bstest'.
    :ivar source_bypass: Set the arm source bypass. Valid entries are
        'source' or 'acceptor'.
    :ivar timer: Set the timer interval in seconds (0.001-99999.99).
    :ivar input_line: The arm input signal line (1-4).
    :ivar output_line: The arm output signal line (1-4).
    :ivar output: The output trigger. Valid entries are 'tenter', 'texit',
        `None`.
    """
    def __init__(self, transport, protocol):
        super(K2401, self).__init__(transport, protocol)
        self.count = Command(
            ':ARM:COUNT?',
            ':ARM:COUNT',
            Integer(min=1, max=2500)
        )
        self.source = Command(
            ':ARM:SOURCE?',
            ':ARM:SOURCE',
            Mapping({'immediate': 'IMM', 'tlink': 'TLIN', 'timer': 'TIM',
                     'manual': 'MAN', 'bus': 'BUS', 'nstest': 'NST',
                     'pstest': 'PST', 'bstest': 'BS'})
        )
        self.timer = Command(
            ':ARM:TIM?',
            ':ARM:TIM',
            Float(min=0.001, max=99999.99)
        )
        self.source_bypass = Command(
            ':ARM:DIR?',
            ':ARM:DIR',
            Mapping({'source': 'SOUR', 'acceptor': 'ACC'})
        )
        self.input_line = Command(
            ':ARM:ILIN?',
            ':ARM:ILIN',
            Integer(min=1, max=4)
        )
        self.output_line = Command(
            ':ARM:ILIN?',
            ':ARM:ILIN',
            Integer(min=1, max=4)
        )
        self.output = Command(
            ':ARM:OUTP?',
            ':ARM:OUTP',
            Mapping({'tenter': 'TENT', 'texit': 'TEX', None: 'NONE'})
        )

class Trigger(Driver):
    """The Trigger command subsystem.

    """
    def __init__(self, transport, protocol):
        super(K2401, self).__init__(transport, protocol)

    def clear(self):
        """Clear any pending input triggers immediately."""
        self._write(':TRIG:CLE')


class Sense(Driver):
    """The Sense command subsystem.

    :param transport: A transport object.

    :ivar function: A list of functions to enable (string list of 'VOLT',
        'CURR', 'RES').
    :ivar volt: The volt sense command subsystem, an instance of
        :class:`~.SenseFunction`.
    :ivar current: The volt sense command subsystem, an instance of
        :class:`~.SenseFunction`.
    :ivar resistance: The volt sense command subsystem, an instance of
        :class:`~.SenseFunction`.
    """
    def __init__(self, transport, protocol):
        super(Sense, self).__init__(transport, protocol)
        # TODO: Implement string list type.
        self.function = Command(
            ':SENS:FUNC?',
            ':SENS:FUNC',
            String
        )
        self.volt = SenseFunction(transport, protocol, 'VOLT')
        self.current = SenseFunction(transport, protocol, 'CURR')
        self.resistance = SenseFunction(transport, protocol, 'RES')


class SenseFunction(Driver):
    """ The SenseFunction command subsystem of the Sense node.

    :ivar auto_range: Enable/Disable auto ranging.
    :ivar nplc: Set integration time in number of power line cycles.
    :ivar protection: Set current/voltage protection limit (not available
        for resistance node).
    :ivar range: Set measurement range.
    """
    def __init__(self, transport, protocol, node):
        super(SenseNode, self).__init__(transport, protocol)
        node = node.upper()
        if node not in ('VOLT', 'CURR', 'RES'):
            raise ValueError("Unknown SENSE node: {}".format(node))

        self.auto_range = Command(
            ':SENS:{}:AUTO?'.format(node),
            ':SENS:{}:AUTO'.format(node),
            Boolean
        )
        self.nplc = Command(
            ':SENS:{}:NPLC?'.format(node),
            ':SENS:{}:NPLC'.format(node),
            Float(min=0.01, max=10)
        )
        if node != 'resistance':
            self.protection = Command(
                ':SENS:{}:PROT?'.format(node),
                ':SENS:{}:PROT'.format(node),
                Float
            )
        self.range = Command(
            ':SENS:{}?'.format(node),
            ':SENS:{}'.format(node),
            Float
        )



