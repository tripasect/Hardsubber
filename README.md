# Hardsubber
<img width="128" height="128" alt="icon_128x128@2x" src="https://github.com/user-attachments/assets/57ab3113-1d60-4671-aa7d-d78fac96660f" />
<img width="960" alt="CleanShot 2026-02-10 at 13 41 59@2x" src="https://github.com/user-attachments/assets/70492b68-6b83-458f-9224-351f06b7f873" />
<br>
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
