from tkinter import *
from tkinter import messagebox
import random
from PIL import Image, ImageTk
from googleapiclient.discovery import build
import requests
import io
import os
import sys
import cv2

def mainWindow():
    window = Tk()
    window.title("Random Youtube Video Fetcher")
    window.geometry("1500x900")
    icon = PhotoImage(file = "niga.png")
    window.iconphoto(True, icon)
    return window

def main():
    finalGUI = mainWindow()
    app = RandomYoutubeApp(finalGUI)
    finalGUI.mainloop()

class RandomYoutubeApp:
    def __init__(self, parentwindow):
        self.master = parentwindow
        self.apiKey = os.environ.get("YOUTUBE_API_KEY")

        if not self.apiKey:
            messagebox.showerror("Configuration Error", 
                                "API Key not found. Please set the 'YOUTUBE_API_KEY' environment variable.")
            sys.exit()

        self.YTSearch = self.searchedTopic
        self.YTApiServiceName = "youtube"
        self.YTAPiVer = "v3"
        self.maxSearchResults = 50

        try:
            self.youtube = build(self.YTApiServiceName, self.YTAPiVer, 
                            developerKey = self.apiKey)
        except Exception as e:
            print(f"Error initialzing Youtube Service: {e}")
            sys.exit()

        self.YTlist = []
        self.newYTlist = []
        self.canvasH = 620
        self.canvasW = 1100
        self.mainCanvas = Canvas(parentwindow, height = self.canvasH, width = self.canvasW,
                            borderwidth = 2, bg = "#414141")
        self.mainCanvas.pack(pady = 30, padx = 20)
        self.getButton = Button(parentwindow, relief = RAISED, width = 10, bg = "#DBDBDB",
                                text = "GET", fg = "#1F1F1F")
        self.getButton.place(y = 657, x = 650)
        self.nextButton = Button(parentwindow, relief = RAISED, width = 10, bg = "#DBDBDB",
                                text = "->", fg = "#1F1F1F")
        self.nextButton.place(y = 657, x = 735)
        self.prevButton = Button(parentwindow, relief = RAISED, width = 10, bg = "#DBDBDB",
                                text = "<-", fg = "#1F1F1F")
        self.prevButton.place(y = 657, x = 565)
        self.searchBar = Entry(parentwindow, width = 40, bg = "#FFFFFF", fg = "#000000",
                               borderwidth = 2)
        self.searchBar.insert(0, "Enter a Topic")
        self.searchBar.place(y = 10, x = 572)

    def searchQuery(self):
        self.userInputSearch = self.searchBar.get()
        try:
            if not self.userInputSearch or self.userInputSearch.isspace():
                return
            self.searchResponse = self.youtube.search().list(
                q = self.userInputSearch,
                part = "id, snippet",
                type = "video",
                maxResults = self.maxSearchResults
            ).execute()
            return self.searchResponse
        except Exception as e:
            messagebox.showerror(f"Failure in fetching Youtube Data {e}")
            return None
    
    def getRandomVideo(self, searchResults):
        if searchResults is None or "items" not in searchResults:
            messagebox.showinfo("No results")
            return None, None, None
        self.allItems = searchResults.get("items", [])
        self.videos = [item for item in self.allItems if item["id"]["kind"] == "youtube#video"]
        if not self.videos:
            messagebox.showinfo("No Videos")
            return None, None, None
        self.gotVideo = random.choice(self.videos) 
        try:
            self.title = self.gotVideo["snippet"]["title"]
            self.thumbnail = self.gotVideo["snippet"]["thumbnails"]["high"]["url"]
            self.videoID = self.gotVideo["id"]["videoId"]
            self.YTlist.append(self.gotVideo)
        except KeyError as e:
            messagebox.showerror(f"Error in extraction of: {e}")
            return None, None, None
        return self.title, self.thumbnail, self.videoID
    
    def handlerOne(self):
        self.searchResults = self.searchQuery()

        if self.searchResults is None:
            self.lastSearchResults = None
            return
        self.lastSearchResults = self.searchResults
        self.title, self.thumbnail, self.videoID = self.getRandomVideo(self.lastSearchResults)
        if self.title is None:
            return
        self.updateDisplay(self.title, self.thumbnail, self.videoID)

    def loadImage(self):
        
        for self.filename in self.YTlist:
            rawImage = cv2.resize(rawImage, (1100, 620))
            self.pilImage = Image.fromarray(self.YTlist)
            self.photo = ImageTk.PhotoImage(self.pilImage)
            self.photo.append(self.newYTlist)

            
    def displayRandomVideo(self):
        self.master.myImage = self.updateDisplay()
        self.mainCanvas.create_image(self.canvasH // 2,\
                                     self.canvasW // 2, 
                                     image = self.updateDisplay(),
                                     anchor = CENTER)
        self.insertMainTitle = self.mainCanvas.insert(self.updateDisplay())
        self.insertMainTitle.pack(pady = 10)
        self.insertVideoId = self.mainCanvas.insert(self.updateDisplay())
        self.insertVideoId.place(y = 10)

    def nextFunction(self):
        if not hasattr(self, "lastSearchResults") or self.lastSearchResults is None:
            messagebox.showinfo("Error, Please GET first")
            return
        title, thumbnail, videoID = self.getRandomVideo(self.lastSearchResults)

        if title is None:
            return
        self.updateDisplay(title, thumbnail, videoID)
     
    #def prevFunction(self):

if __name__ == "__main__":
    main()