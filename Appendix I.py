# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 04:07:30 2016

@author: Daniel
"""

import PIL
import os
import numpy
import scipy
import scipy.stats
import matplotlib as plt
import matplotlib.pyplot as pyplt
from matplotlib.widgets import  RectangleSelector
import Tkinter, tkFileDialog

def initialise():
    global channels, channel1, channel2, channel3, count, count2
    channels = 3        # change to 2 if you are using 2 channels only
    channel1 = 'TDP'    # name of protein in channel 1
    channel2 = 'CLU'    # name of protein in channel 2
    channel3 = 'LC3'    # name of protein in channel 3 - ignore if using 2 channels
    # names only used for results docs, tdp = ch1, clu = ch2, lc3 = ch3 in the code
    count = 0
    count2 = 1
    opener()

def opener():
    global files, directory, list1, list2, list3, list4, list5, list6, list7, list8
    directory = tkFileDialog.askdirectory()
    files = os.listdir(directory)    
    files.sort()    # case-sensitive alphabetical sorting
    thresh_path = directory + '\Thresholded'
    results_path = directory + '\Results'
    if not os.path.exists(thresh_path): os.makedirs(thresh_path)
    if not os.path.exists(results_path): os.makedirs(results_path)
    list1 = [] # lists 1-4 hold colocalisation data
    list2 = []
    list3 = []
    list4 = []
    list5 = [] # lists 5-8 hold chance coinc data
    list6 = []
    list7 = []
    list8 = []
    set_roi()

def set_roi():
    file_tdp = files[count]
    x = 1
    y = 1
    fig = pyplt.figure
    ax = pyplt.subplot(111)
    ax.plot(x,y)        
    image_path = image_path = os.path.join(directory, file_tdp)
    img = PIL.Image.open(image_path)
    array = numpy.array(img)
    imgplot = pyplt.imshow(array)
    toggle_selector.RS = RectangleSelector(ax, onselect, drawtype='box')       
        
def onselect(eclick, erelease):
    'eclick and erelease are matplotlib events at press and release'
    start = (eclick.xdata, eclick.ydata)
    end = (erelease.xdata, erelease.ydata)
    pyplt.close(1)
    threshold(start, end)
    
def toggle_selector(event):
    print ' Key pressed.'
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print ' RectangleSelector deactivated.'
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print ' RectangleSelector activated.'
        toggle_selector.RS.set_active(True)

def threshold(start, end):
    global files, directory, channels, channel1, channel2, channel3, count, count2
    global list1, list2, list3, list4, list5, list6, list7, list8
    top, left = start
    bottom, right = end
    box = (int(left), int(top), int(right), int(bottom))
    
    file_tdp = files[count]
    file_clu = files[count+1]
    file_lc3 = files[count+2]
    file_list = [file_tdp, file_clu, file_lc3]
    thresholded_dict = {}      
    
    for image in file_list:
        image_path = os.path.join(directory, image)
        img = PIL.Image.open(image_path)         
        img = img.crop(box)
 
        array = numpy.array(img)
        brightest = numpy.amax(array)
        threshold = brightest * 0.5
        thresholded = (array > threshold) * 255     # Thresholding here. Works because True = 1.
        outim=PIL.Image.fromarray(thresholded) 
        new_save = directory + '/thresholded/Thresholded_' + str(image)
        outim.save(new_save)
        thresholded_dict[image] = thresholded
    num_clu = float(numpy.sum(thresholded_dict[file_clu])/255)
    num_tdp = float(numpy.sum(thresholded_dict[file_tdp])/255)  

    #  testing for colocalisation
    clu_tdp_colocalised = numpy.logical_and(thresholded_dict[file_clu] != 0, thresholded_dict[file_tdp] != 0)
    clu_lc3_colocalised = numpy.logical_and(thresholded_dict[file_clu] != 0, thresholded_dict[file_lc3] != 0)
    tdp_lc3_colocalised = numpy.logical_and(thresholded_dict[file_tdp] != 0, thresholded_dict[file_lc3] != 0)
    all_colocalised = numpy.logical_and(clu_tdp_colocalised != 0, clu_lc3_colocalised != 0)
    list1.append(round(numpy.sum(clu_tdp_colocalised)/num_clu*100, 2))
    list2.append(round(numpy.sum(clu_lc3_colocalised)/num_clu*100, 2))
    list3.append(round(numpy.sum(tdp_lc3_colocalised)/num_tdp*100, 2))
    list4.append(round(numpy.sum(all_colocalised)/num_clu*100, 2))
    
    #  shuffling arrays
    for key in thresholded_dict:
        shape = thresholded_dict[key].shape
        thresholded_dict[key] = thresholded_dict[key].flatten()
        numpy.random.shuffle(thresholded_dict[key])
        thresholded_dict[key] = thresholded_dict[key].reshape(shape)

    #  testing for chance coincidence
    clu_tdp_chance = numpy.logical_and(thresholded_dict[file_clu] != 0, thresholded_dict[file_tdp] != 0)
    clu_lc3_chance = numpy.logical_and(thresholded_dict[file_clu] != 0, thresholded_dict[file_lc3] != 0)
    tdp_lc3_chance = numpy.logical_and(thresholded_dict[file_tdp] != 0, thresholded_dict[file_lc3] != 0)
    all_chance = numpy.logical_and(clu_tdp_chance != 0, clu_lc3_chance != 0)
    list5.append(round(numpy.sum(clu_tdp_chance)/num_clu*100, 2))
    list6.append(round(numpy.sum(clu_lc3_chance)/num_clu*100, 2))
    list7.append(round(numpy.sum(tdp_lc3_chance)/num_tdp*100, 2))
    list8.append(round(numpy.sum(all_chance)/num_clu*100, 2))

    count2 += 1
    count += 3
    if count < len(files)-2:
        set_roi()
    if count >= (len(files)-2):
        saver()

def saver():
    global files, directory, channels, channel1, channel2, channel3, count, count2
    global list1, list2, list3, list4, list5, list6, list7, list8
    
    clutdp_path = directory + '\Results\CLU_and_TDP_colocalisation.txt'
    clulc3_path = directory + '\Results\CLU_and_LC3_colocalisation.txt'
    tdplc3_path = directory + '\Results\TDP_and_LC3_colocalisation.txt'
    all_path = directory + '\Results\ALL_colocalisation.txt'
    cclutdp_path = directory + '\Results\CLU_and_TDP_chance.txt'
    cclulc3_path = directory + '\Results\CLU_and_LC3_chance.txt'
    ctdplc3_path = directory + '\Results\TDP_and_LC3_chance.txt'
    call_path = directory + '\Results\ALL_chance.txt'
    path_list = [clutdp_path, clulc3_path, tdplc3_path, all_path, cclutdp_path, cclulc3_path, ctdplc3_path, call_path]        
    list_list = [list1, list2, list3, list4, list5, list6, list7, list8]        
    
    for p, l in zip(path_list, list_list):
        with open(p, 'w') as f:
            f.write('Values are number of pixels colocalised\nas percentage clu (tdp for tdp-lc3)\nfor each image set.\n\n')            
            for v in l:
                f.write(str(v)+'\n')

    compiled_path = directory + '\Results\compiled_results.txt'
    with open(compiled_path, 'w') as f:
        f.write('Values are mean +/- SD, n = {0}'.format(len(list1)))
        f.write('\n\n')
        f.write('CLU-TDP43 colocalisation = {0} +/- {1}'.format(round(numpy.mean(list1), 2), round(numpy.std(list1), 2)) + '\n')
        f.write('CLU-LC3 colocalisation = {0} +/- {1}'.format(round(numpy.mean(list2), 2), round(numpy.std(list2), 2)) + '\n')
        f.write('TDP43-LC3 colocalisation = {0} +/- {1}'.format(round(numpy.mean(list3), 2), round(numpy.std(list3), 2)) + '\n')
        f.write('ALL colocalisation = {0} +/- {1}'.format(round(numpy.mean(list4), 2), round(numpy.std(list4), 2)) + '\n')
        f.write('CLU-TDP43 chance = {0} +/- {1}'.format(round(numpy.mean(list5), 2), round(numpy.std(list5), 2)) + '\n')
        f.write('CLU-LC3 chance = {0} +/- {1}'.format(round(numpy.mean(list6), 2), round(numpy.std(list6), 2)) + '\n')
        f.write('TDP43-LC3 chance = {0} +/- {1}'.format(round(numpy.mean(list7), 2), round(numpy.std(list7), 2)) + '\n')
        f.write('ALL chance = {0} +/- {1}'.format(round(numpy.mean(list8), 2), round(numpy.std(list8), 2)))

initialise()
 
