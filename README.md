<div align="center">

# 🎞️ FilmDateStamp

### Authentic Optical Burn-in & Emulsion Halation Engine for ComfyUI

[![Version](https://img.shields.io/badge/version-v1.0.0-ff8c00?style=flat-square)](https://github.com/treeturtlefall-arch/FilmDateStamp/releases)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Node-2ea44f?style=flat-square)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Optical Engine](https://img.shields.io/badge/optics-H%26D_Spectrophotometric-e04000?style=flat-square)](#7-stage-optical-rendering-pipeline)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue?style=flat-square)](LICENSE)
[![Fonts: OFL 1.1](https://img.shields.io/badge/fonts-SIL_OFL_1.1-8a2be2?style=flat-square)](fonts/LICENSE-OFL.txt)

**[🇺🇸 English](README.md)** | **[🇯🇵 日本語 (Japanese)](README_ja.md)**

[Why Optical Burn-in?](#-why-optical-burn-in) •
[Highlight Bleed-Through](#-emulsion-headroom--highlight-bleed-through) •
[8 Curated Fonts](#-8-curated-fonts--visual-size-normalization) •
[12 Style Presets](#-12-era--culture-defining-style-presets) •
[Installation](#-installation) •
[Parameters](#%EF%B8%8F-parameter-reference)

<br>

![FilmDateStamp Hero Banner](assets/hero_banner.png)

*Not a text sticker. A physical simulation of miniature camera LEDs exposing photosensitive silver halide & dye emulsion layers.*

</div>

---

## 🔬 Why Optical Burn-in?

On a real 35mm or disposable film camera, the quartz date stamp is **not printed on top of the photograph**. Instead, a tiny LED or incandescent micro-bulb behind the film gate fires photons directly into the photosensitive emulsion layers from behind or through a micro-lens array.

Conventional digital overlays (`Alpha Blend` or `Screen` + `Gaussian Blur`) look artificial because they lack spectral saturation and emulsion interaction. **FilmDateStamp** replaces flat text blending with a 7-stage physical optical model:

| Optical Property | Standard Text Overlay | Simple Gaussian Glow | **FilmDateStamp (Optical Burn-in)** |
| :--- | :---: | :---: | :---: |
| **Segment Center (Hotspot Ridge)** | ❌ Flat solid color | ❌ Washes out into uniform fog | ✅ **Bleached white-hot filament core** via Euclidean distance ridge |
| **Color Transition** | ❌ Single RGB value | ❌ Monochromatic opacity fade | ✅ **H&D Spectrophotometric Bleaching** (`Red` → `Orange` → `Amber` → `Cream White`) |
| **Light Scattering (PSF)** | ❌ Razor-sharp digital edges | ⚠️ Single-radius blur | ✅ **Multi-Scale PSF** (Narrow Mie forward scatter + wide backplate halation) |
| **Bright Background Behavior** | ❌ Sits on top like a sticker | ⚠️ Artificial bright clip | ✅ **Linear Emulsion Headroom** (Naturally melts into blown-out highlights) |
| **Organic Imperfections** | ❌ 100% uniform computer text | ❌ 100% uniform blur | ✅ **3-Tier Irregularity** (LED jitter, pressure-plate warp, dye-cloud grain) |

![Burn-in vs Overlay Comparison](assets/comparison_burnin_vs_overlay.png)

---

## ☀️ Emulsion Headroom & Highlight Bleed-Through

When photographic film is already heavily exposed by a bright sky or white wall, the silver halide crystals and dye couplers in that region are **already saturated**—leaving zero remaining photosensitive capacity (*Emulsion Headroom*).

FilmDateStamp computes the unexposed capacity of the base image in linear light space ($sRGB \to \text{Linear}$) and applies a physical film shoulder roll-off:

$$I_{\text{exposed}} = \frac{I_{\text{base}} + L_{\text{stamp}}}{1.0 + \max(0,\, I_{\text{base}} + L_{\text{stamp}} - 1.0) \times k_{\text{shoulder}}}$$

- **In Dark Shadows ($I_{\text{base}} \approx 0$)**: Full emulsion headroom is available. The LED stamp burns vividly with rich red-orange halation.
- **In Bright Highlights ($I_{\text{base}} \approx 1$)**: Emulsion headroom is exhausted. The stamp photons blow out and dissolve into pure white—faithfully reproducing how real quartz date stamps vanish into bright skies.

![Highlight Bleed-Through Demo](assets/highlight_bleedthrough_demo.png)

---

## 🔤 8 Curated Fonts & Visual Size Normalization

Includes **4 strictly hardware-accurate in-house TrueType fonts** engineered from scratch to match iconic 1970s–1990s camera modules, **1 clean digital LCD font**, and **3 expressive / speculative fonts**—all licensed under **SIL Open Font License 1.1**.

![Curated Typography Macro Specimens](assets/font_comparison_report_en.png)

| Font Option (`font_type`) | Category | Geometric Specification | Era & Iconic Hardware Inspiration |
| :--- | :--- | :--- | :--- |
| **`FDS_Mechanical_70s (70s Mechanical)`** | ★ In-House Strict | DIN 1451 / JIS industrial engraving, capsule `0`, hooked `1`, slanted dash `'` | **1970s Mechanical Dials**: Canon Canodate E (1970), Canon Datematic (1974), Data Back A |
| **`FDS7_Strict_Compact (80s -7°)`** | ★ In-House Strict | Suwa Seikosha 7-segment geometry ($W/H=0.50$, **$-7.0^\circ$ forward slant**), floating dot `'` | **1980s–90s Compact Golden Era**: Canon Autoboy, Nikon L35AD (Pikaichi), Olympus AF-10 |
| **`FDS7_Strict_SLR (80s 0°)`** | ★ In-House Strict | Upright 7-segment geometry ($W/H=0.50$, **$0.0^\circ$ upright**), floating dot `'` | **1980s SLR Data Backs**: Nikon MF-12 / MF-14 / MF-16, Olympus Recordata, Minolta Data Back G |
| **`FDS_Dot_Strict (90s Dot Matrix)`** | ★ In-House Strict | $5\times7$ grid tall capsule dot matrix ($65\times80$), hollow `0`, 2-dot diagonal `'` | **1990s Disposable & Luxury Compacts**: Fujifilm QuickSnap (*Utsurundesu*), Cardia/Tiara, Ricoh GR1 |
| **`ShareTechMono (LCD Digital)`** | Digital LCD | Clean monospace digital LCD proportions | **Late 90s–2000s Early Digicams**: Early CCD compact cameras, Casio G-SHOCK |
| **`Michroma (Cyber Telemetry)`** | Expressive / Sci-Fi | Ultra-wide geometric euro-stile proportions | **80s–90s Sci-Fi HUD**: Space probe telemetry, *Blade Runner* / *Evangelion* optical readouts |
| **`MochiyPopOne (Y2K Pop)`** | Expressive / Kawaii | Thick rounded mochi-style pop lettering | **Heisei Retro Fancy**: Limited-edition toy cameras, Japanese *Purikura* neon photo booths |
| **`EagleLake (Arcane Script)`** | Expressive / Occult | Calligraphic manuscript ink strokes with organic taper | **Arcane & Dark Fantasy**: Alchemical field ledgers, grimoires, SCP classified anomalies |

> [!TIP]
> **Automatic Visual Size Normalization**: Every font has wildly different internal EM-square metrics and ascender/descender padding. FilmDateStamp automatically normalizes glyph visual height ($4.0\%$ of image short edge at `font_scale = 1.0`) and crops to the **exact lit-pixel bounding box**. You can switch freely between any of the 8 fonts without ever needing to re-adjust `font_scale` or `margin`.

---

## 🎨 12 Era- & Culture-Defining Style Presets

Select a preset from the top **`style_preset`** dropdown to configure typography, spectral palette, exposure intensity, core glow, halation, and regional date formatting in a single click.

![Presets Gallery](assets/presets_showcase_en.png)

### 📸 Authentic Vintage Hardware Presets (9)

| Style Preset | Font Geometry | Spectral Palette | Format & Time | Aesthetic & Cultural Context |
| :--- | :--- | :--- | :--- | :--- |
| **`Japanese Tokyo 90s`** | `FDS7_Strict_Compact` (-7°) | `Amber Classic` | `'YY MM DD` | Everyday 90s Japanese street snapshot; classic golden-amber glow |
| **`Japanese Snap (Disposable)`** | `FDS_Dot_Strict` (5×7 Dot) | `Fuji Orange` | `'YY MM DD HH:MM` | Classic disposable camera (*Utsurundesu*) with vivid orange capsule dots & time |
| **`American West Coast`** | `FDS7_Strict_Compact` (-7°) | `Golden Yellow` | `MM DD 'YY` | Sun-drenched 90s US West Coast road trip with US month-first ordering |
| **`American 80s (Red Quartz)`** | `FDS7_Strict_SLR` (0°) | `Quartz Red` | `MM DD 'YY` | 1980s motel & SLR data back aesthetic with deep red LED halation |
| **`European Classic (Paris/Berlin)`** | `FDS7_Strict_SLR` (0°) | `Amber Classic` | `DD.MM.YY` | Understated European art-photo look with period separators (`DD.MM.YY`) |
| **`Y2K Digicam (Early 2000s)`** | `ShareTechMono` (LCD) | `Golden Yellow` | `'YY MM DD HH:MM` | Early 2000s CCD digital compact camera LCD timestamp |
| **`Compact Fine Dot (Minimal)`** | `FDS_Dot_Strict` (5×7 Dot) | `Fuji Orange` | `'YY MM DD HH:MM` | Refined, crisp micro-dot imprint of 90s titanium luxury compacts |
| **`Monochrome 70s (Canodate E)`** | `FDS_Mechanical_70s` | `Paper White` | `YY MM DD` | 1970s B&W silver gelatin print with clean white optical mask burn |
| **`Vintage 70s Color (Datematic)`** | `FDS_Mechanical_70s` | `Bulb Warm Ivory` | `'YY MM DD` | 1970s warm incandescent micro-bulb exposure on vintage color film |

### ✨ Expressive / Speculative Presets (3)

| Style Preset | Font Geometry | Spectral Palette | Format & Time | Aesthetic & Cultural Context |
| :--- | :--- | :--- | :--- | :--- |
| **`Cyber Telemetry (80s Sci-Fi)`** | `Michroma` | `Cyber Green` | `'YY MM DD HH:MM:SS` | High-precision green laser telemetry HUD (automatically includes `:SS` seconds) |
| **`Y2K Pop (Heisei Fancy)`** | `MochiyPopOne` | `Neo Pink` | `'YY MM DD HH:MM` | Sweet magenta Mie scattering inspired by Heisei retro Purikura booths |
| **`Arcane Occult (Crimson Script)`** | `EagleLake` | `Crimson Red` | `'YY MM DD` | Cursed crimson ink halation for dark fantasy, occult, or SCP photography |

---

## 🧬 7-Stage Optical Rendering Pipeline

<details>
<summary><b>Click to expand technical details of the physical rendering engine</b></summary>

<br>

```text
                       [ Exposure Energy E Distribution ]
                     Saturated Filament Core (Hotspot Ridge)
                                 ┌───────────┐
                                 │           │
                     Narrow-Angle Forward Mie Scattering
                         ┌───────┴───────────┴───────┐
                         │                           │
               Wide-Angle Base & Pressure-Plate Reflection Halation
               ┌─────────┴───────────────────────────┴─────────┐
            ───┴───────────────────────────────────────────────┴─── (Film Emulsion Layer)
```

1. **Stage 1 — Euclidean Distance Ridge & Optical Blooming**: Extracts the medial axis of each stroke to model the intense hotspot directly above the LED die, rounding sharp digital corners via slit diffraction.
2. **Stage 2 — Macro Irregularity (Element Power Jitter)**: Simulates ±10% manufacturing tolerances between individual 7-segment bars/dots and subtle illumination falloff across the projection lens.
3. **Stage 3 — Multi-Scale Anisotropic PSF Scattering**: Convolves energy across narrow-angle forward Mie scattering (amber body), wide-angle film-base reflection (red halation), and ultra-wide veiling glare, with slight elliptical anisotropy.
4. **Stage 4 — Meso Irregularity (Pressure Plate Warping)**: Modulates halation fringes with low-frequency Perlin-like pressure-plate contact clouds and domain-warped displacement fields.
5. **Stage 5 — Micro Irregularity (Silver Halide Grain & Dye Clumping)**: Injects photosensitive threshold noise that dissolves only the faint outer halation skirt into organic dye clouds while keeping the saturated core smooth.
6. **Stage 6 — H&D Spectrophotometric Bleaching**: Evaluates $I = 1.0 - \exp(-E^\gamma)$ per spectral channel. Low energy excites only the long-wavelength red layer; medium energy recruits green (forming orange/amber); high core energy saturates blue, bleaching organically into warm cream-white.
7. **Stage 7 — Linear Emulsion Headroom Composite**: Converts the base image to linear RGB, scales stamp energy by remaining emulsion headroom ($1.0 - L_{\text{base}}^{1.35} \times 0.72$), applies soft-shoulder roll-off, and converts back to sRGB.

</details>

---

## 📦 Installation

### Method 1: ComfyUI-Manager (Recommended)
Open **ComfyUI-Manager**, search for **`Film Date Stamp`** (or `FilmDateStamp`), and click **Install**.

### Method 2: Comfy-CLI
```bash
comfy node install comfyui-film-date-stamp
```

### Method 3: Manual Git Clone
Clone this repository into your `ComfyUI/custom_nodes` directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/treeturtlefall-arch/FilmDateStamp.git
```
*(No extra pip packages required—uses standard `torch`, `numpy`, and `Pillow` bundled with ComfyUI.)*

---

## 🚀 Quick Start & Workflow Integration

1. **Add the Node**: Right-click on the canvas → `image` → `film` → **`Film Date Stamp (Optical Burn-in)`**.
2. **Pick a Vibe**: Choose a preset from **`style_preset`** at the top of the node.
3. **Fine-Tune Freely**: Tweaking any parameter (`font_type`, `preset_color`, `halation`, etc.) automatically switches `style_preset` to `Custom` via the bundled frontend extension.
4. **Sample Workflow**: Drag & drop [`workflows/film_date_stamp_workflow.json`](workflows/film_date_stamp_workflow.json) directly into ComfyUI.

### 💡 Smart Date Input (`date_string`)
No complicated mode switches—just type what you want into `date_string`:
- **Custom Text**: Type any date directly, e.g., `'98 12 24` or `'95 08 15 14:30`.
- **Current System Date**: Type `"auto"`, `"today"`, or `"now"` to format the current runtime date/time using `date_format` and `show_time`.
- **Reproducible Vintage Random**: Type `"random"` to generate a random vintage date (1985–2005) deterministically controlled by `seed`.

### 🔌 Leveraging the 3 Output Slots
- **`image` (`IMAGE`)**: The final composite image with physically burned-in date stamp.
- **`mask` (`MASK`)**: High-precision `[B, H, W]` emission mask (`1.0` at the core, smooth falloff across the halation skirt). Ideal for feeding into downstream **Film Grain** nodes (to add extra grain specifically to the exposed dye cloud) or **Inpaint** nodes.
- **`date_text` (`STRING`)**: The exact resolved string rendered onto the frame (e.g., `'98 12 24 18:30`). Connect this to `SaveImage` filename prefixes or image captioning pipelines.

---

## ⚙️ Parameter Reference

| Parameter | Type | Default | Range / Options | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`style_preset`** | `COMBO` | `Custom` | `Custom` + 12 Presets | Master style selector. Auto-populates font, color, exposure, and date format. |
| **`font_type`** | `COMBO` | `FDS7_Strict_Compact (80s -7°)` | 8 Curated Fonts | Light-emitting element typography (with automatic visual size normalization). |
| **`preset_color`** | `COMBO` | `Amber Classic` | 9 Spectral Palettes | Physical emission spectrum (6 authentic hardware + 3 expressive palettes). |
| **`exposure_intensity`** | `FLOAT` | `1.00` | `0.00` – `2.00` | Master photon exposure energy delivered to the film emulsion. |
| **`core_glow`** | `FLOAT` | `1.00` | `0.00` – `2.00` | Intensity of the bleached white-hot filament core ridge. |
| **`halation`** | `FLOAT` | `1.00` | `0.00` – `3.00` | Spread radius and intensity of multi-scale red emulsion halation. |
| **`date_string`** | `STRING` | `'98 12 24` | Literal / `"auto"` / `"random"` | Literal text to burn in, or dynamic keyword (`"auto"`, `"today"`, `"random"`). |
| **`date_format`** | `COMBO` | `'YY MM DD` | 9 Regional Formats | Date ordering and delimiter syntax used for dynamic/preset dates. |
| **`show_time`** | `BOOLEAN` | `False` | `True` / `False` | Appends `HH:MM` timestamp (or `HH:MM:SS` for Cyber Telemetry). |
| **`position`** | `COMBO` | `bottom_right` | `bottom_right`, `bottom_left`, `top_right`, `top_left` | Corner placement with tight lit-pixel bounding box alignment. |
| **`font_scale`** | `FLOAT` | `1.00` | `0.50` – `2.50` | Stamp size multiplier relative to the image short edge ($4.0\%$ base). |
| **`margin`** | `FLOAT` | `1.00` | `0.00` – `3.00` | Isotropic distance from the frame edge (~5:4 horizontal/vertical ratio). |
| **`irregularity`** *(opt)* | `FLOAT` | `1.00` | `0.00` – `2.00` | Strength of the 3-tier organic irregularity (`0.0` = clean, `1.0` = authentic). |
| **`seed`** *(opt)* | `INT` | `0` | `0` – `2^64-1` | Deterministic seed for `"random"` date generation and organic noise patterns. |

<details>
<summary><b>🌈 Spectral Color Palettes & Regional Date Formats (Click to expand)</b></summary>

### Spectral Color Palettes (`preset_color`)

| Palette Name | Core RGB | Body RGB | Halation RGB | Character |
| :--- | :---: | :---: | :---: | :--- |
| **`Amber Classic`** | `(255, 255, 210)` | `(255, 130, 20)` | `(240, 45, 0)` | Signature 90s compact camera golden amber |
| **`Quartz Red`** | `(255, 230, 220)` | `(255, 40, 20)` | `(200, 10, 0)` | Deep 1980s red LED quartz data back |
| **`Fuji Orange`** | `(255, 250, 190)` | `(255, 115, 20)` | `(250, 60, 10)` | Vivid warm orange of disposable cameras (*QuickSnap*) |
| **`Golden Yellow`** | `(255, 255, 240)` | `(255, 185, 30)` | `(240, 110, 0)` | Bright yellow-amber common in late-90s / Y2K compacts |
| **`Bulb Warm Ivory`** | `(255, 250, 232)` | `(255, 242, 204)` | `(255, 214, 138)` | 1970s incandescent micro-bulb warm ivory (*Datematic*) |
| **`Paper White (Monochrome)`** | `(248, 246, 240)` | `(245, 242, 234)` | `(235, 232, 224)` | 1970s B&W silver print unexposed paper white (*Canodate E*) |
| **`Cyber Green`** *(Expressive)* | `(230, 255, 230)` | `(40, 255, 80)` | `(0, 180, 40)` | Sci-fi space telemetry / Wong Kar-wai neon green |
| **`Neo Pink`** *(Expressive)* | `(255, 235, 248)` | `(255, 70, 170)` | `(230, 25, 115)` | Heisei retro Purikura & toy camera neon magenta |
| **`Crimson Red`** *(Expressive)* | `(255, 235, 225)` | `(235, 25, 35)` | `(185, 5, 15)` | Dark occult / alchemical crimson blood halation |

### Regional Date Formats (`date_format`)

| Format Syntax | Output (`show_time=False`) | Output (`show_time=True`) | Regional Convention |
| :--- | :--- | :--- | :--- |
| **`'YY MM DD`** | `'98 12 24` | `'98 12 24 18:30` | Japan / East Asia standard (most iconic) |
| **`YY MM DD`** | `98 12 24` | `98 12 24 18:30` | No-apostrophe 1970s mechanical standard |
| **`MM DD 'YY`** | `12 24 '98` | `12 24 '98 18:30` | North America (US) standard |
| **`DD MM 'YY`** | `24 12 '98` | `24 12 '98 18:30` | Europe / UK / Commonwealth standard |
| **`DD.MM.YY`** | `24.12.98` | `24.12.98 18:30` | German / Continental European period-separated |
| **`YY-MM-DD`** | `98-12-24` | `98-12-24 18:30` | Hyphen-separated compact |
| **`YY.MM.DD`** | `98.12.24` | `98.12.24 18:30` | Dot-separated compact |
| **`YYYY MM DD`** | `1998 12 24` | `1998 12 24 18:30` | 4-digit year (Y2K-compliant modules) |
| **`YYYY-MM-DD`** | `1998-12-24` | `1998-12-24 18:30` | ISO 8601 4-digit hyphenated |

</details>

---

## 📄 License

- **Source Code**: [MIT License](LICENSE)
- **Bundled Fonts (`fonts/*.ttf`)**: [SIL Open Font License 1.1](fonts/LICENSE-OFL.txt) (including the 4 in-house `FDS*` strict hardware fonts and 4 bundled OFL fonts).
