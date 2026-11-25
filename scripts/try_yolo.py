import sys
import time

from ultralytics import YOLO

image_path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/site1.png"

model = YOLO("yolov8n.pt")  # downloads the weights file the first time (~6 MB)

start = time.perf_counter()
results = model(image_path, conf=0.1)  # ignore detections below 25% confidence
elapsed = time.perf_counter() - start

result = results[0]
print(f"\nImage: {image_path}")
print(f"Inference took {elapsed:.2f}s, found {len(result.boxes)} objects\n")

for box in result.boxes:
    class_name = result.names[int(box.cls)]
    confidence = float(box.conf)
    x1, y1, x2, y2 = (round(v) for v in box.xyxy[0].tolist())
    print(f"{class_name:<12} conf={confidence:.2f}  box=({x1}, {y1}, {x2}, {y2})")

result.save(filename="runs/annotated.png")  # image with boxes drawn on it
print("\nSaved annotated image to runs/annotated.png")