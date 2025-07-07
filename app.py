from flask import Flask, render_template, request, jsonify
from google.cloud import vision
import io
import os
import base64
import platform

# Handle GOOGLE_APPLICATION_CREDENTIALS_BASE64
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_BASE64"):
    decoded_json = base64.b64decode(os.environ["GOOGLE_APPLICATION_CREDENTIALS_BASE64"])
    if platform.system() == "Windows":
        credentials_path = os.path.join(os.getcwd(), "credentials.json")
    else:
        credentials_path = "/tmp/credentials.json"
    with open(credentials_path, "wb") as f:
        f.write(decoded_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

vision_client = vision.ImageAnnotatorClient()

def detect_landmark(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = vision_client.landmark_detection(image=image)
    landmarks = response.landmark_annotations

    print(f"Detected landmarks count: {len(landmarks)}")
    for lm in landmarks:
        print(f"Landmark description: {lm.description}")

    if landmarks:
        landmark = landmarks[0]
        desc = landmark.description
        lat = landmark.locations[0].lat_lng.latitude
        lng = landmark.locations[0].lat_lng.longitude
        return desc, lat, lng
    else:
        return None, None, None

@app.route('/', methods=['GET', 'POST'])
def upload():
    location_url = None
    landmark_name = None

    if request.method == 'POST':
        if 'photo' not in request.files:
            return "No file part", 400
        file = request.files['photo']
        if file.filename == '':
            return "No selected file", 400

        # Check file size (max 10MB)
        file.seek(0, 2)  # go to end of file
        file_size = file.tell()
        file.seek(0)  # rewind
        if file_size > 10 * 1024 * 1024:
            return "File too large. Maximum size is 10MB.", 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            desc, lat, lng = detect_landmark(filepath)
            if desc and lat and lng:
                landmark_name = desc
                location_url = f"https://www.google.com/maps?q={lat},{lng}"
            else:
                location_url = ''
        except Exception as e:
            print(f"Error detecting landmark: {e}")
            location_url = ''
        finally:
            # clean up
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
        
        return render_template('landmark.html',
                               location_url=location_url,
                               landmark_name=landmark_name,
                               fresh_result=True)
    
    return render_template('landmark.html')

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
