from customtkinter import *

from PIL import ImageGrab

class AgentGUI:

    def __init__(self):
        self.app = CTk()
        self.app.geometry("500x400")
        self.setup_ui()
        self.worker_thread = None
        set_appearance_mode("dark")

    def on_read_screen_clicked(self):
        screenshot = ImageGrab.grab()

        temp_path = "/tmp/screen_capture.png"
        screenshot.save(temp_path)

        self.selected_image_path = temp_path
        self.update_image_display()

        label = CTkLabel(master=self.app, text ="Screen captured. Enter query and click Research.")
        label.configure()

    def on_add_image_clicked(self):
        """File dialog for image"""
    
    def on_research_clicked(self):
        """Start research in thread"""
    
    def on_stop_clicked(self):
        """Stop button"""
    
    def on_export_clicked(self):
        """Export results as json"""
    
    def on_copy_results(self):
        """Copy button"""
    
    def display_results(self, response):
        """Show ResearchResponse"""

     def setup_ui(self):
        frame = CTkFrame(master = self.app, text = "Frame", fg_color="#8c1d18", border_color="#050305", border_width=2)

        btn = CTkButton(master = frame, text = "Click me", corner_radius = 32, fg_color="#4158D0", hover_color="#C850C0",
                        border_color="#FFCC70", border_width = 2)
        btn.place(relx = 0.5, rely = 0.5, anchor = "center")

        ss_btn = CTkButton(master=frame, text="Screenshot", command=on_read_screen_clicked)
    
    def run(self):
        """Start GUI"""