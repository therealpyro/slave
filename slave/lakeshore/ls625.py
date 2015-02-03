# -*- coding: utf-8 -*-

"""
The ls625 module implements an interface for the Lakeshore Model 625
Superconducting Magnet Power Supply.
"""

from slave.driver import Command, Driver
from slave.iec60488 import IEC60488
from slave.types import Boolean, Enum, Integer

class LS625(Driver, IEC60488):
    """Provides an interface to the LS625 Superconducting magnet power
    supply.

    :ivar display: Sets the display configuration which is a tuple of the
        form *(<mode>, <volt sense>, <brightness>)* where

        * <mode> specifies the mode (either 'current' or 'field'),
        * <volt sense> specifies if the remote voltage sense reading is
            displayed,
        * <brightness> specifies the screen brightness (range 0-3
            corresponds to brightness 25% to 100%)


    """

    def __init__(self, transport):
        super(LS625, self).__init__(transport)
        self.display = Command(
            'DISP?',
            'DISP',
            [Enum('current', 'field'),
             Boolean,
             Integer(min=0, max=3)
        )



    def defaults(self):
        """Sets all configuration values to factory defaults and resets
        the instrument. This command only works when the instrument is at
        zero amps. 
        """
        self._write('DFLT 99')


