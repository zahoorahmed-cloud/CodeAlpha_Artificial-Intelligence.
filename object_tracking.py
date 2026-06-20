import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

def main():
    # 1. Initialize YOLOv8 Model (Lightweight and fast for real-time)
    model = YOLO("yolov8n.pt")
    
    # Extract the pre-trained class names dictionary (e.g., {0: 'person', 1: 'bicycle'})
    class_names = model.names
    
    # 2. Initialize Deep SORT Tracker
    # max_age: frames to keep a track alive without a detection; n_init: frames to confirm a track
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, max_cosine_distance=0.2)

    # 3. Set up Video Input
    # Use 0 for live webcam. Change to a string path (e.g., "cars.mp4") to read from a video file.
    video_source = 0 
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    print("Press 'q' to exit the video stream safely.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video stream ended or failed to read frame.")
            break

        # 4. Object Detection using YOLOv8
        # stream=True utilizes a generator for optimized memory management
        results = model(frame, stream=True)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Extract coordinates, confidence score, and raw class integer
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                
                # Filter out low-confidence detections to ensure accuracy
                if conf > 0.4:
                    w = x2 - x1
                    h = y2 - y1
                    # Deep SORT strictly requires bounding box format: [left, top, width, height]
                    detections.append(([x1, y1, w, h], conf, cls))

        # 5. Object Tracking using Deep SORT
        # Update the tracker tracks using the current frame's detections
        tracks = tracker.update_tracks(detections, frame=frame)

        # 6. Draw Bounding Boxes, Classes, and Unique IDs
        for track in tracks:
            # Skip tracks that haven't been confirmed yet or are currently inactive
            if not track.is_confirmed():
                continue
                
            # Get tracking ID and bounding box in [left, top, right, bottom] format
            track_id = track.track_id
            ltrb = track.to_ltrb()
            
            x1, y1, x2, y2 = map(int, ltrb)
            
            # Bulletproof extraction of the class ID to safely map it to its real name
            raw_class = track.get_det_class()
            if raw_class is not None and raw_class != 'None':
                class_label = class_names[int(raw_class)]
            else:
                class_label = "Unknown"

            # Draw the primary tracking bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Construct standard label payload (e.g., "ID: 3 | person")
            label = f"ID: {track_id} | {class_label}"
            
            # Render background tag box for optimal font legibility
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + 180, y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        # 7. Display Output UI
        cv2.imshow("Real-Time Object Detection & Tracking", frame)

        # Stop executing immediately if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up and release native system resources
    cap.release()
    cv2.destroyAllWindows()
    print("Resources released. Script closed cleanly.")

if __name__ == "__main__":
    main()
