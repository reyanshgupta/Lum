import io
import os
import numpy as np
from google.cloud import vision
import cv2

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'crested-climber-411318-0efea2445e25.json'
client = vision.ImageAnnotatorClient()

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

class Video(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        emotion_dict = {
            "VERY_UNLIKELY": "Neutral",
            "UNLIKELY": "Neutral",
            "POSSIBLE": "Uncertain",
            "LIKELY": "Likely",
            "VERY_LIKELY": "Very Likely"
        }
        ret, frame = self.video.read()
        if not ret:
            return None, "No Frame"

        _, buffer = cv2.imencode('.jpg', frame)
        content = io.BytesIO(buffer).getvalue()
        image = vision.Image(content=content)

        try:
            response = client.face_detection(image=image)
            faces = response.face_annotations

            if faces:
                face = faces[0]
                emotions = [
                    (face.joy_likelihood, "Happy"),
                    (face.sorrow_likelihood, "Sad"),
                    (face.anger_likelihood, "Angry"),
                    (face.surprise_likelihood, "Surprised")
                ]
                most_likely_emotion = max(emotions, key=lambda item: item[0])
                likelihood, emotion = most_likely_emotion

                current_emotion = emotion_dict.get(likelihood.name, "Neutral")
            else:
                current_emotion = "No Face Detected"
        except Exception as e:
            current_emotion = "Error"

        return frame, current_emotion

