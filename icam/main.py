import streamlit as st
import cv2
import pandas as pd
import os
from datetime import datetime


# Function to capture video from IP Webcam and detect QR codes
def scan_qr_code(ip_address):
    # Capture video from the IP Webcam URL
    cap = cv2.VideoCapture(ip_address)

    if not cap.isOpened():
        st.error("Error: Could not open video stream from IP Webcam.")
        return None

    # Read a single frame from the video stream
    ret, frame = cap.read()
    cap.release()  # Release the video capture after reading one frame

    if not ret:
        st.error("Error: Failed to grab frame.")
        return None

    # Initialize the QRCode detector
    detector = cv2.QRCodeDetector()

    # Detect and decode the QR code
    data, vertices_array, _ = detector.detectAndDecode(frame)

    if vertices_array is not None:
        return data
    else:
        return "No QR code detected."


# Function to save the decoded data to an Excel file
def save_to_excel(data):
    # Define the Excel file name
    file_name = "qr_code_data.xlsx"

    # Check if the file exists
    if os.path.exists(file_name):
        # If the file exists, append to it
        df_existing = pd.read_excel(file_name)
        df_new = pd.DataFrame(data, columns=["Timestamp", "Decoded Data"])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(file_name, index=False)
    else:
        # If the file does not exist, create it
        df = pd.DataFrame(data, columns=["Timestamp", "Decoded Data"])
        df.to_excel(file_name, index=False)

    return file_name


# Streamlit user interface
st.title("QR Code Scanner using IP Webcam")
ip_address = st.text_input("Enter the IP Webcam URL (e.g., 'http://192.168.x.x:8080/video'):")

if st.button("Scan QR Code"):
    if ip_address:
        with st.spinner("Scanning..."):
            decoded_data = scan_qr_code(ip_address)
            if decoded_data:
                st.success(f"Decoded Data: {decoded_data}")

                # Save the decoded data to Excel
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_to_excel([[timestamp, decoded_data]])
                st.success("Data saved to Excel file.")
            else:
                st.warning("No QR code detected.")
    else:
        st.error("Please enter a valid IP Webcam URL.")
