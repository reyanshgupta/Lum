import os
from flask import Flask, render_template, Response, request, jsonify
from camera import Video
from collections import Counter, defaultdict
from threading import Lock
import time
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "muserec-365e8bc91a2f.json" 

app = Flask(__name__)

# Global variables
emotion_counter = Counter()
emotion_duration = defaultdict(int)
camera = Video()
lock = Lock()
start_time = None
emotion_detected_flag = False

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    global emotion_counter, emotion_duration, start_time, emotion_detected_flag
    emotion_counter.clear()
    emotion_duration.clear()
    start_time = None
    emotion_detected_flag = False
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

playlist_mapping = {
    "Happy": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIgBnQZVoxcWq?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXaXB8fQg7xif?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1EIhsvAFc3pIY4?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Sad": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/2U6SPbVuvqX0BSWWylG7ps?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/6b3EXmoElf2UlxuldGjhRX?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>''',
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DWX83CujKHHOn?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ],
    "Angry": [
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
    
    "Surprised": [
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXbVhgADFy3im?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZEVXbqtItH1ORF8f?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
        '''<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXa41CMuUARjl?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'''
    ]
}

def gen():
    global start_time, emotion_counter, emotion_duration, emotion_detected_flag
    while True:
        with lock:
            frame, emotion = camera.get_frame() 

            if start_time:
                elapsed_time = time.time() - start_time
                if emotion:
                    emotion_duration[emotion] += elapsed_time
                    print(f"Emotion detected: {emotion} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    emotion_duration.clear()

            if any(duration >= 5 for duration in emotion_duration.values()):
                emotion_detected_flag = True
                for emo in emotion_duration:
                    emotion_counter[emo] += 1
                emotion_duration.clear()
                start_time = None

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame +
                   b'\r\n\r\n')

@app.route('/check_emotion')
def check_emotion():
    return jsonify({'emotion_detected': emotion_detected_flag})

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global start_time, emotion_detected_flag, emotion_counter, emotion_duration
    start_time = time.time()
    # emotion_detected_flag = False
    # emotion_counter.clear()
    # emotion_duration.clear()
    return '', 204

@app.route('/suggest_playlist')
def suggest_playlist():
    most_common_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else 'Neutral'
    suggested_playlists = playlist_mapping.get(most_common_emotion, [""])
    return render_template('playlist.html', playlists=suggested_playlists, emotion=most_common_emotion)

if __name__ == '__main__':
    app.run(debug=True)
