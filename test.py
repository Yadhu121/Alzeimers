from ultralytics import YOLO
from PIL import Image
import matplotlib.pyplot as plt
import os

# Load your trained model
model = YOLO('best.pt')

# Path to test images directory
test_dir = 'testIMG'

# Get all image files
image_files = [f for f in os.listdir(test_dir) 
               if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

print(f"Found {len(image_files)} images to test\n")

# Process each image
for i, img_name in enumerate(image_files, 1):
    img_path = os.path.join(test_dir, img_name)
    
    # Make prediction
    results = model.predict(source=img_path, verbose=False)
    
    # Get prediction details
    predicted_class = results[0].names[results[0].probs.top1]
    confidence = results[0].probs.top1conf.item()
    
    # Display image with prediction
    img = Image.open(img_path)
    plt.figure(figsize=(8, 6))
    plt.imshow(img, cmap='gray')
    plt.title(f"Image {i}/{len(image_files)}: {img_name}\n"
              f"Prediction: {predicted_class}\n"
              f"Confidence: {confidence:.2%}", 
              fontsize=12, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # Print details
    print(f"{'='*60}")
    print(f"Image {i}: {img_name}")
    print(f"Predicted Class: {predicted_class}")
    print(f"Confidence: {confidence:.2%}")
    print(f"{'='*60}\n")

print("✅ All images processed!")
