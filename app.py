from flask import Flask, render_template, Response
from camera import Video
from collections import Counter

app = Flask(__name__)

# Global variable to store emotions
emotion_counter = Counter()

# Emotion to Spotify playlist embed mapping
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

@app.route('/')
def index():
    global emotion_counter
    emotion_counter.clear()
    return render_template('index.html')

def gen(camera):
    global emotion_counter
    while True:
        frame, emotion = camera.get_frame()
        if emotion:
            emotion_counter[emotion] += 1
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + 
               b'\r\n\r\n')

@app.route('/muserec')
def video():
    return Response(gen(Video()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/suggest_playlist')
def suggest_playlist():
    most_common_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else 'Neutral'
    suggested_playlists = playlist_mapping.get(most_common_emotion, [""])
    return render_template('playlist.html', playlists=suggested_playlists, emotion=most_common_emotion)

if __name__ == '__main__':
    app.run(debug=True)
