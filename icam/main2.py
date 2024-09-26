import streamlit as st
import cv2
import pandas as pd
import os
import time
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

    if vertices_array is not None and data:
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

# Input for the IP Webcam URL
ip_address = st.text_input("Enter the IP Webcam URL (e.g., 'http://192.168.x.x:8080/video'): ")

# Input for the number of scans
num_scans = st.number_input("Enter the number of scans:", min_value=1, value=1)

# Input for the time interval between scans in seconds
interval = st.number_input("Enter the time interval between scans (in seconds):", min_value=1, value=5)

if st.button("Scan QR Code"):
    if ip_address:  # Proceed only if the IP address is provided
        all_decoded_data = []

        for i in range(num_scans):
            with st.spinner(f"Scanning {ip_address}... (Scan {i + 1}/{num_scans})"):
                decoded_data = scan_qr_code(ip_address)
                if decoded_data and decoded_data != "No QR code detected.":
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    all_decoded_data.append([timestamp, decoded_data])
                    st.success(f"Decoded Data: {decoded_data}")
                else:
                    st.warning(f"No QR code detected at {ip_address}.")

            if i < num_scans - 1:  # Wait only between scans, not after the last scan
                time.sleep(interval)

        # Save all decoded data to Excel after completing all scans
        if all_decoded_data:
            save_to_excel(all_decoded_data)
            st.success("All data saved to Excel file.")
    else:
        st.error("Please enter a valid IP Webcam URL.")
