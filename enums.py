# -*- coding: utf-8 -*-
r"""
Enums module file for the dstauffman library.  It defines enumerator related functions for the rest
of the code..

Notes
-----
#.  Written by David C. Stauffer in July 2015.
"""

#%% Imports
from __future__ import print_function
from __future__ import division
from enum import Enum, unique, EnumMeta, _is_dunder
import numpy as np
from six import with_metaclass
import re
import unittest

#%% Private Classes
class _EnumMetaPlus(EnumMeta):
    r"""
    Overrides the repr/str methods of the EnumMeta class to display all possible values.
    Also makes the __getattr__ attribute error more explicit.
    """
    def __repr__(cls):
        text = [repr(field) for field in cls]
        return '\n'.join(text)
    def __str__(cls):
        text = [str(field) for field in cls]
        return '\n'.join(text)
    def __getattr__(cls, name):
        r"""
        Return the enum member matching `name`.
        """
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            return cls._member_map_[name]
        except KeyError:
            text = '"{}" does not have an attribute of "{}"'.format(cls.__name__,name)
            # Future Python v3 only option: raise AttributeError(text) from None
            raise AttributeError(text)
    def list_of_names(self):
        r"""
        Returns a list of all the names within the enumerator.
        """
        output = re.findall(r"\.(.*):", str(self))
        return output
    def list_of_values(self):
        r"""
        Returns a list of all the names within the enumerator.
        """
        output = [int(x) for x in re.findall(r":\s(.*)\n", str(self)+'\n')]
        return output
    def num_values(self):
        output = len(self.list_of_names())
        return output

@unique
class IntEnumPlus(with_metaclass(_EnumMetaPlus, int, Enum)):
    r"""
    Custom IntEnum class based on _EnumMetaPlus metaclass to get more details from repr/str.

    Also forces all values to be unique.
    """
    #__metaclass__ = _EnumMetaPlus
    def __str__(self):
        return '{}.{}: {}'.format(self.__class__.__name__, self.name, self.value)

#%% Functions
def dist_enum_and_mons(num, distribution, max_months, prng, alpha=1, beta=1):
    r"""
    Creates a distribution for an enumerated state with a duration (such as TB status).

    Parameters
    ----------
    num : int
        Number of people in the population
    distribution : array_like
        Likelihood of being in each TB state (should be 4 states and cumsum to 100%)
    max_months : array_like
        Maximum number of months for being in each TB state
    prng : class numpy.random.RandomState
        Pseudo-random number generator
    alpha : int, optional
        The alpha parameter for the beta distribution
    beta : int, optional
        The beta parameter for the beta distribution

    Returns
    -------
    state : ndarray
        Enumerated status for this month for everyone in the population
    mons : ndarray
        Number of months in this state for anyone with an infection

    Notes
    -----
    #.  Written by David C. Stauffer in April 2015.
    #.  Updated by David C. Stauffer in June 2015 to use a beta curve to distribute the number of
        months spent in each state.
    #.  Made into a generic function for the dstauffman library by David C. Stauffer in July 2015.

    Examples
    --------

    >>> from dstauffman import dist_enum_and_mons
    >>> import numpy as np
    >>> num = 10000
    >>> distribution = 1./100*np.array([9.5, 90, 0.25, 0.25])
    >>> max_months = np.array([60, 120, 36, 6])
    >>> prng = np.random.RandomState()
    >>> (state, mons) = dist_enum_and_mons(num, distribution, max_months, prng)

    """
    # do a random draw based on the cumulative distribution
    state = np.sum(prng.rand(num) >= np.expand_dims(np.cumsum(distribution), axis=1), \
        axis=0, dtype=int) + 1
    # set the number of months in this state based on a beta distribution with the given
    # maximum number of months in each state
    mons = np.ceil(max_months[state-1] * prng.beta(alpha, beta, num)).astype(int)
    return (state, mons)

#%% Unit test
if __name__ == '__main__':
    unittest.main(module='tests.test_enums', exit=False)
