import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import base64

class BlinkDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        
        self.EAR_THRESHOLD = 0.20
        self.CLOSED_FRAMES = 2
        
        self.closed_counter = 0
        self.blink_total = 0
        self.start_time = None
        self.duration = 30
        self.running = False
        self.cap = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def euclidean(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))
    
    def eye_aspect_ratio(self, eye):
        A = self.euclidean(eye[1], eye[5])
        B = self.euclidean(eye[2], eye[4])
        C = self.euclidean(eye[0], eye[3])
        return (A + B) / (2.0 * C)
    
    def start(self):

        if self.running:
            return False
            
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            return False
            
        self.running = True
        self.blink_total = 0
        self.closed_counter = 0
        self.start_time = time.time()

        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
        
        return True
    
    def _detection_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            if time.time() - self.start_time > self.duration:
                self.running = False
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)
            
            if results.multi_face_landmarks:
                lm = results.multi_face_landmarks[0].landmark
                
                left_eye = [(int(lm[i].x * w), int(lm[i].y * h)) for i in self.LEFT_EYE]
                right_eye = [(int(lm[i].x * w), int(lm[i].y * h)) for i in self.RIGHT_EYE]

                for point in left_eye:
                    cv2.circle(frame, point, 2, (0, 255, 0), -1)
                for point in right_eye:
                    cv2.circle(frame, point, 2, (0, 255, 0), -1)
                
                for i in range(len(left_eye)):
                    next_i = (i + 1) % len(left_eye)
                    cv2.line(frame, left_eye[i], left_eye[next_i], (255, 0, 0), 1)
                
                for i in range(len(right_eye)):
                    next_i = (i + 1) % len(right_eye)
                    cv2.line(frame, right_eye[i], right_eye[next_i], (255, 0, 0), 1)
                
                left_ear = self.eye_aspect_ratio(left_eye)
                right_ear = self.eye_aspect_ratio(right_eye)
                                
                if left_ear < self.EAR_THRESHOLD and right_ear < self.EAR_THRESHOLD:
                    self.closed_counter += 1

                else:
                    if self.closed_counter >= self.CLOSED_FRAMES:
                        self.blink_total += 1
                    self.closed_counter = 0
            
            with self.frame_lock:
                self.current_frame = frame.copy()
    
    def get_current_frame_base64(self):
        
        with self.frame_lock:
            if self.current_frame is None:

                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                _, buffer = cv2.imencode('.jpg', blank)
                return base64.b64encode(buffer).decode('utf-8')
            
            _, buffer = cv2.imencode('.jpg', self.current_frame)
            return base64.b64encode(buffer).decode('utf-8')
    
    def get_stats(self):

        if not self.running and self.start_time is None:
            return {
                'blink_count': 0,
                'time_remaining': 30,
                'completed': False
            }
        
        time_elapsed = time.time() - self.start_time
        time_remaining = max(0, int(self.duration - time_elapsed))
        completed = time_elapsed >= self.duration or not self.running
        
        return {
            'blink_count': self.blink_total,
            'time_remaining': time_remaining,
            'completed': completed
        }
    
    def stop(self):

        self.running = False
        if self.cap is not None:
            self.cap.release()
        self.cap = None
    
    def get_final_results(self):
        
        blink_count = self.blink_total
        
        if blink_count >= 8:
            risk_level = "NORMAL"
            risk_message = "Low risk"
        elif blink_count >= 5:
            risk_level = "SLIGHT CHANGE"
            risk_message = "Moderate risk - Consider monitoring"
        else:
            risk_level = "HIGH CHANCE"
            risk_message = "Higher risk - Recommend consultation"
        
        return {
            'blink_count': blink_count,
            'risk_level': risk_level,
            'risk_message': risk_message,
            'completed': True
        }