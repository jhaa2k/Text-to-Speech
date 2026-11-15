# VOX STUDIO — Python Text-to-Speech

Python/Kivy voice workshop targeting Android first, with a desktop fallback.

## Current features
- Multi-line script editor with a 20,000-character guard.
- Voice catalogue from the Android system Text-to-Speech service.
- Adjustable speed, pitch and volume.
- Vocal-direction presets: mythic warrior, ancient god, commander, villain, anime hero, robot, narrator, creature, mentor and more.
- WAV synthesis and preview through the native Android TTS service.
- Android 10+ exports are published to Downloads/VOX Studio through MediaStore.
- Desktop fallback through pyttsx3.
- GitHub Actions workflow for a debug APK.

## Build the Android APK
Open Actions, select Build VOX STUDIO Android APK, then choose Run workflow. Download the artifact named vox-studio-debug-apk after a successful run.

## Voice catalogue and character presets
The voice list comes from speech engines and language packs installed on the device. Install additional voices in Android Text-to-Speech settings to expand it. Presets adjust delivery controls; they do not turn a generic system voice into an actor-quality character performance.

Kratos — Mythic Warrior is a low-pitch, slower vocal-direction starting point, not an imitation or recording of the God of War character or actor. Use only recordings you own or have permission to use. Optional voice-cloning engines require separate consent and model-licence review.

## Desktop
Install Kivy and pyttsx3, then run python main.py. Voice availability depends on the operating system.
