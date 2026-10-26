# Model Weights

The model weights (`*.pt`) are **not committed** to this repository. They are
large (the custom models are ~114 MB each, above GitHub's 100 MB file limit) and
are excluded via `.gitignore`. Place the files listed below in this `models/`
directory before running the project.

## Required by the current code

| File | Size | Type | Purpose |
| :--- | :--- | :--- | :--- |
| `yolo12n.pt` | ~5 MB | Base (Ultralytics) | General vehicle / object detection used by `main.py` and `streamlit.py` |
| `helmet.pt` | ~114 MB | Custom-trained | Helmet vs. no-helmet classification (`HelmetDetectionDetector`) |
| `train3_best.pt` | ~114 MB | Custom-trained | License-plate detection, passed to the OCR pipeline (`OCR3`) |

## Also present in the authors' environment (not loaded by current code)

These were used during experimentation and model comparison (see the paper's
Table I) but are **not referenced** by the current entry points. They are listed
only so the full set is documented.

| File | Size | Notes |
| :--- | :--- | :--- |
| `yolo12m.pt` | ~39 MB | Base YOLOv12-medium; paper used a medium model for vehicle detection |
| `yolo12x.pt` | ~114 MB | Base YOLOv12-extra-large; paper used an x model for plate/OCR ROI |
| `best.pt` | ~114 MB | Earlier custom training checkpoint |

## How to obtain the weights

### Base YOLOv12 weights (`yolo12n.pt`, `yolo12m.pt`, `yolo12x.pt`)
These are standard Ultralytics weights and are downloaded automatically the
first time you reference them through Ultralytics, or you can get them from the
[Ultralytics YOLO12 documentation](https://docs.ultralytics.com/models/yolo12/).

### Custom weights (`helmet.pt`, `train3_best.pt`, `best.pt`)
These were trained by the authors on a custom 4K dataset of Indian road scenes
(see the accompanying ICICIS 2025 paper). They are **not** publicly hosted yet.
To obtain them, contact the authors, or train your own equivalents:

- **Helmet model** — a YOLOv12 detector with a no-helmet class (class id `1` in
  the current code). Train on a helmet / no-helmet dataset of two-wheeler riders.
- **License-plate model** — a YOLOv12 detector with a `license_plate` class.
  Train on an Indian license-plate detection dataset.

> **Licensing:** Ultralytics YOLO is distributed under **AGPL-3.0**, and weights
> fine-tuned from it inherit that license. Any redistribution of the custom
> weights must comply with AGPL-3.0, and you must have the rights to the training
> data used to produce them.

## Expected layout

```
models/
├── yolo12n.pt
├── helmet.pt
└── train3_best.pt
```
