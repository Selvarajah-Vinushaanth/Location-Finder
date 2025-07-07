from flask import Flask, render_template, request, jsonify
from google.cloud import vision
from google import genai
import io
import os
import base64
import platform
import json  # Import JSON module for parsing

# Handle GOOGLE_APPLICATION_CREDENTIALS_BASE64 or JSON file
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_BASE64"):
    decoded_json = base64.b64decode(os.environ["GOOGLE_APPLICATION_CREDENTIALS_BASE64"])
    if platform.system() == "Windows":
        credentials_path = os.path.join(os.getcwd(), "credentials.json")
    else:
        credentials_path = "/tmp/credentials.json"
    with open(credentials_path, "wb") as f:
        f.write(decoded_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
elif os.path.exists("d:\\location-finder\\credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "d:\\location-finder\\credentials.json"

# Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set. Ensure the credentials file is properly configured.")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

vision_client = vision.ImageAnnotatorClient()

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBnFQGu-XKiTc_KDwfqE2BChT8cGcukngc"
genai_client = genai.Client(api_key=GEMINI_API_KEY)

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

def generate_landmark_description(landmark_name):
    """Generate a detailed description of the landmark using Gemini API."""
    try:
        prompt = f"""
        Provide a detailed description of the landmark "{landmark_name}" including:
        1. Historical significance
        2. Key architectural features
        3. Cultural importance
        Format the response as a JSON object:
        {{
            "summary": "Brief summary here",
            "details": {{
                "historical_significance": "Historical significance here",
                "key_architectural_features": "Key architectural features here",
                "cultural_importance": "Cultural importance here"
            }},
            "interesting_fact": "An interesting fact here"
        }}
        """
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Remove markdown code block formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove ```
            
        response_text = response_text.strip()
        
        try:
            landmark_info = json.loads(response_text)
            return {
                "summary": landmark_info.get("summary", ""),
                "details": landmark_info.get("details", {}),
                "interesting_fact": landmark_info.get("interesting_fact", "")
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {
                "summary": "Could not parse information about this landmark.",
                "details": {
                    "historical_significance": "Information not available",
                    "key_architectural_features": "Information not available",
                    "cultural_importance": "Information not available"
                },
                "interesting_fact": "Information not available"
            }
    except Exception as e:
        print(f"Error generating landmark description: {e}")
        return {
            "summary": "Fallback summary for the landmark.",
            "details": {
                "historical_significance": "Fallback historical significance.",
                "key_architectural_features": "Fallback architectural features.",
                "cultural_importance": "Fallback cultural importance."
            },
            "interesting_fact": "Fallback interesting fact."
        }

def generate_travel_tips(landmark_name):
    """Generate personalized travel tips for visiting the landmark using Gemini API."""
    try:
        prompt = f"""
        Generate 5 personalized travel tips for visiting "{landmark_name}". Include:
        - Best time to visit
        - Local customs
        - Photography tips
        - Safety precautions
        Format the response as a JSON array:
        ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"]
        """
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Remove markdown code block formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove ```
            
        response_text = response_text.strip()
        
        try:
            tips = json.loads(response_text)
            if isinstance(tips, list):
                return tips
            else:
                print(f"Unexpected format for travel tips: {response_text}")
                return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for travel tips: {e}")
            print(f"Raw response: {response_text}")
            # If parsing fails, try to return lines from the response
            if "[" in response_text and "]" in response_text:
                # Try to extract content between brackets
                content = response_text[response_text.find("[")+1:response_text.rfind("]")]
                tips = [tip.strip().strip('"\'') for tip in content.split('",')]
                return tips
            return [
                "Visit during off-peak hours to avoid crowds.",
                "Follow local customs and etiquette when visiting.",
                "Capture the best photos from recommended vantage points.",
                "Stay alert and watch for pickpockets in tourist areas.",
                "Book tickets in advance to save time."
            ]
    except Exception as e:
        print(f"Error generating travel tips: {e}")
        return [
            "Fallback travel tip 1.",
            "Fallback travel tip 2.",
            "Fallback travel tip 3.",
            "Fallback travel tip 4.",
            "Fallback travel tip 5."
        ]

@app.route('/', methods=['GET', 'POST'])
def upload():
    location_url = None
    landmark_name = None
    landmark_info = None
    travel_tips = None

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
                
                # Generate AI content about the landmark
                landmark_info = generate_landmark_description(landmark_name)
                travel_tips = generate_travel_tips(landmark_name)
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
                               landmark_info=landmark_info,
                               travel_tips=travel_tips,
                               fresh_result=True)
    
    return render_template('landmark.html')

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
