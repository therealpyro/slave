# -*- coding: utf-8 -*-

"""
The ls625 module implements an interface for the Lakeshore Model 625
Superconducting Magnet Power Supply.
"""

from slave.driver import Command, Driver
from slave.iec60488 import IEC60488, Trigger
from slave.types import Boolean, Enum, Float, Integer, Mapping, String

class LS625(IEC60488, Trigger):
    """Provides an interface to the LS625 Superconducting magnet power
    supply.

    .. rubric: Communication related settings.

    :ivar baud: Set or get the RS-232 Baud Rate. Valid baud rates are
        9600, 19200, 38400 or 56700.
    :ivar ieee: Set or get the IEEE-488 Interface parameters, a tuple of
        the form *(<terminator>, <eoi enable>, <address>)* where

        * <terminator> specifies the terminator sign (r'\r\n', r'\n\r',
            r'\n' or `None`),
        * eoi enable sets the EOI Mode,
        * address specifies the IEEE address (1 to 30).
    :ivar ieee_mode: Set or get the IEEE interface mode. Valid entries are
        'local', 'remote' or 'remote with local lockout'.

    .. rubric: User interface related commands.

    :ivar display: Set or get the display configuration which is a tuple
        of the form *(<mode>, <volt sense>, <brightness>)* where

        * <mode> specifies the mode (either 'current' or 'field'),
        * <volt sense> specifies if the remote voltage sense reading is
            displayed,
        * <brightness> specifies the screen brightness (range 0-3
            corresponds to brightness 25% to 100%).
    :ivar key_pressed: Queries if a key was pressed or not.
    :ivar keyboard_lock: Set or get the keyboard lock. The argument is a
        tuple of the form *(<state>, <code>)* where

        * state specifies the lock state ('unlock', 'all', 'limits'),
        * code specifies the lock code (a string of digits in the range
            000-999).

    .. rubric: Magnetic field and current settings.

    :ivar field_params: Set or get the computed magnetic field
        parameter. This is a tuple of the form *(<unit>, <constant>)*
        where

        * <unit> specifies the unit of the constant ('T/A' or 'kG/A'),
        * <constant> specifies the constant itself (0.0010 - 1.0 T/A or
            0.010 - 10.0 kG/A)
    :ivar limits: Set or get the output limits. The limits are specified
        as a tuple of the form *(<current>, <voltage>, <rate>)* where

        * current is the maximum output current (0 - 60.1 A),
        * voltage is the maximum output voltage (0.1 - 5.0 V),
        * rate is the maximum ramp rate (0.0001 - 99.999 A/s).
    :ivar quench_params: Set or get the quench detection parameters. The
        argument is a tuple of the form *(<enable>, <rate>)* where

        * enable specifies if quench detection is used and
        * rate specifies the current step limit for quench detection.
    :ivar setpoint: Set or get the output field setpoint. The unit
        depends on the value of `computed_field_parameter`. Range is 
        -601 - 601 kG for kg/A unit or -60.1 to 60.1 T for T/A unit.
    :ivar setpoint_current: Set or get the output current setpoint. Valid
        range is from -60.1 to 60.1 A.
    :iver setpoint_compoince: Set or get the output voltage compliance
        setpoint. Valid range is from 0.1 to 5 V.

    .. rubric: Ramp settings

    :ivar rate: Get or set the output current ramp rate. Valid range is
        from 0.0001 to 99.999 A/s.
    :ivar rate_persistent: Get or set the ramp rate when the magnet is in
        persistent mode. This command takes a tuple of the form
        *(<enable>, <rate>)* where

        * enable specifies when if the persistent mode ramp mode is used
            or not and
        * rate specifies the ramp rate for the persistent mode ramping.
    :ivar ramp_segments_enabled: Enable/Disable ramp segments.
    :ivar ramp_segment: Set or get ramp segments. This takes a tuple of
        the form *(<segment>, <current>, <rate>)* where

        * segment specifies the ramp segment to be modified/queried (1-5),
        * current specifies the current for this segment (-60.1 - 60.1 A),
        * rate specifies the ramp rate for this segment 
            (0.0001 - 99.999 A/s)

    .. rubric: Persistent switch settings

    :ivar ps_heater: Specify if the switch heater is to be turned on or
        of. Valid entries are 'on', 'off' or 'override'.
    :ivar ps_heater_params: Set or get the persistent switch heater
        parameters. This command takes a tuple of the form 
        *(<enable>, <current>, <delay>)* where

        * enable specifies wether there is a PSH in the system,
        * current specifies the current needed to turn on the PSH 
            (10-125 mA),
        * delay specifies the time needed to turn the PSH on (5-100 s)
    :ivar ps_last_current: Queries the last current setting when the PSH
        was turned off.

    .. rubric: Output readings

    :ivar field: The field output reading.
    :ivar current: The current output reading.
    :ivar voltage_sense: The remote voltage sense reading.
    :ivar voltage: The output voltage reading.

    .. rubric: Error and operational status settings.

    :ivar error_status: Returns the sum of the bit weighting of the error
        status.
    :ivar error_status_enable: Set or get the error status enable register.
    :ivar error_status_register: Queries the error status register.
    :ivar operational_status: Returns the sum of the bit weighting of the
        operational status.
    :ivar operational_status_enable: Set or get the operational status
        enable register.
    :ivar operational_status_register: Queries the operational status
        register.

    .. rubric: Trigger settings

    :ivar trigger_current: Set or get the output current for trigger mode.
        The magnet ramps to this current when the controller is triggered
        via the '*TRG' command.

    .. rubric: External program mode

    :ivar external_program_mode: Enable or disable the external program
        mode. Valid entries are 'internal', 'external' or 'sum'.

    """

    def __init__(self, transport):
        super(LS625, self).__init__(transport)

        self.baud = Command(
            'BAUD?',
            'BAUD',
            Enum(9600, 19200, 38400, 57600)                
        )
        self.ieee = Command(
            'IEEE?',
            'IEEE',
            [Enum('\r\n', '\n\r', '\n', None),
             # Use enum here because True maps to 0 and False to 1.
             Enum(True, False),
             Integer(min=1, max=30)]
        )
        self.ieee_mode = Command(
            'MODE?',
            'MODE',
            Enum('local', 'remote', 'remote with lockout')
        )

        self.display = Command(
            'DISP?',
            'DISP',
            [Enum('current', 'field'),
             Boolean,
             Integer(min=0, max=3)]
        )
        self.key_pressed = Command(
            ('KEYST?', Boolean)
        )
        self.keyboard_lock = Command(
            'LOCK?',
            'LOCK',
            [Enum('unlock', 'all', 'limits'), String]
        )

        # Magnetic field settings.
        self.field_params = Command(
            'FLDS?',
            'FLDS',
            [Enum('T/A', 'kG/A'),
             Float(min=0.0010, max=10.0)]
        )
        self.limits = Command(
            'LIMIT?',
            'LIMIT',
            [Float(min=-60.1, max=60.1), Float(min=0.1, max=5.0),
             Float(min=0.0001, max=99.999)]
        )
        self.quench_params = Command(
            'QNCH?',
            'QNCH',
            [Boolean,
             Float(min=0.010, max=10.0)]
        )
        self.setpoint = Command(
            'SETF?',
            'SETF',
            Float(min=-601.0, max=601.0)
        )
        self.setpoint_current = Command(
            'SETI?',
            'SETI',
            Float(min=-60.1, max=60.1)
        )
        self.setpoint_compliance = Command(
            'SETV?',
            'SETV',
            Float(min=0.1, max=5.0)
        )

        # Ramp settings
        self.rate = Command(
            'RATE?',
            'RATE',
            Float(min=0.0001, max=99.999)
        )
        self.rate_persistent = Command(
            'RATEP?',
            'RATEP',
            [Boolean,
             Float(min=0.0001, max=99.999)]
        )
        self.ramp_segments_enabled = Command(
            'RSEG?',
            'RSEG',
            Boolean
        )
        self.ramp_segment = Command(
            ('RSEGS?', [Float, Float], Integer(min=1, max=5)),
            ('RSEGS',  [Integer(min=1, max=5), 
                        Float(min=-60.1, max=60.1),
                        Float(min=0.0001, max=99.999)])
        )

        # Persistent switch.
        self.ps_heater = Command(
            'PSH?',
            'PSH',
            Mapping({'off': 0, 'on': 1, 'override': 99})
        )
        self.ps_heater_params = Command(
            'PSHS?',
            'PSHS',
            [Boolean,
             Integer(min=10, max=125),
             Integer(min=5, max=100)]
        )
        self.ps_last_current = Command(
            ('PSHIS?', Float)
        )

        # Output readings.
        self.field = Command(('RDGF?', Float))
        self.current = Command(('RDGI?', Float))
        self.voltage_sense = Command(('RDGRV?', Float))
        self.voltage = Command(('RDGV?', Float))

        # Error and operational status.
        self.error_status = Command(
            ('ERST?', [Integer, Integer, Integer])
        )
        self.error_status_enable = Command(
            'ERSTE?',
            'ERSTE',
            [Integer, Integer, Integer]
        )
        self.error_status_register = Command(
            'ERSTR?',
            'ERSTR',
            [Integer, Integer, Integer]
        )
        self.operational_status = Command(
            ('OPST?', Integer)
        )
        self.operational_status_enable = Command(
            'OPSTE?',
            'OPSTE',
            Integer
        )
        self.operational_status_register = Command(
            'OPSTR?',
            'OPSTR',
            Integer
        )

        # Trigger settings
        self.trigger_current = Command(
            'TRIG?',
            'TRIG',
            Float(min=-60.1, max=60.1)
        )

        # External program mode
        self.external_program_mode = Command(
            'XPGM?',
            'XPGM',
            Enum('internal', 'external', 'sum')
        )

    def clear_errors(self):
        """Clear operational and PSH errors. Errors will be only cleared
        if the error conditions have been removed. Hardware errors can
        never be cleared.
        """
        self._write('ERCL')

    def defaults(self):
        """Set all configuration values to factory defaults and resets
        the instrument. This command only works when the instrument is at
        zero amps. 
        """
        self._write('DFLT 99')

    def stop(self):
        """Stop the output current."""
        self._write('STOP')
