from pathlib import Path
import numpy as np

import matplotlib as mpl
from matplotlib.pyplot import figure, show, savefig
import matplotlib.pyplot as plt

from photutils import CircularAperture
from astropy.visualization import simple_norm

from ..constants import tab10, single_column, two_column
#tab10 = ['#e15759','#4e79a7','#f28e2b','#76b7b2','#59a14e','#edc949','#b07aa2','#ff9da7','#9c755f','#bab0ac']    

def classification_map(galaxy,parameters,tbl,filename):
    '''
    Plot data in galaxy for different lines and overplot the position
    of detected sources
    '''

    if "zoomin" in parameters[galaxy.name]:
        x,y,width = parameters[galaxy.name]['zoomin']
        height = width * galaxy.shape[0] / galaxy.shape[1]

        if x+width > galaxy.shape[1]:
            print(f'cutout is too wide')
            new_width =  galaxy.shape[1] - x
            height *= new_width / width 
            width = new_width

        if y+height > galaxy.shape[0]:
            print(f'cutout is to high')
            new_height =  galaxy.shape[0] - y
            width *= new_height / height
            height = new_height

    else:
        x,y=0,0
        height,width = galaxy.shape

    # ====== define input parameters =============================
    labels=['SII6716','HA6562','OIII5006']
    wcs=galaxy.wcs
    # ============================================================

    from pnlf.plot.plot import create_RGB
    #rgb = create_RGB(galaxy.HA6562,galaxy.OIII5006,galaxy.SII6716,percentile=97)
    rgb = create_RGB(galaxy.HA6562,galaxy.OIII5006_DAP,galaxy.SII6716,weights=[0.8,1,0.9],percentile=[97,97,97])

    table = tbl
    #table = tbl[tbl['mOIII']<galaxy.completeness_limit]

    fig = plt.figure(figsize=(two_column,two_column/2))
    ax1 = fig.add_subplot(131,projection=wcs)
    ax2 = fig.add_subplot(132,projection=wcs)
    ax3 = fig.add_subplot(133)

    norm = simple_norm(galaxy.OIII5006_DAP,'linear',clip=False,max_percent=95)
    ax1.imshow(galaxy.OIII5006_DAP,norm=norm,cmap=plt.cm.Greens)

    norm = simple_norm(galaxy.HA6562,'linear',clip=False,max_percent=95)
    ax2.imshow(galaxy.HA6562,norm=norm,cmap=plt.cm.Reds)

    ax3.imshow(rgb)

    print(f'{len(table)} sources')
    for t,c in zip(['SNR','PN'],['royalblue','goldenrod']):
        
        sub = table[table['type']==t]
        print(f'{t:<3}: {len(sub):>3}')
        positions = np.transpose([sub['x'],sub['y']])
        apertures = CircularAperture(positions, r=6)
        #ax1.scatter(sub['x'],sub['y'],marker='o',s=5,lw=0.4,edgecolor=c,facecolors='none')
        apertures.plot(color=c,lw=.2, alpha=1,ax=ax1)
        apertures.plot(color=c,lw=.2, alpha=1,ax=ax2)
        apertures.plot(color=c,lw=.4, alpha=1,ax=ax3)

    '''    
    for row in table[table['type']!='HII']:
        txt,xp,yp = row['id'], row['x']+5, row['y']
        
        #if x<x<x+width and y<y<y+height:
        ax1.annotate(txt, (xp, yp),fontsize=1,color='black')
        #ax2.annotate(txt, (xp, yp),fontsize=0.5)
        ax3.annotate(txt, (xp, yp),fontsize=2,color='white')
    '''
    
    # first we create a legend with three invisible handles
    labels=['HA6562','OIII5006','SII6716']
    labels=[r'Halpha',r'[OIII]',r'[SII]']
    handles = 3*[mpl.patches.Rectangle((0, 0), 0, 0, alpha=0.0)]
    leg = ax3.legend(handles,labels, frameon=True,framealpha=0.7,handlelength=0,prop={'size': 6},loc=3)

    # next we set the color of the three labels
    for color,text in zip(['red','green','blue'],leg.get_texts()):
        text.set_color(color)


    ax1.add_patch(mpl.patches.Rectangle((x,y),width,height,linewidth=0.3,edgecolor='k',facecolor='none'))
    ax2.add_patch(mpl.patches.Rectangle((x,y),width,height,linewidth=0.3,edgecolor='k',facecolor='none'))
    ax3.set_xlim([x,x+width])
    ax3.set_ylim([y,y+height])

    ax1.set(title=r'O[III]',
            xlabel='R.A. (J2000)',
            ylabel='Dec. (J2000)')

    ax2.set(title=r'Halpha',
            xlabel='R.A. (J2000)')
            
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_title('RGB')

    # format ticks with wcs
    # https://docs.astropy.org/en/stable/visualization/wcsaxes/ticks_labels_grid.html
    ax1.coords[0].set_ticks(number=3)
    ax1.coords[1].set_ticks(number=4)
    ax2.coords[0].set_ticks(number=3)
    ax2.coords[1].set_ticklabel_visible(False)

    #plt.subplots_adjust(wspace=-0.4)

    # it is a bit tricky to get the coordinates right (because data uses the wcs coordinates)
    # the easiest thing is to use fractions from the figure size
    # https://matplotlib.org/3.1.3/api/_as_gen/matplotlib.patches.ConnectionPatch.html
    con = mpl.patches.ConnectionPatch(xyA=((x+width)/galaxy.shape[1],(y+height)/galaxy.shape[0]), xyB=(0,1), 
                                      coordsA="axes fraction", coordsB="axes fraction",
                                      axesA=ax2, axesB=ax3, color="black",linewidth=0.3)
    ax3.add_artist(con)
    con = mpl.patches.ConnectionPatch(xyA=((x+width)/galaxy.shape[1],(y)/galaxy.shape[0]), xyB=(0,0), 
                                      coordsA="axes fraction", coordsB="axes fraction",
                                      axesA=ax2, axesB=ax3, color="black",linewidth=0.3)
    ax3.add_artist(con)

    plt.savefig(filename,bbox_inches='tight',dpi=600)


