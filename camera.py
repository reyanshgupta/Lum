import numpy as np
from keras.models import model_from_json
import keras
from google.cloud import vision
import cv2
GOOGLE_APPLICATION_CREDENTIALS="/muserec-365e8bc91a2f.json"

face_detector = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

class Video(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.client = vision.ImageAnnotatorClient()
        self.emotion_model = self.load_emotion_model()

    def __del__(self):
        self.video.release()
        
    def get_frame(self):
        emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
        ret, frame = self.video.read()
        if not ret:
            return None, None

        frame = cv2.resize(frame, (850, 480))
        cv2.imwrite("frame.jpg", frame)
        with open("frame.jpg", "rb") as image_file:
            content = image_file.read()

        current_emotion = None

        response = self.client.face_detection(image=content)
        faces = response.face_annotations

        if faces:
            face = faces[0]
            emotions = face.joy_likelihood, face.sorrow_likelihood, face.anger_likelihood, face.surprise_likelihood
            max_index = np.argmax(emotions) 
            current_emotion = emotion_dict[max_index]
        return frame, current_emotion
    
    
     # def load_emotion_model(self):
    #     json_file = open('Model/emotion_model.json', 'r')
    #     loaded_model_json = json_file.read()
    #     json_file.close()
    #     model = model_from_json(loaded_model_json)
    #     model.load_weights("Model/emotion_model.h5")
    #     return model