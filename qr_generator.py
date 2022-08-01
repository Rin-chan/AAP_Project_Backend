import qrcode
from uuid import uuid4
import time

# website: https://betterprogramming.pub/how-to-generate-and-decode-qr-codes-in-python-a933bce56fd0

def create_qr_code(final_pred):
    # Build base qr
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    # QR Image path
    filename = "qr"+time.strftime("%Y%m%d-%H%M%S")+'.jpg'
    filepath = 'static/qr/'+filename
    # Data Retrieval
    unique_id = str(uuid4())
    points = pred_to_points(final_pred)
    data = '{"customID": "%s", "Points": %d }' %(unique_id, points)
    # Add data
    qr.add_data(data)
    
    # Create QR Code
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    # Save QR Code
    img.save(filepath)

    return filename


def pred_to_points(final_pred):
    if final_pred in ['desktop','printer', 'refrigerator','tv']:
        return 200
    else:
        return 100