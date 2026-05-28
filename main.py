import cv2
import mediapipe as mp
import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

screen_w, screen_h = pyautogui.size()

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
)

landmarker = HandLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)


def distance(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def is_finger_up(hand, tip, pip):
    return hand[tip].y < hand[pip].y


prev_x, prev_y = 0, 0
smoothing = 0.4  # lower = smoother, higher = more responsive

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)

    h, w, _ = frame.shape
    gesture_text = "Move"

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]
        index_tip = hand[8]
        thumb_tip = hand[4]
        middle_tip = hand[12]
        ring_tip = hand[16]
        pinky_tip = hand[20]

        # Move cursor using index finger (smoothed)
        target_x = index_tip.x * screen_w
        target_y = index_tip.y * screen_h
        prev_x = prev_x + (target_x - prev_x) * smoothing
        prev_y = prev_y + (target_y - prev_y) * smoothing
        pyautogui.moveTo(int(prev_x), int(prev_y))

        # Draw landmarks
        for lm in hand:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 3, (255, 0, 0), cv2.FILLED)
        cx, cy = int(index_tip.x * w), int(index_tip.y * h)
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        # Gesture detection
        thumb_index_dist = distance(thumb_tip, index_tip)
        thumb_middle_dist = distance(thumb_tip, middle_tip)
        thumb_ring_dist = distance(thumb_tip, ring_tip)

        index_up = is_finger_up(hand, 8, 6)
        middle_up = is_finger_up(hand, 12, 10)
        ring_up = is_finger_up(hand, 16, 14)
        pinky_up = is_finger_up(hand, 20, 18)

        # Pinch index + thumb = LEFT CLICK
        if thumb_index_dist < 0.05 and middle_up:
            pyautogui.click()
            gesture_text = "Left Click"

        # Pinch middle + thumb = RIGHT CLICK
        elif thumb_middle_dist < 0.05 and index_up:
            pyautogui.rightClick()
            gesture_text = "Right Click"

        # Pinch ring + thumb = DOUBLE CLICK
        elif thumb_ring_dist < 0.05 and index_up and middle_up:
            pyautogui.doubleClick()
            gesture_text = "Double Click"

        # Index + middle up, others down = SCROLL UP
        elif index_up and middle_up and not ring_up and not pinky_up and thumb_index_dist > 0.08:
            pyautogui.scroll(3)
            gesture_text = "Scroll Up"

        # Only pinky up = SCROLL DOWN
        elif pinky_up and not index_up and not middle_up and not ring_up:
            pyautogui.scroll(-3)
            gesture_text = "Scroll Down"

        else:
            gesture_text = "Move"

    else:
        pass

    # Display gesture status
    cv2.putText(frame, gesture_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
