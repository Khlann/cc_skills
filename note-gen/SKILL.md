---
name: note-gen
description: "Generate a polished, illustrated study note as a PDF (with AI figures, equations, and tables) from a topic. Keeps the intermediate LaTeX. Use when the user says \"/note_gen\", \"note-gen\", \"学习笔记\", \"做一份笔记\", \"生成笔记\", or asks for an illustrated explainer/PDF on a concept."
argument-hint: <topic, e.g. 如何理解 flow matching>
allowed-tools: Bash(*), Read, Edit, Write
---

# /note_gen: Illustrated study-note generator

Turn a topic into a polished, **图文并茂** study note: a compiled PDF plus the
intermediate LaTeX source kept for editing. The note weaves together clear prose,
proper equations, tables, and AI-generated explanatory figures.

## ⚠️ Writing language (HARD CONSTRAINT)

**The note body MUST be written in Chinese (中文), with a natural 中英夹杂 style.**
- Write all explanatory prose, intuitions, and transitions in fluent 中文.
- Keep **academic / technical keywords in English** inline, \eg{}
  "我们要学习一个 **velocity field** $v(x,t)$,它定义了从 **prior** 到 **data
  distribution** 的 **transport** 过程。" Do NOT translate established terms like
  *flow matching, velocity field, ODE, score, denoising, transformer, attention,
  loss, gradient, prior, posterior, embedding* — leave them in English.
- Section titles: Chinese with the English term in parentheses where helpful, \eg{}
  `\section{直觉:生成即传输 (Generation as Transport)}`.
- Equations, variable names, and figure labels stay in standard notation/English.
- Figure **captions** are written in the same 中英夹杂 中文 style as the body.
- The abstract / 摘要 is in Chinese.
- The callout boxes keep their English titles (`Key Idea` / `Common Pitfall`) but
  their content is in 中文.

Because the note is in Chinese, **always compile with `xelatex` + `ctex`** (see
the Chinese-aware preamble and compile instructions below), NOT plain pdflatex.

## Output location
Create a fresh working directory under the user's Documents:
```
~/Documents/notes/<slug>/
  ├── note.tex          # main LaTeX source (kept)
  ├── refs.bib          # references, if any (kept)
  ├── figures/          # AI-generated PNGs (kept)
  └── note.pdf          # final compiled PDF
```
`<slug>` = a short kebab-case version of the topic (e.g. `flow-matching`).

## Tools in this skill
- `scripts/gen_figure.py <out.png> "<prompt>"` — generate ONE figure (OpenRouter Gemini, retries).
- `scripts/gen_figures_batch.py <spec.json>` — generate MANY figures from a JSON spec (skips existing).
- `scripts/compile.sh <work_dir> <jobname>` — pdflatex+bibtex+2×pdflatex, reports page count, opens PDF.
- `assets/preamble.tex` — ready-made LaTeX preamble (amsmath, graphicx, tcolorbox callouts, etc.).

The LaTeX toolchain lives at `~/texlive/bin/universal-darwin/` (pdflatex, bibtex).
Image generation uses OpenRouter and **requires the proxy `127.0.0.1:7897`** (already
baked into `gen_figure.py`).

## Workflow

### 1. Plan the note (briefly, in chat)
Decide a structure appropriate to the topic. A good default for a concept explainer:
1. **Intuition / motivation** — why this concept exists, the problem it solves.
2. **Formal definition** — precise statement with notation.
3. **Key equations** — derived or explained step by step.
4. **Worked example / visualization** — concrete illustration.
5. **Connections & contrasts** — how it relates to neighbouring ideas.
6. **Pitfalls & summary** — common misunderstandings, a recap.

Plan **3–5 figures** that genuinely aid understanding (a concept schematic, a
pipeline/flow diagram, a geometric intuition, a comparison chart). Use the
`keybox`/`pitfall` callout environments from the preamble for emphasis.

