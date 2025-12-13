import cv2
import numpy as np
import tempfile
from ultralytics import YOLO
import streamlit as st
from PIL import Image
import io


# Load YOLO model
def load_model():
    """
    Load the YOLOv8 model using the ultralytics library.
    """
    model = YOLO('yolov8n.pt')  # Replace with the correct path to your YOLOv8 model
    return model


def detect_faces_in_image(image, model):
    """
    Detect faces in the uploaded image using YOLOv8.
    """
    # Convert PIL.Image to bytes if necessary
    if isinstance(image, Image.Image):  # Check if the input is a PIL.Image
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()
    else:
        image_bytes = image.read()

    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Process the image with the YOLO model
    results = model(img)

    # Extract bounding box coordinates for the first detected face
    if len(results[0].boxes) > 0:
        bbox = results[0].boxes[0].xyxy[0].tolist()  # Get the first bounding box
        return img, bbox
    else:
        st.error("No face detected in the uploaded image.")
        return None, None


def detect_faces_in_video(video, reference_image, reference_bbox, model, real_time=False):
    """
    Detect faces in the uploaded video or real-time webcam feed and check if the reference face is present.
    """
    if real_time:
        cap = cv2.VideoCapture(0)  # Open webcam feed
        if not cap.isOpened():
            st.error("Error: Could not access the webcam.")
            return False
    else:
        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(video.read())
            temp_video_path = temp_video.name

        cap = cv2.VideoCapture(temp_video_path)  # Open the temporary video file

    # Check if the video file or webcam feed is opened successfully
    if not cap.isOpened():
        st.error("Error: Could not open video. Ensure the file format is supported.")
        return False

    # Convert the reference image to RGB
    reference_image_rgb = cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB)

    # Create a placeholder for displaying frames
    frame_placeholder = st.empty()

    # Loop through video frames
    found_match = False
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Skip every other frame to reduce processing time
        if frame_count % 2 != 0:
            continue

        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, (640, 360))

        # Convert the frame to RGB (YOLO expects RGB images)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # Process the frame with the YOLO model
        results = model(frame_rgb)

        # Render the processed frame (use the first result)
        processed_frame = results[0].plot()

        # Display the processed frame
        frame_placeholder.image(processed_frame, caption="Processed Frame", use_container_width=True)

        # Check if any detected face matches the reference face
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detected_face = frame_rgb[y1:y2, x1:x2]

            # Ensure the detected face region is valid
            if detected_face.size == 0:
                continue

            # Compare the detected face with the reference face using template matching
            result = cv2.matchTemplate(detected_face, reference_image_rgb, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            # If similarity is above a threshold, mark as found
            if max_val > 0.8:  # Adjust threshold as needed
                found_match = True
                break

        if found_match:
            break

    cap.release()
    cv2.destroyAllWindows()

    return found_match