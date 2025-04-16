# Whisper Subtitle Generator (Nederlands)

Een gebruiksvriendelijke desktop applicatie om automatisch Nederlandse ondertitels te genereren voor video's met behulp van OpenAI's Whisper spraakherkenningsmodel.

## Functies

- Automatische spraakherkenning met behulp van OpenAI's Whisper AI
- Gebruiksvriendelijke interface om bestanden te selecteren en ondertitelingsopties in te stellen
- Ondersteuning voor verschillende videoformaten (mp4, avi, mov, mkv, webm, etc.)
- Genereert ondertitels in SRT-formaat met de extensie `.nl.srt`
- Keuze uit verschillende modelgroottes voor verschillende behoeften (compromis tussen nauwkeurigheid en snelheid)
- Real-time voortgangsindicator en logvenster

## Vereisten

- Python 3.8 of hoger
- FFmpeg (moet in het systeempad beschikbaar zijn)
- OpenAI Whisper
- De volgende Python-pakketten:
  - tkinter
  - whisper
  - ffmpeg-python

## Installatie

1. Clone of download deze repository:
   ```
   git clone https://github.com/gebruikersnaam/whisper-subtitle-generator.git
   cd whisper-subtitle-generator
   ```

2. Installeer de benodigde afhankelijkheden:
   ```
   pip install git+https://github.com/openai/whisper.git
   pip install ffmpeg-python
   ```

3. Zorg ervoor dat FFmpeg is geïnstalleerd op je systeem:
   - **Windows**: Download van [ffmpeg.org](https://ffmpeg.org/download.html) en voeg toe aan PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` of equivalent voor je distributie

## Gebruik

1. Start de applicatie:
   ```
   python whisper_subtitle_generator.py
   ```

2. Klik op "Bladeren..." om een videobestand te selecteren

3. Kies de gewenste modelgrootte:
   - **tiny**: Snelste, maar minst nauwkeurige
   - **base**: Sneller, redelijke nauwkeurigheid
   - **small**: Goede balans tussen snelheid en nauwkeurigheid
   - **medium**: Nauwkeuriger, maar langzamer
   - **large**: Meest nauwkeurig, maar traagste

4. (Optioneel) Kies een uitvoermap, of laat het programma de ondertitels naast de video opslaan

5. Klik op "Start" en wacht tot het proces is voltooid

6. De ondertitels worden opgeslagen als `[video-naam].nl.srt` in de gekozen map

## Modelgrootte en prestaties

| Model  | Grootte | Geheugengebruik | Relatieve snelheid | Nauwkeurigheid |
|--------|---------|----------------|-------------------|---------------|
| tiny   | 39M     | ~1GB           | ~32x              | Basis         |
| base   | 74M     | ~1GB           | ~16x              | Redelijk      |
| small  | 244M    | ~2GB           | ~6x               | Goed          |
| medium | 769M    | ~5GB           | ~2x               | Zeer goed     |
| large  | 1550M   | ~10GB          | 1x                | Uitstekend    |

## Probleemoplossing

### FFmpeg kon niet worden gevonden
Zorg ervoor dat FFmpeg correct is geïnstalleerd en beschikbaar is in het systeempad (PATH). Je kunt dit testen door `ffmpeg -version` in de opdrachtprompt uit te voeren.

### Onvoldoende GPU/VRAM
Het bericht "FP16 is not supported on CPU; using FP32 instead" betekent dat je Whisper op de CPU draait in plaats van op een GPU. Dit is normaal als je geen compatibele GPU hebt. Het transcriberen zal langzamer zijn, maar werkt nog steeds.

### Geheugenfouten
Als je een "out of memory" fout krijgt, probeer dan een kleiner model (tiny, base of small).

## Licentie

Dit project is gelicenseerd onder de MIT-licentie - zie het [LICENSE](LICENSE) bestand voor details.

## Erkenningen

- Deze applicatie maakt gebruik van [OpenAI's Whisper](https://github.com/openai/whisper) voor spraakherkenning
- UI gebouwd met Python's Tkinter
