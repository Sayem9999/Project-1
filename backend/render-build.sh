#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading FFmpeg static build..."
mkdir -p tools
mkdir -p storage
# Download reliable static build for Linux (amd64)
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o tools/ffmpeg.tar.xz
tar -xvf tools/ffmpeg.tar.xz -C tools --strip-components=1
rm tools/ffmpeg.tar.xz

echo "FFmpeg installed to ./tools/ffmpeg"
./tools/ffmpeg -version
