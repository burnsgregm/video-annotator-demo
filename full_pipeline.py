from pathlib import Path
from app import extract_frames, predict_frame, annotate_frame, rebuild_video
import cv2

# Paths
video      = Path("uploads/sample.mp4")
all_frames = Path("frames/full_run")
all_annots = Path("annotated_frames/full_run")
output_vid = Path("static/output_full.mp4")

# 1) Extract every frame
extract_frames(video, all_frames, fps_cap=0)

# 2) Annotate each frame
for frame_path in sorted(all_frames.glob("*.jpg")):
    res   = predict_frame(frame_path)
    preds = res["outputs"][0]["model_predictions"]["predictions"]
    dest  = all_annots / frame_path.name
    annotate_frame(frame_path, preds, dest)

# 3) Rebuild video at original FPS
cap      = cv2.VideoCapture(str(video))
orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30
cap.release()
rebuild_video(all_annots, output_vid, fps=int(orig_fps))

print("✅ Done! Full annotated video at", output_vid)