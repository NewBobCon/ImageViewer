# PixInfo.py
# Program to start evaluating an image in python

from PIL import Image, ImageTk
import glob, os, math


# Pixel Info class.
class PixInfo:
    
    # Constructor.
    def __init__(self, master):
    
        self.master = master
        self.imageList = []
        self.photoList = []
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []
        
        # Add each image (for evaluation) into a list, 
        # and a Photo from the image (for the GUI) in a list.
        for infile in glob.glob('images/*.jpg'):
            
            file, ext = os.path.splitext(infile)
            im = Image.open(infile)
            
            
            # Resize the image for thumbnails.
            imSize = im.size
            x = int(imSize[0]/4)
            y = int(imSize[1]/4)
            imResize = im.resize((x, y), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(imResize)
            
            
            # Find the max height and width of the set of pics.
            if x > self.xmax:
              self.xmax = x
            if y > self.ymax:
              self.ymax = y
            
            
            # Add the images to the lists.
            self.imageList.append(im)
            self.photoList.append(photo)


        # Create a list of pixel data for each image and add it
        # to a list.
        for im in self.imageList[:]:
            
            pixList = list(im.getdata())
            CcBins, InBins = self.encode(pixList)
            self.colorCode.append(CcBins)
            self.intenCode.append(InBins)
            return
        
            

    # Bin function returns an array of bins for each 
    # image, both Intensity and Color-Code methods.
    def encode(self, pixlist):
        
        # 2D array initilazation for bins, initialized
        # to zero.
        CcBins = [0]*64
        InBins = [0]*25

           #your code
        bitmask = 192
        for pixel in pixlist:
            
            #Color coding
            R = pixel[0] & bitmask
            G = pixel[1] & bitmask
            B = pixel[2] & bitmask

            colorCode = 0
            colorCode += B
            colorCode = colorCode >> 2
            colorCode += G
            colorCode = colorCode >> 2
            colorCode += R
            colorCode = colorCode >> 2
            CcBins[colorCode] += 1

            #Intensity coding
            intensity = pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114
            intensity = int(intensity / 10)
            if intensity > 24:
                intensity = 24
            InBins[intensity] += 1

        # Return the list of binary digits, one digit for each
        # pixel.
        return CcBins, InBins
    
    
    # Accessor functions:
    def get_imageList(self):
        return self.imageList
    
    def get_photoList(self):
        return self.photoList
    
    def get_xmax(self):
        return self.xmax
    
    def get_ymax(self):
        return self.ymax
    
    def get_colorCode(self):
        return self.colorCode
        
    def get_intenCode(self):
        return self.intenCode
    
    
