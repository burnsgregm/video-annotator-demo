# Video Annotator Demo

A local Flask web application that allows users to upload an MP4 video, performs object detection on each frame using the Roboflow Inference API, overlays bounding boxes and labels, and returns an annotated video for download.

---

## Features

- **Upload & Process**: Upload any `.mp4` video via a simple web interface  
- **Frame Extraction**: Extracts every frame from the video using OpenCV  
- **Object Detection**: Sends each frame to a Roboflow serverless inference endpoint for object detection  
- **Annotation**: Draws bounding boxes and class labels onto each frame with Pillow  
- **Video Reconstruction**: Rebuilds the annotated frames into an MP4 video using OpenCV  
- **Download**: Provides the final annotated video for download

---

## Table of Contents

1. [Demo Screenshot](#demo-screenshot)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Usage](#usage)  
6. [Project Structure](#project-structure)  
7. [Environment Variables](#environment-variables)  
8. [Contributing](#contributing)  
9. [License](#license)  

---

## Demo Screenshot

![Demo Screenshot](./demo_screenshot.png)

---

## Prerequisites

- Python 3.8+  
- `pip` package manager  
- Roboflow account with a deployed workflow  
- `ffmpeg` (optional, for advanced video handling)

---

## Installation

```bash
git clone https://github.com/your-username/video-annotator-demo.git
cd video-annotator-demo

python -m venv venv
# Mac/Linux
source venv/bin/activate
# Windows PowerShell
venv\Scripts\Activate.ps1

pip install -r requirements.txt
