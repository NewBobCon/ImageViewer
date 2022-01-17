# ImageViewer.py
# Program to start evaluating an image in python
#
# Show the image with:
# os.startfile(imageList[n].filename)

from tkinter import *
import math, os, sys, subprocess
from PixInfo import PixInfo

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
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()
        self.list_iterator = -20
        self.max_iterator = 0
        self.images_tup = []
        
        
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
        self.resultsScrollbar = Scrollbar(resultsFrame)
        self.resultsScrollbar.pack(side=RIGHT, fill=Y)

        resultsControl = Frame(resultsFrame)
        resultsControl.pack(side=BOTTOM)
        next20Button = Button(resultsControl, text="Next 20", fg="green", padx=10, width=10, command=lambda: self.show_next(self.images_tup))
        next20Button.pack(side=RIGHT)
        prev20Button = Button(resultsControl, text="Last 20", fg="green", padx=10, width=10, command=lambda: self.show_prev(self.images_tup))
        prev20Button.pack(side=LEFT)
        
        
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
        button.grid(row=0, sticky=E)
        
        self.b1 = Button(controlFrame, text="Color-Code", padx = 10, width=10, command=lambda: self.find_distance(method='CC'))
        self.b1.grid(row=1, sticky=E)
        
        b2 = Button(controlFrame, text="Intensity", padx = 10, width=10, command=lambda: self.find_distance(method='inten'))
        b2.grid(row=2, sticky=E)
        
        self.resultLbl = Label(controlFrame, text="Results:")
        self.resultLbl.grid(row=3, sticky=W)
        
        
        # Layout Preview.
        self.selectImg = Label(previewFrame, image=self.photoList[0])
        self.selectImg.pack()
    
    
    # Event "listener" for listbox change.
    def update_preview(self, event):
        i = self.list.curselection()[0]
        self.selectImg.configure(image=self.photoList[int(i)])
    
    
    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses the comparison method of the passed 
    # binList
    def find_distance(self, method):
        selected = self.list.curselection()[0]
        self.list_iterator = -20
        self.max_iterator = 0
        sortedTup = []
        sortedTup = self.man_dis(method, selected)
        sortedTup.sort(key=lambda x: x[2])
        for i in range(len(sortedTup)):
            filename = sortedTup[i][0].filename
            img = sortedTup[i][1]
            fileObj = [filename, img]
            sortedTup[i] = fileObj
        self.images_tup = sortedTup
        self.show_next(sortedTup)
        return
	#your code

    def man_dis(self, method, selected):
        selectedPixSize = self.pixSizeList[selected]
        distance = 0
        count = 0
        distanceList = []
        if method == "CC":
            selectedCC = self.colorCode[selected]                
            for i in self.colorCode:
                distance = 0
                for j in range(len(i)):
                    otherPixSize = self.pixSizeList[count] #len(list(self.imageList[count].getdata()))
                    distance += abs((selectedCC[j] / selectedPixSize) - (i[j] / otherPixSize))  
                distanceList.append([self.imageList[count], self.photoList[count] ,distance])
                count += 1
            return distanceList
        if method == "inten":
            selectedIn = self.intenCode[selected]
            for i in self.intenCode:
                distance = 0
                for j in range(len(i)):
                    otherPixSize = self.pixSizeList[count] #len(list(self.imageList[count].getdata()))
                    distance += abs((selectedIn[j] / selectedPixSize) - (i[j] / otherPixSize))  
                distanceList.append([self.imageList[count], self.photoList[count] ,distance])
                count += 1
            return distanceList
        return

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
        fullsize = (0, 0, (self.xmax*cols), (self.ymax*cols))
        
        # Initialize the canvas with dimensions equal to the 
        # number of results.
        self.canvas.delete(ALL)
        #resultWin.geometry(str(int(self.xmax*cols)) + 'x' + str(int(self.ymax*cols/2)))
        self.canvas.config(width=self.xmax*cols, height=self.ymax*cols/2, yscrollcommand=self.resultsScrollbar.set, scrollregion=fullsize)
        self.canvas.pack()
        self.resultsScrollbar.config(command=self.canvas.yview)
        
        # your code
        photoRemain = sortedTup
        
        # Place images on buttons, then on the canvas in order
        # by distance.  Buttons envoke the inspect_pic method.
        rowPos = 0
        while photoRemain:
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for (filename, img) in photoRow:
                link = Button(self.canvas, image=img)
                handler = lambda f=filename: self.inspect_pic(f)
                link.config(command=handler)
                link.pack(side=LEFT, expand=YES)
                self.canvas.create_window(colPos, rowPos, anchor=NW, window=link, width=self.xmax, height=self.ymax)
                colPos += self.xmax
                
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
    #resultWin.geometry('300x300')
    resultWin.title('Result Viewer')
    resultWin.protocol('WM_DELETE_WINDOW', lambda: None)

    pixInfo = PixInfo(root)

    imageViewer = ImageViewer(root, pixInfo, resultWin)

    root.mainloop()

