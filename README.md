# 🚦 Intelligent Traffic Surveillance System (ITSS)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![YOLOv12](https://img.shields.io/badge/YOLO-v12-orange?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **Automating Traffic Compliance in India using Attention-Centric Real-Time Object Detection.**

---

## 📖 Table of Contents
- [Abstract](#-abstract)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Methodology & Logic](#-methodology--logic)
- [Tech Stack](#-tech-stack)
- [Performance Evaluation](#-performance-evaluation)
- [Installation](#-installation)
- [Usage](#-usage)
- [References & Citations](#-references--citations)

---

## 📄 Abstract

India’s vast and growing urban population has increased the number of vehicles on the road, and traditional manual traffic monitoring is slow, error-prone, and hard to scale 24/7.

**ITSS (Intelligent Traffic Surveillance System)** is a vision-based automated solution that detects, classifies, and reports traffic rule violations — red-light jumping, speeding, helmet-less riding, and non-compliance with vehicle insurance and Pollution Under Control (PUC). It uses a custom-trained **[YOLOv12 (You Only Look Once)](https://docs.ultralytics.com/models/yolo12/)** detector with real-time object tracking, license-plate extraction, and OCR, and delivers e-challans through an API backend.

Across the authors' test cases the system reported an overall accuracy of **93.76%**. This repository is the implementation accompanying the paper *"Intelligent Traffic Surveillance: A Vision-based System for Detecting Traffic Rule Violations"* (ICICIS 2025) — see [References & Citations](#-references--citations).

---

## ✨ Key Features

### 1. Visual Violation Detection
* **🔴 Red Light Violation:** Detects the traffic signal state and identifies vehicles that cross the stop line while the signal is red.
* **⛑️ Helmet-less Rider Detection:** Classifies two-wheeler riders and specifically detects the absence of a helmet on both the rider and pillion.
* **⚡ Speeding Detection:** Tracks vehicles across frames and estimates speed from centroid displacement using a pixel-to-metre conversion factor.

### 2. Automatic Number Plate Recognition (ANPR)
* **🔍 Plate Extraction:** License-plate region detected with a YOLOv12x model and cropped from the violation frame.
* **📝 OCR Processing:** The cropped plate is read by the **Groq** hosted vision model (**Llama-4-Scout-17B-16E-Instruct**), then validated against Indian plate formats (state-wise and BH series) with regex.

### 3. Compliance & Enforcement
* **☁️ API Integration:** Queries a central database using the extracted plate number.
* **🚫 Document Verification:** Checks for valid Insurance and PUC certificates.
* **📩 E-Challan Generation:** Automatically creates a violation report with time, location, violation type, and evidence image.

---

## 🏗 System Architecture

The system operates on a pipeline approach:

1.  **Input Acquisition:** CCTV feed or pre-recorded video.
2.  **Object Detection (YOLOv12):** Detects classes: `Vehicle`, `License Plate`, `Traffic Light`, `Person`, `Helmet`.
3.  **Object Tracking:** Assigns unique IDs to vehicles across frames using **ByteTrack** (via Ultralytics' built-in tracker) to handle occlusion.
4.  **Violation Logic Module:**
    * *If Red Light AND Vehicle Center > Stop Line → Violation.*
    * *If Vehicle Speed > Speed Limit → Violation.*
    * *If Motorbike AND Head AND No Helmet → Violation.*
5.  **Post-Processing:**
    * Crop the license plate → read it with the Groq vision model → validate against Indian plate formats (state-wise / BH) via regex. If the plate can't be read, the next sharpest frame after the violation is tried.
    * Look up the validated plate against the government RTO API for Insurance / PUC status.
6.  **Output:** Generate an e-challan PDF with the evidence frame, store it in AWS S3, and notify the owner by SMS (Twilio). OCR'd plates are also appended to `ocr results/ocr_results.txt`.

---

## ⚙️ Methodology & Logic

### Why YOLOv12?
We utilize **YOLOv12** by Ultralytics. Unlike previous iterations, YOLOv12 introduces an **attention-centric architecture** that significantly improves feature extraction in complex urban environments (e.g., crowded Indian roads). It balances the speed of CNNs with the global context awareness of Transformers.

The paper compares YOLOv11 and YOLOv12 across the nano → extra-large sizes and selects models by task, trading off accuracy against speed:
* **YOLOv12x** for the accuracy-critical steps — license-plate detection and the OCR region of interest.
* **YOLOv12m** for vehicle detection, which gives near-large accuracy at a fraction of the memory and compute.

The detector is pre-trained on COCO and fine-tuned on a custom dataset of 4K video captured around a local lane from multiple angles and exposures (day, fog, night), annotated with vehicle and license-plate bounding boxes.
* *Reference:* [Ultralytics YOLOv12 Documentation](https://docs.ultralytics.com/models/yolo12/)

### Speed Estimation Logic
To calculate speed from a 2D video feed:
1.  **Centroid Tracking:** Each tracked vehicle's centroid is followed across frames.
2.  **Euclidean Distance:** The pixel distance moved between sampled frames is converted to metres using a `meter_per_pixel` factor.
3.  **Formula:** $Speed = \frac{Distance (meters)}{Time (seconds)} \times 3.6 (km/h)$

> **Limitation:** The current implementation uses a single fixed `meter_per_pixel`
> constant, so it does not account for camera perspective (a vehicle far from the
> camera and one close to it do not share the same pixel-to-metre ratio). A proper
> homography/perspective calibration per camera view is a known improvement and is
> not yet implemented.

---

## 🛠 Tech Stack

| Component | Tool/Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.12 | Core logic and scripting. |
| **Detection Model** | **YOLOv12** (x for plate/OCR, m for vehicles) | Custom trained on a 4K Indian-road dataset. |
| **Framework** | PyTorch / Ultralytics | Model training and inference. |
| **Computer Vision** | OpenCV | Frame processing, cropping, and drawing. |
| **OCR** | Groq hosted vision model (Llama 4 Scout) | Text extraction from license plates. |
| **Tracking** | ByteTrack (Ultralytics) | Multi-object tracking for vehicle persistence. |
| **App / UI** | Streamlit | Upload a video and run the detectors from the browser. |
| **Reporting** | pdfkit + wkhtmltopdf, Jinja2 | E-challan PDF generation from an HTML template. |
| **Integrations** | Twilio (SMS), AWS S3 (storage), RapidAPI RTO | Notifications, PDF hosting, and PUC/Insurance lookup. |

---

## 📊 Performance Evaluation

The figures below are reported in the accompanying ICICIS 2025 paper, evaluated
on the authors' custom dataset.

**Detection models (object detection)**

| Model | mAP@50–95 | Accuracy | F1 Score |
| :--- | :--- | :--- | :--- |
| YOLOv11-l | 88.65% | 97.49% | 99.23% |
| YOLOv11-x | 87.81% | 98.24% | 99.25% |
| YOLOv12-m | 86.66% | 93.29% | 97.94% |
| YOLOv12-l | 88.66% | 98.13% | 99.25% |
| **YOLOv12-x** | **90.61%** | **98.87%** | **99.34%** |

**Pipeline results**

* **Overall accuracy:** 93.76%
* **Vehicle-type identification:** 97.56%
* **OCR (plate text correct):** 92.7%
* **ANPR (plate localization correct):** 98%
* **Helmet detection:** 93.26%

> **Reproducibility note:** The dataset, train/validation/test splits, and the
> training/evaluation scripts behind these numbers are not included in this
> repository, so the results above cannot yet be reproduced from a clone alone.
> To make them reproducible, add the dataset provenance, splits, and scripts
> under `docs/evaluation.md`. Also note that model detection FPS is separate from
> end-to-end throughput, which additionally includes the OCR API call, PDF
> generation, S3 upload, and SMS.

---

## 📦 Installation

### Prerequisites
* Python 3.12 (the environment the project was last tested against)
* The `wkhtmltopdf` binary installed and on your PATH (needed for PDF challans)
  * macOS: `brew install --cask wkhtmltopdf`
  * Debian/Ubuntu: `sudo apt-get install wkhtmltopdf`
  * Windows: install from the official site; the default path is auto-detected
* A CUDA-enabled GPU is recommended for real-time performance (CPU also works, slower)

### Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/RishiiShah/Traffic.git
    cd Traffic
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv .venv

    # macOS / Linux
    source .venv/bin/activate

    # Windows
    .venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    ```bash
    cp .env.example .env   # then edit .env and fill in your keys
    ```
    Notifications are **mocked by default** — no SMS is sent unless you set
    `ENABLE_NOTIFICATIONS=true` with valid Twilio credentials.

5.  **Download the Model Weights**
    The model weights (`*.pt`) are **not committed** to the repository (they are
    large and gitignored). Place the required files in the `models/` directory:

    | File | Purpose |
    | :--- | :--- |
    | `yolo12n.pt` | General vehicle / object detection |
    | `helmet.pt` | Helmet vs. no-helmet classification |
    | `train3_best.pt` | License-plate detection |

    The base YOLO12 weights come from the
    [Ultralytics YOLO12 docs](https://docs.ultralytics.com/models/yolo12/); the
    custom `helmet.pt` and `train3_best.pt` are specific to this project. See
    [`models/README.md`](models/README.md) for full details on each weight, how to
    obtain or train them, and licensing notes.

---

## 💻 Usage

**Command line** — runs all three detectors over `videos/test.mp4`:

```bash
python main.py
```

**Streamlit app** — upload a video and run detection from the browser:

```bash
streamlit run streamlit.py
```

Video paths, model paths, and detection parameters are configured at the top of
`main.py` / `streamlit.py` (command-line flags are not currently parsed).

---

## 🔗 References & Citations

### This Project

This repository accompanies the following paper. If you use this work, please cite:

```bibtex
@inproceedings{samant2025itss,
  title     = {Intelligent Traffic Surveillance: A Vision-based System for Detecting Traffic Rule Violations},
  author    = {Samant, Harsh and Bhosale, Shreevardhan and Doshi, Kush and Kale, Dashrath and Shah, Rishabh},
  booktitle = {2025 2nd International Conference on Integration of Computational Intelligent System (ICICIS)},
  address   = {Pune, India},
  year      = {2025},
  publisher = {IEEE},
  doi       = {10.1109/ICICIS65613.2025.11371065}
}
```

Paper: [IEEE Xplore — DOI 10.1109/ICICIS65613.2025.11371065](https://ieeexplore.ieee.org/document/11371065)

This project also builds on the following research in object detection. If you use the YOLOv12 architecture, please cite the original authors:

### YOLOv12 Architecture

```bibtex
@article{tian2025yolo12,
  title={YOLOv12: Attention-Centric Real-Time Object Detectors},
  author={Tian, Yunjie and Ye, Qixiang and Doermann, David},
  journal={arXiv preprint arXiv:2502.12524},
  year={2025}
}

```

### YOLOv12 Software

```bibtex
@software{yolo12,
  author = {Tian, Yunjie and Ye, Qixiang and Doermann, David},
  title = {YOLO12: Attention-Centric Real-Time Object Detectors},
  year = {2025},
  url = {[https://github.com/sunsmarterjie/yolov12](https://github.com/sunsmarterjie/yolov12)},
  license = {AGPL-3.0}
}

```

### Acknowledgements

* **Ultralytics:** For the YOLO framework implementation. [Docs](https://docs.ultralytics.com/models/yolo12/)
* **OpenCV:** For image processing tools.

---

<div align="center">
<sub>Developed with ❤️ for safer roads in India.</sub>
</div>
