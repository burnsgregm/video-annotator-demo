from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for
import uuid

import os
import base64
import requests
import cv2

from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load .env
load_dotenv()

# Initialize Flask
app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"  # for flash messages

# Directories
BASE_DIR      = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
FRAMES_FOLDER = BASE_DIR / "frames"
ANNOT_FOLDER  = BASE_DIR / "annotated_frames"
STATIC_FOLDER = BASE_DIR / "static"
ALLOWED_EXTS  = {"mp4"}

app.config["UPLOAD_FOLDER"]    = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB upload limit

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS
    
@app.route("/", methods=["GET"])
def index():
    # Render the upload page; no video by default
    return render_template("index.html", output_video=None)


@app.route("/upload", methods=["POST"])
def upload():
    # 1) Validate the upload
    if "video" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["video"]
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)
    if not allowed_file(file.filename):
        flash("Invalid file type. Only .mp4 allowed.")
        return redirect(request.url)

    # 2) Create a unique session directory
    session_id = uuid.uuid4().hex
    upload_dir = UPLOAD_FOLDER / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 3) Save the uploaded video
    video_path = upload_dir / file.filename
    file.save(str(video_path))

    # 4) Run the pipeline end-to-end
    #    a) Extract all frames
    extract_frames(video_path, FRAMES_FOLDER / session_id, fps_cap=0)

    #    b) Annotate each frame
    out_frames = ANNOT_FOLDER / session_id
    for frame in sorted((FRAMES_FOLDER / session_id).glob("*.jpg")):
        res   = predict_frame(frame)
        preds = res["outputs"][0]["model_predictions"]["predictions"]
        dest  = out_frames / frame.name
        annotate_frame(frame, preds, dest)

    #    c) Rebuild into a video
    import cv2 as _cv2
    cap      = _cv2.VideoCapture(str(video_path))
    orig_fps = cap.get(_cv2.CAP_PROP_FPS) or 30
    cap.release()
    output_name = f"{session_id}.mp4"
    rebuild_video(out_frames, STATIC_FOLDER / output_name, fps=int(orig_fps))

    # 5) Render template with download link
    return render_template("index.html", output_video=output_name)


@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    # Serve the annotated video as a download
    return send_from_directory(str(STATIC_FOLDER), filename, as_attachment=True)

# Roboflow credentials & endpoint
ROBOFLOW_API_KEY   = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_INFER_URL = os.getenv("ROBOFLOW_INFER_URL")


def extract_frames(video_path: Path, output_folder: Path, fps_cap: int = 1):
    """
    Extracts frames from a video at approximately fps_cap frames per second.
    Saves them as JPEGs in output_folder.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 1
    interval = int(fps // fps_cap) if fps_cap else 1

    output_folder.mkdir(parents=True, exist_ok=True)

    idx = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % interval == 0:
            out_file = output_folder / f"frame_{saved:05d}.jpg"
            cv2.imwrite(str(out_file), frame)
            saved += 1
        idx += 1

    cap.release()
    print(f"Extracted {saved} frames at ~{fps_cap} fps from {video_path}")


def predict_frame(image_path: Path):
    """
    Calls Roboflow’s serverless infer endpoint via JSON.
    Sends the frame as a base64-encoded string.
    """
    img_bytes = image_path.read_bytes()
    b64_str = base64.b64encode(img_bytes).decode("utf-8")

    payload = {
        "api_key": ROBOFLOW_API_KEY,
        "inputs": {
            "image": {
                "type": "base64",
                "value": b64_str
            }
        }
    }

    resp = requests.post(
        ROBOFLOW_INFER_URL,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    return resp.json()


def annotate_frame(image_path: Path, predictions: list, output_path: Path):
    """
    Draws bounding boxes and labels on a frame.
    `predictions` should be a list of dicts from:
      res["outputs"][0]["model_predictions"]["predictions"]
    """
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # load a font (fallback to default)
    try:
        font = ImageFont.truetype("arial.ttf", size=16)
    except IOError:
        font = ImageFont.load_default()

    for pred in predictions:
        x, y = pred["x"], pred["y"]
        w, h = pred["width"], pred["height"]
        cls = pred.get("class", "")
        conf = pred.get("confidence", 0)

        # convert center-based coords to corners
        x0 = int(x - w/2)
        y0 = int(y - h/2)
        x1 = int(x + w/2)
        y1 = int(y + h/2)

        # draw bounding box
        draw.rectangle([x0, y0, x1, y1], outline="red", width=2)

        # prepare label
        label = f"{cls} {conf:.2f}"
        # measure text size by rendering at origin
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # draw background rectangle for label
        draw.rectangle(
            [x0, y0 - text_height, x0 + text_width, y0],
            fill="red"
        )
        # draw the label text
        draw.text((x0, y0 - text_height), label, fill="white", font=font)

    # ensure output folder exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # save annotated image
    img.save(output_path)
    
def rebuild_video(frame_folder: Path, output_path: Path, fps: int = 30):
    """
    Reads all JPGs in frame_folder (in sorted order) and writes them
    as an .mp4 at the given fps to output_path.
    """
    frames = sorted(frame_folder.glob("*.jpg"))
    if not frames:
        raise ValueError(f"No frames found in {frame_folder}")

    # Read first frame to get dimensions
    first = cv2.imread(str(frames[0]))
    height, width, _ = first.shape

    # Prepare the video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    # Write each frame
    for img_path in frames:
        img = cv2.imread(str(img_path))
        writer.write(img)

    writer.release()
    print(f"Saved video to {output_path}")