"""Clean per-product SVG images — icon only, no duplicate text (title lives in HTML card)."""

import hashlib
import re
from pathlib import Path
from xml.sax.saxutils import escape

THEMES = {
    "electronics": ("#2563eb", "#dbeafe", "#f8fafc"),
    "clothing": ("#be123c", "#fce7f3", "#fafafa"),
    "home": ("#b45309", "#ffedd5", "#fafafa"),
    "books": ("#047857", "#d1fae5", "#fafafa"),
    "sports": ("#c2410c", "#ffedd5", "#fafafa"),
    "beauty": ("#7c3aed", "#ede9fe", "#fafafa"),
}

ANGLE_LABELS = ["Front", "Side", "Detail", "Pack"]

ICON_PATHS = {
    "earbud": '<circle cx="250" cy="250" r="32" fill="{a}"/><circle cx="250" cy="250" r="18" fill="#fff" opacity=".4"/>',
    "watch": '<rect x="200" y="195" width="100" height="120" rx="22" fill="{a}"/><rect x="218" y="218" width="64" height="74" rx="10" fill="#fff" opacity=".45"/>',
    "keyboard": '<rect x="155" y="225" width="190" height="62" rx="10" fill="{a}"/><rect x="172" y="240" width="22" height="14" rx="3" fill="#fff" opacity=".5"/><rect x="202" y="240" width="22" height="14" rx="3" fill="#fff" opacity=".5"/><rect x="232" y="240" width="22" height="14" rx="3" fill="#fff" opacity=".5"/>',
    "shirt": '<path d="M250 155 L320 195 L305 220 L305 345 L195 345 L195 220 L180 195 Z" fill="{a}"/>',
    "shoe": '<ellipse cx="250" cy="285" rx="95" ry="38" fill="{a}"/><path d="M160 265 Q250 205 340 265" fill="none" stroke="#fff" stroke-width="5" opacity=".35"/>',
    "mug": '<rect x="195" y="195" width="110" height="125" rx="12" fill="{a}"/><path d="M305 215 h30 q22 0 22 22 v45 q0 22 -22 22 h-30" fill="none" stroke="{a}" stroke-width="12"/>',
    "book": '<rect x="175" y="175" width="60" height="165" rx="8" fill="{a}" opacity=".85"/><rect x="245" y="160" width="68" height="180" rx="8" fill="{a}"/>',
    "ball": '<circle cx="250" cy="255" r="82" fill="none" stroke="{a}" stroke-width="14"/><path d="M168 255 Q250 175 332 255" fill="none" stroke="{a}" stroke-width="7" opacity=".55"/>',
    "bottle": '<rect x="215" y="165" width="70" height="145" rx="16" fill="{a}"/><ellipse cx="250" cy="325" rx="52" ry="58" fill="{a}" opacity=".9"/><rect x="232" y="148" width="36" height="28" rx="6" fill="{a}"/>',
    "default": '<circle cx="250" cy="250" r="78" fill="{a}" opacity=".18"/><circle cx="250" cy="250" r="52" fill="{a}" opacity=".55"/>',
}


def _shift_hex(hex_color: str, amount: int) -> str:
    r = max(0, min(255, int(hex_color[1:3], 16) + amount))
    g = max(0, min(255, int(hex_color[3:5], 16) + amount))
    b = max(0, min(255, int(hex_color[5:7], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def _stable_seed(slug: str, variant: int = 0) -> int:
    return int(hashlib.md5(f"{slug}:{variant}".encode()).hexdigest(), 16)


def _pick_icon_key(name: str) -> str:
    text = name.lower()
    if re.search(r"earbud|headphone", text):
        return "earbud"
    if re.search(r"watch", text):
        return "watch"
    if re.search(r"keyboard|laptop", text):
        return "keyboard"
    if re.search(r"shirt|jacket|tee|hoodie", text):
        return "shirt"
    if re.search(r"sneaker|shoe|shorts", text):
        return "shoe"
    if re.search(r"mug|pan", text):
        return "mug"
    if re.search(r"book", text):
        return "book"
    if re.search(r"football|cricket|yoga|ball", text):
        return "ball"
    if re.search(r"wash|moistur|serum|oil|balm|lotion|sunscreen", text):
        return "bottle"
    return "default"


def build_product_svg(name: str, category_slug: str, variant: int = 0) -> str:
    cat = category_slug if category_slug in THEMES else "home"
    accent, accent_light, bg = THEMES[cat]
    seed = _stable_seed(name, variant)
    accent = _shift_hex(accent, (seed % 21) - 10)
    accent_light = _shift_hex(accent_light, (seed % 13) - 6)
    scale = 0.92 + (seed % 8) / 100
    rotate = ((seed // 7) % 9) - 4 + (variant * 3)
    icon_key = _pick_icon_key(name)
    shapes = ICON_PATHS[icon_key].format(a=accent)

    safe_name = escape(name)

    badge = ""
    if variant:
        label = ANGLE_LABELS[(variant - 1) % len(ANGLE_LABELS)]
        badge = (
            f'<rect x="24" y="24" width="96" height="30" rx="6" fill="{accent}"/>'
            f'<text x="72" y="44" text-anchor="middle" font-family="system-ui,Arial,sans-serif" '
            f'font-size="12" font-weight="600" fill="#fff">{escape(label)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500" role="img" aria-label="{safe_name}">
  <defs>
    <linearGradient id="bg-{seed}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="{bg}"/>
    </linearGradient>
    <radialGradient id="glow-{seed}" cx="50%" cy="45%" r="50%">
      <stop offset="0%" stop-color="{accent_light}" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{accent_light}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="500" height="500" fill="url(#bg-{seed})"/>
  <circle cx="250" cy="250" r="165" fill="url(#glow-{seed})"/>
  {badge}
  <g transform="translate(250 250) scale({scale}) rotate({rotate}) translate(-250 -250)">
    {shapes}
  </g>
</svg>"""


def write_product_images(base_dir: Path, slug: str, name: str, category_slug: str) -> int:
    out_dir = base_dir / "items"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    main_path = out_dir / f"{slug}.svg"
    main_path.write_text(build_product_svg(name, category_slug, 0), encoding="utf-8")
    count += 1
    for i in range(1, 5):
        path = out_dir / f"{slug}-v{i}.svg"
        path.write_text(build_product_svg(name, category_slug, i), encoding="utf-8")
        count += 1
    return count
