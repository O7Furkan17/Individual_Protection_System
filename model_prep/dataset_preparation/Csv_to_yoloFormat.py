import pandas as pd
import os
import sys


def convert_to_yolo_format(csv_path, output_dir):
    # CSV dosyasını oku
    df = pd.read_csv(csv_path)

    # Her görüntü için YOLO formatında bir txt dosyası oluştur
    for image_file in df['file'].unique():
        # Görüntü dosya adını oluştur
        image_filename = os.path.basename(image_file)
        image_name, _ = os.path.splitext(image_filename)

        objects = []

        for index, row in df[df['file'] == image_file].iterrows():
            # Koordinatları normalleştir. Yolo formatı -> class x_merkez y_merkez genişlik yükseklik
            width = row['width']
            height = row['height']
            x_center = (row['xmin'] + row['xmax']) / (2 * width)
            y_center = (row['ymin'] + row['ymax']) / (2 * height)
            box_width = (row['xmax'] - row['xmin']) / width
            box_height = (row['ymax'] - row['ymin']) / height

            # Tehlikeli nesne sınıf sayısı tek olarak ayarlandı
            # Diğer nesneler için burası değiştirilmeli = 1
            class_index = 0

            # YOLO formatında koordinatları ve sınıf indeksini ekleyin
            objects.append(f"{class_index} {x_center} {y_center} {box_width} {box_height}")


        if objects:
            with open(os.path.join(output_dir, f"{image_name}.txt"), 'w') as txt_file:
                txt_file.write("\n".join(objects))


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Kullanım: python script.py <csv_dosyası_yolu> <output_dizin>")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_dir = sys.argv[2]

    # YOLO formatına dönüştürme işlemini başlat
    convert_to_yolo_format(csv_path, output_dir)
