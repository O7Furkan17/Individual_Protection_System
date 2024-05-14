import os
import shutil
import sys

def move_jpeg_images(source_dir, destination_dir):
    # Hedef klasörü oluştur
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Kaynak klasördeki tüm dosyaları kontrol et
    for filename in os.listdir(source_dir):
        # Dosya yolu oluştur
        file_path = os.path.join(source_dir, filename)

        # Eğer bir dosya ise ve .jpg uzantılı ise
        if os.path.isfile(file_path) and filename.lower().endswith('.jpg') or filename.lower().endswith('.png')  or filename.lower().endswith('.jpeg'):
            # Dosyayı hedef klasöre taşı
            shutil.move(file_path, os.path.join(destination_dir, filename))


if __name__ == "__main__":
    # Kaynak ve hedef klasör yollarını dışarıdan parametre alın
    if len(sys.argv) != 3:
        print("Kullanım: python script.py <kaynak_klasör_yolu> <hedef_klasör_yolu>")
        sys.exit(1)

    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    # .jpg uzantılı resim dosyalarını taşı
    move_jpeg_images(source_dir, destination_dir)
