import os
import io
import cv2
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from multiprocessing import Pool, cpu_count

from PIL import Image
import pytesseract
import whisper

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

import docx
import PyPDF2
import fitz  # PyMuPDF
from pptx import Presentation

from transformers import BlipProcessor, BlipForConditionalGeneration
import threading
import json
import xxhash

CACHE_FILE = "cache.json"

# ===== CONFIG =====
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ⚠️ caricare modelli globali (una sola volta per processo)
whisper_model = None
blip_processor = None
blip_model = None


def init_models():
    global whisper_model, blip_processor, blip_model

    if whisper_model is None:
        print("[INIT] Loading Whisper...")
        whisper_model = whisper.load_model("base")

    if blip_processor is None:
        print("[INIT] Loading BLIP...")
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


# ===== VIDEO =====

def extract_text_from_video(path):
    try:
        temp_audio = f"temp_{datetime.now().timestamp()}.wav"

        clip = VideoFileClip(path)
        if clip.audio is None:
            return "[NO AUDIO TRACK]"

        clip.audio.write_audiofile(temp_audio,logger=None)

        text = whisper_model.transcribe(temp_audio)["text"]

        os.remove(temp_audio)
        return text

    except Exception as e:
        return f"[VIDEO ERROR] {e}"


def extract_video_frames(path, num_frames=2):  # ↓ ridotto per velocità
    frames = []

    cap = cv2.VideoCapture(path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        return frames

    indices = np.linspace(0, total_frames - 1, num=num_frames, dtype=int)

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)

    cap.release()
    return frames


def describe_frame(frame):
    try:
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        inputs = blip_processor(image, return_tensors="pt")
        outputs = blip_model.generate(**inputs)
        return blip_processor.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        return f"[FRAME ERROR] {e}"


# ===== IMMAGINI =====

def generate_image_description(image):
    try:
        inputs = blip_processor(image, return_tensors="pt")
        outputs = blip_model.generate(**inputs)
        return blip_processor.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        return f"[BLIP ERROR] {e}"


def analyze_image_bytes(img_bytes):
    try:
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        ocr_text = pytesseract.image_to_string(image)

        caption = generate_image_description(image)

        return f"[Image OCR]\n{ocr_text.strip()}\n\n[Image Caption]\n{caption.strip()}"

    except Exception as e:
        return f"[IMAGE ERROR] {e}"


# ===== IMMAGINI DA DOCUMENTI =====

def extract_images_from_pdf(pdf_path):
    images = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = doc.extract_image(xref)
                images.append(base_image["image"])
    except:
        pass
    return images


def extract_images_from_docx(docx_path):
    images = []
    try:
        document = docx.Document(docx_path)
        for rel in document.part.rels.values():
            if "image" in rel.target_ref:
                images.append(rel.target_part.blob)
    except:
        pass
    return images


def extract_images_from_pptx(pptx_path):
    images = []
    try:
        presentation = Presentation(pptx_path)
        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "image"):
                    images.append(shape.image.blob)
    except:
        pass
    return images


# ===== DOCUMENTI =====

def extract_text_from_pdf(path):
    text = ""

    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except:
        pass

    for img in extract_images_from_pdf(path):
        text += "\n\n" + analyze_image_bytes(img)

    return text


def extract_text_from_docx(path):
    text = ""

    try:
        doc = docx.Document(path)
        for p in doc.paragraphs:
            text += p.text + "\n"
    except:
        pass

    for img in extract_images_from_docx(path):
        text += "\n\n" + analyze_image_bytes(img)

    return text


def extract_text_from_pptx(path):
    text = ""

    try:
        pres = Presentation(path)
        for slide in pres.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
    except:
        pass

    for img in extract_images_from_pptx(path):
        text += "\n\n" + analyze_image_bytes(img)

    return text


# ===== ROUTER =====

def extract_text(path):
    init_models()

    ext = os.path.splitext(path)[1].lower().strip().replace(".", "")
    print(f"[DEBUG] {path} -> {ext}")

    if ext in ["jpg", "jpeg", "png"]:
        with open(path, "rb") as f:
            return analyze_image_bytes(f.read())

    elif ext in ["mp3", "wav","m4a"]:
        return whisper_model.transcribe(path)["text"]

    elif ext in ["mp4", "avi", "mov"]:
        text = extract_text_from_video(path)

        # commenta se vuoi più velocità
        frames = extract_video_frames(path)
        for f in frames:
            text += "\n\n[Frame]\n" + describe_frame(f)

        return text

    elif ext == "pdf":
        return extract_text_from_pdf(path)

    elif ext == "docx":
        return extract_text_from_docx(path)

    elif ext == "pptx":
        return extract_text_from_pptx(path)

    else:
        return f"[UNSUPPORTED FILE: {ext}]"


# ===== MULTIPROCESS =====

