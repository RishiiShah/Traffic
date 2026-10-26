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

India’s rapid urbanization has led to a surge in vehicular density, rendering traditional manual traffic monitoring inefficient. Manual oversight is prone to human error, corruption, and inability to handle high-volume traffic 24/7. 

**ITSS (Intelligent Traffic Surveillance System)** is a vision-based automated solution designed to enforce traffic laws with high precision. By leveraging the **[YOLOv12 (You Only Look Once)](https://docs.ultralytics.com/models/yolo12/)** architecture, which introduces attention-centric mechanisms for superior real-time performance, this system detects complex violations such as red-light jumping, speeding, and helmet-less riding.

Furthermore, the system integrates an **OCR (Optical Character Recognition)** pipeline to extract license plates and communicates with a backend API to verify **Insurance** and **Pollution Control (PUC)** status, automatically generating e-challans for offenders.

---

## ✨ Key Features

### 1. Visual Violation Detection
* **🔴 Red Light Violation:** Detects the traffic signal state and identifies vehicles that cross the stop line while the signal is red.
* **⛑️ Helmet-less Rider Detection:** Classifies two-wheeler riders and specifically detects the absence of a helmet on both the rider and pillion.
* **⚡ Speeding Detection:** Uses perspective transformation and object tracking to estimate vehicle speed in real-time.

### 2. Automatic Number Plate Recognition (ANPR)
* **🔍 Plate Extraction:** High-accuracy cropping of license plates from moving vehicles.
* **📝 OCR Processing:** Converts plate images to text strings using advanced OCR engines.

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
    * Crop License Plate → Pass to OCR → Get String.
    * Send String to API → specific JSON response.
6.  **Output:** Overlay visuals on video and log data to CSV/Database.

---

## ⚙️ Methodology & Logic

### Why YOLOv12?
We utilize **YOLOv12** by Ultralytics. Unlike previous iterations, YOLOv12 introduces an **attention-centric architecture** that significantly improves feature extraction in complex urban environments (e.g., crowded Indian roads). It balances the speed of CNNs with the global context awareness of Transformers.
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
| **Language** | Python 3.9+ | Core logic and scripting. |
| **Detection Model** | **YOLOv12** | Custom trained on Indian Traffic Dataset. |
| **Framework** | PyTorch / Ultralytics | Model training and inference. |
| **Computer Vision** | OpenCV | Image processing, perspective transforms. |
| **OCR** | Groq hosted vision model (Llama 4 Scout) | Text extraction from license plates. |
| **Tracking** | ByteTrack (Ultralytics) | Multi-object tracking for vehicle persistence. |
| **App / UI** | Streamlit | Upload a video and run the detectors from the browser. |
| **Reporting** | pdfkit + wkhtmltopdf, Jinja2 | E-challan PDF generation from an HTML template. |
| **Integrations** | Twilio (SMS), AWS S3 (storage), RapidAPI RTO | Notifications, PDF hosting, and PUC/Insurance lookup. |

---

## 📊 Performance Evaluation

> **Note:** A reproducible evaluation (dataset splits, scripts, and raw results)
> is not yet published in this repository. Any accuracy, mAP, FPS, or OCR numbers
> should be treated as preliminary until a documented evaluation is added under
> `docs/evaluation.md`. Detection throughput (model FPS) is measured separately
> from the end-to-end pipeline, which also includes the OCR API call, PDF
> generation, S3 upload, and SMS and is therefore much slower per event.

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
    The model weights (`*.pt`) are not committed to the repository (they are large
    and gitignored). Place the following files in a `models/` directory at the
    project root:

    | File | Purpose |
    | :--- | :--- |
    | `yolo12n.pt` | General vehicle / object detection |
    | `helmet.pt` | Helmet vs. no-helmet classification |
    | `train3_best.pt` | License-plate detection |

    Download the base YOLO12 weights from the
    [Ultralytics YOLO12 docs](https://docs.ultralytics.com/models/yolo12/). The
    custom `helmet.pt` and `train3_best.pt` weights are specific to this project;
    host them on a GitHub Release or similar and document the download link here.

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

This project is built upon the cutting-edge research in object detection. If you use this repository or the YOLOv12 architecture in your research, please cite the original authors:

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
