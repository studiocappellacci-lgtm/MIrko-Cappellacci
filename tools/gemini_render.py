#!/usr/bin/env python3
"""Render architettonici con Gemini (generazione/modifica immagini).

Uso:
  python tools/gemini_render.py "prompt" -o out.png
  python tools/gemini_render.py "rendi fotorealistico, luce del tramonto" -i schizzo.png -o render.png
Opzioni: -m modello (default gemini-2.5-flash-image), più -i per più immagini di riferimento.
La chiave si legge da GEMINI_API_KEY; nel cloud la inietta il proxy (basta un valore fittizio).
"""
import argparse, os, sys
from google import genai
from google.genai import types
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("prompt")
p.add_argument("-i", "--image", action="append", default=[])
p.add_argument("-o", "--out", default="render.png")
p.add_argument("-m", "--model", default=os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"))
a = p.parse_args()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "proxy-injected"))
contents = [a.prompt] + [Image.open(f) for f in a.image]
resp = client.models.generate_content(
    model=a.model, contents=contents,
    config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]))

n = 0
for part in resp.candidates[0].content.parts:
    if part.inline_data:
        base, ext = os.path.splitext(a.out)
        path = a.out if n == 0 else f"{base}_{n}{ext}"
        open(path, "wb").write(part.inline_data.data); print("salvato:", path); n += 1
    elif part.text:
        print(part.text)
sys.exit(0 if n else 1)
