import tkinter as tk
from tkinter import filedialog  
import default_video as dv
from PIL import Image, ImageTk
import cv2
from playsound import playsound
import threading
import time
from tkinter import messagebox

class EmptyFrameApp:
    def __init__(self):
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

        self.frame_height = 480
        self.frame_width = 640
        
        self.thread1 = threading.Thread(target=self.danger_playsound)
        self.blinking = False

        self.default_alarm_sound_ = r"InterfaceGUI\Sounds\DangerSound.mp3"
        self.select_alarm=tk.StringVar()
        self.select_alarm.set('Alarm 1')

        self.buttonCreate()
        self.createCanvas()
        self.createRedDot()

        self.timer_label.place_forget()
   
    def createCanvas(self):
        self.canvas = tk.Canvas(self.frame, width=640, height=480, bg="gray")
        self.canvas.place(x=10,y=10)
        self.canvas.bind("<MouseWheel>",self.on_mousewheel)
    
    def buttonCreate(self):
        self.button_cameraOpen = tk.Button(self.root, height=3, width=15, text="Kamerayı başlat", command=self.cameraOpen, bg="pink", fg="black")
        self.button_cameraOpen.place(x=10, y=500)

        self.button_camerazoom = tk.Button(self.root, height=3, width=15, text="Yakınlaştır", command=self.cameraZoom, bg="pink", fg="black")
        self.button_camerazoom.place(x=130,y=500)

        self.button_cameraRemoval = tk.Button(self.root, height=3, width=15, text="Uzaklaştır", command=self.cameraRemoval, bg="pink", fg="black")
        self.button_cameraRemoval.place(x=250,y=500)

        self.button_cameraDanger = tk.Button(self.root, height=5, width=25, text="TEHLİKE", command=self.cameraDanger, bg="red", fg="white")
        self.button_cameraDanger.place(x=10+self.frame_width+10,y=10)

        self.button_snapshot = tk.Button(self.root, height=3, width=15, text="Ekran Görüntüsü", command=self.snapshot, bg="pink", fg="black")
        self.button_snapshot.place(x=370,y=500)

        self.button_report = tk.Button(self.root, height=5, width=25, text="RAPOR", command=self.snapshot, bg="grey", fg="black")
        self.button_report.place(x=10+self.frame_width+10, y=10 + self.button_cameraDanger.winfo_height() + 100)

        self.button_record = tk.Button(self.root, height=3, width=15, text="Kayıt", command=self.record, bg="pink", fg="black")
        self.button_record.place(x=490,y=500)

        self.button_settings = tk.Button(self.root, height=3, width=15, text="Ayarlar", command=self.open_settings_menu, bg="pink", fg="black")
        self.button_settings.place(x=610,y=500)

        self.timer_label = tk.Label(self.root, text="Kayıt Süresi: 00:00", font=("Helvetica", 12), bg="gray", fg="white")
        self.timer_label.place(x=self.frame_width - 150, y=self.frame_height - 50)  # Sağ alt köşe
    
    def createRedDot(self):
        
        self.red_dot_label = tk.Label(self.root, text="●", font=("Helvetica", 20), fg="red")
        self.red_dot_label.place_forget()

    def cameraOpen(self):
        self.camera = dv.TestCamera(width=self.frame_width, height=self.frame_height)
        self.camera_state = self.camera.connect()

        self.canvas.delete("all")
        self.photo = None
        self.update()

    def cameraZoom(self):
        if self.zoom_size <= 2 and self.camera_state:
            self.zoom_size += 0.2
        if not self.camera_state:
            messagebox.showinfo("BİLGİ KUTUSU", "Kamera açmadan yakınlaştırma yapamazsınız!")

    def cameraRemoval(self):
        if self.zoom_size > 1 and self.camera_state: 
            self.zoom_size -= 0.2
        if not self.camera_state:
            messagebox.showinfo("BİLGİ KUTUSU", "Kamera açmadan uzaklaştırma yapamazsınız!")

    def update(self):
        frame = self.camera.get_frame()
        if frame is not None:
            if(self.zoom_size != 1):
                frame = cv2.resize(frame, None, fx=self.zoom_size, fy=self.zoom_size, interpolation=cv2.INTER_LINEAR)

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
            cv2.imwrite("snapshot_"+str(self.i)+".png", frame)
            self.i = self.i + 1
   
    def record(self):
     if self.record_state:
        self.record_state = False
        self.button_record.config(text="Kayıt Başlat")
        self.out.release()
        self.red_dot_label.place_forget()  
        self.timer_label.place_forget()  
     else:
        self.record_state = True
        self.button_record.config(text="Kayıt Durdur")
        
        self.out = cv2.VideoWriter("record_"+str(self.i)+".avi", cv2.VideoWriter_fourcc('M','J','P','G'), 20.0, (self.frame_width, self.frame_height))
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
            timer_text = "Kayıt Süresi: {:02d}:{:02d}".format(minutes, seconds)
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
        self.settings_menu = tk.Toplevel(self.root)
        self.settings_menu.title("Ayarlar")
        self.settings_menu.geometry("300x200")

       
        alarm_button = tk.Button(self.settings_menu, text="Alarm Seç", command=self.select_alarm_sound)
        alarm_button.pack(pady=10)

        sound_on_button = tk.Button(self.settings_menu, text="Ses Aç", command=self.turn_sound_on)
        sound_on_button.pack(pady=10)

        sound_off_button = tk.Button(self.settings_menu, text="Ses Kapa", command=self.turn_sound_off)
        sound_off_button.pack(pady=10)

        camera_settings_button = tk.Button(self.settings_menu, text="Kamera Ayarları", command=self.open_camera_settings)
        camera_settings_button.pack(pady=10)  

    def select_alarm_sound(self):
    
     alarm_file = filedialog.askopenfilename(initialdir="C:/Users/EBRAR TÜRÜDÜ/Desktop/VSCODE PYTHON/InterfaceGUI/Sounds",
                                             title="Alarm Sesini Seç",
                                             filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*")))
     if alarm_file:
        self.select_alarm_sound_path=alarm_file
        print("Seçilen alarm sesi:", alarm_file)
  
    def turn_sound_on(self):
    
        self.sound_on = True
    
        playsound("sound_on.mp3") 

    def turn_sound_off(self):
        
        self.sound_on = False
    
        playsound("sound_off.mp3") 

    def open_camera_settings(self):
    
     camera_settings_window = tk.Toplevel(self.root)
     camera_settings_window.title("Kamera Ayarları")
     camera_settings_window.geometry("300x200")

     apply_button = tk.Button(camera_settings_window, text="Ayarları Uygula", command=camera_settings_window.destroy)
     apply_button.pack()

    def run(self):
        self.root.mainloop()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.cameraZoom()
        elif event.delta < 0:
            self.cameraRemoval()

if __name__ == "__main__":
    app = EmptyFrameApp()
    app.run()