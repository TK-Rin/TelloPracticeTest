# Tello Dual-Mode Drone — Practical Test Practice

Mobile Robot Laboratory (01416328) — Tello EDU Mini-Drone, Drone-2/Drone-3 material
(Mission Control + Vision Control combined into one project).

One drone, two flight modes, switched **live with mission pads** while it's already
in the air:

| Mission Pad | Mode | What it does |
|---|---|---|
| **#1** | Hand Gesture Control | Fly it with your hand — up/down/left/right/record/land |
| **#2** | Human Following | Drone rises, finds a person, and follows them as they walk |
| **#3** | Land | Safe landing from any mode |

Keyboard **`q`** or **`esc`** also lands the drone immediately from anywhere — always
keep a hand near the keyboard during test flights.

📋 **Flying it for real?** Use [HOW_TO_FLY.md](HOW_TO_FLY.md) — a field checklist
that walks through powering on the drone, laying out pads, and running each mode.
The rest of this file covers one-time computer setup.

---

## How it flies

1. Connect to the Tello's Wi-Fi, run `main.py`. The drone checks battery, takes off,
   and rises ~40 cm.
2. It starts **idle**, hovering, watching for a mission pad below/in front of it.
3. Hold/fly it over **Pad #1** or **Pad #2** on the floor to enter that mode — you can
   switch back and forth between pads as many times as you like mid-flight.
4. Fly over **Pad #3**, or press `q`/`esc`, to land.

### Mode 1 — Hand Gesture Control (`modes/gesture_mode.py`)

Show one hand to the front camera. Number of fingers raised = the command. Each
gesture triggers **one discrete move** (same blocking-command style as the mission-pad
lab script), with a ~1.5s cooldown so a held-up hand doesn't repeat the move 10x/sec.

| Gesture | Fingers | Action |
|---|---|---|
| ✊ Fist | 0 | Land |
| ☝️ | 1 | Move up 30 cm |
| ✌️ | 2 | Move down 30 cm |
| 🤟-ish (3 up) | 3 | Move left 30 cm |
| 4 up (no thumb) | 4 | Move right 30 cm |
| 🖐️ Open palm | 5 | Toggle video recording on/off |

Recordings are saved to `media/gesture_record_N.mp4`, written by a background thread
(same pattern as `4newRecordVideo.py`) so recording keeps running smoothly even while
a blocking `move_up()`/`move_left()`/etc. command is executing.

### Mode 2 — Human Following (`modes/follow_mode.py`)

Uses OpenCV's built-in HOG person detector (no model file to download — the laptop
usually has no internet once it's joined the Tello's own Wi-Fi network, so this had to
work fully offline). The drone:

- rotates (yaw) to keep the person centred left/right,
- moves up/down to keep them centred vertically,
- moves forward/back to hold a roughly constant distance, based on how tall their
  detected bounding box is — this is what makes it follow them while they walk,
  not just track them in place.

If nobody is detected for >2 seconds it just hovers and waits, instead of drifting off.

---

## ⚠️ Safety

- Check battery ≥ 20% before every flight — the script refuses to take off below that.
- Attach propeller guards. Fly in a large, clear, indoor space, away from people not
  involved in the test.
- Someone should always be ready to press `q`/`esc` for an emergency landing.
- **All scores are reset to zero if the drone is returned damaged or incomplete** — fly
  gesture mode first in a wide open room before trying it near walls.

---

## Works on a Portable Disk (important!)

This whole folder is meant to live on your portable/external drive and be plugged into
**any** PC (your desktop today, your laptop later). Two things make that safe:

1. **Code never hardcodes a drive letter.** `utils/common.py` resolves `media/` and
   `logs/` relative to the project folder itself, so it doesn't matter if the disk
   shows up as `G:`, `D:`, or `E:` on a different machine.
2. **The virtual environment (`.venv`) does NOT travel with the disk.** A venv bakes
   in absolute paths to a specific Python install on a specific machine — copying the
   folder to another PC and reusing the same `.venv` will not work correctly. Instead,
   **run `setup_venv.bat` once on every new PC** you plug the drive into; it rebuilds
   `.venv` fresh using that machine's own Python 3.11, using the drive's *current*
   drive letter automatically.

