# Hardsubber

Burn subtitles into videos with a simple GUI. No dependencies required.

## Download

Get the latest release from the [Releases](../../releases) page.

## Features

- Simple interface for burning subtitles into videos
- Supports SRT and ASS subtitle formats
- Real-time progress tracking
- Completely self-contained (ffmpeg bundled)

## Usage

1. Download and open Hardsubber.app
2. Select your video file
3. Select your subtitle file
4. Click Start

Output is saved as `[original_name]_subtitled.mp4`

## Building from Source

```bash
./build.sh
```

Requires Python 3 and creates `dist/Hardsubber.app`
