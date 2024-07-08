import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyttsx3
import pygame
import threading
import os
import tempfile
from googletrans import Translator

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Application")

        # Initialize pyttsx3 engine
        self.engine = pyttsx3.init()
        self.is_paused = False
        self.pause_position = 0
        self.temp_file = None

        # Initialize pygame mixer
        pygame.mixer.init()

        # Language selection
        self.language_label = ttk.Label(root, text="Select Language:")
        self.language_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.languages = {'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de','English-US': 'en'}  # Add more languages as needed
        self.language_var = tk.StringVar(value='English')
        self.language_menu = ttk.OptionMenu(root, self.language_var, *self.languages.keys())
        self.language_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Voice selection
        self.voice_label = ttk.Label(root, text="Select Voice:")
        self.voice_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.voices = {'Male': 'english+m7', 'female': 'english+f3','male': 'english+m7'}  # This can be expanded based on the TTS engine capabilities
        self.voice_var = tk.StringVar(value='Male')
        self.voice_menu = ttk.OptionMenu(root, self.voice_var, *self.voices.keys())
        self.voice_menu.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Speech rate adjustment
        self.rate_label = ttk.Label(root, text="Adjust Rate:")
        self.rate_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.rate_scale = ttk.Scale(root, from_=50, to=300, orient=tk.HORIZONTAL)
        self.rate_scale.set(200)  # Default rate
        self.rate_scale.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Volume adjustment
        self.volume_label = ttk.Label(root, text="Adjust Volume:")
        self.volume_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.volume_scale = tk.Scale(root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.1)
        self.volume_scale.set(1.0)  # Default volume
        self.volume_scale.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Text input
        self.text_label = ttk.Label(root, text="Enter Text:")
        self.text_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.text_entry = tk.Text(root, height=10, width=50)
        self.text_entry.grid(row=4, column=1, padx=5, pady=5, columnspan=3)

        # Playback controls
        self.play_button = ttk.Button(root, text="Play", command=self.play_text)
        self.play_button.grid(row=5, column=0, padx=5, pady=5)
        self.pause_button = ttk.Button(root, text="Pause", command=self.pause_text)
        self.pause_button.grid(row=5, column=1, padx=5, pady=5)
        self.resume_button = ttk.Button(root, text="Resume", command=self.resume_text)
        self.resume_button.grid(row=5, column=2, padx=5, pady=5)
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_text)
        self.stop_button.grid(row=5, column=3, padx=5, pady=5)
        self.save_button = ttk.Button(root, text="Save as Audio", command=self.save_audio)
        self.save_button.grid(row=5, column=4, padx=5, pady=5)

        # Reset button
        self.reset_button = ttk.Button(root, text="Reset", command=self.reset_attributes)
        self.reset_button.grid(row=6, column=0, columnspan=5, pady=10)

    def play_text(self):

        text = self.text_entry.get("1.0", tk.END).strip()
        if text:
            self.is_paused = False
            self.pause_position = 0
            threading.Thread(target=self._play_text, args=(text,)).start()
        else:
            messagebox.showerror("Error", "Text field is empty!")


    def _play_text(self, text):
        try:
            
            #setting the rate and volume that user is extracted
            rate = self.rate_scale.get()
            volume = self.volume_scale.get()
            
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            #setting the voice that is male or female
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[0].id if self.voice_var.get() == 'Male' else voices[1].id)

            #translating the to the user specific language
            lang = self.languages[self.language_var.get()]
            translator=Translator()
            translated= translator.translate(text, dest=lang)
            
            # Generate speech and save to a file
            self.temp_file = 'temp_audio.wav'
            if os.path.exists(self.temp_file):
                pygame.quit()
                os.remove(self.temp_file)
                pygame.mixer.init()
            self.engine.save_to_file(translated.text, self.temp_file)
            self.engine.runAndWait()

            # Play the generated speech using pygame
            pygame.mixer.music.load(self.temp_file)
            pygame.mixer.music.play()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while playing the audio: {e}")

    def pause_text(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def resume_text(self):
        if pygame.mixer.music.get_pos() >= 0:
            pygame.mixer.music.unpause()

    def stop_text(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            try:
                if self.temp_file and os.path.exists(self.temp_file):
                    os.remove(self.temp_file)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while deleting the audio file: {e}")

    def save_audio(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        if text:
            try:
                filename = simpledialog.askstring("Save Audio", "Enter filename:")
                if filename:


                    #setting the rate and volume that user is extracted
                    rate = self.rate_scale.get()
                    volume = self.volume_scale.get()
            
                    self.engine.setProperty('rate', rate)
                    self.engine.setProperty('volume', volume)
            
                    #setting the voice that is male or female
                    voices = self.engine.getProperty('voices')
                    self.engine.setProperty('voice', voices[0].id if self.voice_var.get() == 'Male' else voices[1].id)

                    #translating the to the user specific language
                    lang = self.languages[self.language_var.get()]
                    translator=Translator()
                    translated= translator.translate(text, dest=lang)
            
                    # saving the file with mp3 formate
                    outfile = f"{filename}.mp3"
                    self.engine.save_to_file(translated.text, outfile)
                    self.engine.runAndWait()

                    messagebox.showinfo("Success", f"Audio saved as {outfile}")
                else:
                    messagebox.showerror("Error", "Filename cannot be empty!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the audio: {e}")
        else:
            messagebox.showerror("Error", "Text field is empty!")

    def reset_attributes(self):
        self.language_var.set('English')
        self.voice_var.set('Male')
        self.rate_scale.set(200)
        self.volume_scale.set(1.0)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
