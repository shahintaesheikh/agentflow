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
        self.app.geometry("500x400")
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

        label = CTkLabel(master=self.frame, text ="Screen captured. Enter query and click Research.", text_color = "green")
        label.pack(padx = 10, pady = 10)
        self.app.after(5000, label.destroy)

    #def on_add_image_clicked(self):
        """File dialog for image"""
    
    def on_research_clicked(self):
        """Start research in thread"""
        from gui_worker import AgentWorker

        query_text = self.query_textbox.get('1.0', 'end-1c')

        if not query_text.strip():
            error_label = CTkLabel(master = self.frame, text = "Please enter a query", text_color = "red")
            error_label.pack(padx = 10, pady = 10)
            self.app.after(3000, error_label.destroy)
            return
        
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
        if not self.worker_thread or not self.worker_thread.result:
            return
        
        result_dict = self.worker_thread.result.model_dump()
        result_dict['exported_at'] = datetime.now().isoformat()

        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding = 'utf-8') as f:
                json.dump(result_dict, f, indent = 2, ensure_ascii= False)

            print(f"Exported to {filename}")

            success_label = CTkLabel(master=self.frame, text = f"Saved: {filename}", text_color = "green")
            success_label.pack(padx=10, pady=10)
            self.app.after(3000, success_label.destroy)
        except Exception as e:
            print(f"Export failed: {e}")

    def on_copy_results(self):
        """Copy button"""
        if not self.worker_thread or not self.worker_thread.result:
            error_label = CTkLabel(master = self.frame, text = "No output to copy", text_color="red")
            error_label.pack(padx = 10, pady = 10)
            self.app.after(3000, error_label.destroy)
            return

        formatted_text = f"""Topic: {self.worker_thread.result.topic}
                            
                            Summary: {self.worker_thread.result.summary}
                            
                            Sources: {', '.join(self.worker_thread.result.sources) if self.worker_thread.result.sources else 'None'}
                            
                            Tools Used: {', '.join(self.worker_thread.result.tools_used) if self.worker_thread.result.tools_used else 'None'}"""
        
        pyperclip.copy(formatted_text)
        label = CTkLabel(master= self.frame, text = "Results copied to clipboard")
        label.pack(padx = 10, pady = 10)
        self.app.after(3000, label.destroy)

    
    def display_results(self, response : ResearchResponse):
        formatted_text = f"""Topic: {response.topic}

        {response.summary}

        Tools Used: {', '.join(response.tools_used)}

        Sources: {', '.join(response.sources)}"""

        result_textbox = CTkTextbox(master = self.frame, width = 460, height= 200)
        result_textbox.insert("1.0", formatted_text)
        result_textbox.pack(padx = 20, pady = 20)
        result_textbox.configure(state= "disabled") #read only

        clear = CTkButton(master = self.frame, text = "Clear Response", command = result_textbox.destroy)
        clear.pack(padx = 20, pady = 25)

    def setup_ui(self):
        self.query_textbox = CTkTextbox(master=self.frame, border_width = 2, fg_color="#cdb4db",border_color = "#bde0fe")
        self.query_textbox.pack(padx=10, pady=10)

        query_btn = CTkButton(master = self.frame, text="Research", border_width = 2, fg_color = "#cdb4db", border_color ="#bde0fe", hover_color="#bde0fe",command= self.on_research_clicked)
        query_btn.pack(pady = 5)

        copy_btn = CTkButton(master = self.frame, text = "Copy Text", border_width = 2, fg_color = "#cdb4db", border_color ="#bde0fe", hover_color="#bde0fe", command = self.on_copy_results)
        copy_btn.pack(pady = 10)

        ss_btn = CTkButton(master = self.frame, text = "Read Screen", corner_radius = 32, fg_color="#cdb4db", hover_color="#bde0fe",
                        border_color="#bde0fe", border_width = 2, command=self.on_read_screen_clicked)
        ss_btn.place(relx = 0.5, rely = 0.5, anchor = "s")

        export_btn = CTkButton(master = self.frame, text ="Export JSON", border_width = 2, fg_color = "#cdb4db", border_color ="#bde0fe", hover_color="#bde0fe", command = self.on_export_clicked)
        export_btn.pack(pady = 15)

        stop_btn = CTkButton(master = self.frame, text = "Stop", border_width = 2, fg_color = "#cdb4db", border_color ="#bde0fe", hover_color="#bde0fe", command = self.on_stop_clicked)
        stop_btn.pack(pady = 20)
    
    def run(self):
        """Start GUI"""
        self.app.mainloop()

if __name__ == "__main__":
    gui = AgentGUI()
    gui.run()