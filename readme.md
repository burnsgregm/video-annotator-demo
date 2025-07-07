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
