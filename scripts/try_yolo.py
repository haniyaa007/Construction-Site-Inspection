import sys
import time

from ultralytics import YOLO

image_path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/site1.png"
model_path = sys.argv[2] if len(sys.argv) > 2 else "yolov8n.pt"

model = YOLO(model_path)
print(f"\nModel: {model_path}")
print(f"Classes it knows: {list(model.names.values())}")

start = time.perf_counter()
results = model(image_path, conf=0.25)
elapsed = time.perf_counter() - start

result = results[0]
print(f"\nImage: {image_path}")
print(f"Inference took {elapsed:.2f}s, found {len(result.boxes)} objects\n")

for box in result.boxes:
    class_name = result.names[int(box.cls)]
    confidence = float(box.conf)
    x1, y1, x2, y2 = (round(v) for v in box.xyxy[0].tolist())
    print(f"{class_name:<18} conf={confidence:.2f}  box=({x1}, {y1}, {x2}, {y2})")

result.save(filename="runs/annotated.png")
print("\nSaved annotated image to runs/annotated.png")