"""

Image Processing Script

Currently working for images in .bmp format; have not tested for other formats
IC Capture 2.4 outputs this (lossless) format, so it is ideal to use this for saving images

How It Works:
    -A background (noise) image is analyzed. Avg noise from this img is filtered out of further images
    -A Control Image is taken of the darkest fringe (tested using another script: bright_region.py)
    -Find the destructive interference (darkest region) and call this our Region of Interest (roi throughout script)
        -Repeat this task for the Constructive Interference (Brightest spot) 
            -As we put a filter in front of the constructive ROI we must factor in the percentage to which the intensity was nulled into our calculations
    -After experiment is run we test change in intensity between Control Image and Science Image for all of the images collected that trial
    -Histograms of the intensity can also be plotted for further analysis

Note: Intensity and Luminosity are interchangeable throughout this script


******IMPORTANT NOTE**********
For some odd reason coordinates of the Control image and Science Images are transposed;
Meaning if you want to analyze about x,y = 10,20 then the input is x,y = 20,10
Not entirely sure why, may be due to how the two modules PIL & CV2 access image data

"""


import numpy as np
import numpy.ma as ma
import scipy
from scipy.stats import itemfreq
from scipy import stats
import math
from math import sqrt

import cv2

import PIL 
from PIL import Image

import matplotlib
matplotlib.use('TKAgg')
from matplotlib import pyplot as plot
from matplotlib import animation
import matplotlib.image as mpimg

from astropy.table import Table, Column
from astropy.io import ascii

#===================================================================
#			  Data Imports
#===================================================================

fract, fil, lens, visa = np.loadtxt("C:\Users\Justin\Desktop\Images_20151117\Filter2.txt", skiprows = 1, unpack = 'TRUE')


radius2, x12, y12, lum12, vis12, shift12, acc12, percent12, peracc12, x22, y22, lum22, vis22, shift22, acc22, percent22, peracc22, b2d, b2dper, exp = np.loadtxt("C:\Users\Justin\Desktop\Fizeau\Images04\Images\_20150928_02N\Blur_data.txt", skiprows=1, unpack = 'TRUE')



#===================================================================
#			Calibration Image
#===================================================================
#This is our Background Noise Image within any given frame

imag = Image.open("C:\Users\Justin\Desktop\Fizeau\Old_Images\Images03\Calibration01.bmp")

print"Calibration Image Size:", imag.size
#Image Size: 640x480
A,B = imag.size

r = 41

imag = np.array(imag)

