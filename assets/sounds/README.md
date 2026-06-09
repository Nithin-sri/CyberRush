# CyberRush — Sound Assets

Drop sound files into this folder using **these exact filenames**. The game will run fine even when some files are missing — the SoundManager checks for each file and silently skips ones it can't load. This means you can add sounds one at a time as you find ones you like.

## Required filenames

| Filename        | When it plays                          | Suggested length |
| --------------- | -------------------------------------- | ---------------- |
| `click.wav`     | Any UI button click                    | < 0.5 s          |
| `correct.wav`   | Player collects a green (safe) block   | < 1.0 s          |
| `wrong.wav`     | Player hits a red (phishing) block     | < 1.0 s          |
| `gameover.wav`  | Lives reach 0                          | 1–3 s            |
| `music.ogg`     | Looping background music               | 30 s – 3 min     |

> `.wav` and `.ogg` both work. For background music prefer `.ogg` (much smaller file size).
> If you only have `.mp3` files, rename or convert them — pygame's mixer is more reliable with `.wav` and `.ogg`.

## Safe, 100% free, legal sources

All of the sites below let you use sounds in games without paying or asking permission. Always double-check the license shown next to each individual file.

1. **Pixabay Sound Effects** — https://pixabay.com/sound-effects/
   - Free for commercial use, no attribution required.
   - Search terms: `ui click`, `correct chime`, `error buzzer`, `game over`, `cyberpunk loop`.

2. **Mixkit** — https://mixkit.co/free-sound-effects/
   - Free for commercial use, no attribution required.
   - Good categories: *Game*, *Interface*, *Music – Electronic*.

3. **Freesound.org** — https://freesound.org/
   - Requires a free account. Use the **License filter** in the sidebar and pick **"Creative Commons 0"** to get files with no restrictions.

4. **OpenGameArt.org** — https://opengameart.org/art-search?field_art_type_tid%5B%5D=13
   - Filter by **CC0** license. Made specifically for game devs.

## Safety tips when downloading

- Always download from the official site (above), never from third-party "free download" sites.
- After downloading, scan the file or check its extension — make sure `click.wav` really is `.wav` and not `click.wav.exe`.
- Keep files small: under ~200 KB for short SFX, under ~3 MB for music. Big files make the game slow to load.
- Rename the file to **exactly** match the table above (case-sensitive on Linux/macOS).

## What happens if a file is missing?

Nothing breaks. You'll just hear silence for that one event. So you can start with just `click.wav` to test, then add the others later.
