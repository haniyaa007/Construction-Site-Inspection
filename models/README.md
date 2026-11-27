# Detection model

Weights are not stored in Git. Download `best.pt` from
https://huggingface.co/mancalazure/construction-ppe-safety and save it as `models/ppe.pt`.

- Architecture: YOLOv8n, fine-tuned on Roboflow Universe "construction-site-safety" v28
- Classes: Hardhat, Mask, NO-Hardhat, NO-Mask, NO-Safety Vest, Person, Safety Cone, Safety Vest, machinery, vehicle
- License: CC BY 4.0, attribution required (snehilsanyal/Construction-Site-Safety-PPE-Detection; Roboflow Universe)
- No published validation metrics. NO-Hardhat is weak. Absence of a detection is not evidence of non-compliance.
- Thresholds (store >= 0.25, flag >= 0.40) were tuned on 5 sample images only.
