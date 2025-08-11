# import cv2
# import numpy as np

# FONT = cv2.FONT_HERSHEY_SIMPLEX
# CYAN = (255, 255, 0)
# DIGITSDICT = {
#     (1, 1, 1, 1, 1, 1, 0): 0,
#     (0, 1, 1, 0, 0, 0, 0): 1,
#     (1, 1, 0, 1, 1, 0, 1): 2,
#     (1, 1, 1, 1, 0, 0, 1): 3,
#     (0, 1, 1, 0, 0, 1, 1): 4,
#     (1, 0, 1, 1, 0, 1, 1): 5,
#     (1, 0, 1, 1, 1, 1, 1): 6,
#     (1, 1, 1, 0, 0, 1, 0): 7,
#     (1, 1, 1, 1, 1, 1, 1): 8,
#     (1, 1, 1, 1, 0, 1, 1): 9,
# }


# # roi_color = cv2.imread("inter/dbs-roi.png")
# roi_color = cv2.imread("inter/ocbc-roi.png")
# roi = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)

# RATIO = roi.shape[0] * 0.2

# roi = cv2.bilateralFilter(roi, 5, 30, 60)

# trimmed = roi[int(RATIO) :, int(RATIO) : roi.shape[1] - int(RATIO)]
# roi_color = roi_color[int(RATIO) :, int(RATIO) : roi.shape[1] - int(RATIO)]
# cv2.imshow("Blurred and Trimmed", trimmed)
# cv2.waitKey(0)

# edged = cv2.adaptiveThreshold(
#     trimmed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 5
# )
# cv2.imshow("Edged", edged)
# cv2.waitKey(0)

# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 5))
# dilated = cv2.dilate(edged, kernel, iterations=1)

# cv2.imshow("Dilated", dilated)
# cv2.waitKey(0)

# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
# dilated = cv2.dilate(dilated, kernel, iterations=1)

# cv2.imshow("Dilated x2", dilated)
# cv2.waitKey(0)

# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 1),)
# eroded = cv2.erode(dilated, kernel, iterations=1)

# cv2.imshow("Eroded", eroded)
# cv2.waitKey(0)

# h = roi.shape[0]
# ratio = int(h * 0.07)
# eroded[-ratio:,] = 0
# eroded[:, :ratio] = 0

# cv2.imshow("Eroded + Black", eroded)
# cv2.waitKey(0)

# cnts, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# digits_cnts = []

# canvas = trimmed.copy()
# cv2.drawContours(canvas, cnts, -1, (255, 255, 255), 1)
# cv2.imshow("All Contours", canvas)
# cv2.waitKey(0)

# canvas = trimmed.copy()
# for cnt in cnts:
#     (x, y, w, h) = cv2.boundingRect(cnt)
#     if h > 20:
#         digits_cnts += [cnt]
#         cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 0, 0), 1)
#         cv2.drawContours(canvas, cnt, 0, (255, 255, 255), 1)
#         cv2.imshow("Digit Contours", canvas)
#         cv2.waitKey(0)

# print(f"No. of Digit Contours: {len(digits_cnts)}")


# cv2.imshow("Digit Contours", canvas)
# cv2.waitKey(0)


# sorted_digits = sorted(digits_cnts, key=lambda cnt: cv2.boundingRect(cnt)[0])

# canvas = trimmed.copy()


# for i, cnt in enumerate(sorted_digits):
#     (x, y, w, h) = cv2.boundingRect(cnt)
#     cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 0, 0), 1)
#     cv2.putText(canvas, str(i), (x, y - 3), FONT, 0.3, (0, 0, 0), 1)

# cv2.imshow("All Contours sorted", canvas)
# cv2.waitKey(0)

# digits = []
# canvas = roi_color.copy()
# for cnt in sorted_digits:
#     (x, y, w, h) = cv2.boundingRect(cnt)
#     roi = eroded[y : y + h, x : x + w]
#     print(f"W:{w}, H:{h}")
#     # convenience units
#     qW, qH = int(w * 0.25), int(h * 0.15)
#     fractionH, halfH, fractionW = int(h * 0.05), int(h * 0.5), int(w * 0.25)

#     # wikipedia's illustration
#     sevensegs = [
#         ((0, 0), (w, qH)), 
#         ((w - qW, 0), (w, halfH)), 
#         ((w - qW, halfH), (w, h)),  
#         ((0, h - qH), (w, h)),  
#         ((0, halfH), (qW, h)),  
#         ((0, 0), (qW, halfH)), 
#         (
#             (0 + fractionW, halfH - fractionH),
#             (w - fractionW, halfH + fractionH),
#         ),  
#     ]

