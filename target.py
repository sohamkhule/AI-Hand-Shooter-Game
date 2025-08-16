import cv2
import os
import random

class Target:
    COLORS = ["yellow", "blue", "red", "green"]

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.respawn()

    def respawn(self):
        self.x = random.randint(100, self.screen_width - 100)
        self.y = random.randint(100, self.screen_height - 100)
        self.dx = random.choice([-3, -2, 2, 3])
        self.dy = random.choice([-2, -3, 2, 3])

        self.color = random.choice(self.COLORS)
        self.fly_frames = self.load_frames(f"bird-{self.color}-fly")
        self.dead_frames = self.load_frames(f"bird-{self.color}-dead")

        # fallback if color-specific dead folder is broken
        if not self.dead_frames:
            self.dead_frames = self.load_frames("birds-dead")

        self.frame_index = 0
        self.dead = False
        self.fall_speed = 0
        self.dead_frame_index = 0

        if self.fly_frames:
            self.width = self.fly_frames[0].shape[1]
            self.height = self.fly_frames[0].shape[0]
        else:
            self.width = self.height = 60  # default fallback size

    def load_frames(self, folder_path):
        frames = []
        if not os.path.exists(folder_path):
            print(f"⚠️ Missing folder: {folder_path}")
            return frames
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                path = os.path.join(folder_path, filename)
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is None or img.shape[2] != 4:
                    print(f"⚠️ Bad frame: {path}")
                    continue
                img = cv2.resize(img, (60, 60))
                frames.append(img)
        return frames

    def update(self):
        if not self.dead:
            self.x += self.dx
            self.y += self.dy
            if self.x <= 0 or self.x + self.width >= self.screen_width:
                self.dx *= -1
            if self.y <= 0 or self.y + self.height >= self.screen_height:
                self.dy *= -1
        else:
            if self.dead_frame_index < len(self.dead_frames) - 1:
                self.dead_frame_index += 1
            else:
                self.y += self.fall_speed
                self.fall_speed += 0.5
                if self.y > self.screen_height:
                    self.respawn()

    def draw(self, frame):
        if self.dead:
            img = self.dead_frames[self.dead_frame_index]
        else:
            img = self.fly_frames[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.fly_frames)

        self.overlay_image(frame, img, self.x, self.y)

    def is_hit(self, px, py):
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height and not self.dead

    def hit(self):
        self.dead = True
        self.dead_frame_index = 0
        self.fall_speed = 5

    def overlay_image(self, bg, overlay, x, y):
        h, w = overlay.shape[:2]
        for i in range(h):
            for j in range(w):
                if y + i >= bg.shape[0] or x + j >= bg.shape[1] or x + j < 0 or y + i < 0:
                    continue
                alpha = overlay[i, j, 3] / 255.0
                for c in range(3):
                    bg[y + i, x + j, c] = (
                        (1 - alpha) * bg[y + i, x + j, c] + alpha * overlay[i, j, c]
                    )
