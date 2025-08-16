import cv2
import mediapipe as mp
import math
import pygame
import time
from target import Target

# Initialize Pygame for sound
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound("shoot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
screen_height, screen_width = frame.shape[:2]

# Game variables
targets = [Target(screen_width, screen_height) for _ in range(5)]
score = 0
cooldown = 0
start_time = time.time()
game_duration = 60  

def reset_game():
    global score, targets, cooldown, start_time
    score = 0
    cooldown = 0
    targets = [Target(screen_width, screen_height) for _ in range(5)]
    start_time = time.time()

reset_game()

while True:
    success, frame = cap.read()
    if not success or frame is None:
        print("Webcam error")
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)
    index_pos = None

    remaining_time = max(0, int(game_duration - (time.time() - start_time)))

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            index_pos = (int(lm[8].x * w), int(lm[8].y * h))
            ring_tip_y = lm[16].y * h
            ring_pip_y = lm[14].y * h

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if index_pos:
                cv2.circle(frame, index_pos, 10, (255, 0, 0), -1)
                cv2.line(frame, (index_pos[0] - 20, index_pos[1]), (index_pos[0] + 20, index_pos[1]), (255, 0, 0), 2)
                cv2.line(frame, (index_pos[0], index_pos[1] - 20), (index_pos[0], index_pos[1] + 20), (255, 0, 0), 2)

            if ring_tip_y > ring_pip_y and cooldown == 0:
                shoot_sound.play()
                cv2.putText(frame, "🔫 SHOOT!", (index_pos[0], index_pos[1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                for target in targets:
                    if target.is_hit(index_pos[0], index_pos[1]):
                        explosion_sound.play()
                        target.hit()
                        score += 1
                        break

                cooldown = 10

    if cooldown > 0:
        cooldown -= 1

    for target in targets:
        try:
            target.update()
            target.draw(frame)
        except Exception as e:
            print("⚠️ Target draw/update error:", e)

    cv2.putText(frame, f"Score: {score}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
    cv2.putText(frame, f"Time Left: {remaining_time}s", (w - 250, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

    if remaining_time == 0:
        cv2.putText(frame, "🎉 GAME OVER 🎉", (w // 2 - 200, h // 2 - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
        cv2.putText(frame, "Press R to Play Again or Q to Quit", (w // 2 - 270, h // 2 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("🔫 Hand Gesture Shooting Game", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('r') and remaining_time == 0:
        reset_game()

cap.release()
cv2.destroyAllWindows()
