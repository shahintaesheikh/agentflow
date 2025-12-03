import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab

class AgentGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        self.worker_thread = None

    def setup_ui(self):
        """Build UI components"""

    def on_read_screen_clicked(self):
        screenshot = ImageGrab.grab()

        temp_path = "/tmp/screen_capture.png"
        screenshot.save(temp_path)

        self.selected_image_path = temp_path
        self.update_image_display()

        messagebox.showinfo("Screen captured. Enter query and click Research.")
    
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
    
    def run(self):
        """Start GUI"""