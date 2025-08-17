import numpy as np
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import cv2

class MotionDetectionModel:
    def __init__(self):
        # Dummy model architecture
        self.model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(2, activation='softmax')  # 2 classes: moving vs still
        ])
        
        self.scaler = StandardScaler()
        self.baseline_features = None
        self.movement_threshold = 0.85

    def preprocess_frame(self, frame):
        # Resize and normalize frame
        frame = cv2.resize(frame, (64, 64))
        frame = frame / 255.0
        return frame

    def extract_features(self, frame):
        # Extract "motion features" from frame
        features = np.mean(frame, axis=(0, 1))
        features = self.scaler.transform(features.reshape(1, -1))
        return features

    def calibrate(self, initial_frames):
        """Store baseline position from calibration frames"""
        processed_frames = [self.preprocess_frame(frame) for frame in initial_frames]
        self.baseline_features = np.mean([self.extract_features(frame) 
                                        for frame in processed_frames], axis=0)

    def detect_movement(self, current_frame):
        """
        Detect if there's significant movement in current frame
        Returns:
            - movement_detected (bool): True if significant movement detected
            - confidence (float): Confidence score of the prediction
        """
        processed_frame = self.preprocess_frame(current_frame)
        features = self.extract_features(processed_frame)
        
        # Compare with baseline using dummy prediction
        diff = np.mean(np.abs(features - self.baseline_features))
        movement_score = np.clip(diff * 2, 0, 1)  # Scale difference to 0-1
        
        # Dummy prediction format matching real ML model output
        prediction = {
            'movement_detected': movement_score > self.movement_threshold,
            'confidence': movement_score,
            'position_change': {
                'x': float(features[0] - self.baseline_features[0]),
                'y': float(features[1] - self.baseline_features[1])
            }
        }
        
        return prediction

    def get_movement_analysis(self, frame):
        """Detailed movement analysis"""
        prediction = self.detect_movement(frame)
        
        if prediction['movement_detected']:
            if prediction['confidence'] > 0.95:
                return "Significant movement detected - please stay still"
            elif prediction['confidence'] > 0.85:
                return "Minor movement detected - try to maintain position"
        
        return "Position OK"

# Usage example:

# Initialize model
model = MotionDetectionModel()

# During calibration phase
calibration_frames = []  # Collect frames during 3-second calibration
model.calibrate(calibration_frames)

# During monitoring phase
while True:
    current_frame = capture_frame()  # Get frame from webcam
    result = model.detect_movement(current_frame)
    
    if result['movement_detected']:
        show_warning("Please maintain your position")