def process_single(args):
    file_path, output_dir = args

    try:
        filename = os.path.basename(file_path)
        name = os.path.splitext(filename)[0]
        out_path = os.path.join(output_dir, name + ".txt")

        if os.path.exists(out_path):
            return f"SKIP {filename}"

        text = extract_text(file_path)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        return f"OK {filename}"

    except Exception as e:
        return f"ERROR {file_path}: {e}"


def run_pipeline(input_dir, output_dir):
    files = []

    for root, _, filenames in os.walk(input_dir):
        for f in filenames:
            files.append(os.path.join(root, f))

    print(f"[INFO] Totale file: {len(files)}")

    with Pool(max(cpu_count() - 1, 1)) as p:
        results = p.map(process_single, [(f, output_dir) for f in files])

    for r in results:
        print(r)

# ===== CACHE =====

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def file_hash(path):
    h = xxhash.xxh64()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


# ===== FILTER =====

EXT_GROUPS = {
    "immagini": ["jpg", "jpeg", "png"],
    "audio": ["mp3", "wav","m4a"],
    "video": ["mp4", "avi", "mov"],
    "documenti": ["pdf", "docx", "pptx"]
}


# ===== GUI =====

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("RAGForge by Nanni Bassetti")

        self.input_dir = ""
        self.output_dir = ""
        self.use_cache = tk.BooleanVar(value=True)

        self.cache_cb = tk.Checkbutton(
            root,
            text="Esegui solo su file nuovi (usa cache)",
            variable=self.use_cache
        )

        self.cache_cb.pack(pady=5)

        self.cache = load_cache()

        # INPUT
        self.input_label = tk.Label(root, text="Input: -")
        self.input_label.pack()
        tk.Button(root, text="Seleziona INPUT", command=self.select_input).pack()

        # OUTPUT
        self.output_label = tk.Label(root, text="Output: -")
        self.output_label.pack()
        tk.Button(root, text="Seleziona OUTPUT", command=self.select_output).pack()

        # FILTRI
        self.filters = {}
        tk.Label(root, text="Filtri:").pack()

        for key in EXT_GROUPS:
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(root, text=key, variable=var)
            cb.pack(anchor="w")
            self.filters[key] = var

        # COUNT
        self.count_label = tk.Label(root, text="File da processare: 0")
        self.count_label.pack()

        # PROGRESS BAR
        self.progress = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress.pack(pady=10)

        # LOG
        self.log_area = tk.Text(root, height=15, width=80)
        self.log_area.pack()

        # BOTTONI
        tk.Button(root, text="AVVIA", command=self.start).pack(pady=5)
        tk.Button(root, text="EXIT", command=root.quit).pack()

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def select_input(self):
        self.input_dir = filedialog.askdirectory()
        self.input_label.config(text=f"Input: {self.input_dir}")
        self.update_file_count()

    def select_output(self):
        self.output_dir = filedialog.askdirectory()
        self.output_label.config(text=f"Output: {self.output_dir}")

    def get_active_extensions(self):
        exts = []
        for k, var in self.filters.items():
            if var.get():
                exts.extend(EXT_GROUPS[k])
        return exts

    def update_file_count(self):
        if not self.input_dir:
            return

        exts = self.get_active_extensions()
        count = 0

        for root_dir, _, files in os.walk(self.input_dir):
            for f in files:
                ext = os.path.splitext(f)[1].lower().replace(".", "")
                if ext in exts:
                    count += 1

        self.count_label.config(text=f"File da processare: {count}")

    def start(self):
        if not self.input_dir or not self.output_dir:
            messagebox.showerror("Errore", "Seleziona cartelle")
            return

        threading.Thread(target=self.run_pipeline_gui).start()

    def run_pipeline_gui(self):
        exts = self.get_active_extensions()

        files = []
        for root_dir, _, filenames in os.walk(self.input_dir):
            for f in filenames:
                ext = os.path.splitext(f)[1].lower().replace(".", "")
                if ext in exts:
                    files.append(os.path.join(root_dir, f))

        total = len(files)
        self.progress["maximum"] = total

        self.log(f"Totale file: {total}")

        for i, file_path in enumerate(files, 1):
            filename = os.path.basename(file_path)
            name = os.path.splitext(filename)[0]
            out_path = os.path.join(self.output_dir, name + ".txt")

            try:
                h = file_hash(file_path)

                if self.use_cache.get():
                    if file_path in self.cache and self.cache[file_path] == h:
                        self.log(f"SKIP CACHE {filename}")
                        self.progress["value"] = i
                        continue

                text = extract_text(file_path)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)

                self.cache[file_path] = h

                self.log(f"OK {filename}")

            except Exception as e:
                self.log(f"ERROR {filename}: {e}")

            self.progress["value"] = i
            self.root.update_idletasks()

        save_cache(self.cache)

        messagebox.showinfo("Completato", "Estrazione completata!")

# ===== ENTRY POINT =====

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()