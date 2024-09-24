import cv2
import numpy as np
from pyzbar.pyzbar import decode
import streamlit as st
from PIL import Image
import requests

# Function to rotate image and detect QR codes
def scan_qr_code(frame):
    qr_codes = decode(frame)
    if qr_codes:
        for qr_code in qr_codes:
            data = qr_code.data.decode('utf-8')
            return data

    for angle in [90, 180, 270]:
        rotated_frame = np.rot90(frame, k=angle // 90)
        qr_codes_rotated = decode(rotated_frame)
        if qr_codes_rotated:
            for qr_code in qr_codes_rotated:
                data = qr_code.data.decode('utf-8')
                return data
    return None

# Streamlit app for QR code scanning
st.title("IP Webcam QR Code Scanner")

ip_url = st.text_input("Enter the IP Webcam URL (e.g., http://192.168.29.156:8080/shot.jpg)", "")

def get_frame_from_ipcam(ip_url):
    try:
        response = requests.get(ip_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        st.error(f"Error fetching image: {e}")
        return None

if st.button("Start QR Code Scan"):
    if ip_url:
        frame = get_frame_from_ipcam(ip_url)
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            st.image(img_pil, caption="Snapshot from Webcam")

            qr_data = scan_qr_code(frame)
            if qr_data:
                st.success(f"QR Code Content: {qr_data}")
            else:
                st.error("No QR Code detected. Try again!")
        else:
            st.error("Unable to capture frame from IP webcam.")
    else:
        st.warning("Please enter a valid IP webcam URL.")
