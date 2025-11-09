

import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np

# Load Model
model = YOLO("best.pt")  # Ensure best.pt exists
st.set_page_config(
    page_title="EcoLot - Smart Parking System",
    page_icon="assets/logo.png",  # Your logo
    layout="wide"
)

# Hide Streamlit default menu & footer
hide_st_ui = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
# st.markdown(hide_st_ui, unsafe_allow_html=True)
# st.set_page_config(page_title="EcoLot - A smart and predictive parking management system", layout="wide")

st.markdown("""
    <h1 style="text-align:center; color:#2E86C1;">🚗 Smart Parking Detection System</h1>
    <p style="text-align:center; font-size:18px;">Upload a parking lot image to analyze available and occupied spots.</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Parking Lot Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:

    # Store bytes once ✅
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    input_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)  # Keep original copy
    img = input_img.copy()  # We'll draw boxes on this

    # Run YOLO
    results = model(img)

    vacant_count = 0
    car_count = 0
    spot_id = 1
    spot_results = []

    class_names = ['Car', 'Vacant']

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            label = class_names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            spot_label = f"Spot-{spot_id}"
            spot_id += 1

            if label == "Vacant":
                vacant_count += 1
                color = (0, 255, 0)
                spot_results.append(f"<span style='color:green; font-weight:600;'>{spot_label}: ✅ Vacant</span>")
            else:
                car_count += 1
                color = (0, 0, 255)
                spot_results.append(f"<span style='color:red; font-weight:600;'>{spot_label}: 🚗 Occupied</span>")

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, f"{spot_label}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    img_output = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_img_rgb = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Input Image")
        st.image(input_img_rgb, use_column_width=True)

    with col2:
        st.subheader("📤 Processed Output")
        st.image(img_output, use_column_width=True)

    st.markdown("""
        <style>
        .card { padding: 15px; border-radius: 10px; text-align:center; font-size:20px; font-weight:600; }
        .green-card { background-color:#D4EFDF; color:#1D8348; }
        .red-card { background-color:#F5B7B1; color:#922B21; }
        </style>
    """, unsafe_allow_html=True)

    colA, colB = st.columns(2)
    colA.markdown(f"<div class='card green-card'>🟢 Vacant Spots: {vacant_count}</div>", unsafe_allow_html=True)
    colB.markdown(f"<div class='card red-card'>🔴 Occupied Spots: {car_count}</div>", unsafe_allow_html=True)

    st.markdown("<h3>🅿️ Spot-by-Spot Status</h3>", unsafe_allow_html=True)
    for status in spot_results:
        st.markdown(status, unsafe_allow_html=True)

else:
    st.info("⬆️ Please upload an image to begin.")

