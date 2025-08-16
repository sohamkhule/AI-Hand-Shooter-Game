import time
import cv2

class Explosion:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.start_time = time.time()
        self.duration = 0.3  # seconds

    def is_active(self):
        return time.time() - self.start_time < self.duration

    def draw(self, frame):
        if not self.is_active():
            return

        h, w, _ = self.image.shape
        top_left_x = int(self.x - w / 2)
        top_left_y = int(self.y - h / 2)

        overlay_image(frame, self.image, top_left_x, top_left_y)

def overlay_image(background, overlay, x, y):
    h, w, _ = overlay.shape

    for i in range(h):
        for j in range(w):
            if y + i >= background.shape[0] or x + j >= background.shape[1] or x + j < 0 or y + i < 0:
                continue

            alpha = overlay[i, j, 3] / 255.0  # Alpha channel
            for c in range(3):
                background[y + i, x + j, c] = (
                    (1 - alpha) * background[y + i, x + j, c] + alpha * overlay[i, j, c]
                )
