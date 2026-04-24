# APOD Linux

Set NASA's Astronomy Picture of the Day (APOD) as your Linux desktop wallpaper automatically.

## Features

- Fetches the latest APOD image from NASA
- Supports multiple Linux desktop environments:
  - GNOME
  - KDE Plasma
  - Xfce
  - Cinnamon
- Auto-detection of the current desktop environment
- Verbose logging for debugging

## Installation

### Prerequisites

- Python 3.14 or higher
- `uv` package manager

### Setup

1. Clone the repository:
```bash
git clone git@github.com:varadhodiyil/apod-linux.git
cd apod-linux
```

2. Install dependencies:
```bash
uv sync
```

## Usage

### Set today's APOD as wallpaper



```bash
uv run python apod_fetcher.py
```


## How it works

1. Fetches the APOD page from NASA
2. Parses the HTML to extract the high-resolution image URL
3. Downloads the image
4. Sets it as the wallpaper using the appropriate command for your desktop environment

## Supported Image Formats

- JPEG
- PNG
- BMP
- GIF
- WebP

