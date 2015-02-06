#  -*- coding: utf-8 -*-
#
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *

from slave.agilent import N5182A
from slave.transport import SimulatedTransport


def test_n5182a():
    # Test if instantiation fails
    N5182A(SimulatedTransport())

