# Whisper Subtitle Generator

Een gebruiksvriendelijke desktop applicatie om automatisch ondertitels te genereren voor video's met behulp van OpenAI's Whisper spraakherkenningsmodel. Ondersteunt batch-verwerking voor meerdere videobestanden en maakt gebruik van GPU-versnelling wanneer beschikbaar.

![image](https://github.com/user-attachments/assets/4eb01e1a-09bf-41b7-a303-9d5c4860f828)

| Hardware | Relatieve snelheid | Opmerkingen |
|----------|-------------------|------------|
| GPU (NVIDIA GTX 1070 of beter) | 5-10x sneller | Aanbevolen voor grotere bestanden en batch verwerking |
| CPU (moderne multi-core) | Basissnelheid | Werkt op alle computers maar veel langzamer |

Een video van 10 minuten verwerken met het "small" model:
- Met GPU (GTX 1070): ~1-2 minuten
- Met CPU (moderne i7/Ryzen): ~7-15 minuten

**Tip**: Als je een compatibele NVIDIA GPU hebt zoals de GTX 1070, zorg dan dat je de GPU-modus gebruikt voor veel snellere verwerking!# Whisper Subtitle Generator

Een gebruiksvriendelijke desktop applicatie om automatisch ondertitels te genereren voor video's met behulp van OpenAI's Whisper spraakherkenningsmodel. Ondersteunt batch-verwerking voor meerdere videobestanden, maakt gebruik van GPU-versnelling wanneer beschikbaar, en kan automatisch tekst voor slechthorenden verwijderen.

## Functies

- Automatische spraakherkenning met behulp van OpenAI's Whisper AI
- GPU-versnelling voor snellere verwerking (5-10x sneller dan CPU)
- Batch-verwerking van meerdere videobestanden tegelijk
- Automatische verwijdering van tekst voor slechthorenden (optioneel)
- Gebruiksvriendelijke interface om bestanden te selecteren en ondertitelingsopties in te stellen
- Ondersteuning voor verschillende videoformaten (mp4, avi, mov, mkv, webm, etc.)
- Genereert ondertitels in SRT-formaat met de extensie overeenkomstig de gekozen taal (bijv. `.nl.srt`)
- Ondersteuning voor meerdere talen (Nederlands, Engels, Duits, Frans, enz.)
- Automatische bestandsnaamgeving met de juiste taalcode (bijv. video.nl.srt voor Nederlands, video.en.srt voor Engels)
- Real-time voortgangsindicator en logvenster

## Vereisten

- Python 3.8 of hoger
- FFmpeg (moet in het systeempad beschikbaar zijn)
- OpenAI Whisper
- PyTorch (bij voorkeur met CUDA-ondersteuning voor GPU-versnelling)
- NVIDIA GPU met actuele drivers (voor GPU-versnelling)
- De volgende Python-pakketten:
  - tkinter
  - whisper
  - torch
  - ffmpeg-python

## Installatie

1. Clone of download deze repository:
   ```
   git clone https://github.com/vxddavi1979/whisper-subtitle-generator.git
   cd whisper-subtitle-generator
   ```

2. Installeer OpenAI Whisper en FFmpeg Python:
   ```
   pip install git+https://github.com/openai/whisper.git
   pip install ffmpeg-python
   ```

3. Installeer PyTorch met CUDA-ondersteuning (voor GPU-versnelling):
   ```
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   
   Je kunt controleren of PyTorch correct is geïnstalleerd met CUDA-ondersteuning door dit script uit te voeren:
   ```python
   import torch
   print(f"PyTorch versie: {torch.__version__}")
   print(f"CUDA beschikbaar: {torch.cuda.is_available()}")
   if torch.cuda.is_available():
       print(f"CUDA versie: {torch.version.cuda}")
       print(f"GPU: {torch.cuda.get_device_name(0)}")
   ```

4. Zorg ervoor dat FFmpeg is geïnstalleerd op je systeem:
   - **Windows**: Download van [ffmpeg.org](https://ffmpeg.org/download.html) en voeg toe aan PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` of equivalent voor je distributie

5. Zorg voor actuele NVIDIA drivers:
   - Download en installeer de nieuwste drivers van [nvidia.com/Download](https://www.nvidia.com/Download/index.aspx)
   - De CUDA Toolkit (versie 11.8 aanbevolen) kan worden gedownload van [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)

## Gebruik

1. Start de applicatie:
   ```
   python whisper_subtitle_generator.py
   ```

2. Video's toevoegen:
   - Klik op "Toevoegen..." om één of meerdere videobestanden te selecteren
   - Gebruik "Verwijderen" om geselecteerde bestanden te verwijderen
   - Gebruik "Alles verwijderen" om de lijst leeg te maken

3. Kies verwerking op GPU of CPU:
   - GPU: Veel sneller, aanbevolen als je een NVIDIA GPU hebt
   - CPU: Langzamer, maar werkt op alle computers

4. Kies de gewenste modelgrootte:
   - **tiny**: Snelste, maar minst nauwkeurige
   - **base**: Sneller, redelijke nauwkeurigheid
   - **small**: Goede balans tussen snelheid en nauwkeurigheid
   - **medium**: Nauwkeuriger, maar langzamer
   - **large**: Meest nauwkeurig, maar traagste

5. Selecteer de gewenste taal voor je ondertitels:
   - Nederlands (nl)
   - Engels (en)
   - Duits (de)
   - Frans (fr)
   - Spaans (es)
   - En vele andere talen

6. Kies of je tekst voor slechthorenden wilt verwijderen:
   - Vink de optie "Tekst voor slechthorenden verwijderen" aan om beschrijvingen van geluiden, sprekerinformatie en tekst tussen haakjes automatisch te verwijderen

7. (Optioneel) Kies een uitvoermap, of laat het programma de ondertitels naast de video opslaan

8. Klik op "Start" en wacht tot het proces is voltooid
   - De voortgang wordt getoond voor elk bestand
   - Je kunt het proces pauzeren door op "Stop" te klikken

9. De ondertitels worden opgeslagen als `[video-naam].[taalcode].srt` in de gekozen map (bijv. video.nl.srt voor Nederlands) om de lijst leeg te maken

3. Kies de gewenste modelgrootte:
   - **tiny**: Snelste, maar minst nauwkeurige
   - **base**: Sneller, redelijke nauwkeurigheid
   - **small**: Goede balans tussen snelheid en nauwkeurigheid
   - **medium**: Nauwkeuriger, maar langzamer
   - **large**: Meest nauwkeurig, maar traagste

4. Selecteer de gewenste taal voor je ondertitels:
   - Nederlands (nl)
   - Engels (en)
   - Duits (de)
   - Frans (fr)
   - Spaans (es)
   - En vele andere talen

5. (Optioneel) Kies een uitvoermap, of laat het programma de ondertitels naast de video opslaan

6. Klik op "Start" en wacht tot het proces is voltooid
   - De voortgang wordt getoond voor elk bestand
   - Je kunt het proces pauzeren door op "Stop" te klikken

7. De ondertitels worden opgeslagen als `[video-naam].[taalcode].srt` in de gekozen map (bijv. video.nl.srt voor Nederlands, video.en.srt voor Engels)

## Ondertitelreiniging

De Whisper Subtitle Generator bevat een krachtige functie om tekst voor slechthorenden automatisch te verwijderen uit de ondertitels. Dit zorgt voor schonere ondertitels die alleen de gesproken tekst bevatten, zonder afleidende elementen.

De reinigingsfunctie verwijdert:
- Tekst tussen haakjes, bijv. [lacht], (muziek speelt), {deurbel}
- Geluidseffecten zoals *lacht*, #applaus#
- Tekst in hoofdletters voor een dubbele punt (sprekers), bijv. "JOHN:" wordt verwijderd, alleen de tekst blijft over
- Volledige regels in hoofdletters (vaak geluidseffecten of andere aanwijzingen)

Deze functie kan worden in- of uitgeschakeld via de checkbox "Tekst voor slechthorenden verwijderen" in de interface.

## Modelgroottes en prestaties

| Model  | Bestandsgrootte | Geheugengebruik | Relatieve snelheid | Nauwkeurigheid |
|--------|----------------|----------------|-------------------|---------------|
| tiny   | 39M     | ~1GB           | ~32x              | Basis         |
| base   | 74M     | ~1GB           | ~16x              | Redelijk      |
| small  | 244M    | ~2GB           | ~6x               | Goed          |
| medium | 769M    | ~5GB           | ~2x               | Zeer goed     |
| large  | 1550M   | ~10GB          | 1x                | Uitstekend    |

De aanbevolen modelgrootte is "small" voor een goede balans tussen snelheid en nauwkeurigheid. Als je een goede GPU hebt, kun je ook het "medium" model overwegen.

## Bestandsnaamgeving

De generator zorgt ervoor dat de ondertitelbestanden worden opgeslagen met de volledige originele bestandsnaam van de video gevolgd door de taalcode, bijvoorbeeld:

- Voor video `movie.mkv`
- Wordt de ondertitel `movie.nl.srt` (voor Nederlands)

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
