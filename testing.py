import moviepy.editor as mpe
from PIL import Image
from io import BytesIO
import json
import base64
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

video = mpe.VideoFileClip('tes.mp4')
print(video.fps)
frame = video.get_frame(5 * 1/video.fps)  # get the frame at t=2 seconds
