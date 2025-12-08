"""
QR Code generation utilities for credentials
"""
import io
import qrcode
from qrcode.image.pil import PilImage
from django.core.files.base import ContentFile
from django.conf import settings


def generate_qr_code_image(data, size=300, border=4):
    """
    Generate a QR code image from data
    
    Args:
        data: String data to encode in QR code
        size: Size of the QR code image (default: 300x300)
        border: Border size (default: 4)
    
    Returns:
        PIL Image object
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize if needed
    if size != 300:
        img = img.resize((size, size))
    
    return img


def generate_qr_code_file(data, filename=None, size=300):
    """
    Generate a QR code image file from data
    
    Args:
        data: String data to encode in QR code
        filename: Optional filename (default: qr_code.png)
        size: Size of the QR code image (default: 300x300)
    
    Returns:
        Django ContentFile with PNG image
    """
    img = generate_qr_code_image(data, size=size)
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = filename or 'qr_code.png'
    return ContentFile(buffer.read(), name=filename)

