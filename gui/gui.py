from customtkinter import *
from gui_worker import AgentWorker
from PIL import ImageGrab
import pyperclip
import time
import json
from datetime import datetime
from tkinter import filedialog
from agent import ResearchResponse

class AgentGUI:

    def __init__(self):
        self.app = CTk()
        self.app.geometry("600x700")
        self.worker_thread = None
        self.selected_image_path = None
        self.frame = CTkFrame(master = self.app, fg_color="#ffd6e8", border_color="#e7c6ff", border_width=2)
        self.frame.pack(fill="both", expand =True)
        self.setup_ui()
        set_appearance_mode("dark")

    def on_read_screen_clicked(self):
        screenshot = ImageGrab.grab()

        temp_path = "/tmp/screen_capture.png"
        screenshot.save(temp_path)

        self.selected_image_path = temp_path

        self.progress_label.configure(text="📸 Screen captured! Enter query and click Research.", text_color="green")
        self.app.after(5000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))

    #def on_add_image_clicked(self):
        """File dialog for image"""
    
    def on_research_clicked(self):
        """Start research in thread"""
        from gui_worker import AgentWorker

        query_text = self.query_textbox.get('1.0', 'end-1c')

        if not query_text.strip():
            self.progress_label.configure(text="Please enter a query", text_color="red")
            self.app.after(3000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))
            return

        # Disable buttons during research
        self.research_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.screenshot_btn.configure(state="disabled")

        # Reset progress bar
        self.progress_bar.set(0)

        self.worker_thread = AgentWorker(
            query = query_text,
            image_path = self.selected_image_path,
            max_iter = 10,
            callback = self.update_progress
        )

        self.worker_thread.start()

        self.check_progress()
    
    def update_progress(self, data):
        """Called by worker thread with updates"""
        if isinstance(data, tuple):
            msg, pct = data
            # Update progress bar and label
            if pct >= 0:
                self.progress_bar.set(pct / 100)  # CTkProgressBar uses 0.0-1.0
                self.progress_label.configure(text=msg, text_color="#5a189a")
            else:
                # Error state
                self.progress_label.configure(text=msg, text_color="red")
        else:
            msg = data
            self.progress_label.configure(text=msg, text_color="#666666")
    
    def check_progress(self):
        """Check if worker is done"""
        if self.worker_thread and self.worker_thread.is_alive():
            # Still running, check again in 100 ms
            self.app.after(100, self.check_progress)
        else:
            # Finished - re-enable buttons
            self.research_btn.configure(state="normal")
            self.copy_btn.configure(state="normal")
            self.export_btn.configure(state="normal")
            self.screenshot_btn.configure(state="normal")

            if self.worker_thread and self.worker_thread.result:
                self.display_results(self.worker_thread.result)
            else:
                self.progress_label.configure(text="Research completed", text_color="#666666")
    
    def on_stop_clicked(self):
        """Stop button"""
        if self.worker_thread:
            self.worker_thread.stop()
    
    def on_export_clicked(self):
        """Export results as json"""
        if not self.worker_thread or not self.worker_thread.result:
            self.progress_label.configure(text="No results to export", text_color="red")
            self.app.after(3000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))
            return

        result_dict = self.worker_thread.result.model_dump()
        result_dict['exported_at'] = datetime.now().isoformat()

        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            self.progress_label.configure(text=f"💾 Saved: {filename}", text_color="green")
            self.app.after(5000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))
        except Exception as e:
            self.progress_label.configure(text=f"Export failed: {e}", text_color="red")
            self.app.after(5000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))

    def on_copy_results(self):
        """Copy button"""
        if not self.worker_thread or not self.worker_thread.result:
            self.progress_label.configure(text="No results to copy", text_color="red")
            self.app.after(3000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))
            return

        formatted_text = f"""Topic: {self.worker_thread.result.topic}

Summary: {self.worker_thread.result.summary}

Sources: {', '.join(self.worker_thread.result.sources) if self.worker_thread.result.sources else 'None'}

Tools Used: {', '.join(self.worker_thread.result.tools_used) if self.worker_thread.result.tools_used else 'None'}"""

        pyperclip.copy(formatted_text)
        self.progress_label.configure(text="📋 Results copied to clipboard!", text_color="green")
        self.app.after(3000, lambda: self.progress_label.configure(text="Ready", text_color="#666666"))

    
    def display_results(self, response: ResearchResponse):
        """Display research results in the persistent results frame"""
        # Clear previous results and placeholder
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Topic header with emoji
        topic_label = CTkLabel(master=self.results_frame, text=f"📊 {response.topic}",
                              font=("Arial", 16, "bold"), text_color="#5a189a",
                              anchor="w")
        topic_label.pack(pady=(15, 5), padx=15, anchor="w")

        # Summary section
        summary_label = CTkLabel(master=self.results_frame, text="Summary:",
                                font=("Arial", 12, "bold"), text_color="#3c096c",
                                anchor="w")
        summary_label.pack(pady=(10, 5), padx=15, anchor="w")

        summary_box = CTkTextbox(master=self.results_frame, height=200, wrap="word",
                                fg_color="#ffffff", text_color="#000000",
                                border_width=1, border_color="#bde0fe")
        summary_box.insert("1.0", response.summary)
        summary_box.configure(state="disabled")
        summary_box.pack(padx=15, pady=5, fill="both", expand=True)

        # Metadata section
        tools_text = f"🔧 Tools Used: {', '.join(response.tools_used) if response.tools_used else 'None'}"
        tools_label = CTkLabel(master=self.results_frame, text=tools_text,
                              font=("Arial", 10), text_color="#666666",
                              anchor="w")
        tools_label.pack(pady=(10, 2), padx=15, anchor="w")

        sources_text = f"📚 Sources: {len(response.sources)} found"
        sources_label = CTkLabel(master=self.results_frame, text=sources_text,
                                font=("Arial", 10), text_color="#666666",
                                anchor="w")
        sources_label.pack(pady=(2, 15), padx=15, anchor="w")

        # Update progress label
        self.progress_label.configure(text="Research complete!", text_color="green")

    def setup_ui(self):
        # === INPUT SECTION ===
        input_frame = CTkFrame(master=self.frame, fg_color="transparent")
        input_frame.pack(padx=10, pady=10, fill="x")

        self.query_textbox = CTkTextbox(master=input_frame, border_width=2, fg_color="#cdb4db",
                                        border_color="#bde0fe", wrap="word", height=80)
        self.query_textbox.pack(padx=5, pady=5, fill="x")

        self.screenshot_btn = CTkButton(master=input_frame, text="📸 Read Screen", corner_radius=32,
                                       fg_color="#cdb4db", hover_color="#bde0fe",
                                       border_color="#bde0fe", border_width=2,
                                       command=self.on_read_screen_clicked)
        self.screenshot_btn.pack(pady=5)

        # === ACTION BUTTONS ===
        action_frame = CTkFrame(master=self.frame, fg_color="transparent")
        action_frame.pack(pady=10)

        self.research_btn = CTkButton(master=action_frame, text="🔍 Research", border_width=2,
                                     fg_color="#cdb4db", border_color="#bde0fe",
                                     hover_color="#bde0fe", command=self.on_research_clicked,
                                     width=120)
        self.research_btn.pack(side="left", padx=5)

        self.stop_btn = CTkButton(master=action_frame, text="⏹️ Stop", border_width=2,
                                 fg_color="#cdb4db", border_color="#bde0fe",
                                 hover_color="#bde0fe", command=self.on_stop_clicked,
                                 width=120)
        self.stop_btn.pack(side="left", padx=5)

        # === PROGRESS BAR ===
        self.progress_bar = CTkProgressBar(master=self.frame, width=560)
        self.progress_bar.pack(padx=20, pady=5)
        self.progress_bar.set(0)

        self.progress_label = CTkLabel(master=self.frame, text="Ready", text_color="#666666",
                                      font=("Arial", 11))
        self.progress_label.pack(pady=2)

        # === RESULTS SECTION ===
        self.results_frame = CTkFrame(master=self.frame, fg_color="#f0e6ff", corner_radius=10,
                                     border_width=1, border_color="#e7c6ff")
        self.results_frame.pack(padx=15, pady=10, fill="both", expand=True)

        self.results_placeholder = CTkLabel(master=self.results_frame,
                                           text="Results will appear here after research completes",
                                           text_color="#888888", font=("Arial", 12, "italic"))
        self.results_placeholder.pack(pady=40)

        # === EXPORT BUTTONS ===
        export_frame = CTkFrame(master=self.frame, fg_color="transparent")
        export_frame.pack(pady=10)

        self.copy_btn = CTkButton(master=export_frame, text="📋 Copy", border_width=2,
                                 fg_color="#cdb4db", border_color="#bde0fe",
                                 hover_color="#bde0fe", command=self.on_copy_results,
                                 width=120)
        self.copy_btn.pack(side="left", padx=5)

        self.export_btn = CTkButton(master=export_frame, text="💾 Export JSON", border_width=2,
                                   fg_color="#cdb4db", border_color="#bde0fe",
                                   hover_color="#bde0fe", command=self.on_export_clicked,
                                   width=120)
        self.export_btn.pack(side="left", padx=5)
    
    def run(self):
        """Start GUI"""
        self.app.mainloop()

if __name__ == "__main__":
    gui = AgentGUI()
    gui.run()