### 2. Generate figures (run in background, continue writing)
Write a figure spec JSON and launch the batch generator. Each prompt should ask for
a CLEAN ACADEMIC DIAGRAM, white background, labeled, minimalist — the same style
that worked well for technical figures.
```bash
cat > /tmp/figspec.json << 'JSON'
{ "out_dir": "/Users/<you>/Documents/notes/<slug>/figures",
  "figures": [
    {"file": "fig1_intuition.png", "prompt": "Clean academic diagram ... white background, labeled"},
    {"file": "fig2_pipeline.png",  "prompt": "..."}
  ] }
JSON
cd ~/.claude/skills/note-gen/scripts
nohup python3 gen_figures_batch.py /tmp/figspec.json > /tmp/figs.log 2>&1 &
```
While figures generate, write the LaTeX. Create grey **placeholder PNGs** first so
the document compiles even before real figures arrive (see Tips). Swap in the real
figures once `/tmp/figs.log` shows `DONE`.

### 3. Write the LaTeX (in Chinese — see language constraint above)
Start from the **Chinese** preamble (`preamble_zh.tex`, which loads `ctex`), then
write the body in 中文 with English keywords inline. Put figures with
`\includegraphics[width=...]{figures/figN_*.png}` at the points they illuminate.
Use real `equation`/`align` environments, `booktabs` tables, and the callout boxes.
```bash
cp ~/.claude/skills/note-gen/assets/preamble_zh.tex ~/Documents/notes/<slug>/note.tex
# then append \begin{document} ... \end{document} with the 中文 content
```
Prefer the `Edit`/`Write` tools for authoring the `.tex` (avoids shell-escaping pain
with `$`, `\`, `{}`).

### 4. Compile and open (XeLaTeX for Chinese)
```bash
bash ~/.claude/skills/note-gen/scripts/compile.sh ~/Documents/notes/<slug> note xelatex
```
The default engine is already `xelatex` (required for `ctex`/Chinese). This prints
the page count and opens the PDF. If real figures finished after the first compile,
copy them in and recompile.

### 5. Report
Tell the user the PDF path, the kept LaTeX path, page count, and the figure list.

## Tips
- **Placeholders** so it always compiles:
  ```bash
  python3 - << 'PY'
  import struct, zlib, os
  os.makedirs(os.path.expanduser("~/Documents/notes/<slug>/figures"), exist_ok=True)
  def png(p,w=800,h=500):
      ch=lambda t,d:struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
      raw=b"".join(b"\x00"+b"\xe0\xe0\xe0"*w for _ in range(h))
      open(p,"wb").write(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",zlib.compress(raw))+ch(b"IEND",b""))
  for n in ["fig1_intuition","fig2_pipeline"]:
      png(os.path.expanduser(f"~/Documents/notes/<slug>/figures/{n}.png"))
  PY
  ```
- **Missing LaTeX package** (`xxx.sty not found`): install on the fly with
  `~/texlive/bin/universal-darwin/tlmgr install <pkg>`. If tlmgr complains it
  "needs to be updated", first run `~/texlive/bin/universal-darwin/tlmgr update --self`.
  The preamble commonly needs these (install in one shot the first time):
  ```bash
  ~/texlive/bin/universal-darwin/tlmgr install \
    amscls enumitem microtype cite booktabs setspace \
    tcolorbox environ tikzfill pdfcol trimspaces
  ```
  (`amscls` provides `amsthm.sty`; `tcolorbox` needs `environ tikzfill pdfcol`.)
- **Chinese notes**: switch to `xelatex` + `\usepackage{ctex}`; compile with
  `~/texlive/bin/universal-darwin/xelatex` instead of pdflatex.
- **Length**: a focused concept note is typically 4–8 pages. Don't pad; prioritise
  clarity and good figures over page count.
- The API can be briefly overloaded; the scripts already retry. If a figure fails,
  keep its placeholder and note it to the user.
