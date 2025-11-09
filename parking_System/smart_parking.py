from ultralytics import YOLO
import cv2
import screeninfo   # <<---- NEW

# Load your trained model
model = YOLO("best.pt")  # make sure best.pt is in same folder

# Load parking lot image
image_path = "parking4.png"   # change this to your image name
img = cv2.imread(image_path)

# Run prediction
results = model(img)

# Counting
vacant_count = 0
car_count = 0

# Class names from your dataset
class_names = ['Car', 'Vacant']

for result in results:
    for box in result.boxes:
        cls = int(box.cls[0])
        label = class_names[cls]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "Vacant":
            vacant_count += 1
            color = (0, 255, 0)  # Green for empty
        else:
            car_count += 1
            color = (0, 0, 255)  # Red for occupied

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Display counts
cv2.putText(img, f"Vacant Spots: {vacant_count}", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
cv2.putText(img, f"Occupied Spots: {car_count}", (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

# ------------ AUTO-FIT SCREEN DISPLAY (Added) ----------------
screen = screeninfo.get_monitors()[0]
screen_width, screen_height = screen.width, screen.height

cv2.namedWindow("Parking Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Parking Detection", screen_width, screen_height)
# -------------------------------------------------------------

cv2.imshow("Parking Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
