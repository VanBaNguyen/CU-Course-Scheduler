#!/usr/bin/env bash
#
# setup.sh ─ quick bootstrap for the course‑scheduler project
# • Creates term_files/{fall.txt,winter.txt,summer.txt}
# • Sets up Python venv in ./venv
# • Installs matplotlib inside that venv
#
# Usage:
#   chmod +x setup.sh     # (one‑time)
#   ./setup.sh

set -e  # abort on first error

echo "🔧  Creating term_files directory + empty term files ..."
mkdir -p term_files
for f in fall.txt winter.txt summer.txt; do
  if [[ -e "term_files/$f" ]]; then
    echo "    – term_files/$f already exists, leaving it as‑is"
  else
    touch "term_files/$f"
    echo "    – created term_files/$f"
  fi
done

echo ""
echo "🐍  Setting up Python virtual environment (./venv) ..."
if [[ ! -d venv ]]; then
  python3 -m venv venv
  echo "    – venv created"
else
  echo "    – venv already exists, skipping creation"
fi

# shellcheck disable=SC1091
source venv/bin/activate
echo "    – venv activated"

echo ""
echo "📦  Installing required packages ..."
python -m pip install --upgrade pip >/dev/null
python -m pip install matplotlib >/dev/null

echo ""
echo "✅  Done!"
echo "-------------------------------------------------------"
echo "To start using the environment in a new shell session:"
echo "   source venv/bin/activate"
echo ""
echo "Place your course listings in:"
echo "   term_files/fall.txt, winter.txt, summer.txt"
echo "-------------------------------------------------------"
