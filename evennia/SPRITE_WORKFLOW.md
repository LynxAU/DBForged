# Sprite Workflow (DBForged)

This is a practical workflow for creating and iterating on sprites/animation assets with the least pain, while preserving clean alpha and consistent output for the webclient/game.

## Goals

- Keep sprites clean and reusable (transparent PNGs, consistent dimensions).
- Separate "painting" work from "sheet packing / export" work.
- Make iteration fast (preview quickly, export predictably).
- Avoid accidental quality loss (bad scaling, wrong export format, alpha issues).

## Recommended Tool Roles

Use each tool for what it is best at instead of forcing one app to do everything.

## 1. Drawing / Pixel Editing

Best for:
- Hand-pixeling characters/effects
- Cleaning silhouettes
- Palette work
- Frame-by-frame sprite touchups

Recommended tools:
- Aseprite (best overall for pixel animation workflow)
- LibreSprite (Aseprite-like free option)
- Piskel (browser-based quick edits)

Use when:
- You need control over individual pixels
- You are animating frame-by-frame
- You want onion-skinning and timeline tools

Tips:
- Keep a fixed canvas size per animation set (for example `64x64`, `96x96`, etc.)
- Use nearest-neighbor scaling only for pixel art
- Export as `PNG` with transparency

## 2. Painting / Concept / High-Res Cleanup

Best for:
- Painted effects
- Character portraits / key art
- High-res source renders you later downscale
- Glow passes / VFX source textures

Recommended tools:
- Krita (excellent free painting tool)
- GIMP (general image editing + alpha-safe exports)
- Photoshop (if available)

Use when:
- The asset is not strict pixel art
- You need brushes, layers, masks, blending modes

Tips:
- Keep source layered files (`.kra`, `.psd`, `.xcf`)
- Export production assets as `RGBA PNG`
- Check alpha after export (reopen and verify transparency is real)

## 3. Vector / Logo / UI Marks

Best for:
- Logos
- UI icons
- Clean scalable shapes
- Typography-heavy marks

Recommended tools:
- Inkscape (free vector)
- Illustrator (if available)

Use when:
- You need crisp shapes at multiple sizes
- You want to generate multiple resolutions cleanly

Tips:
- Keep vector master (`.svg`)
- Export transparent PNGs at target sizes
- For logos in web UI, crop transparent padding tightly after export

## 4. Sheet Packing / Atlas Generation

Best for:
- Combining many frames into one spritesheet
- Atlas metadata generation (JSON)
- Trimming and packing efficiently

Recommended tools:
- TexturePacker (great workflow, many export formats)
- Free Texture Packer / alternatives
- Custom scripts (when format is simple and fixed)

Use when:
- You have frame folders and need runtime-friendly atlases

Tips:
- Keep original frames separate; packed sheets are build artifacts
- Enable trimming, but keep metadata offsets
- Use consistent naming (`idle_0001`, `run_0001`, etc.)

## 5. Upscaling / Cleanup (Optional)

Best for:
- Prototyping from low-res placeholders
- AI-assisted cleanup (use cautiously)
- Batch resizing to test scales

Recommended tools:
- Waifu2x / ESRGAN variants (for experiments)
- ImageMagick / Pillow scripts (batch resizes)

Use when:
- You are exploring, not finalizing

Tips:
- Do not rely on AI upscales as final pixel art
- Always hand-clean important frames after upscale

## 6. Runtime / Game Integration (This Repo)

Current practical rules:
- Webclient logos/UI art: use transparent `RGBA PNG`
- Keep assets in predictable static paths (for example `evennia/web/static/ui/`)
- Expect browser caching; use cache-busters when swapping art rapidly

For DBForged specifically:
- Prefer real images in the webclient UI (HTML/CSS)
- Avoid forcing complex art into terminal ANSI unless you accept heavy artifacts

## Suggested End-to-End Pipeline

## A. For character sprites / animation

1. Draw and animate frames in Aseprite/LibreSprite.
2. Export individual transparent PNG frames.
3. Pack into an atlas with TexturePacker (or your chosen packer).
4. Export metadata JSON.
5. Drop atlas + metadata into the webclient static asset path.
6. Test in-game and adjust anchors/offsets.

## B. For logos / UI marks

1. Create in vector tool (Inkscape/Illustrator) or layered raster editor.
2. Export transparent PNG at high resolution.
3. Crop transparent padding tightly.
4. Place in `evennia/web/static/ui/`.
5. Update webclient UI to reference it (cache-bust during iteration).

## C. For VFX overlays

1. Paint elements in Krita/GIMP (glows, bursts, energy effects).
2. Export transparent PNG sequences.
3. Pack into atlases if needed.
4. Test blend/look in the webclient at real size.

## Naming / File Hygiene

- Use descriptive names:
  - `goku_idle_0001.png`
  - `goku_run_0012.png`
  - `beam_charge_loop_0004.png`
  - `dbforged_logo_fullcolor_alpha.png`
- Keep source files separate from exported game assets:
  - `art/source/...`
  - `evennia/web/static/ui/...` (runtime assets)

## Export Rules (Important)

- Format: `PNG`
- Color: `RGBA`
- Transparency: enabled
- Scaling: nearest-neighbor for pixel art, bilinear/lanczos for painted/logo assets
- Never use JPEG for sprites/logos with transparency

## Fast Iteration Tips

- Keep one "master" source asset and export variants from it
- Use versioned filenames or cache-busting query params in webclient during iteration
- Test assets in the actual target size/context (not just image viewer)

## Common Failure Modes

- Image looks opaque after export: exported as `RGB` instead of `RGBA`
- Edges look bad: exported against a matte background, then alpha removed
- Looks wrong in-game but fine in viewer: browser cache / wrong file path / wrong asset referenced
- Sprite looks blurry: wrong scaling filter (linear on pixel art)

## Practical Recommendation for DBForged (Short Version)

- Pixel characters/animations: Aseprite (or LibreSprite)
- Painted effects / general edits: Krita or GIMP
- Logos/UI marks: Inkscape (+ PNG export)
- Atlas packing: TexturePacker
- Repo integration: export final transparent PNGs into `evennia/web/static/ui/`

