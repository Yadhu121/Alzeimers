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


# ─────────────────────────────────────────
#  DATABASE MODELS
# ─────────────────────────────────────────

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scans = db.relationship('Scan', backref='patient', lazy=True)
    blink_results = db.relationship('BlinkResult', backref='patient', lazy=True)
    typing_results = db.relationship('TypingResult', backref='patient', lazy=True)


class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    file_path = db.Column(db.String(300))
    scan_type = db.Column(db.String(100))
    scan_date = db.Column(db.String(50))
    predicted_class = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BlinkResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    blink_count = db.Column(db.Integer)
    duration = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TypingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    wpm = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    test_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
#  MODEL LOADING
# ─────────────────────────────────────────

try:
    model = YOLO('best.pt')
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

blink_detector = BlinkDetector()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─────────────────────────────────────────
#  STATIC FILE SERVING
# ─────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filepath>')
def serve_file(filepath):
    try:
        return send_from_directory('.', filepath)
    except Exception:
        return "File not found", 404


# ─────────────────────────────────────────
#  PATIENT REGISTRATION
# ─────────────────────────────────────────

@app.route('/register_patient', methods=['POST'])
def register_patient():
    """Register a new patient and return their patient_id."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    patient = Patient(
        name=name,
        age=data.get('age'),
        gender=data.get('gender', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        address=data.get('address', '')
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({'patient_id': patient.id, 'name': patient.name})


# ─────────────────────────────────────────
#  ADMIN – GET ALL PATIENTS
# ─────────────────────────────────────────

@app.route('/get_patients', methods=['GET'])
def get_patients():
    """Return all patients with their test results."""
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    result = []
    for p in patients:
        scans = [{
            'id': s.id,
            'scan_type': s.scan_type,
            'scan_date': s.scan_date,
            'predicted_class': s.predicted_class,
            'confidence': round(s.confidence * 100, 1) if s.confidence else None,
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else ''
        } for s in p.scans]

        blinks = [{
            'id': b.id,
            'blink_count': b.blink_count,
            'duration': b.duration,
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M') if b.created_at else ''
        } for b in p.blink_results]

        typings = [{
            'id': t.id,
            'wpm': t.wpm,
            'accuracy': t.accuracy,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else ''
        } for t in p.typing_results]

        result.append({
            'id': p.id,
            'name': p.name,
            'age': p.age,
            'gender': p.gender,
            'email': p.email,
            'phone': p.phone,
            'address': p.address,
            'registered_at': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '',
            'scans': scans,
            'blink_results': blinks,
            'typing_results': typings
        })

    return jsonify(result)


@app.route('/get_patient/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Return details for a single patient."""
    p = Patient.query.get_or_404(patient_id)
    return jsonify({
        'id': p.id,
        'name': p.name,
        'age': p.age,
        'gender': p.gender,
        'email': p.email,
        'phone': p.phone,
        'address': p.address,
        'registered_at': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else ''
    })


# ─────────────────────────────────────────
#  MRI PREDICTION
# ─────────────────────────────────────────

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    try:
        patient_id = data.get('patient_id')
        scan_type = data.get('scan_type', 'MRI')
        scan_date = data.get('scan_date', datetime.utcnow().strftime('%Y-%m-%d'))
        image_base64 = data.get('image')

        # If patient_id not provided, create an anonymous patient record
        if not patient_id:
            name = data.get('name', 'Anonymous')
            email = data.get('email', '')
            phone = data.get('phone', '')
            patient = Patient(name=name, email=email, phone=phone)
            db.session.add(patient)
            db.session.commit()
            patient_id = patient.id

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
            patient_id=patient_id,
            file_path=file_path,
            scan_type=scan_type,
            scan_date=scan_date,
            predicted_class=predicted_class,
            confidence=confidence
        )
        db.session.add(scan)
        db.session.commit()

        return jsonify({'class': predicted_class, 'confidence': confidence})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
#  BLINK DETECTION
# ─────────────────────────────────────────

@app.route('/start_blink_detection', methods=['POST'])
def start_blink_detection():
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
    try:
        blink_detector.stop()
        results = blink_detector.get_final_results()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save_blink_result', methods=['POST'])
def save_blink_result():
    """Save completed blink test results linked to a patient."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({'error': 'patient_id required'}), 400

    result = BlinkResult(
        patient_id=patient_id,
        blink_count=data.get('blink_count', 0),
        duration=data.get('duration', 0)
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'status': 'saved', 'id': result.id})


# ─────────────────────────────────────────
#  TYPING TEST
# ─────────────────────────────────────────

@app.route('/save_typing_result', methods=['POST'])
def save_typing_result():
    """Save completed typing test results linked to a patient."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({'error': 'patient_id required'}), 400

    result = TypingResult(
        patient_id=patient_id,
        wpm=data.get('wpm', 0),
        accuracy=data.get('accuracy', 0),
        test_text=data.get('test_text', '')
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'status': 'saved', 'id': result.id})


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False, port=5000)
