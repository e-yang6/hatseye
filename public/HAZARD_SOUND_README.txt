HAZARD SOUND SETUP
==================

The hazard detection feature requires a sound file named 'Hazard.mp3' in this directory.

When a hazard is detected by Roboflow for more than 0.25 seconds, the system will 
automatically play this sound to alert the user.

To set up:
1. Find or create an appropriate alert/warning sound (e.g., beep, alarm, siren)
2. Convert it to MP3 format if needed
3. Name it 'Hazard.mp3'
4. Place it in this directory: /Users/ryan/Desktop/Hatseye2/hatseye/public/

You can use online tools or command-line utilities like ffmpeg to convert audio files:
   ffmpeg -i input_file.wav -b:a 192k Hazard.mp3

Alternative: You can use any royalty-free alert sound from:
- freesound.org
- YouTube Audio Library
- zapsplat.com

The sound should be:
- Short (1-3 seconds ideal)
- Clear and attention-grabbing
- Not too loud or jarring
- MP3 format
