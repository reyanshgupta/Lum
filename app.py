import os
from flask import Flask, redirect, render_template, Response, request, jsonify, session, url_for
from camera import Video
from collections import Counter, defaultdict
from threading import Lock
import time
import cv2
from google.cloud import vision
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'crested-climber-411318-0efea2445e25.json'

app = Flask(__name__)
app.secret_key = 'flasksession1' 
emotion="Neutral"
client = vision.ImageAnnotatorClient()

playlist_mapping = {
    "Joy": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIgBnQZVoxcWq?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXaXB8fQg7xif?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIhsvAFc3pIY4?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Sorrow": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/2U6SPbVuvqX0BSWWylG7ps?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/6b3EXmoElf2UlxuldGjhRX?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DWX83CujKHHOn?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Anger": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIetewBshGEPK?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DX9qNs32fujYe?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1E4AInqF1aqV85?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Neutral": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EVHGWrwldPRtj?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DX4PP3DA4J0N8?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIcJQdzRPklXj?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Fearful": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DX1s9knjP51Oa?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DX4sWSpwq3LiO?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIfPyixpQG2Dl?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Disgusted": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIefLxrHQP8p4?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIdcKjz0pIYET?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIcqNFLKnDOcZ?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    
    "Surprise": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXbVhgADFy3im?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZEVXbqtItH1ORF8f?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXa41CMuUARjl?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ]
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/user_playlist_suggest')
def user_playlist_suggest():
    return render_template('user_playlist_suggest.html')

def get_emotion(face):
    emotions = {
        "joy": face.joy_likelihood,
        "sorrow": face.sorrow_likelihood,
        "anger": face.anger_likelihood,
        "surprise": face.surprise_likelihood
    }
    most_likely_emotion = max(emotions, key=emotions.get)
    return most_likely_emotion.capitalize() if emotions[most_likely_emotion] > 1 else "Neutral"

@app.route('/analyze_emotion', methods=['POST'])
def analyze_emotion():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    content = file.read()
    image = vision.Image(content=content)

    try:
        response = client.face_detection(image=image)
        faces = response.face_annotations
        if faces:
            detected_emotion = get_emotion(faces[0])
            session['emotion'] = detected_emotion
            return redirect(url_for('suggest_playlist'))
        else:
            return jsonify({'emotion_detected': False})
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return jsonify({'error': 'Error processing image'}), 500

@app.route('/suggest_playlist')
def suggest_playlist():
    emotion = session.get('emotion', 'Neutral')
    suggested_playlists = playlist_mapping.get(emotion, playlist_mapping['Neutral'])
    print("Detected emotion:", emotion)
    return render_template('playlist.html', playlists=suggested_playlists, emotion=emotion)

if __name__ == '__main__':
    app.run(debug=True)