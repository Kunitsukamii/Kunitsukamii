#!/usr/bin/env python3
"""Build self-contained Neofetch-style SVG profile cards from GitHub avatar."""
import base64
import io
import os
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

USER = "scriptskk"
AVATAR = "https://avatars.githubusercontent.com/u/165056317?v=4"
OUT = Path("assets")
OUT.mkdir(exist_ok=True)
req = urllib.request.Request(AVATAR, headers={"User-Agent": "scriptskk-profile-card"})
with urllib.request.urlopen(req, timeout=30) as response:
    photo = Image.open(io.BytesIO(response.read())).convert("RGB")
# Recreate the image as a visibly pixelated, vertically cropped portrait.
photo = ImageOps.fit(photo, (74, 100), method=Image.Resampling.LANCZOS)
photo = ImageEnhance.Contrast(photo).enhance(1.12)
photo = photo.resize((360, 480), Image.Resampling.NEAREST)
buf = io.BytesIO()
photo.save(buf, format="PNG", optimize=True)
embedded = base64.b64encode(buf.getvalue()).decode("ascii")
rows = [
("OS", "Arch Linux"), ("Uptime", "Always learning"), ("Host", "github.com"),
("Kernel", "Linux"), ("IDE", "VS Code"), ("", ""),
("Languages.Programming", "TypeScript, Python, JS"),
("Languages.Computer", "React, HTML, CSS, Bash"),
("Languages.Real", "Portuguese"), ("", ""),
("Hobbies.Software", "Open Source, CLI Tools"),
("Hobbies.Hardware", "Computers, Keyboards"), ("", ""),
("Contact", ""), ("GitHub", "github.com/scriptskk"),
("Instagram", "instagram.com/script.ts"),
("Projects", "EVA, NEXUS, SLOT36S"), ("", ""),
("GitHub Stats", ""), ("Profile", "github.com/scriptskk"),
("Status", "Building EVA & NEXUS")
]
for dark in (True, False):
    bg, panel, fg, dim, label, value, rule = (
        ("#0d1117", "#171c23", "#d6dae2", "#7b899e", "#819bb5", "#f1f1ef", "#303b48")
        if dark else
        ("#11151b", "#1d2229", "#e0e2e5", "#87909b", "#819bb5", "#f1f1ef", "#38414b")
    )
    items = []
    for i, (key, val) in enumerate(rows):
        y = 62 + i * 22
        if not key:
            continue
        if key in ("Contact", "GitHub Stats"):
            items.append(f'<text x="409" y="{y}" fill="{fg}">- {key}</text><path d="M{540 if key == "Contact" else 586} {y-5}H950" stroke="{dim}" stroke-width=".8" />')
            continue
        items.append(f'<text x="408" y="{y}" fill="{label}">{escape(key)}:</text>')
        # The dotted leaders are kept behind the text so long labels never overlap.
        items.append(f'<path d="M{min(690, 425+len(key)*10)} {y-5}H735" stroke="{dim}" stroke-dasharray="2 6" stroke-width="1"/>')
        items.append(f'<text x="954" y="{y}" fill="{value}" text-anchor="end">{escape(val)}</text>')
    body = "".join(items)
    grid = '<path d="M0 0V480 M5 0V480 M10 0V480" stroke="#0b111a" opacity=".85"/>' if False else ""
    # A 5px repeating dark grid creates the tiny black-outlined cells in the reference.
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="550" viewBox="0 0 1000 550">
<defs>
 <clipPath id="pic"><rect x="16" y="30" width="360" height="480"/></clipPath>
 <pattern id="grid" width="5" height="5" patternUnits="userSpaceOnUse">
  <path d="M0 0H5V5" fill="none" stroke="#080e15" opacity=".95" stroke-width="1.4"/>
 </pattern>
</defs>
<rect width="1000" height="550" rx="15" fill="{bg}"/>
<rect width="1000" height="550" rx="15" fill="{panel}"/>
<image x="16" y="30" width="360" height="480" href="data:image/png;base64,{embedded}" clip-path="url(#pic)" preserveAspectRatio="none"/>
<rect x="16" y="30" width="360" height="480" fill="url(#grid)"/>
<text x="405" y="33" font-family="monospace" font-size="16" fill="{fg}">Eduardo@scriptskk</text>
<path d="M570 28H959" stroke="{dim}" stroke-width="1" stroke-dasharray="4 4"/>
<g font-family="monospace" font-size="15">{body}</g>
<text x="954" y="532" fill="{dim}" font-family="monospace" font-size="11" text-anchor="end">Updated {datetime.now(timezone.utc).strftime("%b %d, %Y")} UTC</text>
</svg>'''
    (OUT / ("profile-dark.svg" if dark else "profile-light.svg")).write_text(svg, encoding="utf-8")
print("Generated self-contained profile SVGs with embedded, pixelated avatar")
