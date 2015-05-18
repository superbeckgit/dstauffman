# -*- coding: utf-8 -*-
r"""
Test file to execute all the docstrings within the dstauffman code.

Notes
-----
#.  Written by David C. Stauffer in March 2015.
"""

#%% Imports
from __future__ import print_function
from __future__ import division
import doctest
import os
import dstauffman as dcs

#%% Locals
verbose = False

#%% Execution
if __name__ == '__main__':
    folder = dcs.get_root_dir()
    files  = ['classes', 'constants', 'photos', 'plotting', 'quat', 'utils']
    for file in files:
        if verbose:
            print('')
            print('******************************')
            print('******************************')
            print('Testing ' + file + '.py:')
        doctest.testfile(os.path.join(folder, file+'.py'), report=True, verbose=verbose, module_relative=True)
