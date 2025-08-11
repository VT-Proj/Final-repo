import cv2
import numpy as np
import os
from ultralytics import YOLO
from traditional_ImageProcessing_techniques.digitrecognition.detect_digits import (
    detect_digits as detect_seven_segment_digits,
)
import base64
from io import BytesIO
from PIL import Image as PILImage

class ImageProcessingService:
    def __init__(self, model_path='model_detection/yolov8n.pt'):
        """Initialize the image processing service with YOLO model"""
        self.model = YOLO(model_path)
    
    def preprocess_image(self, image_path):
        """Apply traditional preprocessing techniques"""
        img = cv2.imread(image_path)
        if img is None:
            return None, {}
        
        # Convert to different formats for processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply various preprocessing techniques
        results = {}
        
        # 1. Gaussian Blur
        gaussian_blur = cv2.GaussianBlur(img, (5, 5), 0)
        results['gaussian_blur'] = self._image_to_base64(gaussian_blur)
        
        # 2. Mean Blur
        mean_blur = cv2.blur(img, (5, 5))
        results['mean_blur'] = self._image_to_base64(mean_blur)
        
        # 3. Canny Edge Detection
        blurred_gray = cv2.GaussianBlur(gray, (9, 9), 0)
        canny = cv2.Canny(blurred_gray, 50, 180)
        results['canny_edges'] = self._image_to_base64(cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR))
        
        # 4. Sobel Edge Detection
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_combined = cv2.addWeighted(np.absolute(sobel_x), 0.5, np.absolute(sobel_y), 0.5, 0)
        results['sobel_edges'] = self._image_to_base64(cv2.cvtColor(np.uint8(sobel_combined), cv2.COLOR_GRAY2BGR))
        
        # 5. Adaptive Thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        results['adaptive_threshold'] = self._image_to_base64(cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2BGR))
        
        return img, results
    
    def detect_objects(self, image_path):
        """Run YOLO object detection"""
        results = self.model(image_path)
        
        # Parse detection results
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            class_ids = results[0].boxes.cls.cpu().numpy()
            class_names = results[0].names
            
            for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)):
                detections.append({
                    'bbox': box.tolist(),
                    'confidence': float(conf),
                    'class_name': class_names[int(cls_id)],
                    'class_id': int(cls_id)
                })
        
        # Draw bounding boxes on image
        img = cv2.imread(image_path)
        annotated_img = self._draw_detections(img, detections)
        
        return detections, self._image_to_base64(annotated_img)

    def read_meter_display(self, image_path):
        """Crop the meter display using YOLO detection and run seven-segment digit detection.

        Returns a dict with: reading (string), digits (list[int]),
        confidence (float average of display detections), and a cropped preview.
        """
        # Run YOLO and get detections
        results = self.model(image_path)
        if len(results) == 0 or results[0].boxes is None:
            return {
                'reading': None,
                'digits': [],
                'confidence': 0.0,
                'crop_image': None,
            }

        boxes = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy()
        class_names = results[0].names

        # Expect class 'display' to be the meter region
        display_indices = [i for i, cid in enumerate(class_ids) if class_names[int(cid)] == 'display']
        if not display_indices:
            return {
                'reading': None,
                'digits': [],
                'confidence': 0.0,
                'crop_image': None,
            }

        # Take highest confidence display box
        best_idx = max(display_indices, key=lambda i: confidences[i])
        x1, y1, x2, y2 = map(int, boxes[best_idx])

        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        # Clamp coordinates within image
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(0, min(x2, w - 1))
        y2 = max(0, min(y2, h - 1))

        crop = img[y1:y2, x1:x2]
        crop_path = None
        digits = []
        if crop.size != 0:
            # Temporarily write crop to a buffer file to reuse existing detector API
            tmp_dir = os.path.join(os.path.dirname(image_path), 'tmp')
            os.makedirs(tmp_dir, exist_ok=True)
            crop_path = os.path.join(tmp_dir, 'crop.jpg')
            cv2.imwrite(crop_path, crop)
            try:
                digits = detect_seven_segment_digits(crop_path)
            except Exception:
                digits = []

        reading_str = ''.join(str(d) for d in digits) if digits else None

        return {
            'reading': reading_str,
            'digits': digits,
            'confidence': float(confidences[best_idx]),
            'crop_image': self._image_to_base64(crop) if crop.size != 0 else None,
        }
    
    def postprocess_image(self, image_path):
        """Apply traditional postprocessing techniques"""
        img = cv2.imread(image_path)
        if img is None:
            return {}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results = {}
        
        # 1. Contour Detection
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contour_img = img.copy()
        cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
        results['contours'] = self._image_to_base64(contour_img)
        results['contour_count'] = len(contours)
        
        # 2. Morphological Operations
        kernel = np.ones((5, 5), np.uint8)
        
        # Opening (erosion followed by dilation)
        opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        results['morphological_opening'] = self._image_to_base64(cv2.cvtColor(opening, cv2.COLOR_GRAY2BGR))
        
        # Closing (dilation followed by erosion)
        closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        results['morphological_closing'] = self._image_to_base64(cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR))
        
        # 3. Image Sharpening
        kernel_sharpen = np.array([[-1,-1,-1],
                                   [-1, 9,-1],
                                   [-1,-1,-1]])
        sharpened = cv2.filter2D(img, -1, kernel_sharpen)
        results['sharpened'] = self._image_to_base64(sharpened)
        
        return results
    
    def _draw_detections(self, img, detections):
        """Draw bounding boxes and labels on image"""
        annotated = img.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            conf = detection['confidence']
            class_name = detection['class_name']
            
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(annotated, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(annotated, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return annotated
    
    def _image_to_base64(self, img):
        """Convert OpenCV image to base64 string for web display"""
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    
    def process_complete_pipeline(self, image_path):
        """Run complete image processing pipeline"""
        # Preprocessing
        original_img, preprocessing_results = self.preprocess_image(image_path)
        if original_img is None:
            return None
        
        # Object Detection
        detections, detection_image = self.detect_objects(image_path)
        
        # Postprocessing
        postprocessing_results = self.postprocess_image(image_path)
        
        # Original image as base64
        original_base64 = self._image_to_base64(original_img)
        
        return {
            'original_image': original_base64,
            'preprocessing': preprocessing_results,
            'detections': detections,
            'detection_image': detection_image,
            'postprocessing': postprocessing_results,
            'meter_reading': self.read_meter_display(image_path),
        }
