import cv2
import numpy as np
from PIL import Image
import io
import base64

def decode_image(image_data):
    """Decode image from various formats (base64, bytes, file)"""
    try:
        # If it's base64 string
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        return img
    except Exception as e:
        raise ValueError(f"Image decode error: {str(e)}")

def encode_image(img, format='JPEG'):
    """Encode numpy image to base64"""
    _, buffer = cv2.imencode(f'.{format.lower()}', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/{format.lower()};base64,{img_base64}"

def resize_image(img, max_size=800):
    """Resize image while maintaining aspect ratio"""
    h, w = img.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
