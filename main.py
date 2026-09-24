"""
main.py - Practical Test: Dual-Mode Drone Control

Two flight modes, switched live with mission pads while the drone is
already in the air:

    Pad #4 -> Hand Gesture Control mode  (modes/gesture_mode.py)
    Pad #2 -> Human Following mode       (modes/follow_mode.py)
    Pad #3 -> Land

Keyboard 'q' / 'esc' always forces an immediate safe landing too.

Same connect -> battery check -> try/finally safety pattern as every other
script in this course (1TestFlight.py, 4mission-padsNew.py, ...): whatever
happens mid-flight, the finally block always lands the drone and releases
the camera/windows cleanly.
"""
import os
import time

from utils.common import BASE_DIR, ensure_dirs, safe_land

# cvzone's HandDetector caches its ~8MB model file ("hand_landmarker.task") next to
# the current working directory, downloading it only if not already present there.
# Pinning cwd to the project folder BEFORE importing modes.gesture_mode (which builds
# a HandDetector as soon as it's imported) means that file is always found on the
# portable disk and never needs a fresh download at flight time, when the PC has no
# internet (it's joined to the Tello's Wi-Fi) — regardless of how main.py was launched.
os.chdir(BASE_DIR)

import cv2
import keyboard
from djitellopy import Tello

from modes import gesture_mode, follow_mode

MIN_BATTERY = 20

PAD_GESTURE = 4
PAD_FOLLOW = 2
PAD_LAND = 3
PAD_POLL_INTERVAL = 0.3  # how often we re-check the mission pad id (seconds)

FRAME_MIN_HEIGHT = 300  # discard placeholder frames, same check as the other vision labs

MODE_IDLE = "IDLE"
MODE_GESTURE = "GESTURE"
MODE_FOLLOW = "FOLLOW"


def wait_for_stable_frame(frame_read):
    print("Waiting for stable frame...")
    while True:
        frame = frame_read.frame
        if frame is not None and frame.shape[0] > FRAME_MIN_HEIGHT:
            print("Stable frame shape:", frame.shape)
            return frame
        time.sleep(0.1)


def main():
    ensure_dirs()

    tello = Tello()
    tello.connect()

    is_flying = False
    frame_read = None
    mode = MODE_IDLE
    gesture_state = gesture_mode.new_state()
    follow_state = follow_mode.new_state()

    try:
        power = tello.get_battery()
        print("Power Level =", power, "%")
        if power < MIN_BATTERY:
            print(f"Battery too low (<{MIN_BATTERY}%) — aborting takeoff for safety.")
            raise SystemExit

        tello.enable_mission_pads()
        tello.set_mission_pad_detection_direction(2)  # 0=down, 1=forward, 2=both

        tello.streamon()
        frame_read = tello.get_frame_read()
        wait_for_stable_frame(frame_read)

        tello.takeoff()
        is_flying = True
        tello.move_up(40)  # a bit of headroom to see hands / people / pads comfortably

        gesture_state = gesture_mode.new_state(frame_read)
        follow_state = follow_mode.new_state(frame_read)

        print("Ready. Hold the drone over Pad #4 (Gesture) or Pad #2 (Follow).")
        print("Pad #3, or 'q' / 'esc', lands at any time.")

        last_pad_check = 0.0

        while True:
            if keyboard.is_pressed("q") or keyboard.is_pressed("esc"):
                print("Manual stop requested — landing.")
                break

            now = time.time()
            if now - last_pad_check > PAD_POLL_INTERVAL:
                last_pad_check = now
                pad = tello.get_mission_pad_id()

                if pad == PAD_LAND:
                    print("Land pad detected — landing.")
                    break
                elif pad == PAD_GESTURE and mode != MODE_GESTURE:
                    print("Pad #4 detected -> switching to GESTURE mode")
                    if mode == MODE_GESTURE:
                        gesture_mode.stop(gesture_state)
                    mode = MODE_GESTURE
                    gesture_state = gesture_mode.new_state(frame_read)
                    tello.send_rc_control(0, 0, 0, 0)
                elif pad == PAD_FOLLOW and mode != MODE_FOLLOW:
                    print("Pad #2 detected -> switching to FOLLOW mode")
                    if mode == MODE_GESTURE:
                        gesture_mode.stop(gesture_state)
                    mode = MODE_FOLLOW
                    follow_state = follow_mode.new_state(frame_read)
                    tello.send_rc_control(0, 0, 0, 0)

            frame = frame_read.frame
            if frame is None:
                continue
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if mode == MODE_GESTURE:
                gesture_state = gesture_mode.process_frame(tello, frame_bgr, gesture_state)
                if gesture_state["stop"]:
                    print("Gesture FIST -> landing.")
                    break
            elif mode == MODE_FOLLOW:
                follow_state = follow_mode.process_frame(tello, frame_bgr, follow_state)
            else:
                tello.send_rc_control(0, 0, 0, 0)
                cv2.putText(frame_bgr, "IDLE - fly over Pad 4 (Gesture) or Pad 2 (Follow)",
                            (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 2)
                cv2.imshow("Tello", frame_bgr)
                cv2.waitKey(1)

    finally:
        try:
            gesture_mode.stop(gesture_state)
        except Exception:
            pass
        try:
            tello.send_rc_control(0, 0, 0, 0)
        except Exception:
            pass
        safe_land(tello, is_flying)
        try:
            tello.streamoff()
        except Exception:
            pass
        try:
            tello.disable_mission_pads()
        except Exception:
            pass
        cv2.destroyAllWindows()
        tello.end()


if __name__ == "__main__":
    main()
