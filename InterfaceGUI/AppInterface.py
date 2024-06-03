import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import os
import time
import threading
from playsound import playsound
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import default_video as dv
import tkinter as tk
from tkinter import filedialog  
from tkinter import messagebox
from ultralytics import YOLO
import math

class EmptyFrameApp:
    def __init__(self):
        self.out = None
        self.i = 0
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
        self.record_state = False 
        self.camera_state = False
        self.record_start_time = 0
        self.message_box_open = False 

        self.frame_height = 480
        self.frame_width = 640
        
        self.thread1 = threading.Thread(target=self.danger_playsound)
        self.blinking = False

        self.select_alarm_sound_path = r"C:\Users\EBRAR TÜRÜDÜ\Desktop\VSCODE PYTHON\InterfaceGUI\AppData\AppSounds\DangerSound.mp3"
        self.select_alarm = tk.StringVar()
        self.select_alarm.set('Alarm 1')

        self.default_image_path = r"InterfaceGUI\AppData\AppPictures\camera_close.png"         
        self.default_image = Image.open(self.default_image_path)
        self.default_image = self.default_image.resize((self.frame_width, self.frame_height))
        self.default_photo = ImageTk.PhotoImage(self.default_image)

        self.buttonCreate()
        self.createCanvas()
        self.createRedDot()
        self.volumeControl()
        
        self.show_default_image()

        self.timer_label.place_forget()

        self.model = YOLO(r"InterfaceGUI\AppData\best.pt")
        self.classNames = ["handgun","shotgun","weapon","Knife"]
        self.train = False
   
    def createCanvas(self):
        self.canvas = tk.Canvas(self.frame, width=640, height=480, bg="gray")
        self.canvas.place(x=10, y=10)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
    
    def buttonCreate(self):
        self.button_cameraOpen = tk.Button(self.root, height=3, width=15, text="START CAMERA", command=self.cameraOpen, bg="pink", fg="black")
        self.button_cameraOpen.place(x=10, y=500)
        
        img = Image.open(r"InterfaceGUI\AppData\AppPictures\dangerPicture_transparent.png")
        img = img.resize((150, 90))
        self.danger_img = ImageTk.PhotoImage(img)
        self.button_cameraDanger = tk.Button(self.root, image=self.danger_img, command=self.cameraDanger, borderwidth=0, highlightthickness=0)
        self.button_cameraDanger.place(x=10 + self.frame_width + 10, y=10, width=185, height=100)
        
        self.button_snapshot = tk.Button(self.root, height=3, width=15, text="SCREENSHOT", command=self.snapshot, bg="pink", fg="black")
        self.button_snapshot.place(x=250, y=500)

        img_report = Image.open(r"InterfaceGUI\AppData\AppPictures\reportPicture_transparent.png")
        img_report = img_report.resize((150, 90))
        self.report_img = ImageTk.PhotoImage(img_report)
        self.button_report = tk.Button(self.root, image=self.report_img, command=self.report, borderwidth=0, highlightthickness=0)
        self.button_report.place(x=10 + self.frame_width + 10, y=120, width=185, height=100)
        
        self.button_record = tk.Button(self.root, height=3, width=15, text="RECORD", command=self.record, bg="pink", fg="black")
        self.button_record.place(x=130, y=500)

        self.button_settings = tk.Button(self.root,height=3,width=15, text="SETTİNGS" ,command=self.open_settings_menu, bg='pink',fg='black')
        self.button_settings.place(x=370, y=500)

        self.timer_label = tk.Label(self.root, text="REGİSTRATİON DURATİON: 00:00", font=("Helvetica", 12), bg="gray", fg="white")
        self.timer_label.place(x=self.frame_width - 150, y=self.frame_height - 50) 
    
    def createRedDot(self):
        self.red_dot_label = tk.Label(self.root, text="●", font=("Helvetica", 20), fg="red")
        self.red_dot_label.place_forget()

    def report(self):####Bu deneme amaçlı yazılmış bir koddur
     messagebox.showinfo("REPORT", "Rapor oluşturuldu.")  

    def cameraZoom(self):
        if self.zoom_size <= 2 and self.camera_state:
            self.zoom_size += 0.2
        if not self.camera_state:
            messagebox.showinfo("INFORMATION BOX", "You cannot zoom without opening the camera!")

    def cameraRemoval(self):
        if self.zoom_size > 1 and self.camera_state: 
            self.zoom_size -= 0.2
        if not self.camera_state:
            messagebox.showinfo("INFORMATION BOX", "You cannot zoom out without opening the camera!")

    def update(self):
      if self.camera_state: 
        frame = self.camera.get_frame()
        if frame is not None:
            if self.train:
                results = self.model(frame, stream=True)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

                        # put box in cam
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                        # confidence
                        confidence = math.ceil((box.conf[0]*100))/100

                        # class name
                        cls = int(box.cls[0])

                        # object details
                        org = [x1, y1]
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        fontScale = 1
                        color = (255, 0, 0)
                        thickness = 2

                        cv2.putText(frame, self.classNames[cls], org, font, fontScale, color, thickness)
            else:
                if self.zoom_size != 1:
                    frame = cv2.resize(frame, None, fx=self.zoom_size, fy=self.zoom_size, interpolation=cv2.INTER_LINEAR)
                
                if self.record_state and self.out is not None:
                    self.out.write(frame)
        
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        self.root.after(10, self.update)

    def cameraDanger(self):
        if not self.thread1.is_alive():  
            self.thread1 = threading.Thread(target=self.danger_playsound)  
            self.thread1.start()

    def danger_playsound(self):
        playsound(self.select_alarm_sound_path)
    
    def snapshot(self):
        frame = self.camera.get_frame()
        if frame is not None:
            image_path = os.path.join(r"InterfaceGUI\Gallery\Pictures", f"snapshot_{self.i}.png")
            cv2.imwrite(image_path, frame)
            self.i = self.i + 1
            messagebox.showinfo("SUCCESSFULLY", "Screenshot saved successfully.")
        else:
         messagebox.showwarning("WARNING", "Cannot take screenshots when camera is not active!")
   
    def show_snapshot(self):
       
            if hasattr(self, 'snapshot_label'):
                self.snapshot_label.config(image=self.image_path)
            else:
                self.snapshot_label = tk.Label(self.root)
                self.snapshot_label.place(x=10, y=10)  

    def select_images(self):
        image_files = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
        if image_files:
            self.show_selected_images(image_files)

    def show_selected_images(self, image_files):
        self.canvas.delete("all")  

        for image_file in image_files:
            image = Image.open(image_file)
            image = image.resize((850, 570))  
            photo = ImageTk.PhotoImage(image=image)

            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo 

    def cameraOpen(self):
     if self.camera_state:
        self.camera_state = False
        self.button_cameraOpen.config(text="CAMERA OPEN")
        if self.camera:
            self.camera.disconnect()  
            self.show_default_image()  
     else:
        self.camera_state = True
        self.button_cameraOpen.config(text="CAMERA CLOSE")
        self.camera = dv.TestCamera(width=self.frame_width, height=self.frame_height)

        if self.camera.connect():
            self.update()  

    def show_default_image(self):
        if self.canvas is not None:
            self.canvas.create_image(0, 0, image=self.default_photo, anchor=tk.NW)
    
    def record(self):
        if self.record_state:
            self.record_state = False
            self.button_record.config(text="Start Recording")
            if self.out is not None:
                self.out.release()
                self.out = None
            self.red_dot_label.place_forget()  
            self.timer_label.place_forget()
        else:
            self.record_state = True
            self.button_record.config(text="Stop Recording")
           
            self.directory = r"InterfaceGUI\Gallery\Videos"
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
            
            video_path = os.path.join(self.directory, f"record_{self.i}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  
            self.out = cv2.VideoWriter(video_path, fourcc, 20.0, (self.frame_width, self.frame_height))
            self.record_start_time = time.time()
            
            self.blink_red_dot()
            if not self.timer_label.winfo_ismapped():
                self.timer_label.place(x=self.frame_width - 150, y=self.frame_height - 50)

        self.i += 1
        self.update_record_timer()

    def update_record_timer(self):
        if self.record_state:
            current_time = time.time()
            elapsed_time = current_time - self.record_start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            timer_text = "Registration Duration: {:02d}:{:02d}".format(minutes, seconds)
            self.timer_label.config(text=timer_text)
            self.root.after(1000, self.update_record_timer)

    def blink_red_dot(self):
        if self.record_state:
            if self.blinking:
                self.red_dot_label.place_forget()  
                self.blinking = False
            else:
                self.red_dot_label.place(x=self.frame_width - 20, y=10)  
                self.blinking = True
            self.root.after(500, self.blink_red_dot)  
            
    def open_settings_menu(self):
        if not self.message_box_open:
            self.message_box_open=True
            self.settings_menu = tk.Toplevel(self.root)
            self.settings_menu.title("Settings")
            self.settings_menu.geometry("300x200")

            alarm_button = tk.Button(self.settings_menu, text="Select Alarm", command=self.select_alarm_sound)
            alarm_button.pack(pady=10)

            camera_settings_button = tk.Button(self.settings_menu, text="Camera Settings", command=self.open_camera_settings)
            camera_settings_button.pack(pady=10)  

            select_images_button = tk.Button(self.settings_menu, text="Select Images", command=self.select_images)
            select_images_button.pack(pady=10)

            self.settings_menu.protocol("WM_DELETE_WINDOW",self.on_settings_close) 
    
    def on_settings_close(self):
        self.message_box_open=False
        self.settings_menu.destroy()

    def volumeControl(self):
        self.volume_frame = tk.Frame(self.root, width=80, height=80)
        self.volume_frame.place(x=490, y=500)
        
        self.volume_slider = tk.Scale(self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, fg="black")
        self.volume_slider.set(self.get_current_volume())
        self.volume_slider.pack(side=tk.TOP, padx=0, pady=0)
    
        self.volume_frame.bind("<Enter>", self.show_volume_tooltip)
        self.volume_frame.bind("<Leave>", self.hide_volume_tooltip)

    def show_volume_tooltip(self, event=None):
        tooltip_x = self.volume_frame.winfo_rootx() + self.volume_frame.winfo_width() // 2
        tooltip_y = self.volume_frame.winfo_rooty() - 25
        self.volume_tooltip = tk.Label(self.root, text="Sound Level", bg="lightyellow", fg="black", relief=tk.SOLID, borderwidth=1)
        self.volume_tooltip.place(x=tooltip_x, y=tooltip_y)

    def hide_volume_tooltip(self, event=None):
        if hasattr(self, 'volume_tooltip'):
            self.volume_tooltip.destroy()
    
    def select_alarm_sound(self):
        alarm_file = filedialog.askopenfilename(initialdir="C:/Users",
                                                title="Choose Alarm Sound",
                                                filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*")))
        if alarm_file:
            self.select_alarm_sound_path = alarm_file
            print("Selected alarm sound:", alarm_file)
  
    def set_volume(self, volume):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume_level = int(volume) / 100.0
            volume_interface.SetMasterVolume(volume_level, None)

    def get_current_volume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)
            return int(volume_interface.GetMasterVolume() * 100)

    def on_key_press(self, event):
        if event.keysym == 'plus':
            current_volume = self.get_current_volume()
            if current_volume < 100:
                new_volume = min(current_volume + 10, 100)
                self.set_volume(new_volume)
                self.volume_slider.set(new_volume)  
        elif event.keysym == 'minus':
            current_volume = self.get_current_volume()
            if current_volume > 0:
                new_volume = max(current_volume - 10, 0)
                self.set_volume(new_volume)
                self.volume_slider.set(new_volume) 

    def open_camera_settings(self):
        camera_settings_window = tk.Toplevel(self.root)
        camera_settings_window.title("Camera Settings")
        camera_settings_window.geometry("300x200")

        apply_button = tk.Button(camera_settings_window, text="Apply Settings", command=camera_settings_window.destroy)
        apply_button.pack()

    def run(self):
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.mainloop()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.cameraZoom()
        elif event.delta < 0:
            self.cameraRemoval()
            
if __name__ == "__main__":
    app = EmptyFrameApp()
    app.run()