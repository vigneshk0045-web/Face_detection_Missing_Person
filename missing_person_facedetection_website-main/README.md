# missing_person_facedetection_website
Here is the website for the missing persons/criminals face detection using yolo v8.
# Face Recognition Application

This is a face recognition application built using Streamlit, YOLOv8, and MongoDB. The application allows users to upload a photo and enter the name of the person in the photo. Admins can process the uploaded photo using CCTV footage or a webcam to determine if a match is found.

## Features

- **User Dashboard**:
  - Upload a photo and enter the name of the person in the photo.
  - Wait for the admin to process the data and receive real-time updates on whether a match is found.

- **Admin Dashboard**:
  - View uploaded photos and the associated person's name.
  - Process the uploaded photo using CCTV footage or a webcam.
  - Update the match status in the database.

## Prerequisites

- Python 3.8 or higher
- MongoDB installed and running locally or remotely
- Required Python libraries (see below)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sreevanth15/missing_person_facedetection_website.git
   cd missing_person_facedetection_website
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure MongoDB is running locally or update the connection string in `app.py`:
   ```python
   client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
   ```

5. Download the YOLOv8 model (`yolov8n.pt`) and place it in the project directory.

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open the application in your browser at `http://localhost:8501`.

### User Workflow

1. Log in as a **user** using the following credentials:
   - Username: `user`
   - Password: `user123`

2. Upload a photo and enter the name of the person in the photo.

3. Wait for the admin to process the data. The application will notify you whether a match is found.

### Admin Workflow

1. Log in as an **admin** using the following credentials:
   - Username: `admin`
   - Password: `admin123`

2. View the uploaded photo and the associated person's name.

3. Choose to process the photo using either:
   - **CCTV footage**: Upload a video file.
   - **Webcam**: Use the real-time webcam feed.

4. The application will update the match status in the database, and the user will be notified.

## File Structure

```
face/
├── app.py               # Main application file
├── auth.py              # Authentication logic
├── detection.py         # Face detection logic using YOLOv8
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
└── .venv/               # Virtual environment (not included in the repo)
```

## Dependencies

The required Python libraries are listed in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
```

### Key Libraries:
- `streamlit`: For building the web application.
- `pymongo`: For interacting with MongoDB.
- `gridfs`: For storing images in MongoDB.
- `ultralytics`: For YOLOv8 model.
- `opencv-python`: For image and video processing.
- `Pillow`: For image handling.

## Notes

- Ensure MongoDB is running before starting the application.
- Adjust the YOLOv8 model path in `detection.py` if necessary.
- The polling interval for user updates is set to 5 seconds. You can adjust this in `app.py`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [YOLOv8](https://github.com/ultralytics/ultralytics)
- [MongoDB](https://www.mongodb.com/)
