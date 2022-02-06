# ImageViewer.py
# Program to start evaluating an image in python
#
# Show the image with:
# os.startfile(imageList[n].filename)

from tkinter import *
import math, os, sys, subprocess
from PixInfo import PixInfo
import statistics
# Main app.
class ImageViewer(Frame):
    
    # Constructor.
    def __init__(self, master, pixInfo, resultWin):
        
        Frame.__init__(self, master)
        self.master    = master
        self.pixInfo   = pixInfo
        self.resultWin = resultWin
        self.pixSizeList = pixInfo.get_pixSizeList()
        self.colorCode = pixInfo.get_colorCode()
        self.intenCode = pixInfo.get_intenCode()
        self.normalizedFeatureList = pixInfo.get_normalizedFeatureList()
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()
        self.list_iterator = -20
        self.max_iterator = 0
        self.var1 = IntVar()
        self.queryChange = False
        self.images_tup = []
        #Relevancy CheckButton variable list
        self.varList = []
        self.relList = []

        for i in range(100):
            self.varList.append(IntVar())
        
        
        # Create Main frame.
        mainFrame = Frame(master)
        mainFrame.pack()
        
        
        # Create Picture chooser frame.
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT)
        
        
        # Create Control frame.
        controlFrame = Frame(mainFrame)
        controlFrame.pack(side=RIGHT)
        
        
        # Create Preview frame.
        previewFrame = Frame(mainFrame, width=self.xmax+45, height=self.ymax)
        previewFrame.pack_propagate(0)
        previewFrame.pack(side=RIGHT)
        

        # Create Results frame.
        resultsFrame = Frame(self.resultWin)
        resultsFrame.pack(side=TOP)
        self.canvas = Canvas(resultsFrame)

        resultsControl = Frame(resultsFrame)
        resultsControl.pack(side=BOTTOM)

        # Add Buttons to results screen
        next20Button = Button(resultsControl, text="Next 20", fg="green", padx=10, width=10, command=lambda: self.show_next(self.images_tup))
        next20Button.pack(side=RIGHT)
        prev20Button = Button(resultsControl, text="Last 20", fg="green", padx=10, width=10, command=lambda: self.show_prev(self.images_tup))
        prev20Button.pack(side=LEFT)
        self.relCheckButton = Checkbutton(resultsControl, text="Relevance", variable=self.var1, onvalue=1, offvalue=0, command=lambda: self.update_results(self.images_tup[self.list_iterator:self.max_iterator]))
        
        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(listFrame, yscrollcommand=self.listScrollbar.set, selectmode=BROWSE, height=10)
        for i in range(len(self.imageList)):
            self.list.insert(i, self.imageList[i].filename)
        self.list.pack(side=LEFT, fill=BOTH)
        self.list.activate(1)
        self.list.bind('<<ListboxSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.list.yview)
        
        
        # Layout Controls.
        button = Button(controlFrame, text="Inspect Pic", fg="red", padx = 10, width=10, command=lambda: self.inspect_pic(self.list.get(ACTIVE)))
        button.grid(row=0, sticky=NSEW)
        
        self.b1 = Button(controlFrame, text="Color-Code", padx = 10, width=10, command=lambda: self.find_distance(method='CC'))
        self.b1.grid(row=1, sticky=NSEW)
        
        self.b2 = Button(controlFrame, text="Intensity", padx = 10, width=10, command=lambda: self.find_distance(method='inten'))
        self.b2.grid(row=2, sticky=NSEW)

        self.b3 = Button(controlFrame, text="CC + Intensity", padx = 10, width = 10, command=lambda: self.find_distance(method="CC+inten"))
        self.b3.grid(row=3, sticky=NSEW)

        self.resultLbl = Label(controlFrame, text="Results:")
        self.resultLbl.grid(row=4, sticky=NSEW)
        
        # Layout Preview.
        self.selectImg = Label(previewFrame, image=self.photoList[0])
        self.selectImg.pack()
    
    
    # Event "listener" for listbox change.
    def update_preview(self, event):
        self.queryChange = True
        i = self.list.curselection()[0]
        self.selectImg.configure(image=self.photoList[int(i)])
    
    
    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses the comparison method of the passed 
    # binList
    def find_distance(self, method):
        selected = self.list.curselection()[0] #Grab the selected image
        self.list_iterator = -20
        self.max_iterator = 0
        sortedTup = []
        sortedTup = self.man_dis(method, selected) #Get manhattan distance on the selected image using proper method. Returns as [[filename, image_preview, distance_val]]
        sortedTup.sort(key=lambda x: x[2]) #Sort by the distance value returned
        if self.varList[0].get() == 0:
            for i in range(len(sortedTup)): #Iterate through the sorted list to retrieve the file names and images for proper output to results page
                filename = sortedTup[i][0].filename
                sortedTup[i][0] = filename
        else:
            for i, im in enumerate(sortedTup):
                for rel in self.relList:
                    if im[0] == rel[2]:
                        self.varList[i].set(1)
                        break
                    else:
                        self.varList[i].set(0)
        self.images_tup = sortedTup #Allow self to reference the sorted list
        self.show_next(sortedTup) #Push the sorted images to the results screen
        return

    # Manhattan distance function that takes in a method (color code or intensity)
    # and the selected image to compare all other images to.
    # Finds the distance value and puts them into a list
    # to be returned to the find_distance function.
    def man_dis(self, method, selected):
        selectedPixSize = self.pixSizeList[selected]
        distance = 0
        count = 0
        distanceList = []
        self.relList = []

        if method == "CC+inten":
            if self.queryChange:
                for i in range(100):
                    self.varList[i] = IntVar()  
                self.queryChange = False
            if self.varList[0].get() != 0:
                stdevavgList = []
                weightList = []
                minStdev = sys.maxsize
                weight = 1
                weightSum = 0
                self.relList.append([self.normalizedFeatureList[self.images_tup[0][3]], 0, self.images_tup[0][0]])
                for i in range(1, 100):
                    if self.varList[i].get() == 1:
                        self.relList.append([self.normalizedFeatureList[self.images_tup[i][3]], i, self.images_tup[i][0]])                                
                print(len(self.relList))
                for i in range(89):
                    sample = []
                    for j in range(len(self.relList)):
                        sample.append(self.relList[j][0][i])
                    stdeviation = statistics.stdev(sample)
                    if(stdeviation < minStdev and stdeviation != 0):
                        minStdev = stdeviation
                    average = statistics.mean(sample)
                    stdevavgList.append([stdeviation, average])
                for i in range(89):
                    if stdevavgList[i][0] == 0 and stdevavgList[i][1] != 0:
                        stdevavgList[i][0] = 0.5 * minStdev
                        weight = 1/stdevavgList[i][0]
                    elif stdevavgList[i][0] == 0 and stdevavgList[i][1] == 0:
                        weight = 0
                    else:
                        weight = 1 / stdevavgList[i][0]
                    weightSum += weight
                    weightList.append(weight)
                for i in range(89):
                    weightList[i] /= weightSum
                for i in range(1, 100):
                    distance = 0
                    for j in range(89):
                        distance += weightList[j] * abs(self.relList[0][0][j] - self.normalizedFeatureList[self.images_tup[i][3]][j])
                    self.images_tup[i][2] = distance
                return self.images_tup
            self.relCheckButton.pack(side=TOP)
            selectedFeats = self.normalizedFeatureList[selected]
            for i in self.normalizedFeatureList:
                distance = 0
                for j in range(len(i)):
                    distance += 1/89 * abs(selectedFeats[j] - self.normalizedFeatureList[count][j])
                distanceList.append([self.imageList[count], self.photoList[count], distance, count])
                count += 1

        elif method == "CC":
            if(self.var1.get() == 1):
                for i in range(100):
                    self.varList[i] = IntVar()
            self.relCheckButton.pack_forget()
            self.var1.set(0)
            selectedCC = self.colorCode[selected]                
            for i in self.colorCode:
                distance = 0
                for j in range(len(i)):
                    otherPixSize = self.pixSizeList[count]
                    distance += abs((selectedCC[j] / selectedPixSize) - (i[j] / otherPixSize))  
                distanceList.append([self.imageList[count], self.photoList[count] ,distance, count])
                count += 1

        elif method == "inten":
            if(self.var1.get() == 1):
                for i in range(100):
                    self.varList[i] = IntVar()
            self.relCheckButton.pack_forget()
            self.var1.set(0)
            selectedIn = self.intenCode[selected]
            for i in self.intenCode:
                distance = 0
                for j in range(len(i)):
                    otherPixSize = self.pixSizeList[count]
                    distance += abs((selectedIn[j] / selectedPixSize) - (i[j] / otherPixSize))  
                distanceList.append([self.imageList[count], self.photoList[count] ,distance, count])
                count += 1

        return distanceList

    # Increment the results page to the next 20
    # images while checking to make sure it's not
    # gone past the max number of images.
    def show_next(self, sortedTup):
        if(self.max_iterator >= len(sortedTup)):
            return
        self.list_iterator += 20
        self.max_iterator += 20
        Tup20 = []
        for i in range(self.list_iterator, self.max_iterator):
            Tup20.append(sortedTup[i])
        self.update_results(Tup20)
        return

    # Decrements the results page to the last 20
    # images while checking to make sure it's not
    # gone past the minumum number of images.
    def show_prev(self, sortedTup):  
        if(self.max_iterator <= 20):
            return
        Tup20 = []
        self.list_iterator -= 20
        self.max_iterator -= 20
        for i in range(self.list_iterator, self.max_iterator):
            Tup20.append(sortedTup[i])
        self.update_results(Tup20)
        return

    # Update the results window with the sorted results.
    def update_results(self, sortedTup):
        cols = int(math.ceil(math.sqrt(len(sortedTup))))
        
        # Initialize the canvas with dimensions equal to the 
        # number of results.
        self.canvas.delete(ALL)
        self.canvas.config(width=self.xmax*cols, height=self.ymax*cols/1.25)
        self.canvas.pack()
        
        photoRemain = sortedTup
        
        # Place images on buttons, then on the canvas in order
        # by distance.  Buttons envoke the inspect_pic method.
        
        rowPos = 0
        counter = 0
        while photoRemain:
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for (filename, img, distance, index) in photoRow:
                link = Button(self.canvas, image=img)
                handler = lambda f=filename: self.inspect_pic(f)
                link.config(command=handler)
                link.pack(side=LEFT)
                self.canvas.create_window(colPos, rowPos, anchor=NW, window=link, width=self.xmax, height=self.ymax)
                if self.var1.get() == 1:
                    relButton = Checkbutton(link, text="relevant", variable = self.varList[self.list_iterator + counter], onvalue=1, offvalue=0)
                    relButton.pack(side=BOTTOM)  
                else:
                    for i in range(100):
                        self.varList[i] = IntVar()
                colPos += self.xmax
                counter += 1
                
            rowPos += self.ymax
    
    
    # Open the picture with the default operating system image
    # viewer.
    def inspect_pic(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])


# Executable section.
if __name__ == '__main__':

    root = Tk()
    root.title('Image Analysis Tool')

    resultWin = Toplevel(root)
    resultWin.title('Result Viewer')
    resultWin.protocol('WM_DELETE_WINDOW', lambda: None)

    pixInfo = PixInfo(root)

    imageViewer = ImageViewer(root, pixInfo, resultWin)

    root.mainloop()

