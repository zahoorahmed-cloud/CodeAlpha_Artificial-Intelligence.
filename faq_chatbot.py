import string
import threading
import time
import customtkinter as ctk
from tkinter import messagebox
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- FIXED SECTION: Download all newer NLTK structural tab packages silently ---
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)  # <-- Added this line to fix your exact crash
nltk.download('stopwords', quiet=True)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PremiumChatbotDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Engineering ---
        self.title("CodeAlpha AI Enterprise Chat Support")
        self.geometry("950x600")
        self.resizable(False, False)

        # --- FAQ Dataset (Questions & Answers) ---
        self.faq_data = {
            "what is codealpha?": "CodeAlpha is a leading software development company dedicated to driving innovation and excellence across emerging technologies.",
            "what does this internship provide?": "The AI internship provides students with hands-on experience in AI model development, machine learning workflows, and real-time data processing.",
            "what perks do interns get?": "Perks include an Offer Letter, QR-verified Completion Certificate, Letter of Recommendation, and Placement Support.",
            "how do i submit my project?": "You must upload your code to GitHub, post an explanation video on LinkedIn, and submit via the official Google Form provided in your WhatsApp group.",
            "how many tasks must i complete?": "To be eligible for a certificate, participants must complete a minimum of two or three tasks."
        }

        # --- LAYOUT SPLITTER ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#1e1e24")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.sidebar_title = ctk.CTkLabel(
            self.sidebar, text="🤖 CORE-AI HUB", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#3b82f6"
        )
        self.sidebar_title.pack(padx=20, pady=(30, 10), anchor="w")

        self.sidebar_desc = ctk.CTkLabel(
            self.sidebar, text="Enterprise Virtual Assistant\nNLP Math Matcher v1.0",
            font=ctk.CTkFont(size=11, slant="italic"), text_color="gray", justify="left"
        )
        self.sidebar_desc.pack(padx=20, pady=(0, 30), anchor="w")

        self.help_card = ctk.CTkFrame(self.sidebar, fg_color="#141417", border_width=1, border_color="#2d2d34")
        self.help_card.pack(fill="both", expand=True, padx=15, pady=15)

        self.help_title = ctk.CTkLabel(self.help_card, text="💡 SUGGESTED QUESTIONS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a1a1aa")
        self.help_title.pack(padx=10, pady=(12, 8), anchor="w")

        suggestions = ["What is CodeAlpha?", "What are the perks?", "How to submit tasks?", "How many tasks to pass?"]
        for sug in suggestions:
            btn = ctk.CTkButton(
                self.help_card, text=sug, font=ctk.CTkFont(size=11),
                fg_color="transparent", text_color="#e4e4e7", anchor="w",
                hover_color="#27272a", height=28,
                command=lambda s=sug: self.insert_suggested_text(s)
            )
            btn.pack(fill="x", padx=5, pady=2)

        self.chat_workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_workspace.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.chat_timeline = ctk.CTkTextbox(
            self.chat_workspace, font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#121214", border_width=1, border_color="#24242b", state="disabled"
        )
        self.chat_timeline.pack(fill="both", expand=True, padx=5, pady=(0, 15))

        self.input_container = ctk.CTkFrame(self.chat_workspace, fg_color="transparent", height=50)
        self.input_container.pack(fill="x", pady=5)

        self.msg_entry = ctk.CTkEntry(
            self.input_container, placeholder_text="Ask something about the CodeAlpha internship...",
            font=ctk.CTkFont(size=13), height=45, fg_color="#1a1a1e", border_color="#2d2d34"
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(
            self.input_container, text="Send ➔", font=ctk.CTkFont(size=13, weight="bold"),
            width=100, height=45, command=self.send_message
        )
        self.send_btn.pack(side="right")

        self.append_chat_bubble("System Assistant", "Welcome to the CodeAlpha Support Terminal! How can I assist you today?")

    def insert_suggested_text(self, text):
        self.msg_entry.delete(0, "end")
        self.msg_entry.insert(0, text)

    def append_chat_bubble(self, sender, text):
        self.chat_timeline.configure(state="normal")
        timestamp = time.strftime("%H:%M")
        
        if sender == "You":
            self.chat_timeline.insert("end", f"👤 You [{timestamp}]:\n👉 {text}\n\n")
        else:
            self.chat_timeline.insert("end", f"🤖 Assistant [{timestamp}]:\n💬 {text}\n\n")
            
        self.chat_timeline.configure(state="disabled")
        self.chat_timeline.see("end")

    def preprocess_text(self, text):
        text = text.lower()
        tokens = word_tokenize(text)
        clean_tokens = [w for w in tokens if w not in string.punctuation and w not in stopwords.words('english')]
        return " ".join(clean_tokens)

    def send_message(self):
        user_query = self.msg_entry.get().strip()
        if not user_query:
            return

        self.append_chat_bubble("You", user_query)
        self.msg_entry.delete(0, "end")

        threading.Thread(target=self.generate_bot_response, args=(user_query,), daemon=True).start()

    def generate_bot_response(self, query):
        try:
            time.sleep(0.2) 
            clean_query = self.preprocess_text(query)
            faq_questions = list(self.faq_data.keys())
            clean_faqs = [self.preprocess_text(q) for q in faq_questions]

            if not clean_query:
                reply = "I'm sorry, that sentence doesn't contain enough keywords. Try asking something else!"
                self.after(0, lambda: self.append_chat_bubble("Assistant", reply))
                return

            all_texts = [clean_query] + clean_faqs
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            best_match_idx = similarity_scores.argmax()
            highest_score = similarity_scores[0][best_match_idx]

            if highest_score > 0.15: 
                matched_q = faq_questions[best_match_idx]
                reply = self.faq_data[matched_q]
            else:
                reply = "I apologize, I am currently unable to match that question. Please try rephrasing!"
            
            self.after(0, lambda: self.append_chat_bubble("Assistant", reply))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("System Error", f"An internal error occurred: {e}"))

if __name__ == "__main__":
    app = PremiumChatbotDashboard()
    app.mainloop()
