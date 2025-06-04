import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import queue
import logging
from typing import Callable, Optional
import os
import json

# Frutiger Aero color palette
AERO_BG = '#eaf6fb'  # light blue/white
AERO_ACCENT = '#1ca3b5'  # teal from logo
AERO_DARK = '#22292f'  # dark for text
AERO_BUTTON = '#e3f1fa'  # glossy button
AERO_BUTTON_HOVER = '#b8e6f7'
AERO_BORDER = '#b2c7d9'
AERO_SHADOW = '#b0c4d8'
AERO_WHITE = '#ffffff'
AERO_GRAY = '#e0e0e0'
AERO_FONT = 'Segoe UI'

class SpotifyDownloaderGUI:
    def __init__(self):
        """Initialize the GUI."""
        self.cancel_requested = False
        self.setup_logging()
        self.setup_window()
        self.setup_widgets()
        self.setup_queue()
        self.spotify_handler = None

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_window(self):
        """Set up the main window."""
        self.window = ctk.CTk()
        self.window.title("ipodfiller")
        self.window.geometry("820x640")
        self.window.minsize(820, 640)
        self.window.configure(bg=AERO_BG)
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def setup_queue(self):
        """Set up queue for thread-safe communication."""
        self.queue = queue.Queue()
        self.window.after(100, self.process_queue)

    def set_spotify_handler(self, handler):
        """Set the Spotify handler instance."""
        self.spotify_handler = handler
        if not handler.is_configured():
            self.show_credentials_dialog()

    def show_credentials_dialog(self):
        """Show dialog for entering Spotify credentials."""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Spotify Credentials - ipodfiller")
        dialog.geometry("520x420")
        dialog.minsize(520, 420)
        dialog.configure(bg=AERO_BG)
        dialog.transient(self.window)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog, fg_color=AERO_BG, corner_radius=18)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        instructions = (
            "To get your Spotify credentials:\n\n"
            "1. Go to https://developer.spotify.com/dashboard\n"
            "2. Log in with your Spotify account\n"
            "3. Click 'Create App'\n"
            "4. Fill in the app details (name and description)\n"
            "5. Accept the terms and create the app\n"
            "6. Copy the Client ID and Client Secret\n"
            "7. Paste them below and click Save"
        )
        instructions_label = tk.Label(
            main_frame,
            text=instructions,
            justify="left",
            font=(AERO_FONT, 11),
            wraplength=450,
            bg=AERO_BG,
            fg=AERO_DARK
        )
        instructions_label.pack(pady=(0, 12), anchor='w')

        cred_frame = ctk.CTkFrame(main_frame, fg_color=AERO_WHITE, corner_radius=12)
        cred_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        tk.Label(cred_frame, text="Client ID:", font=(AERO_FONT, 11, "bold"), bg=AERO_WHITE, fg=AERO_DARK).pack(pady=(10, 2), anchor='w', padx=10)
        client_id_entry = ctk.CTkEntry(cred_frame, width=400, height=35, font=(AERO_FONT, 12))
        client_id_entry.pack(pady=(0, 10), padx=10)

        tk.Label(cred_frame, text="Client Secret:", font=(AERO_FONT, 11, "bold"), bg=AERO_WHITE, fg=AERO_DARK).pack(pady=(0, 2), anchor='w', padx=10)
        client_secret_entry = ctk.CTkEntry(cred_frame, width=400, height=35, font=(AERO_FONT, 12), show='*')
        client_secret_entry.pack(pady=(0, 10), padx=10)

        def save_credentials():
            client_id = client_id_entry.get().strip()
            client_secret = client_secret_entry.get().strip()
            if not client_id or not client_secret:
                messagebox.showerror("Error", "Please enter both Client ID and Client Secret")
                return
            if self.spotify_handler.configure(client_id, client_secret):
                config = {'client_id': client_id, 'client_secret': client_secret}
                config_path = os.path.join(os.path.dirname(__file__), 'config.json')
                try:
                    with open(config_path, 'w') as f:
                        json.dump(config, f)
                except Exception as e:
                    logging.error(f"Failed to save config: {str(e)}")
                dialog.destroy()
                messagebox.showinfo("Success", "Credentials saved successfully!")
            else:
                messagebox.showerror("Error", "Invalid credentials")

        # Save button at the bottom, always visible
        save_btn_frame = ctk.CTkFrame(dialog, fg_color=AERO_BG)
        save_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 16))
        ctk.CTkButton(
            save_btn_frame,
            text="Save Credentials",
            width=200,
            height=40,
            font=(AERO_FONT, 12, "bold"),
            fg_color=AERO_ACCENT,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_WHITE,
            command=save_credentials
        ).pack(pady=0)

    def setup_widgets(self):
        """Set up all GUI widgets."""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.window, fg_color=AERO_BG, corner_radius=18)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # App title
        title_label = tk.Label(
            self.main_frame,
            text="ipodfiller",
            font=(AERO_FONT, 28, "bold"),
            bg=AERO_BG,
            fg=AERO_ACCENT
        )
        title_label.pack(pady=(10, 0), anchor='n')

        # URL input
        self.url_label = ctk.CTkLabel(
            self.main_frame,
            text="Spotify Playlist URL:",
            font=(AERO_FONT, 14),
            text_color=AERO_DARK,
            fg_color=AERO_BG
        )
        self.url_label.pack(pady=(30, 5), anchor="w", padx=90)

        self.url_entry = ctk.CTkEntry(
            self.main_frame,
            width=600,
            height=35,
            font=(AERO_FONT, 12),
            fg_color=AERO_WHITE,
            border_color=AERO_BORDER,
            border_width=2
        )
        self.url_entry.pack(pady=(0, 20), padx=90)

        # Download directory selection
        self.dir_frame = ctk.CTkFrame(self.main_frame, fg_color=AERO_BG)
        self.dir_frame.pack(fill=tk.X, pady=(0, 20), padx=90)

        self.dir_label = ctk.CTkLabel(
            self.dir_frame,
            text="Download Directory:",
            font=(AERO_FONT, 14),
            text_color=AERO_DARK,
            fg_color=AERO_BG
        )
        self.dir_label.pack(side=tk.LEFT, padx=(0, 10))

        self.dir_entry = ctk.CTkEntry(
            self.dir_frame,
            width=400,
            height=35,
            font=(AERO_FONT, 12),
            fg_color=AERO_WHITE,
            border_color=AERO_BORDER,
            border_width=2
        )
        self.dir_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.browse_button = ctk.CTkButton(
            self.dir_frame,
            text="Browse",
            width=100,
            fg_color=AERO_BUTTON,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_DARK,
            font=(AERO_FONT, 12),
            command=self.browse_directory
        )
        self.browse_button.pack(side=tk.LEFT)

        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color=AERO_BG)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20), padx=90)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Progress:",
            font=(AERO_FONT, 14),
            text_color=AERO_DARK,
            fg_color=AERO_BG
        )
        self.progress_label.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=600,
            fg_color=AERO_GRAY,
            progress_color=AERO_ACCENT
        )
        self.progress_bar.pack(pady=(5, 10))
        self.progress_bar.set(0)

        # Status text
        self.status_text = ctk.CTkTextbox(
            self.main_frame,
            width=600,
            height=200,
            font=(AERO_FONT, 12),
            fg_color=AERO_WHITE,
            border_color=AERO_BORDER,
            border_width=2,
            text_color=AERO_DARK
        )
        self.status_text.pack(pady=(0, 20), padx=90)

        # In-app prompt for another download (initially hidden)
        self.another_frame = ctk.CTkFrame(self.main_frame, fg_color=AERO_BG)
        self.another_label = ctk.CTkLabel(
            self.another_frame,
            text="Download completed successfully! Download another playlist?",
            font=(AERO_FONT, 14),
            text_color=AERO_DARK,
            fg_color=AERO_BG
        )
        self.another_label.pack(side=tk.LEFT, padx=(0, 10))
        self.another_yes = ctk.CTkButton(
            self.another_frame,
            text="Yes",
            width=80,
            fg_color=AERO_ACCENT,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_WHITE,
            font=(AERO_FONT, 12, "bold"),
            command=self.reset_for_new_download_and_hide_prompt
        )
        self.another_yes.pack(side=tk.LEFT, padx=(0, 10))
        self.another_no = ctk.CTkButton(
            self.another_frame,
            text="No",
            width=80,
            fg_color=AERO_BUTTON,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_DARK,
            font=(AERO_FONT, 12),
            command=self.hide_another_prompt
        )
        self.another_no.pack(side=tk.LEFT)
        self.another_frame.pack_forget()

        # Control buttons
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color=AERO_BG)
        self.button_frame.pack(fill=tk.X, padx=90)

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Download",
            width=150,
            fg_color=AERO_ACCENT,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_WHITE,
            font=(AERO_FONT, 12, "bold"),
            command=self.start_download
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            width=150,
            fg_color=AERO_BUTTON,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_DARK,
            font=(AERO_FONT, 12),
            command=self.cancel_download,
            state="disabled"
        )
        self.cancel_button.pack(side=tk.LEFT)

        # Settings button
        self.settings_button = ctk.CTkButton(
            self.button_frame,
            text="Settings",
            width=100,
            fg_color=AERO_BUTTON,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_DARK,
            font=(AERO_FONT, 12),
            command=self.show_credentials_dialog
        )
        self.settings_button.pack(side=tk.RIGHT)

        # Instructions button next to Settings
        self.instructions_button = ctk.CTkButton(
            self.button_frame,
            text="Instructions",
            width=120,
            fg_color=AERO_BUTTON,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_DARK,
            font=(AERO_FONT, 12),
            command=self.show_instructions_panel
        )
        self.instructions_button.pack(side=tk.RIGHT, padx=(0, 10))

        # Instructions panel (hidden by default)
        self.instructions_panel = None

    def browse_directory(self):
        """Open directory selection dialog."""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def update_status(self, message: str):
        """Update the status text box."""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)

    def update_progress(self, value: float):
        """Update the progress bar."""
        self.progress_bar.set(value)

    def process_queue(self):
        """Process messages from the queue."""
        try:
            while True:
                message = self.queue.get_nowait()
                if isinstance(message, str):
                    if message.strip() == "DONE":
                        self.download_complete()
                    else:
                        self.update_status(message)
                elif isinstance(message, float):
                    self.update_progress(message)
                elif message == "ERROR":
                    self.download_error()
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.process_queue)

    def start_download(self):
        """Start the download process."""
        if not self.spotify_handler.is_configured():
            messagebox.showerror("Error", "Please configure Spotify credentials first")
            self.show_credentials_dialog()
            return

        url = self.url_entry.get().strip()
        directory = self.dir_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a Spotify playlist URL")
            return

        if not directory:
            messagebox.showerror("Error", "Please select a download directory")
            return

        if not os.path.exists(directory):
            messagebox.showerror("Error", "Selected directory does not exist")
            return

        self.start_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.progress_bar.set(0)
        self.cancel_requested = False

        # Start download in a separate thread
        self.download_thread = threading.Thread(
            target=self.download_process,
            args=(url, directory)
        )
        self.download_thread.start()

    def cancel_download(self):
        """Cancel the download process."""
        if hasattr(self, 'download_thread') and self.download_thread.is_alive():
            self.cancel_requested = True
            self.update_status("Cancelling download...")
            self.cancel_button.configure(state="disabled")

    def download_complete(self):
        """Handle download completion."""
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.show_another_prompt()

    def show_another_prompt(self):
        self.another_frame.pack(pady=(0, 20), padx=90)

    def hide_another_prompt(self):
        self.another_frame.pack_forget()

    def reset_for_new_download_and_hide_prompt(self):
        self.reset_for_new_download()
        self.hide_another_prompt()

    def download_error(self):
        """Handle download error."""
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        messagebox.showerror("Error", "An error occurred during download")

    def download_process(self, url: str, directory: str):
        """Main download process (to be implemented by the main application)."""
        pass

    def is_cancelled(self):
        return self.cancel_requested

    def reset_for_new_download(self):
        self.url_entry.delete(0, tk.END)
        self.status_text.delete(1.0, tk.END)
        self.progress_bar.set(0)
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")

    def show_instructions_panel(self):
        if self.instructions_panel is not None:
            return  # Already open
        # Panel size: 80% width, 80% height, always centered
        panel_width = int(self.window.winfo_width() * 0.8)
        panel_height = int(self.window.winfo_height() * 0.8)
        self.instructions_panel = ctk.CTkFrame(
            self.window,
            fg_color=AERO_WHITE,
            corner_radius=18,
            width=panel_width,
            height=panel_height
        )
        self.instructions_panel.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            self.instructions_panel,
            text="How to Use ipodfiller",
            font=(AERO_FONT, 20, "bold"),
            text_color=AERO_ACCENT
        )
        title.pack(pady=(20, 10))

        instructions = (
            "1. Click the Settings button and enter your Spotify API credentials.\n"
            "2. Paste a public Spotify playlist URL into the 'Spotify Playlist URL' field.\n"
            "3. Choose a download directory where your music will be saved.\n"
            "4. Click 'Start Download' to begin.\n"
            "5. Watch the progress and status updates.\n"
            "6. When finished, you can download another playlist or close the app.\n"
            "\nNotes:\n- Only public Spotify playlists are supported.\n- You need FFmpeg installed and accessible in your system PATH.\n- Downloaded files will be MP3s with full metadata."
        )
        disclaimer = (
            "\nDisclaimer:\n"
            "This app is for personal use only. Download only music you have the legal right to access. "
            "You are responsible for complying with copyright laws. The author is not liable for misuse."
        )
        full_text = instructions + disclaimer

        instr_label = ctk.CTkTextbox(
            self.instructions_panel,
            width=panel_width - 40,
            height=panel_height - 120,
            font=(AERO_FONT, 13),
            fg_color=AERO_WHITE,
            border_color=AERO_BORDER,
            border_width=1,
            text_color=AERO_DARK,
            wrap='word',
            activate_scrollbars=True
        )
        instr_label.insert("1.0", full_text)
        instr_label.configure(state="disabled")
        instr_label.pack(padx=20, pady=(0, 10), fill='both', expand=True)

        close_btn = ctk.CTkButton(
            self.instructions_panel,
            text="Close",
            width=100,
            fg_color=AERO_ACCENT,
            hover_color=AERO_BUTTON_HOVER,
            text_color=AERO_WHITE,
            font=(AERO_FONT, 12, "bold"),
            command=self.hide_instructions_panel
        )
        close_btn.pack(pady=(0, 20))

    def hide_instructions_panel(self):
        if self.instructions_panel is not None:
            self.instructions_panel.destroy()
            self.instructions_panel = None

    def run(self):
        """Start the GUI main loop."""
        self.window.mainloop() 