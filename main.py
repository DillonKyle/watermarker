from PIL import Image, ImageDraw, ImageFont
import os, sys
from exif import Image as ExifImage
import PySimpleGUI as sg

def generate_watermark_images(photo_dir):
    export_dir = (photo_dir + '/watermarked_images/')
    if os.path.exists(export_dir) == False:
        os.mkdir(export_dir)
    for filename in os.listdir(photo_dir):
        if filename.endswith('.JPG') or filename.endswith('.jpg'):
            file_path = f'{photo_dir}/{filename}'
            export_path = f'{export_dir}{filename}'

            # images
            base_image = Image.open(file_path)
            watermarked_image = base_image.copy()
            meta_image = ExifImage(file_path)

            # extract metadata
            date_time = meta_image.get("datetime")
            lat_dms = meta_image.get("gps_latitude")
            lat = (float(lat_dms[0]) + float(lat_dms[1])/60 + float(lat_dms[2])/(60*60))
            long_dms = meta_image.get("gps_longitude")
            long = (float(long_dms[0]) + float(long_dms[1])/60 + float(long_dms[2])/(60*60)) * -1
            exif = base_image.info['exif']

            # Thermal images (smaller resolution)
            if base_image.size[0] < 2000 and base_image.size[1] < 2000:
                # watermark params
                draw = ImageDraw.Draw(watermarked_image)
                watermark = "Firmatek, LLC " + str(date_time) + ", Lat: " + str(lat) + ", Long: " + str(long) + " "
                font = ImageFont.truetype("arial.ttf", 10)
                position = (2, 2)
                bbox = draw.textbbox((position[0] - 2, position[1] - 2), watermark, font=font)

                # add watermark
                draw.rectangle(bbox, fill="white")
                draw.text(position, watermark, font=font, fill="black")

                # export image
                watermarked_image.save(export_path, exif=exif)

            # RGB images (higher resolution)
            elif base_image.size[0] > 2000 and base_image.size[1] > 2000:
                # watermark params
                draw = ImageDraw.Draw(watermarked_image)
                watermark = "Firmatek, LLC " + str(date_time) + ", Lat: " + str(lat) + ", Long: " + str(long) + " "
                font = ImageFont.truetype("arial.ttf", 48)
                position = (10, 10)
                bbox = draw.textbbox((position[0] - 5, position[1] - 5), watermark, font=font)

                # add watermark
                draw.rectangle(bbox, fill="white")
                draw.text(position, watermark, font=font, fill="black")

                # export image
                watermarked_image.save(export_path, exif=exif)
    return


sg.theme('DarkAmber')

status = [(''), ('Generating Watermarked Images, Please Wait...'), ('No Images Selected')]

folder = [[sg.Text('Image Folder'), sg.In(size=(25,1), enable_events=True ,key='photo_dir'), sg.FolderBrowse()]]
layout = [[sg.Column(folder, element_justification='c')],[sg.Text(text=status[0], size=(50,1), text_color='white', key='INDICATOR', justification='center')],[sg.Button('Ok'), sg.Button('Cancel')]]    
window = sg.Window('Watermarker', layout,resizable=True)   

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == 'Ok' and values['photo_dir'] == '':
        window['INDICATOR'].update(value=status[2])
    elif event == 'Ok' and values['photo_dir']:
        window['INDICATOR'].update(value=status[1])
        photo_dir = values['photo_dir']
        window.perform_long_operation(lambda:generate_watermark_images(photo_dir), 'COMPLETE')
    elif event =='COMPLETE':
        window['INDICATOR'].update(value=status[0])
        sg.popup("Watermarking Completed")
        
    if event =='Cancel':
        raise SystemExit 
window.close()