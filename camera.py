import cv2
import numpy as np
from keras.models import model_from_json

face_detector = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

class Video(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        # Load the emotion model here to avoid reloading for each frame
        self.emotion_model = self.load_emotion_model()
    
    def __del__(self):
        self.video.release()

    def load_emotion_model(self):
        json_file = open('Model/emotion_model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights("Model/emotion_model.h5")
        return model
        
    def get_frame(self):
        emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
        ret, frame = self.video.read()
        if not ret:
            return None, None

        frame = cv2.resize(frame, (1280, 720))
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        num_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

        current_emotion = None

        for (x, y, w, h) in num_faces:
            roi_gray_frame = gray_frame[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)

            emotion_prediction = self.emotion_model.predict(cropped_img)
            maxindex = int(np.argmax(emotion_prediction))
            current_emotion = emotion_dict[maxindex]

            cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 4)
            cv2.putText(frame, current_emotion, (x+5, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes(), current_emotion
