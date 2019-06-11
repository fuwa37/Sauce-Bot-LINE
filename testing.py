import moviepy.editor as mpe
from PIL import Image
import base64
from io import BytesIO
import json
import os
import cloudinary.uploader
import cloudinary.api
import trace
from hsauce.get_source import get_source_data


config = json.loads(os.environ.get('cloudinary_config', None))

cloudinary.config(
    cloud_name=config['name'],
    api_key=config['key'],
    api_secret=config['secret']
)

video = mpe.VideoFileClip('tes2.gif')
frame = video.get_frame(1)  # get the frame at t=2 seconds

pil_img = Image.fromarray(frame)
buff = BytesIO()
pil_img.save(buff, format="JPEG")
b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
res = cloudinary.uploader.upload('data:image/jpg;base64,' + b64, tags="TEMP")

url = res['url']

print(trace.res(url))