#     # initialize to off : no segment matched
#     on = [0] * 7

#     for (i, ((p1x, p1y), (p2x, p2y))) in enumerate(sevensegs):
#         region = roi[p1y:p2y, p1x:p2x]
#         print(
#             f"{i}: Sum of 1: {np.sum(region == 255)}, Sum of 0: {np.sum(region == 0)}, Shape: {region.shape}, Size: {region.size}"
#         )
#         if np.sum(region == 255) > region.size * 0.5:
#             on[i] = 1
#         print(f"State of ON: {on}")

#     digit = DIGITSDICT[tuple(on)]
#     print(f"Digit is: {digit}")
#     digits += [digit]
#     cv2.rectangle(canvas, (x, y), (x + w, y + h), CYAN, 1)
#     cv2.putText(canvas, str(digit), (x - 5, y + 6), FONT, 0.3, (0, 0, 0), 1)
#     cv2.imshow("Digit", canvas)
#     cv2.waitKey(0)

# print(f"Digits on the token are: {digits}")


import cv2
import numpy as np
import os

FONT = cv2.FONT_HERSHEY_SIMPLEX
CYAN = (255, 255, 0)
DIGITSDICT = {
    (1, 1, 1, 1, 1, 1, 0): 0,
    (0, 1, 1, 0, 0, 0, 0): 1,
    (1, 1, 0, 1, 1, 0, 1): 2,
    (1, 1, 1, 1, 0, 0, 1): 3,
    (0, 1, 1, 0, 0, 1, 1): 4,
    (1, 0, 1, 1, 0, 1, 1): 5,
    (1, 0, 1, 1, 1, 1, 1): 6,
    (1, 1, 1, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9,
}

def detect_digits(image_path, save_debug=False):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # --- ROI detection (like roi_02.py automatic approach) ---
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)
    
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        raise ValueError("No contours found for ROI.")
    
    # Take largest contour as ROI
    c = max(cnts, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    roi_color = img[y:y+h, x:x+w]
    roi_gray = gray[y:y+h, x:x+w]
    
    # --- Preprocessing (from your latest code) ---
    RATIO = roi_gray.shape[0] * 0.2
    roi_gray = cv2.bilateralFilter(roi_gray, 5, 30, 60)
    trimmed = roi_gray[int(RATIO):, int(RATIO):roi_gray.shape[1] - int(RATIO)]
    roi_color = roi_color[int(RATIO):, int(RATIO):roi_color.shape[1] - int(RATIO)]
    
    edged = cv2.adaptiveThreshold(trimmed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 5, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 5))
    dilated = cv2.dilate(edged, kernel, iterations=1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
    dilated = cv2.dilate(dilated, kernel, iterations=1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 1))
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    h = roi_gray.shape[0]
    ratio = int(h * 0.07)
    eroded[-ratio:,] = 0
    eroded[:, :ratio] = 0
    
    # --- Find digit contours ---
    cnts, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    digits_cnts = [c for c in cnts if cv2.boundingRect(c)[3] > 20]
    sorted_digits = sorted(digits_cnts, key=lambda c: cv2.boundingRect(c)[0])
    
    # --- Recognize digits ---
    digits = []
    for cnt in sorted_digits:
        (x, y, w, h) = cv2.boundingRect(cnt)
        roi_digit = eroded[y:y+h, x:x+w]
        qW, qH = int(w * 0.25), int(h * 0.15)
        fractionH, halfH, fractionW = int(h * 0.05), int(h * 0.5), int(w * 0.25)
        
        sevensegs = [
            ((0, 0), (w, qH)), 
            ((w - qW, 0), (w, halfH)), 
            ((w - qW, halfH), (w, h)),  
            ((0, h - qH), (w, h)),  
            ((0, halfH), (qW, h)),  
            ((0, 0), (qW, halfH)), 
            ((fractionW, halfH - fractionH),
             (w - fractionW, halfH + fractionH)),
        ]
        
        on = [0] * 7
        for i, ((p1x, p1y), (p2x, p2y)) in enumerate(sevensegs):
            region = roi_digit[p1y:p2y, p1x:p2x]
            if np.sum(region == 255) > region.size * 0.5:
                on[i] = 1
        
        digit = DIGITSDICT.get(tuple(on), None)
        if digit is not None:
            digits.append(digit)
    
    if save_debug:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/roi.png", roi_color)
        cv2.imwrite("debug/trimmed.png", trimmed)
        cv2.imwrite("debug/eroded.png", eroded)
    
    return digits

if __name__ == "__main__":
    img_path = "inter/ocbc-roi.png"  # change to your test image
    result = detect_digits(img_path, save_debug=True)
    print("Detected Digits:", result)