def classification_map_small(galaxy,parameters,tbl,filename):
    '''
    Plot data in galaxy for different lines and overplot the position
    of detected sources
    '''

    if "zoomin" in parameters[galaxy.name]:
        x,y,width = parameters[galaxy.name]['zoomin']
        height = width * galaxy.shape[0] / galaxy.shape[1]

        if x+width > galaxy.shape[1]:
            print(f'cutout is too wide')
            new_width =  galaxy.shape[1] - x
            height *= new_width / width 
            width = new_width

        if y+height > galaxy.shape[0]:
            print(f'cutout is to high')
            new_height =  galaxy.shape[0] - y
            width *= new_height / height
            height = new_height

    else:
        x,y=0,0
        height,width = galaxy.shape

    # ====== define input parameters =============================
    labels=['SII6716','HA6562','OIII5006']
    wcs=galaxy.wcs
    # ============================================================

    #rgb = create_RGB(galaxy.HA6562,galaxy.OIII5006,galaxy.SII6716,percentile=97)
    r,g,b = galaxy.HA6562,galaxy.OIII5006_DAP,galaxy.SII6716

    # create an empty array with teh correct size
    rgb = np.empty((*r.shape,3))
    
    g=np.power(1.3,g)
    percentile = [99,97.5,99]
    # assign the input arrays to the 3 channels and normalize them to 1
    rgb[...,0] = r / np.nanpercentile(r,percentile[0])
    rgb[...,1] = g / np.nanpercentile(g,percentile[1])
    rgb[...,2] = b / np.nanpercentile(b,percentile[2])
    rgb = np.clip(np.nan_to_num(rgb,nan=1),a_min=0,a_max=1)

    table = tbl
    #table = tbl[tbl['mOIII']<galaxy.completeness_limit]

    fig = plt.figure(figsize=(two_column,two_column/2))
    ax1 = fig.add_subplot(121,projection=wcs)
    ax2 = fig.add_subplot(122,projection=wcs)

    norm = simple_norm(galaxy.OIII5006_DAP,'linear',clip=False,max_percent=95)
    ax1.imshow(galaxy.OIII5006_DAP,norm=norm,cmap=plt.cm.gray_r)

    ax2.imshow(rgb)

        
    sub = table[table['type']=='PN']
    positions = np.transpose([sub['x'],sub['y']])
    apertures = CircularAperture(positions, r=7)
    apertures.plot(color='green',lw=.3, alpha=1,ax=ax1)
    apertures.plot(color='white',lw=.2, alpha=1,ax=ax2)
    
    # first we create a legend with three invisible handles
    labels=['HA6562','OIII5006','SII6716']
    labels=[r'H$\alpha$',r'[OIII]',r'[SII]']
    handles = 3*[mpl.patches.Rectangle((0, 0), 0, 0, alpha=0.0)]
    leg = ax2.legend(handles,labels,bbox_to_anchor=(0.5,-0.05), ncol=3,frameon=True,framealpha=0.9,handlelength=0,prop={'size': 8},loc='center')

    # next we set the color of the three labels
    for color,text in zip(['red','green','blue'],leg.get_texts()):
        text.set_color(color)

    ax1.add_patch(mpl.patches.Rectangle((x,y),width,height,linewidth=0.3,edgecolor='k',facecolor='none'))
    ax2.set_xlim([x,x+width])
    ax2.set_ylim([y,y+height])

    ax1.set(title=r'O[III]',
            xlabel='R.A. (J2000)',
            ylabel='Dec. (J2000)')
            
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_title('RGB')

    # format ticks with wcs
    # https://docs.astropy.org/en/stable/visualization/wcsaxes/ticks_labels_grid.html
    ax1.coords[0].set_ticks(number=3)
    ax1.coords[1].set_ticks(number=4)
    ax2.coords[0].set_ticklabel_visible(False)
    ax2.coords[1].set_ticklabel_visible(False)
    ax2.coords[0].set_ticks_visible(False)
    ax2.coords[1].set_ticks_visible(False)
    #plt.subplots_adjust(wspace=-0.4)

    # it is a bit tricky to get the coordinates right (because data uses the wcs coordinates)
    # the easiest thing is to use fractions from the figure size
    # https://matplotlib.org/3.1.3/api/_as_gen/matplotlib.patches.ConnectionPatch.html
    con = mpl.patches.ConnectionPatch(xyA=((x+width)/galaxy.shape[1],(y+height)/galaxy.shape[0]), xyB=(0,1), 
                                      coordsA="axes fraction", coordsB="axes fraction",
                                      axesA=ax1, axesB=ax2, color="black",linewidth=0.3)
    ax2.add_artist(con)
    con = mpl.patches.ConnectionPatch(xyA=((x+width)/galaxy.shape[1],(y)/galaxy.shape[0]), xyB=(0,0), 
                                      coordsA="axes fraction", coordsB="axes fraction",
                                      axesA=ax1, axesB=ax2, color="black",linewidth=0.3)
    ax2.add_artist(con)

    plt.savefig(filename,bbox_inches='tight',dpi=900)