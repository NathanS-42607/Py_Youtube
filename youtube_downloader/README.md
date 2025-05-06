# YouTube Video Downloader

A simple Python script to download YouTube videos in MP4 format.

## Requirements

- Python 3.8 or higher
- Required packages: pytube

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python youtube_downloader.py
```

2. Enter the YouTube video URL when prompted
3. Choose whether to use the default download path (Downloads folder) or specify a custom path
4. The script will download the video in the highest available resolution that includes both audio and video

## Features

- Downloads videos in MP4 format
- Automatic selection of highest quality progressive stream
- Progress tracking during download
- Option to choose custom download location
- Error handling for invalid URLs or network issues
