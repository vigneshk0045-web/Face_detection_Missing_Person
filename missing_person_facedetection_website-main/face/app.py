import streamlit as st
from detection import detect_faces_in_image, detect_faces_in_video, load_model
from auth import login, logout, is_logged_in, get_user_role
from pymongo import MongoClient  # Import MongoDB client
import gridfs  # For storing images in MongoDB
import io
from PIL import Image
import time  # Add this for polling

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["face_app"]  # Database name
fs = gridfs.GridFS(db)  # GridFS for storing images
entries_collection = db["entries"]  # Collection for storing match details


def save_to_db(photo, photo_name, person_name, match_status=None, found=None, not_found=None):
    """
    Save uploaded photo, photo name, person name, and match details to MongoDB.
    """
    # Convert photo to bytes
    photo_bytes = io.BytesIO()
    photo.save(photo_bytes, format="PNG")
    photo_id = fs.put(photo_bytes.getvalue(), filename=photo_name)  # Use the photo name

    # Save match details
    entries_collection.insert_one({
        "photo_id": photo_id,
        "photo_name": photo_name,  # Store photo name
        "person_name": person_name,  # Store person name
        "match_status": match_status,
        "found": found,
        "not_found": not_found
    })


def get_latest_entry():
    """
    Retrieve the latest entry from MongoDB.
    """
    entry = entries_collection.find_one(sort=[("_id", -1)])
    if entry:
        photo = Image.open(io.BytesIO(fs.get(entry["photo_id"]).read()))
        return photo, entry["photo_name"], entry["person_name"], entry["match_status"], entry["found"], entry["not_found"]
    return None, None, None, None, None, None


def user_dashboard():
    st.title("User Dashboard")
    st.header("Upload a Photo and Enter Name")
    uploaded_photo = st.file_uploader("Choose an image (e.g., a face photo)...", type=["jpg", "jpeg", "png"])
    person_name = st.text_input("Enter the name of the person in the photo")

    if uploaded_photo and person_name:
        photo_name = uploaded_photo.name  # Get the name of the uploaded photo
        save_to_db(Image.open(uploaded_photo), photo_name, person_name)  # Save photo and name to MongoDB
        st.success("Photo and name uploaded successfully. Please wait for the admin to process the data.")

        # Poll for match status updates
        st.info("Waiting for admin to process the data...")
        while True:
            entry = entries_collection.find_one({"photo_name": photo_name})  # Ensure correct entry is retrieved
            if entry and entry.get("match_status") is not None:  # Check if match_status is updated
                match_status = entry["match_status"]
                if match_status == "Match Found":
                    st.success("Match found!")
                else:
                    st.warning("No match found.")
                break
            time.sleep(5)  # Poll every 5 seconds


def admin_dashboard():
    st.title("Admin Dashboard")
    st.header("Process Uploaded Photo")

    photo, photo_name, person_name, match_status, found, not_found = get_latest_entry()

    if photo is not None:
        st.image(photo, caption=f"Uploaded Photo: {photo_name}", use_container_width=True)
        st.write(f"Person Name: {person_name}")

        # Choose between CCTV footage or real-time webcam feed
        st.header("Choose Video Source")
        video_source = st.radio("Select a video source:", ("Upload CCTV Footage", "Use Webcam"))

        if st.button("Process"):
            model = load_model()
            reference_image, reference_bbox = detect_faces_in_image(photo, model)

            if reference_image is not None:
                match_status = "No Match Found"
                found, not_found = 0, 0

                if video_source == "Upload CCTV Footage":
                    uploaded_video = st.file_uploader("Choose a video file (e.g., CCTV footage)...", type=["mp4", "avi", "mov"])
                    if uploaded_video is not None:
                        st.write("Processing CCTV footage...")
                        found = detect_faces_in_video(uploaded_video, reference_image, reference_bbox, model, real_time=False)

                        if found:
                            st.success("Match found in the CCTV footage!")
                            match_status = "Match Found"
                        else:
                            st.warning("No match found in the CCTV footage.")

                elif video_source == "Use Webcam":
                    st.write("Accessing webcam...")
                    found = detect_faces_in_video(None, reference_image, reference_bbox, model, real_time=True)

                    if found:
                        st.success("Match found in the webcam feed!")
                        match_status = "Match Found"
                    else:
                        st.warning("No match found in the webcam feed.")

                not_found = 1 - found
                # Update the database with match results
                entries_collection.update_one(
                    {"photo_name": photo_name},
                    {"$set": {"match_status": match_status, "found": found, "not_found": not_found}}
                )
    else:
        st.warning("No photo has been uploaded by the user yet.")


# Main App
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

if not is_logged_in():
    login()  # Show login page
else:
    st.sidebar.button("Logout", on_click=logout)  # Add logout button
    role = get_user_role()
    if role == "admin":
        admin_dashboard()  # Show admin dashboard for admin users
    else:
        user_dashboard()  # Show user dashboard for regular users