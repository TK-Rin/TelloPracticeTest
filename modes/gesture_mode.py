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
    5 fingers  (open palm)   -> Nothing (hover)

Video recording was removed on purpose: it drained the battery too fast.
"""
import time

import cv2
from cvzone.HandTrackingModule import HandDetector
from djitellopy import TelloException

FRAME_W, FRAME_H = 640, 480
MOVE_CM = 30
ACTION_COOLDOWN = 1.5  # seconds between two discrete gesture actions, so one
                        # held-up hand doesn't fire the same move 10x/sec

_detector = HandDetector(detectionCon=0.75, maxHands=1)


def new_state():
    return {
        "last_action_time": 0.0,
        "stop": False,
    }


def _try_move(move):
    """Run a move; if the Tello rejects it, warn and keep hovering instead of crashing."""
    try:
        move(MOVE_CM)
    except TelloException as e:
        print("Move rejected by the drone, ignoring:", e)


def process_frame(tello, frame_bgr, state):
    # Zero out any leftover RC velocity from FOLLOW mode before we hover here.
    tello.send_rc_control(0, 0, 0, 0)

    small = cv2.resize(frame_bgr, (FRAME_W, FRAME_H))
    hands, drawn = _detector.findHands(small, draw=True)

    now = time.time()
    if hands and (now - state["last_action_time"]) > ACTION_COOLDOWN:
        fingers = _detector.fingersUp(hands[0])
        count = sum(fingers)

        if count == 5:
            print("Gesture: FIST -> land")
            state["stop"] = True
        elif count == 1:
            print("Gesture: 1 finger -> move up")
            _try_move(tello.move_up)
        elif count == 2:
            print("Gesture: 2 fingers -> move down")
            _try_move(tello.move_down)
        elif count == 3:
            print("Gesture: 3 fingers -> move left")
            _try_move(tello.move_left)
        elif count == 4:
            print("Gesture: 4 fingers -> move right")
            _try_move(tello.move_right)

        state["last_action_time"] = now

    cv2.putText(drawn, "GESTURE MODE", (10, 30),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Tello", drawn)
    cv2.waitKey(1)
    return state
