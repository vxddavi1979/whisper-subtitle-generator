#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Whisper Subtitle Generator met taalselectie

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import subprocess

class WhisperSubtitleGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Subtitle Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Instellingen
        self.video_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_dir.set(os.path.expanduser("~/Documents"))
        self.model_size = tk.StringVar(value="small")  # Standaard model grootte
        self.taal = tk.StringVar(value="nl")  # Nederlands als standaard
        
        # Taal naar ISO-code mapping
        self.taal_mapping = {
            "Nederlands": "nl",
            "Engels": "en",
            "Duits": "de",
            "Frans": "fr",
            "Spaans": "es",
            "Italiaans": "it",
            "Portugees": "pt",
            "Russisch": "ru",
            "Chinees": "zh",
            "Japans": "ja",
            "Koreaans": "ko",
            "Arabisch": "ar",
            "Hindi": "hi",
            "Turks": "tr",
            "Pools": "pl",
            "Zweeds": "sv",
            "Deens": "da",
            "Noors": "no",
            "Fins": "fi"
        }
        
        # Omgekeerde mapping voor weergave
        self.iso_naar_taal = {v: k for k, v in self.taal_mapping.items()}
        
        # Status variabelen
        self.is_processing = False
        
        # UI opbouwen
        self.create_widgets()
        
    def create_widgets(self):
        # Hoofdframe
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="Whisper Subtitle Generator", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Bestandsselectie
        file_frame = ttk.LabelFrame(main_frame, text="Video selecteren", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Video bestand:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Bladeren...", command=self.browse_video).grid(row=0, column=2, padx=5, pady=5)
        
        # Model instellingen
        model_frame = ttk.LabelFrame(main_frame, text="Whisper Model Instellingen", padding="10")
        model_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(model_frame, text="Model grootte:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(model_frame, textvariable=self.model_size, 
                    values=["tiny", "base", "small", "medium", "large"]).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(model_frame, text="Taal:").grid(row=1, column=0, sticky=tk.W, pady=5)
        taal_combobox = ttk.Combobox(model_frame, width=20)
        taal_combobox['values'] = list(self.taal_mapping.keys())
        taal_combobox.current(0)  # Standaard selecteert Nederlands
        taal_combobox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Combobox event handler om de taal-code bij te werken wanneer de gebruiker een taal selecteert
        def on_taal_selected(event):
            selected_taal = taal_combobox.get()
            self.taal.set(self.taal_mapping[selected_taal])
        
        taal_combobox.bind('<<ComboboxSelected>>', on_taal_selected)
        
        ttk.Label(model_frame, text="Uitvoer map:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(model_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(model_frame, text="Bladeren...", command=self.browse_output_dir).grid(row=2, column=2, padx=5, pady=5)
        
        # Instructies
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructies", padding="10")
        instructions_frame.pack(fill=tk.X, pady=10)
        
        instructions_text = (
            "1. Selecteer een videobestand\n"
            "2. Kies de gewenste model grootte (grotere modellen zijn nauwkeuriger maar langzamer)\n"
            "3. Selecteer de taal voor de ondertitels\n"
            "4. Selecteer optioneel een uitvoermap (standaard naast de video)\n"
            "5. Klik op 'Start' om Whisper te starten\n"
            "6. Wacht tot het proces is voltooid\n\n"
            "Let op: Dit programma vereist dat OpenAI Whisper en FFmpeg zijn geïnstalleerd.\n"
            "Installeer deze met: pip install git+https://github.com/openai/whisper.git ffmpeg-python"
        )
        
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # Log venster
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Voortgangsbalk
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X)
        
        # Actieknoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Afsluiten", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
    
    def browse_video(self):
        filetypes = (
            ("Video bestanden", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("Alle bestanden", "*.*")
        )
        
        filename = filedialog.askopenfilename(
            title="Selecteer een video bestand",
            filetypes=filetypes
        )
        
        if filename:
            self.video_path.set(filename)
            # Standaard uitvoermap instellen op dezelfde map als de video
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(filename))
            self.log(f"Video geselecteerd: {filename}")
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(
            title="Selecteer uitvoer map"
        )
        
        if directory:
            self.output_dir.set(directory)
            self.log(f"Uitvoer map geselecteerd: {directory}")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_dependencies(self):
        try:
            import whisper
            self.log("OpenAI Whisper succesvol geladen.")
        except ImportError:
            self.log("FOUT: OpenAI Whisper is niet geïnstalleerd!")
            messagebox.showerror("Ontbrekende afhankelijkheid", 
                              "OpenAI Whisper is niet geïnstalleerd. Installeer het met:\n\npip install git+https://github.com/openai/whisper.git")
            return False
        
        try:
            # Controleer of ffmpeg beschikbaar is
            result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise Exception("FFmpeg niet gevonden")
            self.log("FFmpeg succesvol gevonden.")
        except:
            self.log("FOUT: FFmpeg is niet geïnstalleerd of niet beschikbaar in PATH!")
            messagebox.showerror("Ontbrekende afhankelijkheid", 
                              "FFmpeg is niet geïnstalleerd of niet beschikbaar in PATH.\n"
                              "Installeer FFmpeg en zorg dat het in je systeem PATH staat.")
            return False
            
        return True
    
    def start_processing(self):
        if self.is_processing:
            return
            
        video_path = self.video_path.get()
        output_dir = self.output_dir.get()
        model_size = self.model_size.get()
        taal = self.taal.get()
        
        if not video_path:
            messagebox.showerror("Fout", "Selecteer eerst een video bestand.")
            return
        
        if not os.path.exists(video_path):
            messagebox.showerror("Fout", "Het geselecteerde video bestand bestaat niet.")
            return
        
        # Als er geen uitvoermap is geselecteerd, gebruik de map van de video
        if not output_dir:
            output_dir = os.path.dirname(video_path)
            self.output_dir.set(output_dir)
        
        if not os.path.exists(output_dir):
            messagebox.showerror("Fout", "De geselecteerde uitvoer map bestaat niet.")
            return
            
        # Controleer dependencies voordat we beginnen
        if not self.check_dependencies():
            return
            
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start(10)
        
        taal_naam = self.iso_naar_taal.get(taal, taal.upper())
        self.log(f"Geselecteerde taal: {taal_naam} ({taal})")
        
        # Start verwerking in een aparte thread
        threading.Thread(target=self.run_whisper, args=(video_path, output_dir, model_size, taal), daemon=True).start()
    
    def stop_processing(self):
        if not self.is_processing:
            return
            
        self.is_processing = False
        self.log("Verwerking wordt gestopt...")
        self.stop_button.config(state=tk.DISABLED)
    
    def run_whisper(self, video_path, output_dir, model_size, taal):
        try:
            # Laad Whisper modules hier zodat ze alleen binnen de thread worden geïmporteerd
            import whisper
            from whisper.utils import get_writer
            
            # Toon bestandsinfo
            video_name = os.path.basename(video_path)
            base_name = os.path.splitext(video_name)[0]
            output_path = os.path.join(output_dir, f"{base_name}.{taal}.srt")
            
            self.log(f"Spraakherkenning starten op: {video_name}")
            self.log(f"Model grootte: {model_size}")
            self.log(f"Uitvoer bestand: {output_path}")
            
            # Laad het model
            self.log(f"Model laden... (dit kan even duren)")
            model = whisper.load_model(model_size)
            
            # Voer transcriptie uit met de geselecteerde taal
            self.log("Transcriptie uitvoeren...")
            result = model.transcribe(
                video_path,
                language=taal,  # Gebruik de geselecteerde taal
                task="transcribe",
                verbose=False
            )
            
            # Maak SRT writer
            srt_writer = get_writer("srt", output_dir)
            
            # Schrijf SRT-bestand
            self.log("SRT-bestand genereren...")
            srt_writer(result, base_name, {"max_line_width": 42, "max_line_count": 2})
            
            # Hernoem bestand naar [taal].srt als dat nog niet is gedaan
            srt_default_path = os.path.join(output_dir, f"{base_name}.srt")
            if os.path.exists(srt_default_path) and not os.path.exists(output_path):
                os.rename(srt_default_path, output_path)
                
            self.log(f"Ondertitels gegenereerd en opgeslagen in: {output_path}")
            messagebox.showinfo("Voltooid", f"Ondertitels zijn succesvol gegenereerd en opgeslagen als:\n{output_path}")
            
        except Exception as e:
            self.log(f"FOUT tijdens verwerking: {str(e)}")
            messagebox.showerror("Fout", f"Er is een fout opgetreden tijdens het verwerken: {str(e)}")
        finally:
            self.is_processing = False
            self.progress.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)


# Applicatie starten
if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperSubtitleGenerator(root)
    root.mainloop()