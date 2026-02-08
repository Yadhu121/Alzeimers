from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
from PIL import Image
import io
import base64
import os

app = Flask(__name__, static_folder='.', static_url_path='')

# Load the model
try:
    model = YOLO('best.pt')
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filepath>')
def serve_file(filepath):
    try:
        return send_from_directory('.', filepath)
    except Exception as e:
        print(f"Error serving {filepath}: {e}")
        return f"File not found: {filepath}", 404

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        print("❌ Error: Model not loaded")
        return jsonify({'error': 'Model not loaded'}), 500

    print("\n" + "="*50)
    print("📡 RECEIVED PREDICTION REQUEST")
    
    data = request.json
    if 'image' not in data:
        print("❌ Error: No image data provided")
        return jsonify({'error': 'No image data provided'}), 400

    try:
        # Decode base64 image
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        
        print(f"📷 Image received: {img.size[0]}x{img.size[1]} px, Mode: {img.mode}")

        # Run inference
        results = model.predict(source=img, verbose=False)
        
        # Get top prediction
        probs = results[0].probs
        top1_index = probs.top1
        predicted_class = results[0].names[top1_index]
        confidence = float(probs.top1conf)

        print("-" * 30)
        print("🧠 MODEL PREDICTIONS:")
        # detailed probabilities
        for i, conf in enumerate(probs.data):
             class_name = results[0].names[i]
             print(f"   - {class_name}: {conf:.2%}")

        print("-" * 30)
        print(f"✅ FINAL RESULT: {predicted_class} ({confidence:.2%})")
        print("="*50 + "\n")

        return jsonify({
            'class': predicted_class,
            'confidence': confidence
        })

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
   app.run(debug=True, use_reloader=False, port=5000)

