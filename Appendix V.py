# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 04:53:47 2016

@author: Daniel
"""

import PIL
import os
import numpy as np
import matplotlib.pyplot as pyplt
from matplotlib.widgets import  RectangleSelector
import Tkinter, tkFileDialog
from matplotlib.patches import Rectangle
import csv

def initialise():
    global cells_to_analyse, start_coords, end_coords, images_per_channel, images_to_discard_mid, images_to_discard_start
    images_per_channel = 54
    cells_to_analyse = 10
    images_to_discard_mid = 2
    images_to_discard_start = 0
    start_coords = []    
    end_coords = []    
    opener()

def opener():
    global files, directory
    root = Tkinter.Tk()
    root.wm_attributes("-topmost", 1)
    
    directory = tkFileDialog.askdirectory()
    root.withdraw()
    files = os.listdir(directory)    
    files.sort()       
    results_path = directory + '\Results'
    if not os.path.exists(results_path): os.makedirs(results_path)  
    boxes()
    
def boxes():
    global files, directory,images_per_channel
    for f in files:
        if 'C2' in f:
            x = 1
            y = 1
            fig = pyplt.figure
            ax = pyplt.subplot(111)
            ax.plot(x,y)
            red_image_path = os.path.join(directory, f)            
            img = PIL.Image.open(os.path.join(directory, f))
            try:
                img.seek(images_per_channel-1)
            except:
                pass
                        
            currentAxis = pyplt.gca()
            for coord1, coord2 in zip(start_coords, end_coords):
                x,y1 = coord1
                x1,y = coord2
                upper_left = (x,y1)    
                width = x1-x
                height = y-y1
                currentAxis.add_patch(Rectangle(upper_left, width, height, facecolor="none"))
            figManager = pyplt.get_current_fig_manager()
            figManager.window.showMaximized()            
            pyplt.imshow(img)
            toggle_selector.RS = RectangleSelector(ax, onselect, drawtype='box')       
        
def onselect(eclick, erelease):
    global cells_to_analyse
    'eclick and erelease are matplotlib events at press and release'
    start = (eclick.xdata, eclick.ydata)
    end = (erelease.xdata, erelease.ydata)
    start_coords.append(start)
    end_coords.append(end)
    pyplt.close(1)
    cells_to_analyse -= 1
    if cells_to_analyse != 0:
        boxes()
    else:
        analyse()

def toggle_selector(event):
    print ' Key pressed.'
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print ' RectangleSelector deactivated.'
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print ' RectangleSelector activated.'
        toggle_selector.RS.set_active(True)

def analyse():
    global files, directory, images_per_channel
    count = 1
    uv_dict = {}
    red_dict = {}
    ratio_dict = {}

    for coord1, coord2 in zip(start_coords, end_coords):
        uv = []
        red = []
        x,y = coord1
        x1,y1 = coord2
        x = int(x)
        x1 = int(x1)
        y = int(y)
        y1 = int(y1)
        for f in files:
            if 'C2' in f:
                redimg2 = PIL.Image.open(os.path.join(directory, f))
                for i in range(images_per_channel):
                    try:
                        redimg2.seek(i)
                        redarr2 = np.array(redimg2)
                        redarr3 = redarr2[y:y1,x:x1]
                        red.append(np.mean(redarr3))
                    except:
                        pass
                red_dict[count] = red
            if 'C1' in f:
                uvimg2 = PIL.Image.open(os.path.join(directory, f))
                for i in range(images_per_channel):
                    try:
                        uvimg2.seek(i)
                        uvarr2 = np.array(uvimg2)
                        uvarr3 = uvarr2[y:y1,x:x1]
                        uv.append(np.mean(uvarr3))
                    except:
                        pass
                uv_dict[count] = uv            
        count += 1
        print 'Working...'

    for key in red_dict:
        ratio = []
        for b,m in zip(red_dict[key], uv_dict[key]):
            ratio.append(b/m)
        ratio_dict[key] = ratio            
    
    before_treat = images_per_channel/2
    x_ax = []
    before_treat_slopes = []
    for x in xrange(images_to_discard_start, before_treat):
        x_ax.append(x)
    for key in ratio_dict:
        y_ax = []
        for x in xrange(images_to_discard_start, before_treat):
            val = ratio_dict[key][x]
            y_ax.append(val)
        slope, intercept = np.polyfit(x_ax, y_ax, 1)
        before_treat_slopes.append(slope)
    
    after_treat_start = images_per_channel/2+images_to_discard_mid
    x_ax = []
    after_treat_slopes = []
    for x in xrange(after_treat_start, images_per_channel):
        x_ax.append(x)
    for key in ratio_dict:
        y_ax = []
        for x in xrange(after_treat_start, images_per_channel):
            val = ratio_dict[key][x]
            y_ax.append(val)
        slope, intercept = np.polyfit(x_ax, y_ax, 1)
        after_treat_slopes.append(slope)
    
    results_uv_path = directory + '\Results\uv_channel.csv'
    results_red_path = directory + '/Results/red_channel.csv'
    results_slopes_path = directory + '/Results/slopes.csv'
    
    with open(results_uv_path, 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(zip(*uv_dict.values()))
    with open(results_red_path, 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(zip(*red_dict.values()))
    with open(results_slopes_path, 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Before treatment','After treatment'])
        writer.writerows(zip(before_treat_slopes, after_treat_slopes))
        
    print 'Done!'
initialise()