So: plug in the disk → double-click `setup_venv.bat` → wait for it to finish → you're
set up on that machine, every time.

One more offline detail: the first time `main.py` runs, `cvzone` downloads an ~8MB
hand-tracking model file, `hand_landmarker.task`, straight into the project folder
(not into `.venv`) and reuses it after that instead of re-downloading. That means it
only needs internet **once, ever** — do that first run on Wi-Fi with internet (before
connecting to the Tello), then the file travels with the disk to every other PC too,
so Gesture mode keeps working even with no internet once you're joined to the drone's
Wi-Fi.

---

## Syncing Between PCs (Git)

This project is also on GitHub: https://github.com/TK-Rin/TelloPracticeTest — so you
don't strictly need the portable disk just to move code between machines; `git`
works too, and lets both machines' changes merge cleanly instead of one copy
silently overwriting the other.

**First time on a new PC (no local copy yet):**
```
git clone https://github.com/TK-Rin/TelloPracticeTest.git
cd TelloPracticeTest
setup_venv.bat
```

**Already have a local copy (on the disk, or a previous clone) — pull the latest:**
```
git pull
```

**After making changes you want to keep, on either machine:**
```
git add -A
git commit -m "what changed"
git push
```

Whichever machine you edit on, `git pull` before you start and `git push` when
you're done keeps both PCs (and the disk) consistent. `.venv` is still excluded
from git (see `.gitignore`) — `setup_venv.bat` remains the way to (re)build it on
each machine.

---

## First-Time Setup (per machine)

### 1. Check Python 3.11 is installed

```
python --version
```

If it's missing or a different version, install Python 3.11.9 (64-bit), checking
✅ **"Add python.exe to PATH"** during install:
https://www.python.org/downloads/release/python-3119/

Verify with:
```
py -0
```
You should see `-V:3.11` listed.

### 2. Create the environment

Just double-click **`setup_venv.bat`** in this folder (or run it from a terminal) —
it creates `.venv` and installs everything in `requirements.txt`.

### 3A. VS Code

1. `code .`
2. Terminal → PowerShell: `.\.venv\Scripts\Activate.ps1`
   (If blocked by execution policy, run once:
   `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)
3. `Ctrl+Shift+P` → **Python: Select Interpreter** → pick the `.venv` (3.11) one.

### 3B. PyCharm

1. **File → Open** → select this folder.
2. **Settings → Project → Python Interpreter → Add Interpreter → Add Local
   Interpreter → Virtual Environment → Existing** → point it at `.venv` (created by
   `setup_venv.bat`).

### Verify

```
python -c "from djitellopy import Tello; import cv2; import cvzone; print('OK')"
```

---

## Running it

1. Power on the Tello, connect your PC/laptop's Wi-Fi to the drone's `TELLO-XXXXXX`
   network.
2. Place mission pads #1, #2, #3 on the floor within the flight area.
3. Activate the venv, then:
   ```
   python main.py
   ```

---

## Project Structure

```
tellodrone/
├── main.py                # entry point: connect, takeoff, mission-pad mode switch
├── modes/
│   ├── gesture_mode.py     # hand-gesture control (cvzone/MediaPipe)
│   └── follow_mode.py      # human following (OpenCV HOG)
├── utils/
│   └── common.py           # portable paths + safe-land helper
├── setup_venv.bat          # recreate .venv on whichever PC this disk is plugged into
├── requirements.txt
├── hand_landmarker.task    # gesture model, auto-downloaded once, then cached here
├── media/                  # pictures/recordings saved here (gitignored)
└── logs/                   # (gitignored)
```

---

## Windows Firewall (if connect/stream fails)

Tello uses UDP (command port 8889, video port 11111). If `tello.connect()` times out
or `streamon()` shows no image:

1. **Windows Security → Firewall & network protection → Allow an app through
   firewall → Allow another app** → browse to `tellodrone\.venv\Scripts\python.exe` →
   check both **Private** and **Public**.
2. Or open the ports directly (PowerShell as Administrator):
   ```powershell
   New-NetFirewallRule -DisplayName "Tello Command" -Direction Inbound -Protocol UDP -LocalPort 8889 -Action Allow
   New-NetFirewallRule -DisplayName "Tello Video"   -Direction Inbound -Protocol UDP -LocalPort 11111 -Action Allow
   ```
