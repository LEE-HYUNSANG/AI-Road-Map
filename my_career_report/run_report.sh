#!/usr/bin/env bash
set -e
pip install -r requirements.txt
npm install --silent
python generate_report.py
echo "Generated HTML at dist/report.html and PDF at dist/report.pdf"
