#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Whisper Subtitle Generator met GPU ondersteuning en ondertitelreiniging
# Versie 1.2 - Met verbeterde bestandsnaamgeving

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import subprocess
import queue
from tkinter.scrolledtext import ScrolledText

class WhisperSubtitleGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Subtitle Generator")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Instellingen
        self.video_paths = []  # We gebruiken een lijst in plaats van een StringVar
        self.model_size = tk.StringVar(value="small")  # Standaard model grootte
        self.taal = tk.StringVar(value="nl")  # Nederlands als standaard
        self.use_gpu = tk.BooleanVar(value=True)  # Standaard GPU gebruiken indien beschikbaar
        self.clean_subtitles = tk.BooleanVar(value=True)  # Standaard tekst voor slechthorenden verwijderen
        
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
        self.task_queue = queue.Queue()
        self.current_file = tk.StringVar(value="")
        
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
        file_frame = ttk.LabelFrame(main_frame, text="Video's selecteren", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        # Listbox voor geselecteerde bestanden
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=0, column=0, rowspan=3, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.files_listbox = tk.Listbox(list_frame, width=70, height=5)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # Knoppen voor bestandsbeheer
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nw")
        
        ttk.Button(button_frame, text="Toevoegen...", command=self.browse_videos).pack(pady=2, fill=tk.X)
        ttk.Button(button_frame, text="Verwijderen", command=self.remove_selected_video).pack(pady=2, fill=tk.X)
        ttk.Button(button_frame, text="Alles verwijderen", command=self.clear_videos).pack(pady=2, fill=tk.X)
        
        # Model instellingen
        model_frame = ttk.LabelFrame(main_frame, text="Whisper Model Instellingen", padding="10")
        model_frame.pack(fill=tk.X, pady=10)
        
        # Model grootte
        ttk.Label(model_frame, text="Model grootte:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(model_frame, textvariable=self.model_size, 
                    values=["tiny", "base", "small", "medium", "large"]).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # GPU / CPU keuze
        gpu_frame = ttk.Frame(model_frame)
        gpu_frame.grid(row=0, column=2, padx=15, pady=5, sticky=tk.W)
        
        ttk.Radiobutton(gpu_frame, text="GPU (sneller)", variable=self.use_gpu, value=True).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(gpu_frame, text="CPU (langzamer)", variable=self.use_gpu, value=False).pack(side=tk.LEFT, padx=5)
        
        # Taal
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
        
        # Clean ondertitels optie
        ttk.Checkbutton(model_frame, text="Tekst voor slechthorenden verwijderen", 
                       variable=self.clean_subtitles).grid(row=1, column=2, padx=15, sticky=tk.W)
        
        # Huidige voortgang
        current_frame = ttk.LabelFrame(main_frame, text="Huidige verwerking", padding="10")
        current_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(current_frame, text="Bestand:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(current_frame, textvariable=self.current_file).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Voortgangsbalk
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(current_frame, variable=self.progress_var, length=100, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        
        # Informatie over GPU
        gpu_info_frame = ttk.Frame(current_frame)
        gpu_info_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        
        gpu_tip = ttk.Label(gpu_info_frame, text="Tip: GPU verwerking is meestal 5-10x sneller dan CPU. Gebruik GPU indien beschikbaar.", font=("Arial", 9, "italic"))
        gpu_tip.pack(anchor=tk.W)
        
        # Log venster
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Actieknoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Afsluiten", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Check GPU beschikbaarheid
        self.check_gpu_availability()
    
    def check_gpu_availability(self):
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            
            if has_cuda:
                gpu_name = torch.cuda.get_device_name(0)
                self.log(f"NVIDIA GPU gedetecteerd: {gpu_name}")
                self.log("GPU verwerking is ingeschakeld (veel sneller)")
            else:
                self.log("Geen CUDA-compatibele GPU gedetecteerd. Terugvallen op CPU.")
                self.log("Waarschuwing: CPU verwerking is aanzienlijk langzamer")
                # Zet standaard naar CPU modus
                self.use_gpu.set(False)
                
        except Exception as e:
            self.log("Kon GPU beschikbaarheid niet bepalen. Fout: " + str(e))
            self.log("Terugvallen op CPU verwerking")
            self.use_gpu.set(False)
    
    def browse_videos(self):
        filetypes = (
            ("Video bestanden", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("Alle bestanden", "*.*")
        )
        
        filenames = filedialog.askopenfilenames(
            title="Selecteer videobestand(en)",
            filetypes=filetypes
        )
        
        if filenames:
            # Voeg nieuwe bestanden toe aan de lijst
            for file in filenames:
                if file not in self.video_paths:
                    self.video_paths.append(file)
                    self.files_listbox.insert(tk.END, os.path.basename(file))
            
            self.log(f"{len(filenames)} video bestand(en) toegevoegd")
    
    def remove_selected_video(self):
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            return
        
        # Verwijder van laatste naar eerste om indexverschuiving te vermijden
        for i in sorted(selected_indices, reverse=True):
            del self.video_paths[i]
            self.files_listbox.delete(i)
        
        self.log(f"{len(selected_indices)} bestand(en) verwijderd uit de lijst")
    
    def clear_videos(self):
        self.video_paths.clear()
        self.files_listbox.delete(0, tk.END)
        self.log("Alle bestanden verwijderd uit de lijst")
    
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
            
            # Controleer torch en CUDA
            import torch
            self.log(f"PyTorch versie: {torch.__version__}")
            if torch.cuda.is_available() and self.use_gpu.get():
                self.log(f"CUDA is beschikbaar: {torch.cuda.get_device_name(0)}")
            else:
                if self.use_gpu.get():
                    self.log("CUDA is niet beschikbaar, maar GPU is geselecteerd. Controleer NVIDIA drivers.")
                else:
                    self.log("GPU modus is uitgeschakeld, gebruikt CPU (langzamer).")
                
        except ImportError as e:
            self.log(f"FOUT: Ontbrekende dependency: {str(e)}")
            messagebox.showerror("Ontbrekende afhankelijkheid", 
                              f"Ontbrekende dependency: {str(e)}\n\nInstalleer deze met pip install.")
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
            
        if not self.video_paths:
            messagebox.showerror("Fout", "Selecteer eerst één of meer videobestanden.")
            return
        
        # Controleer dependencies voordat we beginnen
        if not self.check_dependencies():
            return
            
        # Start verwerking in een aparte thread
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start(10)
        
        # Reset de verwerkingswachtrij
        while not self.task_queue.empty():
            self.task_queue.get()
        
        # Zet alle bestanden in de wachtrij
        for video_path in self.video_paths:
            self.task_queue.put(video_path)
        
        total_files = len(self.video_paths)
        self.log(f"Start verwerking van {total_files} bestand(en)")
        
        # Log device info
        if self.use_gpu.get():
            self.log("Verwerking op GPU ingeschakeld (sneller)")
        else:
            self.log("Verwerking op CPU ingeschakeld (langzamer)")
            
        # Log of ondertitelreiniging is ingeschakeld
        if self.clean_subtitles.get():
            self.log("Reiniging van tekst voor slechthorenden is ingeschakeld")
        
        # Start verwerking in een aparte thread
        processing_thread = threading.Thread(target=self.process_files, daemon=True)
        processing_thread.start()
    
    def stop_processing(self):
        if not self.is_processing:
            return
            
        self.is_processing = False
        self.log("Verwerking wordt gestopt...")
        self.stop_button.config(state=tk.DISABLED)
        self.current_file.set("Gestopt")
    
    def clean_srt_file(self, srt_path):
        """
        Verwijdert tekst voor slechthorenden uit SRT-bestanden:
        - Tekst tussen haakjes [tekst], (tekst), {tekst}
        - Tekst in hoofdletters (als het een heel woord is)
        - Tekst voor dubbele punt als het in hoofdletters is (PERSOON: tekst)
        - Geluidseffecten zoals *lacht*, #muziek#, etc.
        """
        try:
            self.log(f"Opschonen van ondertitelbestand: {os.path.basename(srt_path)}")
            
            # Lees het SRT-bestand
            with open(srt_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            cleaned_lines = []
            i = 0
            
            # SRT-bestanden bestaan uit blokken met 4 regels:
            # 1: Volgnummer
            # 2: Tijdcodes
            # 3: Ondertiteltekst (soms meerdere regels)
            # 4: Lege regel
            
            while i < len(lines):
                # Bewaar volgnummer en tijdcodes ongewijzigd
                if i < len(lines) and lines[i].strip().isdigit():
                    # Volgnummer
                    cleaned_lines.append(lines[i])
                    i += 1
                    
                    # Tijdcodes (als we nog niet aan het einde zijn)
                    if i < len(lines) and '-->' in lines[i]:
                        cleaned_lines.append(lines[i])
                        i += 1
                        
                        # Ondertiteltekst (kan meerdere regels zijn)
                        subtitle_lines = []
                        while i < len(lines) and lines[i].strip() != '':
                            subtitle_lines.append(lines[i])
                            i += 1
                        
                        # Reinig deze ondertiteltekst
                        cleaned_subtitle = self.clean_subtitle_text('\n'.join(subtitle_lines))
                        
                        # Voeg alleen toe als er tekst overblijft na het reinigen
                        if cleaned_subtitle.strip():
                            cleaned_lines.append(cleaned_subtitle + '\n')
                        else:
                            # Als alle tekst is verwijderd, verwijder volgnummer en tijdcodes ook
                            cleaned_lines.pop()  # Verwijder tijdcodes
                            cleaned_lines.pop()  # Verwijder volgnummer
                        
                        # Lege regel
                        if i < len(lines):
                            cleaned_lines.append(lines[i])
                            i += 1
                else:
                    # Onverwacht formaat, behoud de regel
                    cleaned_lines.append(lines[i])
                    i += 1
            
            # Schrijf de opgeschoonde tekst terug naar het bestand
            with open(srt_path, 'w', encoding='utf-8') as file:
                file.writelines(cleaned_lines)
                
            self.log(f"Ondertitelbestand succesvol opgeschoond")
            return True
            
        except Exception as e:
            self.log(f"Fout bij opschonen van ondertitelbestand: {str(e)}")
            return False

    def clean_subtitle_text(self, text):
        """
        Reinigt een stuk ondertiteltekst door tekst voor slechthorenden te verwijderen
        """
        import re
        
        # Verwijder tekst tussen verschillende soorten haakjes
        # [tekst], (tekst), {tekst}
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'\{.*?\}', '', text)
        
        # Verwijder geluidseffecten met * of #
        text = re.sub(r'\*.*?\*', '', text)
        text = re.sub(r'#.*?#', '', text)
        
        # Verwijder tekst in hoofdletters voor een dubbele punt
        # Bijv. "JOHN: Hallo" wordt "Hallo"
        text = re.sub(r'[A-Z]{2,}[A-Z\s]*:', '', text)
        
        # Verwijder hele regels die volledig in hoofdletters staan
        # (vaak geluidseffecten of sprekerinformatie)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Als de regel niet volledig in hoofdletters is of alleen maar leestekens/getallen bevat
            if not (line.strip() and line.strip().upper() == line.strip() and any(c.isalpha() for c in line)):
                cleaned_lines.append(line)
        
        # Voeg de regels weer samen
        text = '\n'.join(cleaned_lines)
        
        # Verwijder dubbele witruimte en witruimte aan begin/eind
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def process_files(self, output_dir):
        """
        Verwerkt alle bestanden in de task_queue en genereert ondertitels.
        Deze functie wordt uitgevoerd in een aparte thread.
        """
        model_size = self.model_size.get()
        taal = self.taal.get()
        taal_naam = self.iso_naar_taal.get(taal, taal.upper())
        use_gpu = self.use_gpu.get()
        
        self.log(f"Geselecteerde taal: {taal_naam} ({taal})")
        self.log(f"Model grootte: {model_size}")
        
        total_files = self.task_queue.qsize()
        processed_files = 0
        
        try:
            # Laad Whisper modules
            import whisper
            from whisper.utils import get_writer
            import torch
            
            # Set device
            device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
            if device == "cuda":
                self.log("Gebruik NVIDIA GPU voor verwerking")
            else:
                if use_gpu:
                    self.log("GPU niet beschikbaar, terugvallen op CPU")
                else:
                    self.log("CPU geselecteerd voor verwerking")
            
            # Laad het model eenmalig voor alle bestanden
            self.log(f"Model '{model_size}' laden op {device}... (dit kan even duren)")
            start_time = time.time()
            model = whisper.load_model(model_size, device=device)
            load_time = time.time() - start_time
            self.log(f"Model geladen in {load_time:.2f} seconden")
            
            while not self.task_queue.empty() and self.is_processing:
                video_path = self.task_queue.get()
                processed_files += 1
                
                # Update huidige bestand info
                video_name = os.path.basename(video_path)
                self.current_file.set(f"({processed_files}/{total_files}) {video_name}")
                
                try:
                    # Bepaal de bestandsnamen
                    video_full_name = os.path.basename(video_path)
                    video_name_without_ext = os.path.splitext(video_full_name)[0]  # Verbeterd: gebruik os.path.splitext
                    output_path = os.path.join(output_dir, f"{video_name_without_ext}.{taal}.srt")
                    
                    # Bewaar de originele bestandsnaam voor logging doeleinden
                    original_filename_base = video_name_without_ext
                    
                    # Log informatie over de bestandsnamen
                    self.log(f"Oorspronkelijke video bestandsnaam: {video_name}")
                    self.log(f"Verwachte ondertitel bestandsnaam: {video_name_without_ext}.{taal}.srt")
                    
                    self.log(f"Verwerking van: {video_name} ({processed_files}/{total_files})")
                    
                    # Voer transcriptie uit met de geselecteerde taal
                    self.log(f"Transcriptie uitvoeren op {video_name}...")
                    transcribe_start = time.time()
                    result = model.transcribe(
                        video_path,
                        language=taal,  # Gebruik de geselecteerde taal
                        task="transcribe",
                        verbose=False,
                        fp16=(device == "cuda")  # Gebruik FP16 alleen op GPU
                    )
                    transcribe_time = time.time() - transcribe_start
                    self.log(f"Transcriptie voltooid in {transcribe_time:.2f} seconden")
                    
                    # Maak SRT writer
                    srt_writer = get_writer("srt", output_dir)
                    
                    # Schrijf ondertitels direct naar een tijdelijk bestand
                    import tempfile
                    
                    # Maak een tijdelijke directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Gebruik een eenvoudige bestandsnaam voor het tijdelijke bestand
                        temp_filename = "temp_subtitle"
                        
                        # Maak SRT writer voor de tijdelijke map
                        self.log(f"SRT-bestand genereren voor {video_name}...")
                        temp_srt_writer = get_writer("srt", temp_dir)
                        temp_srt_writer(result, temp_filename, {"max_line_width": 42, "max_line_count": 2})
                        
                        # Pad naar het gegenereerde tijdelijke SRT-bestand
                        temp_srt_path = os.path.join(temp_dir, f"{temp_filename}.srt")
                        
                        if os.path.exists(temp_srt_path):
                            # Lees de inhoud van het tijdelijke SRT-bestand
                            with open(temp_srt_path, 'r', encoding='utf-8') as src_file:
                                srt_content = src_file.read()
                            
                            # Schrijf naar het definitieve SRT-bestand met de juiste naam
                            if os.path.exists(output_path):
                                self.log(f"Bestaand bestand overschrijven: {output_path}")
                                os.remove(output_path)
                                
                            with open(output_path, 'w', encoding='utf-8') as dest_file:
                                dest_file.write(srt_content)
                                
                            self.log(f"Ondertitels opgeslagen met correcte bestandsnaam: {os.path.basename(output_path)}")
                        else:
                            self.log(f"FOUT: Tijdelijk SRT-bestand werd niet aangemaakt: {temp_srt_path}")
                            raise Exception("Kon geen ondertitels genereren met Whisper")
                        
                    self.log(f"Ondertitels opgeslagen in: {output_path}")
                    
                    # Als opschonen is ingeschakeld, reinig het bestand
                    if self.clean_subtitles.get() and os.path.exists(output_path):
                        self.clean_srt_file(output_path)
                    
                except Exception as e:
                    self.log(f"FOUT bij verwerking van {video_name}: {str(e)}")
            
            if self.is_processing:  # Als we niet handmatig zijn gestopt
                self.log(f"Alle {processed_files} bestanden zijn verwerkt")
                messagebox.showinfo("Voltooid", f"Alle {processed_files} bestanden zijn succesvol verwerkt.")
            
        except Exception as e:
            self.log(f"FOUT tijdens verwerking: {str(e)}")
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
        finally:
            self.is_processing = False
            self.progress.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.current_file.set("")


# Applicatie starten
if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperSubtitleGenerator(root)
    root.mainloop()
