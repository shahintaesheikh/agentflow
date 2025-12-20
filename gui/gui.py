from customtkinter import *
from gui_worker import AgentWorker
from PIL import ImageGrab
import pyperclip
import time

class AgentGUI:

    def __init__(self):
        self.app = CTk()
        self.app.geometry("500x400")
        self.setup_ui()
        self.query = None
        self.worker_thread = None
        self.selected_image_path = None
        self.response = None
        set_appearance_mode("dark")

    def on_read_screen_clicked(self):
        screenshot = ImageGrab.grab()

        temp_path = "/tmp/screen_capture.png"
        screenshot.save(temp_path)

        self.selected_image_path = temp_path
        self.update_image_display()

        label = CTkLabel(master=self.app, text ="Screen captured. Enter query and click Research.")
        label.configure()

    #def on_add_image_clicked(self):
        """File dialog for image"""
    
    def on_research_clicked(self):
        """Start research in thread"""
        from gui_worker import AgentWorker

        query_text = self.query_textbox.get('1', 'end-1c')

        if not query_text.strip():
            raise RuntimeError("No query entered")
            return
        
        self.worker_thread = AgentWorker(
            query = self.query,
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
            #update progress
            print(f"Progress: {msg}, ({pct}%)")
        else:
            msg = data
            print(f"Status: {msg}")
    
    def check_progress(self):
        """Check if worker is done"""
        if self.worker_thread and self.worker_thread.is_alive():
            #still running check again in 100 ms
            self.app.after(100, self.check_progress)
        else:
            #finished
            if self.worker_thread and self.worker_thread.result:
                self.display_results(self.worker_thread.result)
    
    def on_stop_clicked(self):
        """Stop button"""
        if self.worker_thread:
            self.worker_thread.stop()
    
    def on_export_clicked(self):
        """Export results as json"""
    
    def on_copy_results(self):
        """Copy button"""
        pyperclip.copy(self.response)
        label = CTkLabel(master= self.app, text = "Results copied to clipboard")
        label.pack(padx = 10, pady = 10)
        time.sleep(2)
        label.pack_forget()

    
    def display_results(self, response):
        self.repsonse = response.summary
        print(f"Results: {response.summary}")

    def setup_ui(self):
        frame = CTkFrame(master = self.app, fg_color="#ffd6e8", border_color="#e7c6ff", border_width=2)
        frame.pack(fill="both", expand =True)

        query_textbox = CTkTextbox(master=frame, border_width = 2, fg_color="#cdb4db",border_color = "#bde0fe")
        query_textbox.pack(padx=10, pady=10)
        self.query = query_textbox.get('1.0', 'end-1c')

        query_btn = CTkButton(master = frame, text="Research", border_width = 2, fg_color = "#cdb4db", border_color ="#bde0fe", hover_color="#bde0fe",command= self.on_research_clicked, command = query_textbox.delete('1.0', 'end-1c'))
        query_btn.pack(pady = 5)

        copy_btn = CTkButton(master = frame, text = "Copy Text", border_width = 2, fg_color = "#cdb4db", border_color ="#bde0fe", hover_color="#bde0fe", command = self.on_copy_results)

        ss_btn = CTkButton(master = frame, text = "Read Screen", corner_radius = 32, fg_color="#cdb4db", hover_color="#bde0fe",
                        border_color="#bde0fe", border_width = 2, command=self.on_read_screen_clicked)
        ss_btn.place(relx = 0.5, rely = 0.5, anchor = "s")
    
    def run(self):
        """Start GUI"""