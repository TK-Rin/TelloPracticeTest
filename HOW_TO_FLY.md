# How to Fly It — Step by Step

A field checklist for running the dual-mode project on the real Tello drone.
(For first-time computer setup — installing Python, creating `.venv` — see
[README.md](README.md) instead. This assumes that part is already done.)

---

## 0. Before you fly (safety checklist)

- [ ] Battery charged to **at least 20%** (the script refuses takeoff below that —
      charge closer to 100% if you're doing a full test run).
- [ ] Propeller guards attached.
- [ ] Large, open, indoor space, clear of people not involved in the test.
- [ ] Mission Pads **#4**, **#2**, **#3** on hand, laid flat, face up.
- [ ] `.venv` already created on this PC (`setup_venv.bat` has been run at least once).
- [ ] Someone ready at the keyboard to hit `q` / `esc` for an emergency landing.

---

## 1. Lay out the mission pads

Put the 3 pads flat on the floor, a meter or two apart, somewhere the drone will
pass over/near during flight:

```
   [Pad 4]         [Pad 2]         [Pad 3]
   Gesture         Follow           Land
    mode            mode
```

They don't need to be in a straight line — just spaced out enough that flying to
one doesn't accidentally trigger another.

---

## 2. Power on the Tello

Press the power button once. Wait for the LED to finish blinking and settle
(solid/slow-blink amber = ready, not bound to an app).

---

## 3. Connect your PC/laptop to the drone's Wi-Fi

On your computer's Wi-Fi list, connect to the drone's own network, named something
like:

```
TELLO-XXXXXX
```

(No internet during this — you're connected directly to the drone. That's expected;
see the "offline" note in the README about why gesture mode still works without
internet.)

---

## 4. Open a terminal in the project folder and activate the venv

```
cd path\to\tellodrone
.venv\Scripts\activate
```

You should see `(.venv)` appear at the start of your prompt.

---

## 5. Run it

```
python main.py
```

What happens automatically, in order:

1. Connects to the drone, prints the battery %.
2. Aborts (prints a message, does **not** take off) if battery < 20%.
3. Enables mission pad detection.
4. Turns on the video stream and waits for a stable frame.
5. **Takes off** and rises ~40 cm.
6. Sits in **IDLE**, hovering, waiting to see a mission pad.

A window titled **"Tello"** opens showing the live camera feed — keep an eye on it,
it shows which mode is active and what the drone currently sees.

---

## 6. Fly to a mode

Physically fly (or gently guide, if you're close enough) the drone so Pad #4 or
Pad #2 is visible to it (downward or forward, both are checked):

- **Pad #4 → Gesture mode.** Terminal prints `switching to GESTURE mode`.
- **Pad #2 → Follow mode.** Terminal prints `switching to FOLLOW mode`.

You can fly back over the other pad at any time to switch again — it doesn't need
to land in between.

---

## 7a. Using Gesture mode

Stand a meter or two in front of the drone, hand clearly lit, palm facing the
camera. Hold a shape steady for about a second:

| Show this | Fingers | Drone does |
|---|---|---|
| ✊ Fist | 0 | **Lands** |
| ☝️ | 1 | Moves up 30 cm |
| ✌️ | 2 | Moves down 30 cm |
| 3 fingers | 3 | Moves left 30 cm |
| 4 fingers (no thumb) | 4 | Moves right 30 cm |
| 🖐️ Open palm | 5 | Nothing (keeps hovering) |

There's a ~1.5s cooldown between actions, so it won't repeat a move while you hold
the same shape.

## 7b. Using Follow mode

Step back far enough that your **whole body** is in frame (the HOG detector looks
for a full person, not just a face/torso). Walk slowly — toward/away from the
drone, and side to side — it should rotate, rise/descend, and move forward/back to
keep you centered and at a steady distance. If it loses you for more than 2
seconds it just hovers in place until it sees you again ("searching for
person..." shows on screen).

---

## 8. Landing

Any of these lands it:

- Fly over **Pad #3**.
- Press **`q`** or **`esc`** (works even if the terminal window isn't focused).
- Ctrl+C in the terminal (last resort — the `finally` block still tries to land
  safely).

After landing, the script also turns off the video stream, disables mission pads,
and closes the camera window automatically.

---

## 9. After the flight

- Battery below ~10%? Recharge before the next run.
- Going to a different PC? See the **"Works on a Portable Disk"** section of
  [README.md](README.md) — run `setup_venv.bat` there first.

---

## Quick troubleshooting

| Symptom | Likely cause |
|---|---|
| `connect()` hangs / times out | Not connected to `TELLO-XXXXXX` Wi-Fi, or Windows Firewall blocking UDP — see README's Firewall section |
| Video window is black / never opens | `streamon()` blocked by firewall, or drone too far from PC |
| Gestures not recognized | Hand too close/far, poor lighting, or hand partly out of frame — check the "Tello" window to see what the camera sees |
| Drone won't follow anyone | Stand further back so your full body is visible; HOG needs a mostly-upright, mostly-unobstructed person |
| "Battery too low" and it won't take off | Recharge — this is a hard safety cutoff at 20% |
