#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

for tool in python3 node ffmpeg ffprobe actionlint git; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done
if ! node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)'; then
  echo 'Node 22 or newer is required for the Taste toolkit tests.' >&2
  exit 1
fi
encoders=$(ffmpeg -hide_banner -encoders 2>/dev/null)
for codec in libx264 aac; do
  if ! printf '%s\n' "$encoders" | awk -v codec="$codec" '$2 == codec { found=1 } END { exit !found }'; then
    echo "Missing required FFmpeg encoder: $codec" >&2
    exit 1
  fi
done

echo 'Checking workflows and whitespace'
actionlint -shellcheck= .github/workflows/*.yml
git diff --check
git diff --cached --check
git show --format= --check HEAD
if [[ -n "${CHECK_BASE_SHA:-}" && "$CHECK_BASE_SHA" != 0000000000000000000000000000000000000000 ]]; then
  if git cat-file -e "${CHECK_BASE_SHA}^{commit}" 2>/dev/null; then
    git diff --check "$CHECK_BASE_SHA" HEAD
  else
    echo 'Previous revision is unavailable; whitespace check covers HEAD only.' >&2
  fi
fi

echo 'Checking skills'
python3 scripts/skills.py check
echo 'Running unit tests (conditional skips are reported below)'
python3 -m unittest discover -s tests -v
