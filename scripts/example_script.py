# -*- coding: utf-8 -*-
r"""
Example script for generating plots using the dstauffman library.

Notes
-----
#.  Written by David C. Stauffer in May 2015.
"""
# pylint: disable=E1101, C0103

#%% Imports
import numpy as np
import dstauffman as dcs

#%% Main function
if __name__=='__main__':

    #%% Create some fake data
    # random data
    data = np.random.rand(10, 10)
    # normalize the random data
    data = dcs.unit(data, axis=0)
    # labels for the plot
    labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    # make some symmetric data
    sym = data.copy()
    num = sym.shape[0]
    for j in range(num):
        for i in range(num):
            if i == j:
                sym[i, j] = 1
            elif i > j:
                sym[i, j] = data[j, i]
            else:
                pass
    # create opts
    opts = dcs.Opts()

    #%% Create the plots
    fig1 = dcs.plot_correlation_matrix(data, labels, opts=opts)
    fig2 = dcs.plot_correlation_matrix(sym, labels, opts=opts)
