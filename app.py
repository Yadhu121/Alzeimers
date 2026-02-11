from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from ultralytics import YOLO
from PIL import Image
import io
import base64
import os
import uuid
from datetime import datetime
from blink_model import BlinkDetector

app = Flask(__name__, static_folder='.', static_url_path='')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))


class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    file_path = db.Column(db.String(300))
    scan_type = db.Column(db.String(100))
    scan_date = db.Column(db.String(50))
    predicted_class = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


try:
    model = YOLO('best.pt')
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

blink_detector = BlinkDetector()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filepath>')
def serve_file(filepath):
    try:
        return send_from_directory('.', filepath)
    except Exception:
        return "File not found", 404


@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.json

    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    try:

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        scan_type = data.get("scan_type")
        scan_date = data.get("scan_date")
        image_base64 = data.get("image")

        patient = Patient(name=name, email=email, phone=phone)
        db.session.add(patient)
        db.session.commit()

        image_data = image_base64.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        img = Image.open(io.BytesIO(image_bytes))

        results = model.predict(source=img, verbose=False)
        probs = results[0].probs
        predicted_class = results[0].names[probs.top1]
        confidence = float(probs.top1conf)

        scan = Scan(
            patient_id=patient.id,
            file_path=file_path,
            scan_type=scan_type,
            scan_date=scan_date,
            predicted_class=predicted_class,
            confidence=confidence
        )

        db.session.add(scan)
        db.session.commit()

        return jsonify({
            'class': predicted_class,
            'confidence': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_blink_detection', methods=['POST'])
def start_blink_detection():
    """Start the blink detection process"""
    try:
        success = blink_detector.start()
        if success:
            return jsonify({'status': 'started'})
        else:
            return jsonify({'status': 'error', 'error': 'Failed to start camera'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/get_blink_stats', methods=['GET'])
def get_blink_stats():
    """Get current blink detection statistics and video frame"""
    try:
        stats = blink_detector.get_stats()
        frame_base64 = blink_detector.get_current_frame_base64()
        
        return jsonify({
            'blink_count': stats['blink_count'],
            'time_remaining': stats['time_remaining'],
            'completed': stats['completed'],
            'frame': frame_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stop_blink_detection', methods=['POST'])
def stop_blink_detection():
    """Stop the blink detection process"""
    try:
        blink_detector.stop()
        results = blink_detector.get_final_results()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False, port=5000)
