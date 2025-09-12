import qrcode
from io import BytesIO
import base64

def generate_bus_qr_code(bus_id, base_url):
    """
    Generate a QR code image as base64 string for the bus boarding URL.
    :param bus_id: ID of the bus
    :param base_url: Base URL of the site, e.g. https://example.com
    :return: base64 encoded PNG image string
    """
    url = f"{base_url}handle_boarding/{bus_id}/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str
