import os
from PIL import Image, ImageDraw, ImageFont

icons_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
os.makedirs(icons_dir, exist_ok=True)

# 1. SVG Favicon
favicon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A" />
      <stop offset="100%" stop-color="#0D9488" />
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="24" fill="url(#grad)" />
  <path d="M50 20 L20 45 L26 45 L26 76 L44 76 L44 56 L56 56 L56 76 L74 76 L74 45 L80 45 Z" fill="#F8FAFC" />
  <circle cx="50" cy="40" r="5" fill="#10B981" />
  <path d="M48 66 L52 66" stroke="#0D9488" stroke-width="2" stroke-linecap="round"/>
</svg>"""

with open(os.path.join(icons_dir, 'favicon.svg'), 'w', encoding='utf-8') as f:
    f.write(favicon_svg)

# 2. Property Placeholder SVG
placeholder_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">
  <rect width="800" height="600" fill="#1E293B"/>
  <defs>
    <linearGradient id="pgrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#334155" />
      <stop offset="100%" stop-color="#1E293B" />
    </linearGradient>
  </defs>
  <rect x="20" y="20" width="760" height="560" rx="16" fill="url(#pgrad)" stroke="#475569" stroke-width="2" stroke-dasharray="8 8"/>
  <path d="M400 200 L260 320 L290 320 L290 420 L370 420 L370 340 L430 340 L430 420 L510 420 L510 320 L540 320 Z" fill="#64748B" opacity="0.8"/>
  <circle cx="400" cy="275" r="16" fill="#0D9488" />
  <text x="400" y="470" font-family="sans-serif" font-size="24" font-weight="600" fill="#94A3B8" text-anchor="middle">HOMETRACE PROPERTY PHOTOGRAPH</text>
  <text x="400" y="505" font-family="sans-serif" font-size="16" fill="#64748B" text-anchor="middle">Nigeria Verified Real Estate Listing</text>
</svg>"""

with open(os.path.join(icons_dir, 'property-placeholder.svg'), 'w', encoding='utf-8') as f:
    f.write(placeholder_svg)

# 3. Generate 192x192 and 512x512 PNGs
def generate_png_icon(size, filename):
    img = Image.new('RGBA', (size, size), color=(15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Draw rounded gradient-like background & border
    margin = int(size * 0.08)
    radius = int(size * 0.22)
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, fill=(13, 148, 136, 255))

    # Inner house roof
    center_x = size // 2
    roof_top = int(size * 0.28)
    roof_left = int(size * 0.24)
    roof_right = int(size * 0.76)
    roof_bottom = int(size * 0.50)

    draw.polygon([
        (center_x, roof_top),
        (roof_left, roof_bottom),
        (roof_right, roof_bottom)
    ], fill=(248, 250, 252, 255))

    # Body
    body_left = int(size * 0.30)
    body_right = int(size * 0.70)
    body_top = roof_bottom
    body_bottom = int(size * 0.75)

    draw.rectangle([body_left, body_top, body_right, body_bottom], fill=(248, 250, 252, 255))

    # Door
    door_w = int(size * 0.14)
    door_h = int(size * 0.20)
    door_left = center_x - (door_w // 2)
    draw.rectangle([door_left, body_bottom - door_h, door_left + door_w, body_bottom], fill=(15, 23, 42, 255))

    # Emerald focal accent
    draw.ellipse([center_x - int(size * 0.04), int(size * 0.42), center_x + int(size * 0.04), int(size * 0.50)], fill=(16, 185, 129, 255))

    img.save(os.path.join(icons_dir, filename), 'PNG')
    print(f"Generated {filename}")

generate_png_icon(192, 'icon-192x192.png')
generate_png_icon(512, 'icon-512x512.png')
print("PWA icons generation complete!")
