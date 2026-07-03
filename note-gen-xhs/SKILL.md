---
name: note-gen-xhs
description: "Generate a polished Chinese technical study note plus Xiaohongshu-ready assets: PDF, LaTeX, AI figures, rendered page PNGs under pages/, pages.zip, AIGC-style cover, and xhs-content.md. Also known as note_gen_xhs. Use when the user asks for /note_gen_xhs, note-gen-xhs, 小红书笔记, 生成笔记并配封面/文案, or wants a technical PDF packaged for Xiaohongshu/Notion/AirDrop."
argument-hint: <topic or URL, e.g. 如何理解 DPO>
allowed-tools: Bash(*), Read, Edit, Write
---

# note-gen-xhs

Create a complete technical-note publishing bundle:

```text
~/Documents/notes/<slug>/
  note.tex
  refs.bib
  figures/
  note.pdf                  # compile artifact
  <slug>-note.pdf           # user-facing PDF
  pages/                    # PDF pages rendered as PNG
  pages.zip
  pages-xhs-1280x1706-72dpi/ # when Xiaohongshu page images are requested
  pages-xhs-1280x1706-72dpi.zip
  xhs-cover-aigc-refined.png
  xhs-cover-aigc-refined.jpg
  xhs-content.md
```

## Non-negotiables

- Write the note body in Chinese with natural 中英夹杂 style.
- Keep established technical terms in English: `loss`, `policy`, `reward model`,
  `diffusion`, `action chunk`, `preference pair`, `reference model`, etc.
- Every note must include formulas, diagrams/charts/tables, and code/pseudocode.
- Use `xelatex` + `ctex` for Chinese notes.
- The final PDF must be title-prefixed: `<slug>-note.pdf`, not only `note.pdf`.
- Render PDF pages into the concrete note directory: `~/Documents/notes/<slug>/pages/`.
- Also create `pages.zip` in the same note directory.
- For cover images, avoid always using `手撕 XX`. Prefer varied hooks such as:
  `为什么 DPO 不需要 PPO？`, `偏好对如何变成 Loss`, `从噪声到动作`,
  `Action Chunk 到底解决什么`, `一张图看懂 ...`.

## Workflow

### 1. Research and plan

If the topic includes a URL, paper, current library, or anything likely to drift,
open/check authoritative sources first. Then plan:

- 4-8 page note outline.
- 3-5 figures that genuinely explain the concept.
- The core formula(s).
- One table/comparison chart.
- One compact code/pseudocode block.
- Xiaohongshu hook/title direction.

### 2. Create workspace

```bash
mkdir -p ~/Documents/notes/<slug>/figures
cp ~/.codex/skills/note-gen-xhs/assets/preamble_zh.tex ~/Documents/notes/<slug>/note.tex
```

If installed elsewhere, resolve the skill directory and copy `assets/preamble_zh.tex`
from this skill.

### 3. Generate high-quality figures

Prefer the built-in `image_gen` tool for important diagrams. Use AIGC for visual
quality, but keep exact formulas in LaTeX whenever possible. For generated diagrams:

- Ask for clean academic/NeurIPS-style educational diagrams.
- Use minimal labels; avoid long formulas inside generated images.
- Save final selected images to `~/Documents/notes/<slug>/figures/`.
- Never leave note-used images only under `~/.codex/generated_images/`.

Good prompt pattern:

```text
Create a high-quality academic diagram explaining <concept>.
Clean white or premium dark background, crisp vector-like shapes, strong visual
metaphor, minimal large English labels, no watermark. Avoid dense tiny math.
```

### 4. Write LaTeX

Use the Chinese preamble. The document must contain:

- Abstract in Chinese.
- Core equations in `equation`/`align`.
- AI figures or diagrams with captions.
- At least one `booktabs` table.
- At least one `lstlisting` code/pseudocode block.
- `Key Idea` and/or `Common Pitfall` callout boxes when useful.

### 5. Compile

```bash
bash ~/.codex/skills/note-gen-xhs/scripts/compile.sh ~/Documents/notes/<slug> note xelatex
```

This creates/updates `<slug>-note.pdf` and opens it.

### 6. Render pages

Always render the final PDF into the note directory:

```bash
bash ~/.codex/skills/note-gen-xhs/scripts/render_pages.sh ~/Documents/notes/<slug> <slug>-note.pdf
```

This writes:

- `~/Documents/notes/<slug>/pages/<slug>-page-1.png`, etc.
- `~/Documents/notes/<slug>/pages.zip`

### 7. Optional Xiaohongshu page images

When the user asks for 小红书尺寸 or upload-ready page images:

```bash
python3 ~/.codex/skills/note-gen-xhs/scripts/resize_xhs_pages.py \
  --src ~/Documents/notes/<slug>/pages \
  --out ~/Documents/notes/<slug>/pages-xhs-1280x1706-72dpi
```

Target size is **1280 x 1706 px** with **72 DPI** metadata. Preserve full page
content by fitting proportionally on a white canvas; do not crop or stretch.

### 8. Generate Xiaohongshu cover

Use a two-step approach for quality and text reliability:

1. Generate an AIGC background with `image_gen` and ask for **no text**.
2. Overlay exact title/formula/checklist/code locally:

```bash
python3 ~/.codex/skills/note-gen-xhs/scripts/overlay_xhs_cover.py \
  --background ~/Documents/notes/<slug>/figures/<cover-bg>.png \
  --out-dir ~/Documents/notes/<slug> \
  --title "为什么 DPO|不需要 PPO？" \
  --kicker "从 RLHF 到 Direct Optimization" \
  --formula "Delta = beta[(log pi - log pi_ref)_w - (log pi - log pi_ref)_l]" \
  --checklist "不用 reward model？;log-ratio 怎么来？;beta 到底管什么？" \
  --code "pi_w - ref_w;-(pi_l - ref_l);loss = -logsigmoid"
```

The script writes `xhs-cover-aigc-refined.png` and `.jpg`.

### 9. Write Xiaohongshu content

Create `xhs-content.md` in the note directory with:

- `# 小红书标题`
- `# 小红书正文`
- `# 标签`
- `# 封面文案方向`

Tone: natural, not list-heavy, not too AI-ish. Mention why the concept is worth
learning, what the note covers, and who it is useful for. Add relevant hashtags.

### 10. Report

Report these paths:

- `<slug>-note.pdf`
- `note.tex`
- `figures/`
- `pages/`
- `pages.zip`
- `pages-xhs-1280x1706-72dpi/` if created
- `xhs-cover-aigc-refined.png`
- `xhs-content.md`

