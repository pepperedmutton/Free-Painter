import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import os

MAX_WIDTH = 1000
MAX_HEIGHT = 800

class MosaicEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Mosaic Drawer")

        file_path = filedialog.askopenfilename(title="Select Image")
        if not file_path:
            exit()
        self.file_path = os.path.abspath(file_path)

        self.load_folder()

        selected_filename = os.path.basename(self.file_path)
        for i, path in enumerate(self.all_images):
            if os.path.basename(path) == selected_filename:
                self.current_index = i
                break
        else:
            return

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.block_size = tk.IntVar(value=10)
        scale_frame = tk.Frame(root)
        scale_frame.pack(pady=5)
        tk.Label(scale_frame, text="Mosaic Strength:").pack(side="left")
        tk.Scale(scale_frame, from_=5, to=100, resolution=5,
                 orient="horizontal", variable=self.block_size).pack(side="left")

        self.edited = False
        self.load_image()

        self.canvas.bind("<B1-Motion>", self.draw_mosaic)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="← Back", command=self.back).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save & Next →", command=self.save_and_next).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Quit", command=root.quit).pack(side="left", padx=5)

    def load_folder(self):
        folder = os.path.dirname(self.file_path)
        supported = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        self.all_images = sorted([
            os.path.abspath(os.path.join(folder, f))
            for f in os.listdir(folder)
            if f.lower().endswith(supported)
        ])
        if not self.all_images:
            exit()

    def load_image(self):
        self.original_image = Image.open(self.all_images[self.current_index]).convert("RGB")
        self.image = self.original_image.copy()
        self.display_image = self.resize_image(self.image)
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.edited = False

    def resize_image(self, img):
        ratio = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height, 1)
        self.scale = ratio
        return img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

    def draw_mosaic(self, event):
        size = self.block_size.get()
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        bx = (x // size) * size
        by = (y // size) * size

        block = self.image.crop((bx, by, bx + size, by + size))
        avg_color = block.resize((1, 1), resample=Image.BILINEAR).getpixel((0, 0))

        draw = ImageDraw.Draw(self.image)
        draw.rectangle([bx, by, bx + size, by + size], fill=avg_color)

        self.display_image = self.resize_image(self.image)
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.edited = True

    def save_current_image(self):
        if not self.edited:
            return
        clean = Image.new("RGB", self.image.size)
        clean.paste(self.image)
        clean.save(self.all_images[self.current_index])

    def save_and_next(self):
        self.save_current_image()
        self.current_index += 1
        if self.current_index >= len(self.all_images):
            self.root.quit()
        else:
            self.load_image()

    def back(self):
        self.save_current_image()
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = 0
        self.load_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = MosaicEditor(root)
    root.mainloop()
