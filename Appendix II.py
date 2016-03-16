# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 04:23:37 2016

@author: Daniel
"""

# GUI and plotting not shown for clarity
from tkFileDialog import askopenfilename
import numpy as np  
import os

def opener():
    path = askopenfilename()
    donor = []
    acceptor = []

    with open(path,'r') as file:
        namer = file.name
        namez = namer[:-4] + '_compact.txt'
        lines = file.readlines()
        # Creates new file with preface cut off
        open(namez, 'w').writelines(lines[25:])
    with open(namez, 'r') as file:
        # Opens new file and adds data in to list
        for row in file:
            a,don,b,acc,c = row.split()
            donor.append(float(don))
            acceptor.append(float(acc))
    os.remove(namez)
        
    donor_array = np.array(donor)
    acceptor_array = np.array(acceptor)
    donor_auto = 0
    acceptor_auto = 0
    crosstalk = 0
    donor_array = donor_array - donor_auto
    acceptor_array = acceptor_array - acceptor_auto - (crosstalk * donor_array)
    return donor_array, acceptor_array

def maxq():
    donor_array, acceptor_array = opener()

    td = 100
    ta = 100
    donor_shuff = np.copy(donor_array)
    np.random.shuffle(donor_shuff)

    Qvals = np.zeros((td+1, ta+1))

    for td_cycler in xrange(0,(td+1)):
        for ta_cycler in xrange(0,(ta+1)):
            Q_val,coinc,desynch = q_calc(donor_array, acceptor_array,td_cycler,ta_cycler,donor_shuff)
            Qvals[td_cycler][ta_cycler] = Q_val
       
    max_q = np.max(Qvals)
    index_q = np.where(Qvals == max_q)
    max_d, max_a = index_q # max q at these donor and acceptor thresholds
    
def q_calc(donor_array,acceptor_array,td,ta,donor_shuff):
    d_rate = len(donor_array[(donor_array > td)])
    a_rate = float(len(acceptor_array[(acceptor_array > ta)]))
    coinc = len(donor_array[(donor_array > td) & (acceptor_array > ta)])
    des_events = float(len(donor_shuff[(donor_shuff > td) &
            (acceptor_array > ta)]))
    Q_val = 100*(round(((coinc - des_events) / (d_rate + a_rate -
            (coinc - des_events))), 4))
    return Q_val,coinc,des_events


maxq()
