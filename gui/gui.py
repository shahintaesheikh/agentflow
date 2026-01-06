from customtkinter import *
from gui_worker import AgentWorker
from PIL import ImageGrab
import pyperclip
import json
from datetime import datetime
from tkinter import filedialog
from agent import ResearchResponse

class AgentGUI:
    """Modern AI Research Assistant GUI with sleek dark theme and glass-morphism effects"""

    # Design System Constants
    COLORS = {
        'bg_primary': '#1a1a1a',
        'bg_secondary': '#2d2d2d',
        'bg_card': '#1e1e2e',
        'accent_primary': '#00d4ff',
        'accent_secondary': '#9d4edd',
        'success': '#14f195',
        'error': '#ff4757',
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0a0',
        'text_tertiary': '#6b6b6b',
        'border': '#3d3d3d',
        'hover': '#3a3a3a'
    }

    FONTS = {
        'heading': ("Segoe UI", 20, "bold"),
        'subheading': ("Segoe UI", 14, "bold"),
        'body': ("Segoe UI", 12),
        'caption': ("Segoe UI", 10),
        'button': ("Segoe UI", 11, "bold")
    }

    def __init__(self):
        self.app = CTk()
        self.app.geometry("900x750")
        self.app.title("AI Research Assistant")
        self.worker_thread = None
        self.selected_image_path = None

        # Set dark theme
        set_appearance_mode("dark")
        set_default_color_theme("blue")

        # Configure window background
        self.app.configure(fg_color=self.COLORS['bg_primary'])

        # Main container with padding
        self.main_frame = CTkFrame(master=self.app, fg_color=self.COLORS['bg_primary'])
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.setup_ui()

    def setup_ui(self):
        """Build the modern UI layout"""

        # === HEADER BAR ===
        self.create_header()

        # === CONTENT CONTAINER ===
        content_frame = CTkFrame(master=self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # === INPUT SECTION ===
        self.create_input_section(content_frame)

        # === ACTION BUTTONS ===
        self.create_action_buttons(content_frame)

        # === PROGRESS SECTION ===
        self.create_progress_section(content_frame)

        # === RESULTS CARD ===
        self.create_results_section(content_frame)

        # === BOTTOM ACTIONS ===
        self.create_bottom_actions(content_frame)

    def create_header(self):
        """Create custom header bar with app title and status"""
        header = CTkFrame(master=self.main_frame, fg_color=self.COLORS['bg_secondary'],
                         height=60, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # App title
        title_label = CTkLabel(master=header, text="⚡ AI Research Assistant",
                              font=self.FONTS['heading'], text_color=self.COLORS['text_primary'])
        title_label.pack(side="left", padx=20, pady=15)

        # Status indicator
        self.status_frame = CTkFrame(master=header, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20)

        self.status_dot = CTkLabel(master=self.status_frame, text="●",
                                  font=("Segoe UI", 16), text_color=self.COLORS['success'])
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_text = CTkLabel(master=self.status_frame, text="Ready",
                                   font=self.FONTS['caption'], text_color=self.COLORS['text_secondary'])
        self.status_text.pack(side="left")

    def create_input_section(self, parent):
        """Create modern input section with search-style textbox"""
        input_container = CTkFrame(master=parent, fg_color="transparent")
        input_container.pack(fill="x", pady=(20, 15))

        # Input label
        input_label = CTkLabel(master=input_container, text="Research Query",
                              font=self.FONTS['subheading'], text_color=self.COLORS['text_primary'],
                              anchor="w")
        input_label.pack(fill="x", pady=(0, 8))

        # Input field with modern styling
        self.query_textbox = CTkTextbox(
            master=input_container,
            height=100,
            wrap="word",
            fg_color=self.COLORS['bg_secondary'],
            text_color=self.COLORS['text_primary'],
            border_color=self.COLORS['border'],
            border_width=1,
            corner_radius=12,
            font=self.FONTS['body']
        )
        self.query_textbox.pack(fill="x", pady=(0, 12))

        # Screenshot button (modern pill style)
        self.screenshot_btn = CTkButton(
            master=input_container,
            text="📸  Capture Screen",
            font=self.FONTS['button'],
            fg_color=self.COLORS['bg_secondary'],
            hover_color=self.COLORS['hover'],
            text_color=self.COLORS['text_secondary'],
            border_color=self.COLORS['border'],
            border_width=1,
            corner_radius=20,
            height=36,
            command=self.on_read_screen_clicked
        )
        self.screenshot_btn.pack(anchor="w")

    def create_action_buttons(self, parent):
        """Create primary action buttons"""
        action_container = CTkFrame(master=parent, fg_color="transparent")
        action_container.pack(fill="x", pady=15)

        button_frame = CTkFrame(master=action_container, fg_color="transparent")
        button_frame.pack()

        # Primary Research button with cyan accent
        self.research_btn = CTkButton(
            master=button_frame,
            text="🔍  Start Research",
            font=self.FONTS['button'],
            fg_color=self.COLORS['accent_primary'],
            hover_color="#00b8e6",
            text_color="#000000",
            corner_radius=8,
            height=44,
            width=160,
            command=self.on_research_clicked
        )
        self.research_btn.pack(side="left", padx=6)

        # Stop button with secondary styling
        self.stop_btn = CTkButton(
            master=button_frame,
            text="⏹  Stop",
            font=self.FONTS['button'],
            fg_color=self.COLORS['bg_secondary'],
            hover_color=self.COLORS['hover'],
            text_color=self.COLORS['text_secondary'],
            border_color=self.COLORS['border'],
            border_width=1,
            corner_radius=8,
            height=44,
            width=120,
            command=self.on_stop_clicked
        )
        self.stop_btn.pack(side="left", padx=6)

    def create_progress_section(self, parent):
        """Create modern progress bar with gradient effect"""
        progress_container = CTkFrame(master=parent, fg_color="transparent")
        progress_container.pack(fill="x", pady=15)

        # Progress bar with modern styling
        self.progress_bar = CTkProgressBar(
            master=progress_container,
            height=8,
            corner_radius=4,
            fg_color=self.COLORS['bg_secondary'],
            progress_color=self.COLORS['accent_primary'],
            border_width=0
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)

        # Progress label with percentage
        self.progress_label = CTkLabel(
            master=progress_container,
            text="Ready to research",
            font=self.FONTS['caption'],
            text_color=self.COLORS['text_tertiary']
        )
        self.progress_label.pack()

    def create_results_section(self, parent):
        """Create glass-morphism results card"""
        # Results card with glass effect
        self.results_card = CTkFrame(
            master=parent,
            fg_color=self.COLORS['bg_card'],
            border_color=self.COLORS['border'],
            border_width=1,
            corner_radius=16
        )
        self.results_card.pack(fill="both", expand=True, pady=15)

        # Scrollable frame for results
        self.results_scroll = CTkScrollableFrame(
            master=self.results_card,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['bg_secondary'],
            scrollbar_button_hover_color=self.COLORS['hover']
        )
        self.results_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # Placeholder
        self.results_placeholder = CTkLabel(
            master=self.results_scroll,
            text="Results will appear here\n\nEnter a query and click 'Start Research' to begin",
            font=self.FONTS['body'],
            text_color=self.COLORS['text_tertiary'],
            justify="center"
        )
        self.results_placeholder.pack(expand=True, pady=60)

    def create_bottom_actions(self, parent):
        """Create bottom action buttons for export/copy"""
        bottom_container = CTkFrame(master=parent, fg_color="transparent")
        bottom_container.pack(fill="x", pady=(5, 0))

        button_frame = CTkFrame(master=bottom_container, fg_color="transparent")
        button_frame.pack()

        # Copy button
        self.copy_btn = CTkButton(
            master=button_frame,
            text="📋  Copy Results",
            font=self.FONTS['button'],
            fg_color=self.COLORS['bg_secondary'],
            hover_color=self.COLORS['hover'],
            text_color=self.COLORS['text_secondary'],
            border_color=self.COLORS['border'],
            border_width=1,
            corner_radius=8,
            height=40,
            width=140,
            command=self.on_copy_results
        )
        self.copy_btn.pack(side="left", padx=6)

        # Export button with accent
        self.export_btn = CTkButton(
            master=button_frame,
            text="💾  Export JSON",
            font=self.FONTS['button'],
            fg_color=self.COLORS['accent_secondary'],
            hover_color="#8b3ed4",
            text_color=self.COLORS['text_primary'],
            corner_radius=8,
            height=40,
            width=140,
            command=self.on_export_clicked
        )
        self.export_btn.pack(side="left", padx=6)

    # ========== EVENT HANDLERS ==========

    def on_read_screen_clicked(self):
        """Capture screenshot for vision analysis"""
        screenshot = ImageGrab.grab()
        temp_path = "/tmp/screen_capture.png"
        screenshot.save(temp_path)
        self.selected_image_path = temp_path

        self.update_status("Screen captured successfully", "success")
        self.app.after(5000, lambda: self.update_status("Ready", "success"))

    def on_research_clicked(self):
        """Start research in background thread"""
        query_text = self.query_textbox.get('1.0', 'end-1c')

        if not query_text.strip():
            self.update_status("Please enter a query", "error")
            self.app.after(3000, lambda: self.update_status("Ready", "success"))
            return

        # Disable buttons during research
        self.research_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.screenshot_btn.configure(state="disabled")

        # Reset progress
        self.progress_bar.set(0)
        self.update_status("Researching...", "active")

        self.worker_thread = AgentWorker(
            query=query_text,
            image_path=self.selected_image_path,
            max_iter=10,
            callback=self.update_progress
        )

        self.worker_thread.start()
        self.check_progress()

    def update_progress(self, data):
        """Update progress bar and status from worker thread"""
        if isinstance(data, tuple):
            msg, pct = data
            if pct >= 0:
                self.progress_bar.set(pct / 100)
                self.progress_label.configure(text=f"{msg} ({pct}%)")
                self.status_text.configure(text="Processing...")
            else:
                # Error state
                self.update_status(msg, "error")
        else:
            self.progress_label.configure(text=data)

    def check_progress(self):
        """Monitor worker thread completion"""
        if self.worker_thread and self.worker_thread.is_alive():
            self.app.after(100, self.check_progress)
        else:
            # Re-enable buttons
            self.research_btn.configure(state="normal")
            self.copy_btn.configure(state="normal")
            self.export_btn.configure(state="normal")
            self.screenshot_btn.configure(state="normal")

            if self.worker_thread and self.worker_thread.result:
                self.display_results(self.worker_thread.result)
                self.update_status("Research complete", "success")
            else:
                self.update_status("Ready", "success")

    def on_stop_clicked(self):
        """Stop research execution"""
        if self.worker_thread:
            self.worker_thread.stop()
            self.update_status("Research stopped", "error")

    def on_export_clicked(self):
        """Export results to JSON file"""
        if not self.worker_thread or not self.worker_thread.result:
            self.update_status("No results to export", "error")
            self.app.after(3000, lambda: self.update_status("Ready", "success"))
            return

        result_dict = self.worker_thread.result.model_dump()
        result_dict['exported_at'] = datetime.now().isoformat()
        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            self.update_status(f"Exported: {filename}", "success")
            self.app.after(5000, lambda: self.update_status("Ready", "success"))
        except Exception as e:
            self.update_status(f"Export failed: {e}", "error")
            self.app.after(5000, lambda: self.update_status("Ready", "success"))

    def on_copy_results(self):
        """Copy results to clipboard"""
        if not self.worker_thread or not self.worker_thread.result:
            self.update_status("No results to copy", "error")
            self.app.after(3000, lambda: self.update_status("Ready", "success"))
            return

        formatted_text = f"""Topic: {self.worker_thread.result.topic}

Summary: {self.worker_thread.result.summary}

Sources: {', '.join(self.worker_thread.result.sources) if self.worker_thread.result.sources else 'None'}

Tools Used: {', '.join(self.worker_thread.result.tools_used) if self.worker_thread.result.tools_used else 'None'}"""

        pyperclip.copy(formatted_text)
        self.update_status("Copied to clipboard", "success")
        self.app.after(3000, lambda: self.update_status("Ready", "success"))

    def display_results(self, response: ResearchResponse):
        """Display research results in modern card layout"""
        # Clear previous results
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        # Topic header
        topic_frame = CTkFrame(master=self.results_scroll, fg_color="transparent")
        topic_frame.pack(fill="x", padx=20, pady=(20, 10))

        topic_icon = CTkLabel(master=topic_frame, text="📊", font=("Segoe UI", 24))
        topic_icon.pack(side="left", padx=(0, 12))

        topic_label = CTkLabel(
            master=topic_frame,
            text=response.topic,
            font=("Segoe UI", 18, "bold"),
            text_color=self.COLORS['text_primary'],
            anchor="w",
            justify="left"
        )
        topic_label.pack(side="left", fill="x", expand=True)

        # Summary card
        summary_card = CTkFrame(
            master=self.results_scroll,
            fg_color=self.COLORS['bg_secondary'],
            corner_radius=12
        )
        summary_card.pack(fill="both", expand=True, padx=20, pady=15)

        summary_header = CTkLabel(
            master=summary_card,
            text="Summary",
            font=self.FONTS['subheading'],
            text_color=self.COLORS['accent_primary'],
            anchor="w"
        )
        summary_header.pack(fill="x", padx=20, pady=(20, 10))

        summary_text = CTkTextbox(
            master=summary_card,
            wrap="word",
            fg_color="transparent",
            text_color=self.COLORS['text_primary'],
            font=("Segoe UI", 12),
            border_width=0,
            height=200
        )
        summary_text.insert("1.0", response.summary)
        summary_text.configure(state="disabled")
        summary_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Metadata section
        meta_frame = CTkFrame(master=self.results_scroll, fg_color="transparent")
        meta_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Tools used
        if response.tools_used:
            tools_label = CTkLabel(
                master=meta_frame,
                text=f"🔧 Tools: {', '.join(response.tools_used)}",
                font=self.FONTS['caption'],
                text_color=self.COLORS['text_tertiary'],
                anchor="w"
            )
            tools_label.pack(fill="x", pady=4)

        # Sources count
        sources_label = CTkLabel(
            master=meta_frame,
            text=f"📚 Sources: {len(response.sources)} found",
            font=self.FONTS['caption'],
            text_color=self.COLORS['text_tertiary'],
            anchor="w"
        )
        sources_label.pack(fill="x", pady=4)

    def update_status(self, message: str, status_type: str = "success"):
        """Update status indicator and message"""
        color_map = {
            "success": self.COLORS['success'],
            "error": self.COLORS['error'],
            "active": self.COLORS['accent_primary']
        }

        self.status_dot.configure(text_color=color_map.get(status_type, self.COLORS['success']))
        self.status_text.configure(text=message)
        self.progress_label.configure(text=message)

    def run(self):
        """Start the GUI application"""
        self.app.mainloop()


if __name__ == "__main__":
    gui = AgentGUI()
    gui.run()
