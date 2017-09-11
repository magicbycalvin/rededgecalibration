import Tkinter
import PIL
from osgeo import gdal
import os
import numpy
import exifread
import tkFileDialog

#only perform an Exposure Compensation if you camera was on automatic mode (i.e. had changing shutter speed)
root = Tkinter.Tk()
currdir = os.getcwd() # current working directory
img_dir = str(tkFileDialog.askdirectory(parent=root, initialdir=currdir, title='Please select your image directory' )) # generates GUI for selecting directory with images

root = Tkinter.Tk()
save_dir = str(tkFileDialog.askdirectory(parent=root, initialdir=img_dir, title='Please select your save directory' )) # generates GUI for selecting save directory

# generate list with paths for all images
def filenames(folder):
    os.chdir(folder)
    y = []
    #SET directories (such as 001SET )
    p = []
    #other dirs such as (000, 001, etc.)
    z = []
    #image names
    e = []
    #image directory names
    for path, subdirs, files in os.walk(os.getcwd()):
        #appends list of .tif files to image names list
        for t in files:
                if t.endswith('.tif'):
                    z.append(t)
        #appends both SET and other subdirectories to list 
        for x in subdirs:
            if x.endswith('SET'):
                y.append(x)
            else:
                p.append(x)

    p = list(set(p))
    #removes the duplicates in the list
    z = list(set(z))
    #removes the duplicates in the list
    for setdir in y:
        for otherdir in p:
            for img in z:
                u = os.path.join(folder,setdir,otherdir,img)
                #make file path out of all combinations of SET folders, other folders and images
                if os.path.exists(u) == True:
                #if that image / location actually exists append it to the list
                    e.append(u)
    return e

imgpaths = filenames(img_dir)

# opens each image as numpyarray
r = 0
while r < len(imgpaths):
    filename = imgpaths[r]
    name = filename[-14:]
    t = gdal.Open(filename)
    numpyimg = numpy.array(t.GetRasterBand(1).ReadAsArray())

    # reads exposure, aperture and ISO speed
    import exifread
    f = open(filename,'rb')
    # reading exif of image, generates a dictionary
    tags = exifread.process_file(f, details=False)
    # getting specific information from exif tags
    # aperture
    if not 'EXIF FNumber' in tags:
        k = 'x'
        print filename + ' has no FNumber information!'
    else:
        k = tags['EXIF FNumber']
        k = str(k)
        k = k.split('/')
        k = float(k[0])/float(k[1])

    # exposure
    if not 'EXIF ExposureTime' in tags:
        exp = 'x'
        print filename + ' has no Exposure information!'
    else:
        exp = tags['EXIF ExposureTime']
        exp = str(exp)
        exp = exp.split('/')
        exp = float(exp[0])/float(exp[1])

    #ISO
    if not 'EXIF ISOSpeed' in tags:
        K = 'x'
        print filename + ' has no ISO information!'
    else:
        K = tags['EXIF ISOSpeed']
        K = str(K)
        K = int(K)

    # saving images in the same subdirectory format in the save directory
    if k == 'x' or exp == 'x' or K == 'x':
        r = r + 1
    else:
        subdir = filename.split(img_dir)        
        savedir = save_dir + subdir[1][:-15]
        subdir1 = subdir[1].split('SET')
        setdir = save_dir + subdir1[0]+'SET'
        if not os.path.exists(setdir):
            os.mkdir(setdir)
        if not os.path.exists(savedir):
            os.mkdir(savedir)
        os.chdir(savedir)
        # performs exposure compensation on images using equation from Pix4D, 2017
        img = numpyimg * ((((1/k)**2)/(exp*K)))
        img = PIL.Image.fromarray(img, mode=None)
        img.save(name)
        r = r + 1
        # exports images as tiffs