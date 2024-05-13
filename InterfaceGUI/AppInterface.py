import tkinter as tk
import default_video as dv
from PIL import Image, ImageTk
import cv2
from playsound import playsound
import threading
import time
import os
from tkinter import messagebox

class EmptyFrameApp:
    def __init__(self):
       
        self.i=0
        self.root = tk.Tk()
        self.root.title("Individual Protection System")
        self.root.geometry("+200+100")
        self.root.resizable(False, False)  
       
        self.frame = tk.Frame(self.root, width=850, height=570)
        self.frame.pack()

        self.camera = None  
        self.canvas = None  
        self.photo = None  
        self.zoom_size = 1
        self.camera_state = False 
        self.frame_height=480
        self.frame_width= 640
        
        self.thread1 = threading.Thread(target=self.danger_playsound)

        self.buttonCreate()
        self.createCanvas()
   
    def createCanvas(self):
        self.canvas = tk.Canvas(self.frame, width=640, height=480, bg="gray")  
        self.canvas.place(x=10,y=10)
    
    def buttonCreate(self):
        button_cameraOpen = tk.Button(self.root, height=3, width=15, text="Kamerayı başlat", command=self.cameraOpen)
        button_cameraOpen.place(x=10, y=500)  

        button_camerazoom=tk.Button(self.root, height=3, width=15, text="Yakınlaştır", command=self.cameraZoom)
        button_camerazoom.place(x=130,y=500) 

        button_cameraRemoval=tk.Button(self.root,height=3, width=15, text="Uzaklaştır", command=self.cameraRemoval)
        button_cameraRemoval.place(x=250,y=500) 

        button_cameraDanger=tk.Button(self.root,height=5, width=25, text="TEHLİKE", command=self.cameraDanger,bg="red",fg="white")
        button_cameraDanger.place(x=10+self.frame_width+10,y=10)

        button_snapshot=tk.Button(self.root,height=3, width=15, text="Ekran Görüntüsü", command=self.snapshot)
        button_snapshot.place(x=370,y=500) 

        button_report=tk.Button(self.root,height=5, width=25, text="RAPOR", command=self.snapshot,bg="grey",fg="black")
        button_report.place(x=10+self.frame_width+10, y=10 + button_cameraDanger.winfo_height() + 100)

    def cameraOpen(self):
        self.camera = dv.TestCamera(width=self.frame_width, height=self.frame_height)
        self.camera_state = self.camera.connect()

        self.canvas.delete("all")  
        self.photo = None  
        self.update()  
    
    def cameraZoom(self):
        if self.zoom_size <= 2 and self.camera_state:
            self.zoom_size += 0.2
        if self.camera_state==False:
            messagebox.showinfo("BİLGİ KUTUSU", "Kamera açmadan yakınlaştırma yapamazsınız!" )    
        
    def cameraRemoval(self):
        if self.zoom_size > 1 and self.camera_state: 
            self.zoom_size -= 0.2
        if self.camera_state==False:
            messagebox.showinfo("BİLGİ KUTUSU", "Kamera açmadan uzaklaştırma yapamazsınız!" )       

    def update(self):
        frame = self.camera.get_frame()
        if frame is not None:
            if(self.zoom_size != 1):
                frame = cv2.resize(frame, None, fx=self.zoom_size, fy=self.zoom_size, interpolation=cv2.INTER_LINEAR)

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.root.after(10, self.update)  

    def cameraDanger(self):
        if self.thread1.is_alive()==False:
            self.thread1.start()

    def danger_playsound(self):
        playsound('C:\\Users\\EBRAR TÜRÜDÜ\\Desktop\\VSCODE PYTHON\\ArayuzGUI\\Sounds\\DangerSound.mp3')

    def snapshot(self):
        frame = self.camera.get_frame()  
        if frame is not None:
            cv2.imwrite("snapshot_"+str(self.i)+".png", frame)
            self.i = self.i + 1

    def run(self):
        
        self.root.mainloop()

if __name__ == "__main__":
    app = EmptyFrameApp()
    app.run()
