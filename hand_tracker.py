import cv2
import mediapipe as mp
import pyautogui
import math
import time

from pycaw.pycaw import AudioUtilities

# ==========================
# SETTINGS
# ==========================

pyautogui.FAILSAFE = False

smoothening = 5

prev_x = 0
prev_y = 0

last_click_time = 0
last_zoom_time = 0

# ==========================
# CAMERA
# ==========================

cap = cv2.VideoCapture(0)

# ==========================
# MEDIAPIPE
# ==========================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# ==========================
# SCREEN SIZE
# ==========================

screen_w, screen_h = pyautogui.size()

print("Screen Width :", screen_w)
print("Screen Height:", screen_h)

# ==========================
# VOLUME SETUP
# ==========================

devices = AudioUtilities.GetSpeakers()
volume = devices.EndpointVolume

min_vol, max_vol, _ = volume.GetVolumeRange()

print("Volume Ready")

# ==========================
# MAIN LOOP
# ==========================

while True:

    success, img = cap.read()

    if not success:
        continue

    img = cv2.flip(img, 1)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                img,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            h, w, c = img.shape

            # LANDMARKS

            thumb_tip = hand.landmark[4]
            index_tip = hand.landmark[8]
            middle_tip = hand.landmark[12]
            ring_tip = hand.landmark[16]

            thumb_x = int(thumb_tip.x * w)
            thumb_y = int(thumb_tip.y * h)

            index_x = int(index_tip.x * w)
            index_y = int(index_tip.y * h)

            middle_x = int(middle_tip.x * w)
            middle_y = int(middle_tip.y * h)

            ring_x = int(ring_tip.x * w)
            ring_y = int(ring_tip.y * h)

            # DRAW

            cv2.circle(img, (index_x, index_y), 10, (0, 255, 0), -1)
            cv2.circle(img, (thumb_x, thumb_y), 10, (255, 0, 0), -1)

            cv2.line(
                img,
                (thumb_x, thumb_y),
                (index_x, index_y),
                (255, 0, 0),
                3
            )

            # DISTANCES

            distance = math.hypot(
                index_x - thumb_x,
                index_y - thumb_y
            )

            middle_distance = math.hypot(
                middle_x - thumb_x,
                middle_y - thumb_y
            )

            ring_distance = math.hypot(
                ring_x - thumb_x,
                ring_y - thumb_y
            )

            # ==================
            # MOUSE MOVEMENT
            # ==================

            mouse_x = int(index_tip.x * screen_w)
            mouse_y = int(index_tip.y * screen_h)

            curr_x = prev_x + (
                mouse_x - prev_x
            ) / smoothening

            curr_y = prev_y + (
                mouse_y - prev_y
            ) / smoothening

            pyautogui.moveTo(curr_x, curr_y)

            prev_x = curr_x
            prev_y = curr_y

            current_time = time.time()

            # ==================
            # LEFT CLICK
            # ==================

            if distance < 30:

                if current_time - last_click_time > 0.5:

                    pyautogui.click()

                    print("LEFT CLICK")

                    last_click_time = current_time

            # ==================
            # VOLUME CONTROL
            # ==================

            if 40 < distance < 200:

                volume_level = min_vol + (
                    (distance - 40) / 160
                ) * (max_vol - min_vol)

                volume.SetMasterVolumeLevel(
                    volume_level,
                    None
                )

            # ==================
            # ZOOM IN
            # ==================

            if middle_distance < 30:

                if current_time - last_zoom_time > 1:

                    pyautogui.hotkey("ctrl", "+")

                    print("ZOOM IN")

                    last_zoom_time = current_time

            # ==================
            # ZOOM OUT
            # ==================

            if ring_distance < 30:

                if current_time - last_zoom_time > 1:

                    pyautogui.hotkey("ctrl", "-")

                    print("ZOOM OUT")

                    last_zoom_time = current_time

    cv2.imshow("Virtual Mouse Pro", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()