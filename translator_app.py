import threading
import customtkinter as ctk
from tkinter import messagebox
from deep_translator import GoogleTranslator

# Set the overall theme color and style
ctk.set_appearance_mode("System")  # Automatically matches Windows Dark/Light mode
ctk.set_default_color_theme("blue") # Standard professional blue theme accents

class ProfessionalTranslator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("CodeAlpha Language Translator Pro")
        self.geometry("600x620")
        self.resizable(False, False)
        
        # Supported Language Dictionary
        self.languages = {
            "English": "english", "Spanish": "spanish", "French": "french", 
            "German": "german", "Hindi": "hindi", "Arabic": "arabic", "Chinese": "chinese"
        }

        # --- Header Section ---
        self.header_label = ctk.CTkLabel(
            self, text="🎯 AI TRANSLATOR PRO", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=(20, 10))

        # --- Layout Frame ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=10)

        # 1. Source Language Selection Block
        self.src_label = ctk.CTkLabel(self.main_frame, text="From Language:", font=ctk.CTkFont(size=13, weight="bold"))
        self.src_label.pack(anchor="w", padx=20, pady=(15, 2))
        
        self.src_lang_combo = ctk.CTkComboBox(self.main_frame, values=list(self.languages.keys()), width=250)
        self.src_lang_combo.set("English")
        self.src_lang_combo.pack(anchor="w", padx=20, pady=(0, 10))

        # 2. Input Box Block
        self.input_label = ctk.CTkLabel(self.main_frame, text="Enter Text to Translate:", font=ctk.CTkFont(size=12))
        self.input_label.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.text_entry = ctk.CTkTextbox(self.main_frame, height=110, width=510, font=ctk.CTkFont(size=14))
        self.text_entry.pack(padx=20, pady=(0, 15))

        # 3. Target Language Selection Block
        self.tgt_label = ctk.CTkLabel(self.main_frame, text="To Language:", font=ctk.CTkFont(size=13, weight="bold"))
        self.tgt_label.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.tgt_lang_combo = ctk.CTkComboBox(self.main_frame, values=list(self.languages.keys()), width=250)
        self.tgt_lang_combo.set("Spanish")
        self.tgt_lang_combo.pack(anchor="w", padx=20, pady=(0, 10))

        # 4. Process Action Button
        self.translate_btn = ctk.CTkButton(
            self.main_frame, text="Translate Text", 
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42, width=200, command=self.start_translation_thread
        )
        self.translate_btn.pack(pady=15)

        # 5. Output Box Block
        self.output_label = ctk.CTkLabel(self.main_frame, text="Translated Output:", font=ctk.CTkFont(size=13, weight="bold"))
        self.output_label.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.output_entry = ctk.CTkTextbox(self.main_frame, height=110, width=510, font=ctk.CTkFont(size=14), fg_color="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#e0e0e0")
        self.output_entry.pack(padx=20, pady=(0, 20))

        # --- Footer Section ---
        self.footer_label = ctk.CTkLabel(self, text="CodeAlpha Internship Project Portfolio", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray")
        self.footer_label.pack(pady=(5, 15))

    def start_translation_thread(self):
        """Dispatches translation process onto a background thread to prevent GUI freezing."""
        threading.Thread(target=self.process_translation, daemon=True).start()

    def process_translation(self):
        input_text = self.text_entry.get("1.0", "end-1c").strip()
        source_name = self.src_lang_combo.get()
        target_name = self.tgt_lang_combo.get()
        
        if not input_text:
            messagebox.showwarning("Input Missing", "Please provide a valid input string to process.")
            return
        
        # Update UI to signal processing state
        self.translate_btn.configure(state="disabled", text="Translating...")
        
        try:
            # Map visual language selection back to deep-translator lookup tags
            src_slug = self.languages[source_name]
            tgt_slug = self.languages[target_name]
            
            translator = GoogleTranslator(source=src_slug, target=tgt_slug)
            translated_result = translator.translate(input_text)
            
            # Clear target text view block and populate fresh results safely
            self.output_entry.delete("1.0", "end")
            self.output_entry.insert("1.0", translated_result)
            
        except Exception as err:
            messagebox.showerror("Network/API Fault", f"An execution fault emerged: {err}")
        finally:
            # Reset UI state back to active defaults
            self.translate_btn.configure(state="normal", text="Translate Text")

if __name__ == "__main__":
    app = ProfessionalTranslator()
    app.mainloop()
