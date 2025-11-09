from tkinter import *
from tkinter import messagebox
import random
from PIL import Image, ImageTk
from googleapiclient.discovery import build
import requests
import io
import os
import sys

def mainWindow():
    window = Tk()
    window.title("Random Youtube Video Fetcher")
    window.geometry("1500x900")
    try:
        icon = PhotoImage(file = "niga.png")
        window.iconphoto(True, icon)
    except Exception:
        # ignore missing icon
        pass
    return window

def main():
    finalGUI = mainWindow()
    app = RandomYoutubeApp(finalGUI)
    finalGUI.mainloop()

class RandomYoutubeApp:
    def __init__(self, parentwindow):
        self.master = parentwindow
        # prefer environment variable, fallback to any hardcoded key if present
        self.apiKey = os.getenv("YOUTUBE_API_KEY") 
        if not self.apiKey:
            messagebox.showerror("Configuration Error", 
                                "API Key not found. Please set the 'YOUTUBE_API_KEY' environment variable.")
            sys.exit()

        self.YTApiServiceName = "youtube"
        self.YTAPiVer = "v3"
        self.maxSearchResults = 50

        try:
            self.youtube = build(self.YTApiServiceName, self.YTAPiVer, developerKey = self.apiKey)
        except Exception as e:
            messagebox.showerror("Youtube Init Error", f"Error initializing Youtube Service: {e}")
            sys.exit()

        # storage for videos (dicts from API) and current index
        self.YTlist = []
        self.currentIndex = -1

        # canvas sizes
        self.canvasH = 620
        self.canvasW = 1100
        self.mainCanvas = Canvas(parentwindow, height = self.canvasH, width = self.canvasW,
                            borderwidth = 2, bg = "#414141")
        self.mainCanvas.pack(pady = 30, padx = 20)

        # buttons and search
        self.getButton = Button(parentwindow, relief = RAISED, width = 10, bg = "#DBDBDB",
                                text = "GET", fg = "#1F1F1F", command = self.handlerOne)
        self.getButton.place(y = 657, x = 650)
        self.nextButton = Button(parentwindow, relief = RAISED, width = 10, bg = "#DBDBDB",
                                text = "->", fg = "#1F1F1F", command = self.nextFunction)
        self.nextButton.place(y = 657, x = 735)
        self.prevButton = Button(parentwindow, relief = RAISED, width = 10, bg = "#DBDBDB",
                                text = "<-", fg = "#1F1F1F", command = self.prevFunction)
        self.prevButton.place(y = 657, x = 565)
        self.searchBar = Entry(parentwindow, width = 40, bg = "#FFFFFF", fg = "#000000",
                               borderwidth = 2)
        self.searchBar.insert(0, "Enter a Topic")
        self.searchBar.place(y = 10, x = 572)

        # keep reference to PhotoImage to prevent GC
        self._photo_image = None

    def searchQuery(self):
        self.userInputSearch = self.searchBar.get().strip()
        try:
            if not self.userInputSearch:
                return None
            self.searchResponse = self.youtube.search().list(
                q = self.userInputSearch,
                part = "id,snippet",
                type = "video",
                maxResults = self.maxSearchResults
            ).execute()
            return self.searchResponse
        except Exception as e:
            messagebox.showerror("Youtube Search Error", f"Failure in fetching Youtube Data: {e}")
            return None

    def pickRandomFromResults(self, searchResults):
        if searchResults is None or "items" not in searchResults:
            messagebox.showinfo("No results")
            return None
        items = searchResults.get("items", [])
        videos = [item for item in items if item.get("id", {}).get("kind") == "youtube#video"]
        if not videos:
            messagebox.showinfo("No Videos Found")
            return None
        return random.choice(videos)

    def download_and_prepare_image(self, url):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
            img = img.resize((self.canvasW, self.canvasH), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def displayVideo(self, index):
        if index < 0 or index >= len(self.YTlist):
            return
        video = self.YTlist[index]
        title = video["snippet"]["title"]
        thumbnail_url = video["snippet"]["thumbnails"].get("high", {}).get("url") or \
                        video["snippet"]["thumbnails"].get("default", {}).get("url")
        video_id = video["id"].get("videoId") or video["id"].get("channelId") or ""

        # clear canvas
        self.mainCanvas.delete("all")

        # download and show thumbnail
        img = None
        if thumbnail_url:
            img = self.download_and_prepare_image(thumbnail_url)
        if img:
            self._photo_image = img  # keep reference
            self.mainCanvas.create_image(self.canvasW//2, self.canvasH//2, image=self._photo_image, anchor=CENTER)
        else:
            # placeholder rectangle if no image
            self.mainCanvas.create_rectangle(0, 0, self.canvasW, self.canvasH, fill="#222222")

        # draw title and id
        # title at bottom
        self.mainCanvas.create_text(self.canvasW//2, self.canvasH - 30, text=title, fill="white", font=("Arial", 18), width=self.canvasW-20)
        # video id at top-left
        self.mainCanvas.create_text(10, 10, text=f"Video ID: {video_id}", fill="white", anchor="nw", font=("Arial", 10))

    def handlerOne(self):
        searchResults = self.searchQuery()
        if searchResults is None:
            return
        picked = self.pickRandomFromResults(searchResults)
        if picked is None:
            return
        # reset list and add first picked
        self.YTlist = [picked]
        self.currentIndex = 0
        self.displayVideo(self.currentIndex)

    def nextFunction(self):
        if not self.YTlist:
            messagebox.showinfo("Error", "Please GET first")
            return
        # If there are more cached videos, go next; otherwise pick a new random and append
        if self.currentIndex < len(self.YTlist) - 1:
            self.currentIndex += 1
        else:
            # try to pick another from the last search results if available
            try:
                last_search = getattr(self, "searchResponse", None)
                picked = self.pickRandomFromResults(last_search)
                if picked:
                    self.YTlist.append(picked)
                    self.currentIndex = len(self.YTlist) - 1
            except Exception:
                pass
        self.displayVideo(self.currentIndex)

    def prevFunction(self):
        if not self.YTlist:
            messagebox.showinfo("Error", "Please GET first")
            return
        self.currentIndex = (self.currentIndex - 1) % len(self.YTlist)
        self.displayVideo(self.currentIndex)

if __name__ == "__main__":
    main()