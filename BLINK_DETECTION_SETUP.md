# Blink Detection Setup Instructions

## Files Created:
1. **blink_detection.html** - Frontend page for blink detection
2. **blink_model.py** - Backend logic for blink detection using MediaPipe
3. **app.py** - Updated Flask app with blink detection routes

## Setup Steps:

### 1. Install Required Dependencies
```bash
pip install opencv-python mediapipe flask flask-sqlalchemy ultralytics pillow
```

### 2. File Placement
- Place `blink_detection.html` in your project root directory (same level as index.html)
- Place `blink_model.py` in your project root directory
- Replace your existing `app.py` with the new one provided

### 3. Update index.html
In your `index.html`, find the Blink Detection button section (around line 677-690) and change:
```html
<a href="#" class="feature-card glass-card"
```
to:
```html
<a href="blink_detection.html" class="feature-card glass-card"
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access Blink Detection
- Open browser and go to: http://localhost:5000/
- Click on "Blink Detection" button
- Allow camera access when prompted
- Click "Start Detection" to begin the 30-second test

## How It Works:

### Frontend (blink_detection.html):
- Displays live video feed from webcam
- Shows real-time blink count and timer
- Progress bar for 30-second test
- Results display with risk assessment

### Backend (blink_model.py):
- Uses MediaPipe Face Mesh for eye tracking
- Calculates Eye Aspect Ratio (EAR) to detect blinks
- Runs in separate thread for smooth video streaming
- Returns base64 encoded video frames to frontend

### Flask Routes (app.py):
- `/start_blink_detection` - Starts the detection process
- `/get_blink_stats` - Returns current stats and video frame
- `/stop_blink_detection` - Stops detection and returns final results

## Risk Assessment Criteria:
- **Normal (Low Risk)**: 8+ blinks in 30 seconds
- **Slight Change (Moderate Risk)**: 5-7 blinks in 30 seconds
- **Significant Deviation (Higher Risk)**: <5 blinks in 30 seconds

## Troubleshooting:

### Camera Not Working:
- Ensure webcam is connected and not in use by another application
- Check browser permissions for camera access
- Try a different browser

### Module Not Found Errors:
```bash
pip install --break-system-packages opencv-python mediapipe
```

### Port Already in Use:
Change port in app.py:
```python
app.run(debug=True, use_reloader=False, port=5001)
```

## Testing the Integration:
1. Start the Flask server: `python app.py`
2. Navigate to http://localhost:5000/
3. Click "Blink Detection" in the analysis section
4. Grant camera permissions
5. Click "Start Detection"
6. Blink normally for 30 seconds
7. View your results and download the report

## Notes:
- The blink detection uses your webcam
- Test duration is 30 seconds (adjustable in blink_model.py)
- Results are not stored in database (can be added if needed)
- Works best with good lighting and clear view of face
