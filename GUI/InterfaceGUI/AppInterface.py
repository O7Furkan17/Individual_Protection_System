import datetime
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pygame
import time
import math
from ultralytics import YOLO
from MongoDB.MongoDB_connect import MongoDBConnection
from MongoDB.insertData import DetectionData
from AlertSending import AlertSending
from image_taking.Computer_video import default_video as dv

pygame.init()

class EmptyFrameApp:
    def __init__(self):
        self.out = None
        self.i = 0
        self.root = tk.Tk()
        self.root.title("Individual Protection System")
        self.root.geometry("+200+100")
        self.root.resizable(False, False)
        self.root_closed = False

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

        self.select_alarm_sound_path = "../AppData/AppSounds/DangerSound.mp3"
        self.select_alarm = tk.StringVar()
        self.select_alarm.set('Alarm 1')

        self.default_image_path = "../AppData/AppPictures/camera_close.png"
        self.default_image = Image.open(self.default_image_path)
        self.default_image = self.default_image.resize((self.frame_width, self.frame_height))
        self.default_photo = ImageTk.PhotoImage(self.default_image)

        self.buttonCreate()
        self.createCanvas()
        self.createRedDot()
        self.volumeControl()

        self.show_default_image()

        self.timer_label.place_forget()

        self.model = YOLO("../../object-detection/training/yolov8_train-2.0/weights/best.pt")
        self.classNames = ['Gun', 'Knife']
        self.train = True

        self.db_connection = MongoDBConnection()
        self.detection_data = DetectionData(self.db_connection, 'DetectionDB')

        self.alert_sender = AlertSending.AlertSending()
        self.alert_sender.alertConfig("senderemeail@gmail.com", "app password")
        self.last_alert_time = None

    def createCanvas(self):
        self.canvas = tk.Canvas(self.frame, width=640, height=480, bg="gray")
        self.canvas.place(x=10, y=10)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    def buttonCreate(self):
        self.button_cameraOpen = tk.Button(self.root, height=3, width=15, text="Kamerayı başlat",
                                           command=self.cameraOpen,
                                           bg="pink", fg="black")
        self.button_cameraOpen.place(x=10, y=500)

        img = Image.open("../AppData/AppPictures/dangerPicture_transparent.png")
        img = img.resize((150, 90))
        self.danger_img = ImageTk.PhotoImage(img)
        self.button_cameraDanger = tk.Button(self.root, image=self.danger_img, command=self.cameraDanger, borderwidth=0,
                                             highlightthickness=0)
        self.button_cameraDanger.place(x=10 + self.frame_width + 10, y=10, width=185, height=100)

        self.button_snapshot = tk.Button(self.root, height=3, width=15, text="Ekran Görüntüsü", command=self.snapshot,
                                         bg="pink", fg="black")
        self.button_snapshot.place(x=250, y=500)

        img_report = Image.open("../AppData/AppPictures/reportPicture_transparent.png")
        img_report = img_report.resize((150, 90))
        self.report_img = ImageTk.PhotoImage(img_report)
        self.button_report = tk.Button(self.root, image=self.report_img, command=self.report, borderwidth=0,
                                       highlightthickness=0)
        self.button_report.place(x=10 + self.frame_width + 10, y=120, width=185, height=100)

        self.button_record = tk.Button(self.root, height=3, width=15, text="Kayıt", command=self.record, bg="pink",
                                       fg="black")
        self.button_record.place(x=130, y=500)

        img_settings = Image.open("../AppData/AppPictures/settings_transparent.png")
        img_settings = img_settings.resize((80, 90))
        self.settings_img = ImageTk.PhotoImage(img_settings)
        self.button_settings = tk.Button(self.root, image=self.settings_img, command=self.open_settings_menu, height=50,
                                         width=90)
        self.button_settings.place(x=370, y=500)

        self.timer_label = tk.Label(self.root, text="Kayıt Süresi: 00:00", font=("Helvetica", 12), bg="gray",
                                    fg="white")
        self.timer_label.place(x=self.frame_width - 150, y=self.frame_height - 50)

    def createRedDot(self):
        self.red_dot_label = tk.Label(self.root, text="●", font=("Helvetica", 20), fg="red")
        self.red_dot_label.place_forget()

    def report(self):  # not using
        detection_list= []
        self.send_alert_email(detection_list)
        messagebox.showinfo("Rapor", "Rapor oluşturuldu.")

    def send_alert_email(self, detections_list):
        alert_subject = "Detection Alert"
        alert_body = "An object was detected:\n"
        for detection in detections_list:
            alert_body += f"Class: {detection['class_name']}, Confidence: {detection['confidence']}, " \
                          f"BBox: {detection['bbox']}\n"

        alert_receivers = ["youremail@gmail.com"]

        for receiver in alert_receivers:
            self.alert_sender.send_email(receiver, alert_subject, alert_body)

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
        if self.camera_state:
            frame = self.camera.get_frame()
            if frame is not None:
                if self.train:
                    results = self.model(frame, stream=True)
                    for r in results:
                        boxes = r.boxes
                        detections_list = []
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

                            # put box in cam
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                            # confidence
                            confidence = math.ceil((box.conf[0] * 100)) / 100

                            # class name
                            cls = int(box.cls[0])
                            class_name = self.classNames[cls]

                            # object details
                            org = [x1, y1]
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            fontScale = 1
                            color = (255, 0, 0)
                            thickness = 2

                            cv2.putText(frame, class_name, org, font, fontScale, color, thickness)

                            # Add detection to the list
                            detections_list.append({
                                "class_name": class_name,
                                "confidence": confidence,
                                "bbox": [x1, y1, x2, y2]
                            })

                        if detections_list:
                            # Save the detected frame
                            timestamp = datetime.datetime.now()
                            image_path = f"detected_frames/detected_{timestamp}.jpg"
                            os.makedirs(os.path.dirname(image_path), exist_ok=True)
                            cv2.imwrite(image_path, frame)
                            image = Image.fromarray(frame)

                            # Insert detection data into MongoDB
                            self.detection_data.insert_detection(image, detections_list)

                            if self.last_alert_time is None or (timestamp - self.last_alert_time).total_seconds() >= 60:
                                self.send_alert_email(detections_list)
                                self.last_alert_time = timestamp
                            self.danger_playsound()
                else:
                    if self.zoom_size != 1:
                        frame = cv2.resize(frame, None, fx=self.zoom_size, fy=self.zoom_size,
                                           interpolation=cv2.INTER_LINEAR)

                    if self.record_state and self.out is not None:
                        self.out.write(frame)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            if not self.root_closed:
                self.root.after(10, self.update)
            else:
                self.camera.disconnect()
                self.db_connection.close_connection()
                cv2.destroyAllWindows()
                pygame.quit()


    def cameraDanger(self):
        if not self.thread1.is_alive():
            self.thread1 = threading.Thread(target=self.danger_playsound)
            self.thread1.start()

    def danger_playsound(self):
        pygame.mixer.music.load(self.select_alarm_sound_path)
        pygame.mixer.music.play()
        time.sleep(2)
        pygame.mixer.music.stop()

    def snapshot(self):
        frame = self.camera.get_frame()
        if frame is not None:
            image_path = os.path.join(r"Gallery\Pictures", f"snapshot_{self.i}.png")
            cv2.imwrite(image_path, frame)
            self.i = self.i + 1
            messagebox.showinfo("Başarılı", "Ekran görüntüsü başarıyla kaydedildi.")
        else:
            messagebox.showwarning("Uyarı", "Kamera aktif değilken ekran görüntüsü alınamaz!")

    def show_snapshot(self):
        if hasattr(self, 'snapshot_label'):
            self.snapshot_label.config(image=self.image_path)
        else:
            self.snapshot_label = tk.Label(self.root)
            self.snapshot_label.place(x=10, y=10)

    def select_images(self):
        image_files = filedialog.askopenfilenames(initialdir="../AppData/AppPictures",
                                                  filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
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
            self.button_cameraOpen.config(text="Kamerayı Aç")
            if self.camera:
                self.camera.disconnect()
                self.show_default_image()
        else:
            self.camera_state = True
            self.button_cameraOpen.config(text="Kamerayı Kapat")
            self.camera = dv.TestCamera(width=self.frame_width, height=self.frame_height)

            if self.camera.connect():
                self.update()

    def show_default_image(self):
        if self.canvas is not None:
            self.canvas.create_image(0, 0, image=self.default_photo, anchor=tk.NW)

    def record(self):
        if self.record_state:
            self.record_state = False
            self.button_record.config(text="Kayıt Başlat")
            if self.out is not None:
                self.out.release()
                self.out = None
            self.red_dot_label.place_forget()
            self.timer_label.place_forget()
        else:
            self.record_state = True
            self.button_record.config(text="Kayıt Durdur")

            directory = r"Gallery\Videos"
            if not os.path.exists(directory):
                os.makedirs(directory)

            video_path = os.path.join(directory, f"record_{self.i}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(video_path, fourcc, 20.0, (self.frame_width, self.frame_height))
            self.record_start_time = time.time()

            self.blink_red_dot()
            if not self.timer_label.winfo_ismapped():
                self.timer_label.place(x=self.frame_width - 150, y=self.frame_height - 50)

        self.i += 1
        self.update_recording_time()

    def blink_red_dot(self):
        if self.record_state:
            if self.red_dot_label.winfo_ismapped():
                self.red_dot_label.place_forget()
            else:
                self.red_dot_label.place(x=self.frame_width - 20, y=10)
            self.root.after(500, self.blink_red_dot)

    def update_recording_time(self):
        if self.record_state:
            elapsed_time = int(time.time() - self.record_start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.timer_label.config(text=f"Kayıt Süresi: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_recording_time)

    def open_settings_menu(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ayarlar")
        settings_window.geometry("300x200")

        alarm_label = tk.Label(settings_window, text="Alarm Seçin:")
        alarm_label.pack(pady=10)
        alarm_options = ["Alarm 1", "Alarm 2", "Alarm 3"]
        alarm_menu = tk.OptionMenu(settings_window, self.select_alarm, *alarm_options,
                                   command=self.update_alarm_sound_path)
        alarm_menu.pack()

        button_close = tk.Button(settings_window, text="Kapat", command=settings_window.destroy)
        button_close.pack(pady=20)

        select_images_button = tk.Button(settings_window, text="Resim Seç", command=self.select_images)
        select_images_button.pack(pady=10)

    def update_alarm_sound_path(self, selection):
        sound_map = {
            'Alarm 1': "../AppData/AppSounds/DangerSound.mp3",
            'Alarm 2': "../AppData/AppSounds/DangerSounds2.mp3",
            'Alarm 3': "../AppData/AppSounds/DangerSounds3.mp3"
        }
        self.select_alarm_sound_path = sound_map.get(selection, "../AppData/AppSounds/DangerSounds2.mp3")

    def volumeControl(self):
        self.volume_frame = tk.Frame(self.root)
        self.volume_frame.place(x=500, y=500)

        self.volume_label = tk.Label(self.volume_frame, text="Ses Seviyesi")
        self.volume_label.pack()

        self.volume_slider = tk.Scale(self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(50)
        self.volume_slider.pack()

        self.volume_tooltip = tk.Label(self.volume_frame, text="Ses seviyesini ayarlayın", bg="yellow", fg="black")
        self.volume_tooltip.place_forget()

        self.volume_slider.bind("<Enter>", self.show_tooltip)
        self.volume_slider.bind("<Leave>", self.hide_tooltip)

    def set_volume(self, volume_level):
        pygame.mixer.music.set_volume(float(volume_level) / 100.0)  # Set the volume of Pygame music

    def show_tooltip(self, event):
        self.volume_tooltip.place(x=event.x_root, y=event.y_root - 30)

    def hide_tooltip(self, event):
        self.volume_tooltip.place_forget()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.cameraZoom()
        else:
            self.cameraRemoval()

    def run(self):
        self.root.mainloop()
        self.root_closed = True


app = EmptyFrameApp()
app.run()

