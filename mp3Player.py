#imports
import tkinter as tk
from tkinter import filedialog
import pygame
import os
import random

class Y2KMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 𝓂𝓊𝓈𝒾𝒸 𝓅𝓁𝒶𝓎ℯ𝓇 🎵")
        self.root.geometry("550x580")
        
        # Muted blue color scheme
        self.bg_color = "#4A6FA5"  # Muted blue
        self.accent_color = "#7EB2DD"  # Soft light blue
        self.text_color = "#F0F4F8"  # Off-white
        self.button_bg = "#2C4C6E"  # Dark muted blue
        self.secondary_bg = "#3D5A80"  # Medium muted blue
        self.progress_color = "#98C1D9"  # Pale blue for progress
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.current_song = ""
        self.song_length = 0  # Total duration in seconds
        self.paused = False
        self.playing = False
        self.update_id = None
        self.animation_id = None
        self.seeking = False
        
        # Setup UI
        self.setup_ui()
        
        # Start time update
        self.update_progress()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="✨ 𝓭𝓲𝓰𝓲𝓽𝓪𝓵 𝓶𝓾𝓼𝓲𝓬 𝓹𝓵𝓪𝔂𝓮𝓻 ✨", 
                               font=("Courier New", 14, "bold"),
                               fg=self.text_color, bg=self.bg_color)
        title_label.pack()
        
        stars = tk.Label(title_frame, text="⭐ 🌟 ⭐", 
                        font=("Arial", 12), fg="#FFD700", bg=self.bg_color)
        stars.pack()
        
        self.visualizer = tk.Canvas(main_frame, width=150, height=150, 
                                    bg=self.secondary_bg, highlightthickness=2,
                                    highlightcolor=self.accent_color)
        self.visualizer.pack(pady=(0, 15))
        self.circle = self.visualizer.create_oval(10, 10, 140, 140, outline=self.accent_color, width=3)
        self.visualizer.create_text(75, 75, text="🎵", font=("Arial", 40), 
                                   fill=self.text_color)
        self.visualizer.create_text(75, 110, text="click play", 
                                   font=("Arial", 8), fill=self.accent_color)
        
        self.song_label = tk.Label(main_frame, text="💿 ℕ𝕠 𝕤𝕠𝕟𝕘 𝕝𝕠𝕒𝕕𝕖𝕕 💿", 
                                   font=("Courier New", 12, "bold"),
                                   fg=self.text_color, bg=self.bg_color)
        self.song_label.pack(pady=(0, 5))
        
        self.info_label = tk.Label(main_frame, text="──────────────", 
                                   font=("Arial", 9), fg=self.accent_color, 
                                   bg=self.bg_color)
        self.info_label.pack(pady=(0, 20))
        
        # Progress bar frame
        progress_frame = tk.Frame(main_frame, bg=self.bg_color)
        progress_frame.pack(fill='x', pady=(0, 10))
        
        # Time labels
        self.current_time_label = tk.Label(progress_frame, text="0:00", 
                                          font=("Arial", 10, "bold"), 
                                          fg=self.text_color,
                                          bg=self.bg_color)
        self.current_time_label.pack(side='left')
        
        self.duration_label = tk.Label(progress_frame, text="0:00", 
                                      font=("Arial", 10, "bold"),
                                      fg=self.text_color,
                                      bg=self.bg_color)
        self.duration_label.pack(side='right')
        
        # Progress bar with click and drag functionality
        self.progress_canvas = tk.Canvas(main_frame, height=25, bg=self.secondary_bg,
                                        highlightthickness=2, 
                                        highlightcolor=self.accent_color)
        self.progress_canvas.pack(fill='x', pady=(0, 20))
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 25, 
                                                                  fill=self.progress_color,
                                                                  outline="")
        
        # Progress bar handle/dragger
        self.handle = self.progress_canvas.create_rectangle(-5, 5, 5, 20, 
                                                            fill=self.accent_color,
                                                            outline=self.text_color,
                                                            width=2)
        
        # Bind events for seeking
        self.progress_canvas.bind("<Button-1>", self.start_seek)
        self.progress_canvas.bind("<B1-Motion>", self.drag_seek)
        self.progress_canvas.bind("<ButtonRelease-1>", self.end_seek)
        
        # Control buttons frame
        controls_frame = tk.Frame(main_frame, bg=self.bg_color)
        controls_frame.pack(pady=(0, 20))
        
        button_configs = [
            ("⏮", self.previous_song, 3),
            ("▶", self.play_pause, 4),
            ("⏸", self.pause_music, 3),
            ("⏹", self.stop_music, 3),
            ("⏭", self.next_song, 3)
        ]
        
        self.buttons = {}
        for text, command, width in button_configs:
            btn = tk.Button(controls_frame, text=text, command=command,
                           font=("Arial", 14, "bold"), width=width, height=1,
                           relief="raised", bd=3, bg=self.button_bg, 
                           fg=self.text_color, activebackground=self.accent_color,
                           activeforeground=self.button_bg)
            btn.pack(side='left', padx=5)
            if text == "▶":
                self.play_btn = btn
        
        load_frame = tk.Frame(main_frame, bg=self.bg_color)
        load_frame.pack(pady=(0, 15))
        
        self.load_btn = tk.Button(load_frame, text="📀 𝕃𝕆𝔸𝔻 𝕄𝕌𝕊𝕀ℂ 📀", 
                                 command=self.load_song,
                                 font=("Courier New", 11, "bold"),
                                 bg=self.button_bg, fg=self.text_color,
                                 activebackground=self.accent_color,
                                 relief="raised", bd=3, padx=20, pady=8)
        self.load_btn.pack()
        
        bottom_frame = tk.Frame(main_frame, bg=self.bg_color)
        bottom_frame.pack()
        
        marquee = tk.Label(bottom_frame, text="◈ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ⋯ ◈", 
                          font=("Arial", 8), fg=self.accent_color, bg=self.bg_color)
        marquee.pack(pady=(10, 0))
        
        self.blink_cursor()
    
    def blink_cursor(self):
        # Animated blinking cursor
        cursor_frame = tk.Frame(self.root, bg=self.bg_color)
        cursor_frame.pack(side='bottom', pady=(0, 10))
        
        self.cursor_text = tk.Label(cursor_frame, text="█", font=("Arial", 12, "bold"),
                                   fg=self.accent_color, bg=self.bg_color)
        self.cursor_text.pack()
        
        def blink():
            if hasattr(self, 'cursor_text') and self.cursor_text.winfo_exists():
                current = self.cursor_text.cget("fg")
                new_color = self.bg_color if current == self.accent_color else self.accent_color
                self.cursor_text.config(fg=new_color)
                self.root.after(500, blink)
        
        blink()
    
    def format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def get_song_duration(self, file_path):
        """Get song duration using pygame"""
        try:
            # Load the song to get duration
            pygame.mixer.music.load(file_path)
            return 0
        except:
            return 0
    
    def load_song(self):
        file = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg"), 
                      ("MP3 files", "*.mp3"), 
                      ("All files", "*.*")]
        )
        if file:
            self.current_song = file
            filename = os.path.basename(file)
            if len(filename) > 35:
                filename = filename[:32] + "..."
            
            self.song_label.config(text=f"💿 {filename} 💿")
            
            try:
                sound = pygame.mixer.Sound(file)
                self.song_length = sound.get_length()
                self.duration_label.config(text=self.format_time(self.song_length))
            except:
                try:
                    pygame.mixer.music.load(file)
                    self.song_length = 0
                    self.duration_label.config(text="--:--")
                except:
                    self.song_length = 0
                    self.duration_label.config(text="--:--")
            
            self.info_label.config(text="✦ ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ ✦")
            
            self.current_time_label.config(text="0:00")
            self.update_progress_bar(0)
    
    def update_progress_bar(self, current_time):
        """Update progress bar position based on current time"""
        if self.song_length > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                # Calculate position percentage
                percentage = current_time / self.song_length
                bar_width = width * percentage
                
                # Update the progress bar rectangle
                self.progress_canvas.coords(self.progress_bar, 0, 0, bar_width, 25)
                
                # Update the handle position
                handle_x = bar_width
                self.progress_canvas.coords(self.handle, handle_x - 5, 5, handle_x + 5, 20)
        else:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                wave_pos = (current_time * 50) % width
                self.progress_canvas.coords(self.progress_bar, 0, 0, wave_pos, 25)
    
    def start_seek(self, event):
        """Start seeking when clicking on progress bar"""
        self.seeking = True
        self.drag_seek(event)
    
    def drag_seek(self, event):
        """Handle dragging on progress bar"""
        if self.seeking and self.song_length > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                x = max(0, min(event.x, width))
                percentage = x / width
                seek_time = percentage * self.song_length
                
                self.current_time_label.config(text=self.format_time(seek_time))
                
                self.progress_canvas.coords(self.progress_bar, 0, 0, x, 25)
                self.progress_canvas.coords(self.handle, x - 5, 5, x + 5, 20)
    
    def end_seek(self, event):
        """Finish seeking and jump to position"""
        if self.seeking and self.song_length > 0 and self.current_song:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                # Calculate final seek position
                x = max(0, min(event.x, width))
                percentage = x / width
                seek_time = percentage * self.song_length
                
                # Seek to position if playing
                if self.playing:
                    pygame.mixer.music.play(start=seek_time)
                    if self.paused:
                        pygame.mixer.music.pause()
                
                # Update current time display
                self.current_time_label.config(text=self.format_time(seek_time))
        
        self.seeking = False
    
    def animate_visualizer(self):
        def pulse():
            if self.playing and not self.paused and hasattr(self, 'circle'):
                colors = ["#7EB2DD", "#98C1D9", "#5A8BB8", "#3D5A80", "#4A6FA5"]
                new_color = random.choice(colors)
                self.visualizer.itemconfig(self.circle, outline=new_color)
                self.animation_id = self.root.after(400, pulse)
            elif self.playing and hasattr(self, 'circle'):
                self.animation_id = self.root.after(400, pulse)
        
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        pulse()
    
    def play_pause(self):
        if not self.current_song:
            self.load_song()
            if not self.current_song:
                return
        
        if self.playing and not self.paused:
            # Pause
            pygame.mixer.music.pause()
            self.playing = False
            self.paused = True
            self.play_btn.config(text="▶", bg=self.button_bg)
            self.info_label.config(text="⏸ ᴘᴀᴜsᴇᴅ ⏸")
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
        else:
            # Play or resume
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            else:
                # Get current position from progress bar before playing
                if hasattr(self, 'current_seek_time'):
                    pygame.mixer.music.load(self.current_song)
                    pygame.mixer.music.play(start=self.current_seek_time)
                else:
                    pygame.mixer.music.load(self.current_song)
                    pygame.mixer.music.play()
            self.playing = True
            self.play_btn.config(text="⏸", bg=self.accent_color)
            self.info_label.config(text="🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ 🎵")
            self.animate_visualizer()
    
    def pause_music(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.playing = False
            self.paused = True
            self.play_btn.config(text="▶", bg=self.button_bg)
            self.info_label.config(text="⏸ ᴘᴀᴜsᴇᴅ ⏸")
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_btn.config(text="▶", bg=self.button_bg)
        self.info_label.config(text="⏹ sᴛᴏᴘᴘᴇᴅ ⏹")
        self.current_time_label.config(text="0:00")
        self.update_progress_bar(0)
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.visualizer.itemconfig(self.circle, outline=self.accent_color)
    
    def previous_song(self):
        if self.current_song:
            self.stop_music()
            self.play_pause()
            self.info_label.config(text="◀ ᴘʀᴇᴠɪᴏᴜs ᴛʀᴀᴄᴋ ◀")
            self.root.after(1500, lambda: self.info_label.config(text="🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ 🎵") if self.playing else None)
    
    def next_song(self):
        if self.current_song:
            self.stop_music()
            self.play_pause()
            self.info_label.config(text="ɴᴇxᴛ ᴛʀᴀᴄᴋ ▶")
            self.root.after(1500, lambda: self.info_label.config(text="🎵 ɴᴏᴡ ᴘʟᴀʏɪɴɢ 🎵") if self.playing else None)
    
    def update_progress(self):
        if self.playing and not self.paused and not self.seeking:
            try:
                # Get current position in seconds
                current_pos = pygame.mixer.music.get_pos() / 1000
                
                if current_pos >= 0:
                    # Update time display
                    self.current_time_label.config(text=self.format_time(current_pos))
                    
                    # Update progress bar if we have song length
                    if self.song_length > 0:
                        self.update_progress_bar(current_pos)
                        
                        # Check if song ended
                        if current_pos >= self.song_length - 0.5:
                            self.stop_music()
                    else:
                        if current_pos > 0 and self.song_length == 0:
                            pass
                        
            except Exception as e:
                # Silently handle errors
                pass
        
        # Update every 100ms
        self.update_id = self.root.after(100, self.update_progress)

if __name__ == "__main__":
    root = tk.Tk()
    player = Y2KMusicPlayer(root)
    root.mainloop()