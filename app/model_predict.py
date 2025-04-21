import cv2,os
from ultralytics import YOLO


# Load the YOLO model
basedir = os.path.abspath(os.path.dirname(__file__))
model_path = os.path.join(basedir, 'best_model', 'best.pt')

model = YOLO(model_path)
# Function to process the video and detect accidents
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    accident_count = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        results = model.predict(
            source=frame,
            conf=0.7,
            stream=False,
            verbose=False
        )

        for result in results:
            if result.boxes is not None and len(result.boxes.cls) > 0:
                classes = result.boxes.cls.cpu().numpy()
                if 0 in classes:  # class 0 = accident
                    accident_count += 1
                    break

    cap.release()

    if accident_count > 10:
        return {
            "code": 1,
            "message": "Accident Detected"
        }
    else:
        return {
            "code": 0,
            "message": "Non-Accident"
        }
