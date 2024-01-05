from flask import Flask, request, jsonify
import cv2
import numpy as np
from keras.models import model_from_json

app = Flask(__name__)

# Load the emotion detection model
# Replace this with your model loading code
def load_emotion_model():
    json_file = open('Model/emotion_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights('Model/emotion_model.h5')
    return model

emotion_model = load_emotion_model()
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

# Function to process each frame and predict emotion
def detect_emotion(frame, model):
    pred = model.predict(frame)
    emotion = emotion_dict[np.argmax(pred)]
    
    return emotion

@app.route('/video_feed', methods=['POST'])
def video_feed():
    if 'frame' not in request.files:
        return jsonify({"error": "No frame part"}), 400

    file = request.files['frame']
    npimg = np.fromfile(file, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Detect emotion
    detected_emotion = detect_emotion(frame, emotion_model)
    
    return jsonify({"emotion": detected_emotion})

@app.route('/')
def index():
    return "Emotion Detection API"

if __name__ == '__main__':
    app.run(debug=True)