cblur = cv2.GaussianBlur(imag, (r, r), 0)
(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(cblur)
imag = np.array(cblur)
imag = Image.fromarray(imag)


#Compiling luminosity (Intensity) of each pixel
lum_pix = []
def f():
    Lum = imag.getpixel((X,Y))
    lumpix = np.array([Lum])
    lum_pix.extend(lumpix)


for X,Y in np.ndindex((A, B)):
    f()


#Finding Average Noise
luminosity = np.array([lum_pix])
stdev1 = np.std(lum_pix)
print"Standard Deviation:", stdev1
sterr = stdev1/sqrt(len(lum_pix))
print"Standard Error:", sterr
noise = np.average(luminosity)
print"Average noise:", noise

#===================================================================
#			IMG_1 (Control)
#===================================================================

print("Acquiring Image Data...")
img = Image.open('C:\Users\Justin\Desktop\Images_20151204\Exp691_20151208_01T.bmp')
A,B = img.size
plot.title("Intensity")
plot.imshow(img)
plot.show(img)



#Convert to an array to analyze for ROI
#resp = 0.015/(4.8*33333)
#resp = 0.015/(4.8*195)
resp = 0.015/(4.8*691)
gray = np.array(img)
gfilter = np.array((gray - noise)*resp)




#===================================================================
#			REGIONS OF INTEREST [IMG_1]
#===================================================================

# apply a Gaussian blur to the image
grayroi = cv2.GaussianBlur(gfilter, (r, r), 0)
(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(grayroi)

# display the results of our newly improved method
#cv2.imshow("Regions of Interest", grayroi)
cv2.waitKey(0)

#Convert to an array to analyze
grayroi = np.array(grayroi)

r2 = 7

#_EXP195
#x = 24
#y = 12

#_EXP318
#x = 24
#y = 11

#_EXP33333_01
#x = 147
#y = 143

#EXP691_1208
x = 169
y = 88

#Generating Dark ROI IMG
roi = grayroi[x - r2: x + r2, y - r2: y + r2]
roi = np.array(roi)
roi = Image.fromarray(roi)
#plot.imshow(roi)
print"Region of Interest (DARK) Size:", roi.size

#_EXP195
#x2 = 193
#y2 = 410

#_EXP318
#x2 = 180
#y2 = 400

#_EXP33333_01
#x2 = 420
#y2 = 585

#EXP691_1208
x2 = 417
y2 = 577


#Generating Bright ROI IMG
roi2 = grayroi[x2 - r2: x2 + r2, y2 - r2: y2 + r2]
roi2 = np.array(roi2)
roi2 = Image.fromarray(roi2)
print"Region of Interest (BRIGHT) Size:", roi2.size
A2,B2 = roi2.size

#Compiling luminosity of each pixel
lum_calibration = []
lum_calib = []
lum_calibration2 = []
lum_calib2 = []
def g():
    Lum = roi.getpixel((X,Y))
    lumcalibration = np.array([Lum])
    lum_calibration.extend(lumcalibration)
    Lum2 = roi2.getpixel((X,Y))
    lumcalibration2 = np.array([Lum2])
    lum_calibration2.extend(lumcalibration2)


for X,Y in np.ndindex((A2, B2)):
    g()

#===================================================================
#			Calculations [IMG_DARK_1]
#===================================================================

#Filtering & masking Bad Data (DARK)
x = np.array(lum_calibration)
lumcalib = x[~np.isnan(x)] 
lum_calib.extend(lumcalib)


#Calculating Avg, StDev & St Error (DARK)
lumcalib = np.array([lum_calib])
stdev2 = np.std(lum_calib)
print"Standard Deviation:", stdev2
sterr2 = stdev2/sqrt(len(lum_calib))
print"Standard Error:", sterr2
calibsum = np.sum([lumcalib])
avgcalib = np.average(lumcalib)
print"Average Dark luminosity (Calibrated):", avgcalib, "+/-", sterr2
#Bada boom, bada bing you've got the avg brightness of an image right there. 



#Visibility (DARK)
#Tells us how well we aligned interferometer
maxlum = max(lum_calib)
minlum = min(lum_calib)
print"Max*Min:",abs(maxlum*minlum)
squareroot = math.sqrt(abs(maxlum*minlum))
print"Sqrt:",squareroot
denom = maxlum + minlum
vis = 2*squareroot / denom
print"Image Visibility:", vis


#===================================================================
#			CALCULATIONS [IMG_BRIGHT_1] 
#===================================================================

#Filtering Data (BRIGHT)
x2 = np.array(lum_calibration2)
#x2 = x2[x2 > noise]
lumcalib2 = x2[~np.isnan(x2)]
lum_calib2.extend(lumcalib2)

#Calculating Avg, StDev & St Error (BRIGHT)
lens = lens*resp
print"lens:",lens
lumcalib2 = np.array([(lum_calib2 + lens)])
#lumcalib2 = np.array([lum_calib2])
#We apply the Responsivity factor again as gshift ~60/256 and has not been corrected
stdev2 = np.std(lum_calib2)
print"Standard Deviation (B):", stdev2
sterr2 = stdev2/sqrt(len(lum_calib2))
print"Standard Error (B):", sterr2
avgcalib2 = np.average(lumcalib2)
print"Average Bright luminosity (Calibrated):", avgcalib2, "+/-", sterr2


#Visibility (BRIGHT)
maxlum2 = max(lum_calib2)
minlum2 = min(lum_calib2)
print"Max*Min:",abs(maxlum2*minlum2)
squareroot2 = math.sqrt(abs(maxlum2*minlum2))
print"Sqrt:",squareroot2
denom2 = maxlum2 + minlum2
vis2 = 2*squareroot2 / denom2
print"Image Visibility (BRIGHT):", vis2


#===================================================================
#			IMG_2 (Test)
#===================================================================

#Various Images to be analyzed
#filenames may need changing for further analysis if output is to a different folder
patterns = ['01']
filenames = ['C:\Users\Justin\Desktop\Images_20151204\LC_Exp691_20151208_{}T.bmp'.format(pattern) for pattern in patterns]

#for loop to open each image and print size
per_cent = []
int_shift = []
per_cent2 = []
int_shift2 = []
st_dev = []
st_err = []
st_dev2 = []
st_err2 = []
avg_sci2 = []
avg_sci = []
for filename in filenames:
    img2 = Image.open(filename)
    A, B = img2.size
    gray2 = np.array(img2)
    gfilter2 = np.array((gray2 - noise)*resp)
    #print(filename)
    grayblur = cv2.GaussianBlur(gfilter2, (r, r), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(grayblur)
    gfilter2 = np.array(grayblur)

    #Dimensions of ROI (2Rx2R)
    r2 = 7

    #Analyzing the DARK ROI

    #_EXP195
    #x = 24
    #y = 12

    #_EXP318
    #x = 24
    #y = 11

    #_12/04
    #x = 147
    #y = 143

    #EXP691_1208
    x = 169
    y = 88

    print"Dark coordinates:", x, y
    roi = gfilter2[x - r2: x + r2, y - r2: y + r2]
    roi = np.array(roi)
    roi = Image.fromarray(roi)
    A,B = roi.size
    print"Region of Interest Size:", roi.size



    #Analyzing the BRIGHT ROI

    #_EXP195
    #x2 = 193
    #y2 = 410

    #_EXP318
    #x2 = 180
    #y2 = 400

    #_EXP33333_01
    #x2 = 420
    #y2 = 585

    #EXP691_1208
    x2 = 417
    y2 = 577

    print"Bright coordinates:", x2, y2
    roi2 = gfilter2[x2 - r2: x2 + r2, y2 - r2: y2 + r2]
    roi2 = np.array(roi2)
    roi2 = Image.fromarray(roi2)
    A2,B2 = roi.size

    #Compiling luminosity of each pixel of given image ROI
    sci_calib = []
    sci_calibration = []
    sci_calib2 = []
    sci_calibration2 = []
    def h():
        sci = roi.getpixel((X,Y))
        scicalibration = np.array([sci])
        sci_calibration.extend(scicalibration)
        sci2 = roi2.getpixel((X,Y))
        scicalibration2 = np.array([sci2])
        sci_calibration2.extend(scicalibration2)

    for X,Y in np.ndindex((A2, B2)):
        h()




    #===================================================================
    #				Calculations [IMG2_DARK]
    #===================================================================

    #Filtering Data
    scicalib = np.array(sci_calibration)
    #lens = lens*resp
    #rint"lens:",lens
    #lumcalib2 = y[y > noise]
    sci_calib.extend(scicalib)

    #Calculating Avg Intensity, Standard Deviation, Standard Error
    scicalib = np.array([sci_calib], dtype = object)
    avgsci = np.average(scicalib)
    avgsci11 = np.array([avgsci])
    avg_sci.extend(avgsci11)
    print"Average luminosity 2nd Image (DRK):", avgsci

    #Intensity Shift between (DARK) images
    shift = np.array([(avgsci - avgcalib - shift22)])
    stdev = np.std(shift)
    stdev = np.array([stdev])
    st_dev.extend(stdev)
    sterr = stdev/sqrt(len(st_dev))
    sterr = np.array([sterr])
    st_err.extend(sterr)
    #print"Shift in grayscale:", shift
    percent = np.array([(shift/256)*100])
    #print"Shift in Intensity:", percent,"%"
    per_cent.extend(percent)
    int_shift.extend(shift)

    #===================================================================
    #				Calculations [IMG2_BRIGHT]
    #===================================================================

    #Filtering Data
    scicalib2 = np.array(sci_calibration2)
    scicalib2 = np.array(scicalib2)
    scicalib2 = np.array(scicalib2)
    #scicalib2 = y[y > noise]
    sci_calib2.extend(scicalib2)

    #Calculating Avg Intensity, Standard Deviation, Standard Error
    #print("Calibrated Luminosity:", lumcalib2)
    stdev2 = np.std(scicalib2)
    stdev2 = np.array([stdev2])
    #st_dev2.extend(stdev2)
    print"Standard Deviation:", stdev2
    sterr2 = stdev2/sqrt(len(sci_calib2))
    sterr2 = np.array([sterr2])
    #st_err2.extend(sterr2)
    print"Standard Error:", sterr2
    avgsci2 = np.average((scicalib2+ lens))
    avgsci22 = np.array([avgsci2])
    avg_sci2.extend(avgsci22)
    print"Average luminosity 2nd Image (BRITE):", avgsci2
    print"Avgsci2:", avgsci22

    #Intensity Shift between images
    shift2 = np.array([(avgsci2 - avgcalib2 - shift22)])
    #shift22 is the noise in intensity shift that occurs as a result of the noise in the lab
    stdev2 = np.std(shift2)
    stdev2 = np.array([stdev2])
    st_dev2.extend(stdev2)
    sterr2 = stdev2/sqrt(len(st_dev2))
    sterr2 = np.array([sterr2])
    st_err2.extend(sterr2)
    #shift2 = np.array([shift2 + (256*fract)])
    #Shift needs to be corrected for filter decreasing intensity
    percent2 = np.array([(shift2/256)*100])
    per_cent2.extend(percent2)
    int_shift2.extend(shift2)

scicalib = np.array([avgsci])
scicalib2 = np.array([avgsci2])


#===================================================================
#			Compiling Data
#===================================================================

print" "
#Compiling the data (DARK)
print"Radius of ROI:", r2
print"Average Dark luminosity (Initial):", avgcalib
print"Control Image (DARK) Visibility (Accuracy):", vis

#Standard Dev & Error (DARK)
stdev = np.array([st_dev])
avgstd = np.average(stdev)
sterr = np.array([st_err])
avgste = np.average(sterr)
pererr = (avgste/256)*100

#Percentage (DARK)
intpercent = np.array(per_cent)
persum = np.sum([intpercent])
avgper = np.average(intpercent)
stdev = np.array([st_dev])
sterr = np.array([st_err])
print"AVG Percent Change (DARK) :", avgper, "+/-", pererr,"%"

#Grayscale
intshift = np.array(int_shift)
avgshift = np.average(intshift)
print"AVG Grayscale Intensity shift (DARK):", avgshift, "+/-", avgste

DRKratio = (avgsci)/avgcalib
print"Ratio of Initial to final (DARK) Intensities:", DRKratio

print" "

#Compiling the data (BRIGHT)
print"Average Bright luminosity (Calibrated):", avgcalib2
print"Image Visibility (BRIGHT):", vis2

#Standard Dev & Error
stdev2 = np.array([st_dev2])
stdavg2 = np.average(stdev2)
sterr2 = np.array([st_err2])
avgste2 = np.average(sterr2)
pererr2 = (avgste2/256)*100

#Percent
intpercent2 = np.array(per_cent2)
avgper2 = np.average(intpercent2)
print"AVG Percent Change (BRIGHT) :", avgper2,"+/-", pererr2,"%"

#Grayscale
intshift2 = np.array(int_shift2)
avgshift2 = np.average(intshift2)
print"AVG Grayscale Intensity shift (BRIGHT):", avgshift2, "+/-", avgste2

BRTratio = (avgsci2)/avgcalib2
print"Ratio of Initial to final (BRIGHT) Intensities:", BRTratio

SUM = np.array([DRKratio,BRTratio])
print"Ratios",SUM
stdratio = np.std([SUM])
st_rat_err = []
raterr = stdratio/sqrt(len(SUM))
print(stdratio)
print"Standard Error (Ratio):", raterr
sumavg = np.average(SUM)
error = raterr/sumavg
print"Error:", (error*100), "%"

"""
error = np.array(1 - (SUM - raterr)/SUM)
avgerr = np.average(error)
print"Error:", error
print"Avg error:", (avgerr*100), "%"
"""


#===================================================================
#		Writing Data to Table
#===================================================================

r = [r2]
x = [x]
y = [y]
a = [avgcalib]
b = [vis]
c = [avgshift]
acc = [avgste]
d = [avgper]
peracc = [pererr]
x2 = [x2]
y2 = [y2]
avg2 = [avgcalib2]
e = [vis2]
f = [avgshift2]
acc2 = [avgste2]
g = [avgper2]
peracc2 = [pererr2]
h = [318]
Dratio = [DRKratio]
Bratio = [BRTratio]
stdev = [stdratio]
sterr = [raterr]


table2 = Table([a, c, acc, avg2, f, acc2, h, Dratio, Bratio, stdev, sterr], names=('Intensity (DRK)', 'D Shift', 'D acc', 'Intensity (BRITE)', 'B shift', 'B acc', 'Exp', 'D Ratio', 'B Ratio', 'St Dev', 'St Err'))
print(table2)

#ascii.write([a, c, acc, avg2, f, acc2, h, Dratio, Bratio, stdev, sterr],"C:\Users\Justin\Desktop\Image_Scripts\Exp691_2015108.txt", names=('Intensity (DRK)', 'D Shift', 'D acc', 'Intensity (BRITE)', 'B shift', 'B acc', 'Exp', 'D Ratio', 'B Ratio','St Dev', 'St Err'))


"""
Sources:

Brightness
http://stackoverflow.com/questions/6442118/python-measuring-pixel-brightness
Histograms: bin width
http://stats.stackexchange.com/questions/798/calculating-optimal-number-of-bins-in-a-histogram-for-n-where-n-ranges-from-30
Finding brightest region
http://www.pyimagesearch.com/2014/09/29/finding-brightest-spot-image-using-python-opencv/

"""
