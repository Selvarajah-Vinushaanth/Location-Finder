# 🏛️ Landmark Location Finder

A powerful AI-driven web application that detects landmarks from uploaded images and provides detailed information about them.


## ✨ Features

- **🔍 AI-Powered Landmark Detection**: Utilizes Google Cloud Vision API to accurately identify landmarks in uploaded photos
- **🤖 AI-Generated Information**: Leverages Gemini API to provide rich details about each landmark:
  - Historical significance
  - Architectural features
  - Cultural importance
  - Interesting facts
- **🧭 Travel Tips**: Personalized travel recommendations for each landmark
- **🗺️ Interactive Maps**: View the landmark location on Google Maps
- **📱 Mobile-Friendly Design**: Responsive interface that works on all devices
- **🛡️ Privacy-Focused**: Uploaded images are processed securely and automatically deleted

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with Vision API enabled
- Google Generative AI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Selvarajah-Vinushaanth/Location-Finder.git
   cd Location-Finder
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Option 1: Create a `credentials.json` file in the project root directory
   - Option 2: Set the `GOOGLE_APPLICATION_CREDENTIALS_BASE64` environment variable with base64-encoded credentials

4. Configure the Gemini API key:
   - Update the `GEMINI_API_KEY` in `app.py` or set it as an environment variable

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and go to:
   ```
   http://localhost:5000
   ```

## 🧰 Tech Stack

- **Backend**:
  - Flask: Web framework
  - Google Cloud Vision API: For landmark detection
  - Google Generative AI (Gemini): For detailed descriptions and travel tips

- **Frontend**:
  - HTML5, CSS3, JavaScript
  - Font Awesome: Icon library
  - Responsive design with CSS Grid and Flexbox

## 📋 Usage

1. **Upload an Image**:
   - Drag and drop an image onto the upload area
   - Or click the "Choose Image" button to browse for an image
   - Supported formats: JPG, PNG, WEBP (max size: 10MB)

2. **View Results**:
   - See the detected landmark name and location
   - Read AI-generated information about the landmark
   - Follow personalized travel tips

3. **Share and Explore**:
   - Share the landmark location with friends
   - Get directions to the landmark
   - View the landmark on Google Maps

## 🔒 Privacy & Security

- Images are temporarily stored during processing and immediately deleted afterward
- No user data is retained
- Maximum file size limit (10MB) to prevent abuse
- Input validation to ensure only supported image types are processed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [Google Cloud Vision API](https://cloud.google.com/vision)
- [Google Generative AI (Gemini)](https://ai.google.dev/)
- [Flask](https://flask.palletsprojects.com/)
- [Font Awesome](https://fontawesome.com/)

---


