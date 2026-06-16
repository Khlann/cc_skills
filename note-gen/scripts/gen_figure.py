#!/usr/bin/env python3
"""Generate a single figure via OpenRouter (Gemini image model) and save it to a path.

Usage:
    python3 gen_figure.py <output_path> "<prompt>"

Designed for the note-gen skill: robust retries, saves PNG, prints status.
"""
import sys, subprocess, json, base64, time, os

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3-pro-image-preview"
PROXY = "127.0.0.1:7897"


def generate(out_path: str, prompt: str, retries: int = 6) -> bool:
    if not API_KEY:
        print("ERROR: set OPENROUTER_API_KEY environment variable", file=sys.stderr)
        return False
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "max_tokens": 4096,
    })
    for attempt in range(1, retries + 1):
        try:
            r = subprocess.run(
                [
                    "curl", "-s", "--proxy", PROXY, URL,
                    "-H", f"Authorization: Bearer {API_KEY}",
                    "-H", "Content-Type: application/json",
                    "-d", payload,
                ],
                capture_output=True, text=True, timeout=180,
            )
            data = json.loads(r.stdout)
            msg = data.get("choices", [{}])[0].get("message", {})
            images = msg.get("images", [])
            if images:
                url = images[0]["image_url"]["url"]
                if url.startswith("data:"):
                    raw = base64.b64decode(url.split(",", 1)[1])
                else:
                    raw = subprocess.run(
                        ["curl", "-s", "--proxy", PROXY, url],
                        capture_output=True,
                    ).stdout
                with open(out_path, "wb") as f:
                    f.write(raw)
                print(f"OK  {os.path.basename(out_path)}  ({len(raw)//1024} KB)")
                return True
            err = data.get("error", {})
            print(f"[{attempt}/{retries}] no image: {str(err)[:80]}")
            time.sleep(8)
        except Exception as e:  # noqa: BLE001
            print(f"[{attempt}/{retries}] error: {e}")
            time.sleep(8)
    print(f"FAIL {os.path.basename(out_path)}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gen_figure.py <output_path> \"<prompt>\"")
        sys.exit(1)
    ok = generate(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
