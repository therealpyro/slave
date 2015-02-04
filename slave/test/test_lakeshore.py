#  -*- coding: utf-8 -*-
#
# Slave, (c) 2014, see AUTHORS.  Licensed under the GNU GPL.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *

from slave.lakeshore import LS340, LS370, LS625
from slave.transport import SimulatedTransport


def test_ls340():
    # Test if instantiation fails
    LS340(SimulatedTransport())


def test_ls370():
    # Test if instantiation fails
    LS370(SimulatedTransport())


def test_ls625():
    # Test if instantiation fails
    LS625(SimulatedTransport())

