"""
modes/follow_mode.py - Human Following

Detects the largest person in frame with OpenCV's built-in HOG people
detector (no model file to download - important since the laptop is
connected to the Tello's own Wi-Fi and usually has no internet access at
flight time) and keeps the drone centred on, and at a set distance from,
that person using proportional RC-velocity control.

This is the same deadzone -> velocity idea as the Drone-3 object-tracking
lab (ObjectTrackingTello), just extended with a third axis: forward/back
control based on how tall the person's box is, which is what makes the
drone actually follow someone as they walk toward/away/sideways instead of
only rotating and bobbing up/down in place.
"""
import time

import cv2

FRAME_W, FRAME_H = 600, 400
DEAD_ZONE_X = 60
DEAD_ZONE_Y = 60
TARGET_BOX_HEIGHT = 260   # person box height (px) we try to hold distance at
DIST_DEAD_ZONE = 40

YAW_SPEED = 45
UPDOWN_SPEED = 35
FWD_BACK_SPEED = 25

LOST_TIMEOUT = 2.0  # seconds with nobody detected before we stop drifting and just hover

_hog = cv2.HOGDescriptor()
_hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def new_state(frame_read=None):
    return {"stop": False, "last_seen": time.time()}


def _largest_person(frame_bgr):
    small = cv2.resize(frame_bgr, (FRAME_W, FRAME_H))
    boxes, _weights = _hog.detectMultiScale(small, winStride=(8, 8), padding=(8, 8), scale=1.05)
    if len(boxes) == 0:
        return small, None
    # same "biggest wins" idea as getContours() picking the largest blob
    x, y, w, h = max(boxes, key=lambda b: b[2] * b[3])
    return small, (x, y, w, h)


def process_frame(tello, frame_bgr, state):
    frame, box = _largest_person(frame_bgr)

    lr, fb, ud, yaw = 0, 0, 0, 0

    if box is not None:
        state["last_seen"] = time.time()
        x, y, w, h = box
        cx, cy = x + w // 2, y + h // 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # left/right -> yaw, to keep the person centred horizontally
        if cx < FRAME_W // 2 - DEAD_ZONE_X:
            yaw = -YAW_SPEED
        elif cx > FRAME_W // 2 + DEAD_ZONE_X:
            yaw = YAW_SPEED

        # up/down -> keep the person roughly centred vertically
        if cy < FRAME_H // 2 - DEAD_ZONE_Y:
            ud = UPDOWN_SPEED
        elif cy > FRAME_H // 2 + DEAD_ZONE_Y:
            ud = -UPDOWN_SPEED

        # forward/back -> hold distance using box height as a distance proxy
        if h < TARGET_BOX_HEIGHT - DIST_DEAD_ZONE:
            fb = FWD_BACK_SPEED       # person looks small/far -> move closer
        elif h > TARGET_BOX_HEIGHT + DIST_DEAD_ZONE:
            fb = -FWD_BACK_SPEED      # person looks large/close -> back off

        cv2.putText(frame, f"person h={h}", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 0), 2)
    else:
        if time.time() - state["last_seen"] > LOST_TIMEOUT:
            lr = fb = ud = yaw = 0  # hover in place, wait for the person to come back
        cv2.putText(frame, "searching for person...", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)

    tello.send_rc_control(lr, fb, ud, yaw)

    cv2.putText(frame, "FOLLOW MODE", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Tello", frame)
    cv2.waitKey(1)
    return state
