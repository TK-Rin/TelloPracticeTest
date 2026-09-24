"""
modes/gesture_mode.py - Hand Gesture Control

Uses cvzone's HandTrackingModule (built on MediaPipe) to count how many
fingers are raised on one hand and maps that count to a drone command.
Each gesture fires ONE discrete, blocking command - the same pattern as
the mission-pad lab script (4mission-padsNew.py) - so one clear hand shape
always means one clear, predictable drone action (no drift like RC control
would give).

Gesture map (finger count, thumb included):
    0 fingers  (fist)        -> Land
    1 finger   (index)       -> Move Up
    2 fingers  (index+mid)   -> Move Down
    3 fingers                -> Move Left
    4 fingers  (no thumb)    -> Move Right
    5 fingers  (open palm)   -> Toggle video Recording on/off

Recording reuses the threaded-recorder pattern from 4newRecordVideo.py: a
background thread keeps pulling frame_read.frame on its own, so recording
stays smooth even while a blocking move command (e.g. move_up) is running.
"""
import time
from threading import Thread

import cv2
from cvzone.HandTrackingModule import HandDetector

from utils.common import MEDIA_DIR

FRAME_W, FRAME_H = 640, 480
MOVE_CM = 30
ACTION_COOLDOWN = 1.5  # seconds between two discrete gesture actions, so one
                        # held-up hand doesn't fire the same move 10x/sec

_detector = HandDetector(detectionCon=0.75, maxHands=1)


def new_state(frame_read=None):
    return {
        "frame_read": frame_read,
        "last_action_time": 0.0,
        "recording": False,
        "keep_recording": False,
        "record_thread": None,
        "video_index": 1,
        "stop": False,
    }


def _start_recording(state):
    if state["recording"] or state["frame_read"] is None:
        return
    frame_read = state["frame_read"]
    state["keep_recording"] = True
    state["recording"] = True

    def _recorder():
        frame = frame_read.frame
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        height, width, _ = frame_bgr.shape
        path = MEDIA_DIR / f"gesture_record_{state['video_index']}.mp4"
        video = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 30, (width, height))
        if not video.isOpened():
            print("VideoWriter failed to open!")
            return
        print(f"Recording started -> {path.name}")
        while state["keep_recording"]:
            frame = frame_read.frame
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if frame_bgr.shape[1] == width and frame_bgr.shape[0] == height:
                video.write(frame_bgr)
            time.sleep(1 / 30)
        video.release()
        print(f"Recording saved -> {path.name}")

    state["record_thread"] = Thread(target=_recorder, daemon=True)
    state["record_thread"].start()


def _stop_recording(state):
    if not state["recording"]:
        return
    state["keep_recording"] = False
    if state["record_thread"] is not None:
        state["record_thread"].join()
    state["recording"] = False
    state["video_index"] += 1


def stop(state):
    """Call when leaving gesture mode (mode switch or shutdown) to close any open recording."""
    _stop_recording(state)


def process_frame(tello, frame_bgr, state):
    # Zero out any leftover RC velocity from FOLLOW mode before we hover here.
    tello.send_rc_control(0, 0, 0, 0)

    small = cv2.resize(frame_bgr, (FRAME_W, FRAME_H))
    hands, drawn = _detector.findHands(small, draw=True)

    now = time.time()
    if hands and (now - state["last_action_time"]) > ACTION_COOLDOWN:
        fingers = _detector.fingersUp(hands[0])
        count = sum(fingers)

        if count == 0:
            print("Gesture: FIST -> land")
            stop(state)
            state["stop"] = True
        elif count == 1:
            print("Gesture: 1 finger -> move up")
            tello.move_up(MOVE_CM)
        elif count == 2:
            print("Gesture: 2 fingers -> move down")
            tello.move_down(MOVE_CM)
        elif count == 3:
            print("Gesture: 3 fingers -> move left")
            tello.move_left(MOVE_CM)
        elif count == 4:
            print("Gesture: 4 fingers -> move right")
            tello.move_right(MOVE_CM)
        elif count == 5:
            if state["recording"]:
                print("Gesture: OPEN PALM -> stop recording")
                _stop_recording(state)
            else:
                print("Gesture: OPEN PALM -> start recording")
                _start_recording(state)

        state["last_action_time"] = now

    cv2.putText(drawn, f"GESTURE MODE | recording={state['recording']}", (10, 30),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Tello", drawn)
    cv2.waitKey(1)
    return state
