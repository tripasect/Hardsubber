#!/usr/bin/env python3
import re

# Read SRT
with open('sub.srt', 'r', encoding='utf-8') as f:
    srt_content = f.read()

# Create ASS file with styling
ass_header = """[Script Info]
Title: Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 800

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,SF Arabic MPV,56,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Parse SRT and convert to ASS
def srt_time_to_ass(srt_time):
    match = re.match(r'(\d+):(\d+):(\d+),(\d+)', srt_time)
    if match:
        h, m, s, ms = match.groups()
        centiseconds = int(ms) // 10
        return f'{h}:{m}:{s}.{centiseconds:02d}'
    return srt_time

blocks = re.split(r'\n\n+', srt_content.strip())
events = []

for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) >= 3:
        timing = lines[1]
        text = '\n'.join(lines[2:])
        # Remove HTML tags but keep content
        text = re.sub(r'<[^>]+>', '', text)
        # Convert newlines to ASS format line breaks
        text = text.replace('\n', '\\N')
        
        times = timing.split(' --> ')
        if len(times) == 2:
            start = srt_time_to_ass(times[0].strip())
            end = srt_time_to_ass(times[1].strip())
            events.append(f'Dialogue: 0,{start},{end},Default,,0,0,0,,{text}')

with open('sub.ass', 'w', encoding='utf-8') as f:
    f.write(ass_header)
    f.write('\n'.join(events))

print('Created sub.ass with bold font styling')
