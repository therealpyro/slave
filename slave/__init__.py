#  -*- coding: utf-8 -*-
#
# Slave, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

import warnings

# Test if ipythons autocall feature is enabled. It can cause serious problems,
# because attributes are executed twice. This means commands are send twice and
# e.g. error flags might get cleared.
try:
    if __IPYTHON__.rc.autocall == 1:
        warnings.warn('Autocall is enabled. Correct execution can not be '
                      'guaranteed. To turn it off call ipython with '
                      '-autocall 0.')
except NameError:
    pass

del warnings