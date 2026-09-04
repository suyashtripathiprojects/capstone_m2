import customtkinter as ctk
import base64
import codecs
import urllib.parse

# --- CORE TRANSFORM FUNCTIONS ---
def safe_encode(func, s):
    try:
        return func(s)
    except Exception as e:
        return f"[error: {str(e)}]"

def rot13(s):
    return codecs.encode(s, 'rot_13')

def leetspeak(s):
    leet_map = {'a':'4', 'e':'3', 'i':'1', 'o':'0', 's':'5', 't':'7', 'b':'8', 'g':'9', 'l':'1'}
    return ''.join(leet_map.get(c.lower(), c) for c in s)

def homoglyph(s):
    h_map = {'a':'а', 'e':'е', 'o':'о', 'p':'р', 'c':'с', 'x':'х', 'y':'у', 'i':'і', 'j':'ј', 's':'ѕ'}
    return ''.join(h_map.get(c, c) for c in s)

TRANSFORMS = {
    "Base64 Encode": lambda s: safe_encode(lambda x: base64.b64encode(x.encode('utf-8')).decode('utf-8'), s),
    "Base64 Decode": lambda s: safe_encode(lambda x: base64.b64decode(x.encode('utf-8')).decode('utf-8'), s),
    "ROT13": rot13,
    "Leetspeak": leetspeak,
    "Hex Encode": lambda s: safe_encode(lambda x: x.encode('utf-8').hex(' '), s),
    "Hex Decode": lambda s: safe_encode(lambda x: bytes.fromhex(x).decode('utf-8'), s),
    "URL Encode": lambda s: urllib.parse.quote(s),
    "URL Decode": lambda s: urllib.parse.unquote(s),
    "Binary Encode": lambda s: ' '.join(format(ord(c), '08b') for c in s),
    "Binary Decode": lambda s: safe_encode(lambda x: ''.join(chr(int(b, 2)) for b in x.split()), s),
    "Reverse String": lambda s: s[::-1],
    "Homoglyph": homoglyph,
    "Zero-Width": lambda s: '\u200B'.join(s)
}

# --- GUI APPLICATION CLASS ---
class ObfuscationPipeline(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Obfuscation Pipeline — Encoding Toolkit")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.stages = [] # Holds the pipeline sequence

        self.setup_ui()
        self.render_pipeline()

    def setup_ui(self):
        # Main Container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        self.header = ctk.CTkLabel(self.main_frame, text="OBFUSCATION PIPELINE", font=("Courier", 24, "bold"), text_color="#E8A33D")
        self.header.pack(anchor="w", pady=(0, 5))
        self.sub_header = ctk.CTkLabel(self.main_frame, text="Chain text transforms to evaluate encoding-based filter bypasses", font=("Courier", 12), text_color="gray")
        self.sub_header.pack(anchor="w", pady=(0, 20))

        # Input Section
        self.lbl_input = ctk.CTkLabel(self.main_frame, text="INPUT TEXT", font=("Courier", 12, "bold"))
        self.lbl_input.pack(anchor="w")
        
        self.input_box = ctk.CTkTextbox(self.main_frame, height=80, font=("Courier", 14))
        self.input_box.pack(fill="x", pady=(5, 20))
        self.input_box.insert("0.0", "Meet me at the usual place tonight.")
        self.input_box.bind("<KeyRelease>", self.on_input_change)

        # Stage Selection Section
        self.control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.control_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_add = ctk.CTkLabel(self.control_frame, text="ADD A STAGE:", font=("Courier", 12, "bold"))
        self.lbl_add.pack(side="left", padx=(0, 10))

        self.stage_var = ctk.StringVar(value="Base64 Encode")
        self.dropdown = ctk.CTkComboBox(self.control_frame, values=list(TRANSFORMS.keys()), variable=self.stage_var, width=200)
        self.dropdown.pack(side="left", padx=(0, 10))

        self.btn_add = ctk.CTkButton(self.control_frame, text="+ Add Stage", fg_color="#E8A33D", text_color="black", hover_color="#C78B33", font=("Courier", 12, "bold"), command=self.add_stage)
        self.btn_add.pack(side="left")

        # Pipeline Display Section (Scrollable)
        self.lbl_pipeline = ctk.CTkLabel(self.main_frame, text="PIPELINE", font=("Courier", 12, "bold"))
        self.lbl_pipeline.pack(anchor="w")
        
        self.pipeline_frame = ctk.CTkScrollableFrame(self.main_frame, height=200, fg_color="#101C19", border_color="#1E332E", border_width=1)
        self.pipeline_frame.pack(fill="both", expand=True, pady=(5, 20))

        # Final Output Section
        self.lbl_output = ctk.CTkLabel(self.main_frame, text="FINAL OUTPUT", font=("Courier", 12, "bold"))
        self.lbl_output.pack(anchor="w")

        self.output_box = ctk.CTkTextbox(self.main_frame, height=80, font=("Courier", 14), fg_color="#0D1815", text_color="#3DDBD9", border_color="#E8A33D", border_width=1)
        self.output_box.pack(fill="x", pady=(5, 0))

    def on_input_change(self, event):
        self.render_pipeline()

    def add_stage(self):
        selected_stage = self.stage_var.get()
        self.stages.append(selected_stage)
        self.render_pipeline()

    def remove_stage(self, index):
        self.stages.pop(index)
        self.render_pipeline()

    def render_pipeline(self):
        # Clear existing pipeline UI
        for widget in self.pipeline_frame.winfo_children():
            widget.destroy()

        current_text = self.input_box.get("0.0", "end").strip()

        if not self.stages:
            empty_lbl = ctk.CTkLabel(self.pipeline_frame, text="No stages yet — add a transform above to start building the pipeline.", text_color="gray")
            empty_lbl.pack(pady=20)
            self.update_final_output(current_text)
            return

        # Build pipeline UI and calculate transforms iteratively
        for i, stage_name in enumerate(self.stages):
            # Calculate transform
            func = TRANSFORMS[stage_name]
            current_text = func(current_text)

            # Create Stage Card
            card = ctk.CTkFrame(self.pipeline_frame, fg_color="#1a2b27", corner_radius=5)
            card.pack(fill="x", pady=5, padx=5)

            # Card Header
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(10, 5))
            
            lbl_name = ctk.CTkLabel(header, text=f"{i+1}. {stage_name}", font=("Courier", 12, "bold"), text_color="#E8A33D")
            lbl_name.pack(side="left")

            btn_del = ctk.CTkButton(header, text="✕", width=30, height=24, fg_color="#E2555A", hover_color="#C1454A", command=lambda idx=i: self.remove_stage(idx))
            btn_del.pack(side="right")

            # Card Output Box
            stage_output = ctk.CTkTextbox(card, height=40, font=("Courier", 12), text_color="gray", fg_color="#101C19")
            stage_output.pack(fill="x", padx=10, pady=(0, 10))
            stage_output.insert("0.0", current_text)
            stage_output.configure(state="disabled") # Make read-only

        self.update_final_output(current_text)

    def update_final_output(self, text):
        self.output_box.configure(state="normal")
        self.output_box.delete("0.0", "end")
        self.output_box.insert("0.0", text)
        self.output_box.configure(state="disabled")

if __name__ == "__main__":
    app = ObfuscationPipeline()
    app.mainloop()