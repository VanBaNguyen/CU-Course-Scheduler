#!/usr/bin/env bash
# UNTESTED
# setup.sh ─ quick bootstrap for the course‑scheduler project
# • Creates terms/{fall.txt,winter.txt,summer.txt}
# • Sets up Python venv in ./venv
# • Installs matplotlib inside that venv
#
# Usage:
#   chmod +x setup.sh     # (one‑time)
#   ./setup.sh

set -e  # abort on first error

echo "🔧  Creating terms directory + empty term files ..."
mkdir -p terms
for f in fall.txt winter.txt summer.txt; do
  if [[ -e "terms/$f" ]]; then
    echo "    – terms/$f already exists, leaving it as‑is"
  else
    touch "terms/$f"
    echo "    – created terms/$f"
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
echo "   terms/fall.txt, winter.txt, summer.txt"
echo "-------------------------------------------------------"
