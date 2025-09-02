'''
GUI for the panoramic video measurement and tracking app using CustomTkinter
'''

import threading
import gc
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import re
import numpy as np
import cv2
import PIL
import customtkinter as ctk
from icon import icon_PVMAT
from fractions import Fraction
from PIL import ImageTk, Image, ImageDraw
from Stitcher import Stitcher
from typing import Callable, List, Tuple, Union

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PVMATApp(ctk.CTk):
    '''
    The main application window using CustomTkinter
    '''
    def __init__(self):
        super().__init__()
        
        # Configure the main window
        self.title("MotionField")
        self.geometry("1400x900")
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Initialize variables
        self.current_frame = None
        self.video_path = None
        self.stitcher = None
        self.panorama = None
        self.frame_locations = []
        self.num_frames = 0
        self.current_frame_num = 1
        self.play = False
        self.delay = 0.03
        
        # Measurement variables
        self.distance_units = 'px'
        self.dragging = False
        self.start_point = None
        self.end_point = None
        self.lastxy = None
        self.last_figure = None
        self.calibration_ratio = -1
        self.Lines = {}
        self.calibrating = False
        self.pixel_dist = -1
        self.line_color = 'white'
        
        # Tracker variables
        self.fps = None
        try:
            self.tracker = cv2.TrackerCSRT_create()
        except AttributeError:
            self.tracker = cv2.legacy.TrackerCSRT_create()
        self.bounding_boxes = []
        self.draw_bounding_boxes = False
        self.bounding_id = None
        self.pano_width = 0
        self.pano_height = 0
        self.path_id = None
        self.COM_points = []
        self.COM_path = []
        self.draw_path = False
        self.velocities = []
        self.velocity_text_id = None
        self.velocity_background = None
        self.draw_velocity = False
        self.vel_units_ratio = -1
        self.velocity_units = 'km/h'
        
        # Create the UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create all the UI widgets"""
        
        # Top toolbar
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # File selection
        self.file_label = ctk.CTkLabel(self.top_frame, text="Select Video File:")
        self.file_label.pack(side="left", padx=10)
        
        self.file_button = ctk.CTkButton(self.top_frame, text="Browse", command=self.browse_file)
        self.file_button.pack(side="left", padx=5)
        
        self.file_path_label = ctk.CTkLabel(self.top_frame, text="No file selected")
        self.file_path_label.pack(side="left", padx=10)
        
        # Help button
        self.help_button = ctk.CTkButton(self.top_frame, text="Help", command=self.show_help)
        self.help_button.pack(side="right", padx=10)
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas for displaying video/panorama
        self.canvas = tk.Canvas(self.main_frame, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Left sidebar - Tools
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Distance tools
        self.distance_label = ctk.CTkLabel(self.left_frame, text="Distance Tools", font=ctk.CTkFont(size=16, weight="bold"))
        self.distance_label.pack(pady=10)
        
        self.draw_line_var = tk.StringVar(value="draw")
        self.draw_line_radio = ctk.CTkRadioButton(self.left_frame, text="Draw Line", variable=self.draw_line_var, value="draw")
        self.draw_line_radio.pack(pady=5)
        
        self.select_line_radio = ctk.CTkRadioButton(self.left_frame, text="Select Line", variable=self.draw_line_var, value="select")
        self.select_line_radio.pack(pady=5)
        
        self.erase_line_radio = ctk.CTkRadioButton(self.left_frame, text="Erase Line", variable=self.draw_line_var, value="erase")
        self.erase_line_radio.pack(pady=5)
        
        self.clear_all_button = ctk.CTkButton(self.left_frame, text="Clear All", command=self.clear_all_lines)
        self.clear_all_button.pack(pady=10)
        
        # Distance units
        self.units_label = ctk.CTkLabel(self.left_frame, text="Distance Units:")
        self.units_label.pack(pady=5)
        
        self.units_var = tk.StringVar(value="Meters")
        self.units_combo = ctk.CTkComboBox(self.left_frame, values=["Meters", "Feet and Inches"], variable=self.units_var)
        self.units_combo.pack(pady=5)
        
        # Line color
        self.color_label = ctk.CTkLabel(self.left_frame, text="Line Color:")
        self.color_label.pack(pady=5)
        
        self.color_var = tk.StringVar(value="white")
        self.color_combo = ctk.CTkComboBox(self.left_frame, values=["white", "red", "green", "blue", "yellow"], variable=self.color_var)
        self.color_combo.pack(pady=5)
        
        # Right sidebar - Controls
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        # Main controls
        self.controls_label = ctk.CTkLabel(self.right_frame, text="Controls", font=ctk.CTkFont(size=16, weight="bold"))
        self.controls_label.pack(pady=10)
        
        self.track_button = ctk.CTkButton(self.right_frame, text="Track Object", command=self.track_object)
        self.track_button.pack(pady=10)
        
        self.calibrate_button = ctk.CTkButton(self.right_frame, text="Calibrate Distance", command=self.calibrate_distance)
        self.calibrate_button.pack(pady=10)
        
        # Playback controls
        self.playback_label = ctk.CTkLabel(self.right_frame, text="Playback", font=ctk.CTkFont(size=14, weight="bold"))
        self.playback_label.pack(pady=10)
        
        self.playback_frame = ctk.CTkFrame(self.right_frame)
        self.playback_frame.pack(pady=5, fill="x", padx=10)
        
        self.prev_button = ctk.CTkButton(self.playback_frame, text="⏮", width=40, command=self.prev_frame)
        self.prev_button.pack(side="left", padx=2)
        
        self.play_button = ctk.CTkButton(self.playback_frame, text="▶", width=40, command=self.toggle_play)
        self.play_button.pack(side="left", padx=2)
        
        self.next_button = ctk.CTkButton(self.playback_frame, text="⏭", width=40, command=self.next_frame)
        self.next_button.pack(side="left", padx=2)
        
        # Frame slider
        self.slider = ctk.CTkSlider(self.right_frame, from_=0, to=100, command=self.on_slider_change)
        self.slider.pack(pady=10, padx=10, fill="x")
        
        self.frame_label = ctk.CTkLabel(self.right_frame, text="Frame: 0/0")
        self.frame_label.pack(pady=5)
        
        # Tracking options
        self.tracking_label = ctk.CTkLabel(self.right_frame, text="Tracking Options", font=ctk.CTkFont(size=14, weight="bold"))
        self.tracking_label.pack(pady=10)
        
        self.show_path_var = tk.BooleanVar()
        self.show_path_check = ctk.CTkCheckBox(self.right_frame, text="Show Path", variable=self.show_path_var)
        self.show_path_check.pack(pady=5)
        
        self.show_box_var = tk.BooleanVar()
        self.show_box_check = ctk.CTkCheckBox(self.right_frame, text="Show Bounding Box", variable=self.show_box_var)
        self.show_box_check.pack(pady=5)
        
        self.show_velocity_var = tk.BooleanVar()
        self.show_velocity_check = ctk.CTkCheckBox(self.right_frame, text="Show Velocity", variable=self.show_velocity_var)
        self.show_velocity_check.pack(pady=5)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready - Please select a video file")
        self.status_label.pack(side="left", padx=10)
        
    def browse_file(self):
        """Open file dialog to select video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.mkv *.avi *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            self.file_path_label.configure(text=f"Selected: {file_path.split('/')[-1]}")
            self.status_label.configure(text="Processing video...")
            self.process_video()
    
    def process_video(self):
        """Process the selected video file"""
        if not self.video_path:
            return
            
        try:
            # Initialize stitcher
            self.stitcher = Stitcher(self)
            
            # Process video in a separate thread
            thread = threading.Thread(target=self._process_video_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process video: {str(e)}")
            self.status_label.configure(text="Error processing video")
    
    def _process_video_thread(self):
        """Thread function for video processing"""
        try:
            # Stitch the panorama
            self.panorama = self.stitcher.stitch(self.video_path)
            
            # Get video info
            cap = cv2.VideoCapture(self.video_path)
            self.num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Update UI on main thread
            self.after(0, self._on_video_processed)
            
        except Exception as e:
            self.after(0, lambda error_msg=e: self._on_video_error(error_msg))
    
    def _on_video_processed(self):
        """Called when video processing is complete"""
        self.status_label.configure(text="Video processed successfully")
        self.current_frame_num = 1
        self.update_frame_display()
        self.enable_controls()
    
    def _on_video_error(self, error_msg):
        """Called when video processing fails"""
        messagebox.showerror("Error", f"Failed to process video: {error_msg}")
        self.status_label.configure(text="Error processing video")
    
    def update_frame_display(self):
        """Update the frame display on the canvas"""
        if self.panorama is None:
            return
            
        # For now, just display the panorama
        # In a full implementation, you'd display the current frame
        if hasattr(self.panorama, 'shape'):
            # Convert numpy array to PIL Image
            if len(self.panorama.shape) == 3:
                image = Image.fromarray(cv2.cvtColor(self.panorama, cv2.COLOR_BGR2RGB))
            else:
                image = Image.fromarray(self.panorama)
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.current_frame = ImageTk.PhotoImage(image)
                
                # Clear canvas and display image
                self.canvas.delete("all")
                self.canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.current_frame, anchor="center"
                )
    
    def enable_controls(self):
        """Enable all the control buttons"""
        self.track_button.configure(state="normal")
        self.calibrate_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.play_button.configure(state="normal")
        self.next_button.configure(state="normal")
        self.slider.configure(state="normal")
    
    def track_object(self):
        """Start object tracking"""
        self.status_label.configure(text="Object tracking not implemented yet")
        messagebox.showinfo("Info", "Object tracking feature will be implemented in the next version")
    
    def calibrate_distance(self):
        """Start distance calibration"""
        self.status_label.configure(text="Distance calibration not implemented yet")
        messagebox.showinfo("Info", "Distance calibration feature will be implemented in the next version")
    
    def toggle_play(self):
        """Toggle play/pause"""
        self.play = not self.play
        if self.play:
            self.play_button.configure(text="⏸")
            self.play_video()
        else:
            self.play_button.configure(text="▶")
    
    def play_video(self):
        """Play video frames"""
        if self.play and self.current_frame_num < self.num_frames:
            self.next_frame()
            self.after(int(self.delay * 1000), self.play_video)
    
    def prev_frame(self):
        """Go to previous frame"""
        if self.current_frame_num > 1:
            self.current_frame_num -= 1
            self.update_frame_display()
            self.update_frame_label()
            self.update_slider()
    
    def next_frame(self):
        """Go to next frame"""
        if self.current_frame_num < self.num_frames:
            self.current_frame_num += 1
            self.update_frame_display()
            self.update_frame_label()
            self.update_slider()
    
    def update_frame_label(self):
        """Update the frame counter label"""
        self.frame_label.configure(text=f"Frame: {self.current_frame_num}/{self.num_frames}")
    
    def update_slider(self):
        """Update the slider position"""
        if self.num_frames > 0:
            self.slider.set(self.current_frame_num / self.num_frames * 100)
    
    def on_slider_change(self, value):
        """Handle slider value change"""
        if self.num_frames > 0:
            frame_num = int(value / 100 * self.num_frames)
            if frame_num != self.current_frame_num:
                self.current_frame_num = frame_num
                self.update_frame_display()
                self.update_frame_label()
    
    def clear_all_lines(self):
        """Clear all drawn lines"""
        self.canvas.delete("line")
        self.Lines.clear()
        self.status_label.configure(text="All lines cleared")
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if self.draw_line_var.get() == "draw":
            self.start_point = (event.x, event.y)
            self.dragging = True
        elif self.draw_line_var.get() == "erase":
            # Find and delete line at click position
            self.erase_line_at_position(event.x, event.y)
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if self.dragging and self.start_point:
            # Clear previous preview line
            self.canvas.delete("preview")
            
            # Draw preview line
            self.canvas.create_line(
                self.start_point[0], self.start_point[1],
                event.x, event.y,
                fill=self.color_var.get(), width=2, tags="preview"
            )
    
    def on_canvas_release(self, event):
        """Handle canvas release events"""
        if self.dragging and self.start_point:
            self.end_point = (event.x, event.y)
            
            # Remove preview line
            self.canvas.delete("preview")
            
            # Draw final line
            line_id = self.canvas.create_line(
                self.start_point[0], self.start_point[1],
                self.end_point[0], self.end_point[1],
                fill=self.color_var.get(), width=2, tags="line"
            )
            
            # Calculate distance
            distance = np.sqrt((self.end_point[0] - self.start_point[0])**2 + 
                             (self.end_point[1] - self.start_point[1])**2)
            
            # Store line data
            self.Lines[line_id] = {
                'start': self.start_point,
                'end': self.end_point,
                'distance': distance,
                'color': self.color_var.get()
            }
            
            self.status_label.configure(text=f"Line drawn - Distance: {distance:.1f} pixels")
            
            # Reset
            self.dragging = False
            self.start_point = None
            self.end_point = None
    
    def on_canvas_motion(self, event):
        """Handle canvas motion events"""
        # Update cursor based on tool
        if self.draw_line_var.get() == "draw":
            self.canvas.configure(cursor="cross")
        elif self.draw_line_var.get() == "erase":
            self.canvas.configure(cursor="X_cursor")
        else:
            self.canvas.configure(cursor="arrow")
    
    def erase_line_at_position(self, x, y):
        """Erase line at given position"""
        # Find closest line to the click position
        closest_line = None
        min_distance = float('inf')
        
        for line_id, line_data in self.Lines.items():
            # Calculate distance from point to line
            x1, y1 = line_data['start']
            x2, y2 = line_data['end']
            
            # Distance from point to line segment
            A = x - x1
            B = y - y1
            C = x2 - x1
            D = y2 - y1
            
            dot = A * C + B * D
            len_sq = C * C + D * D
            
            if len_sq == 0:
                param = 0
            else:
                param = dot / len_sq
            
            if param < 0:
                xx, yy = x1, y1
            elif param > 1:
                xx, yy = x2, y2
            else:
                xx = x1 + param * C
                yy = y1 + param * D
            
            distance = np.sqrt((x - xx)**2 + (y - yy)**2)
            
            if distance < min_distance and distance < 10:  # 10 pixel threshold
                min_distance = distance
                closest_line = line_id
        
        if closest_line:
            self.canvas.delete(closest_line)
            del self.Lines[closest_line]
            self.status_label.configure(text="Line erased")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
PV-MAT - Panoramic Video Measurement and Tracking

Instructions:
1. Click 'Browse' to select a video file
2. Wait for the video to be processed
3. Use the distance tools to measure objects:
   - Draw Line: Click and drag to draw measurement lines
   - Select Line: Click on lines to select them
   - Erase Line: Click on lines to delete them
4. Use Track Object to track moving objects
5. Use Calibrate Distance to set real-world measurements
6. Use playback controls to navigate through frames

Tips:
- Keep videos short (6-10 seconds) for best results
- Shoot video with movement on a single axis
- Use the slider to quickly navigate through frames
        """
        
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help")
        help_window.geometry("500x400")
        
        help_text_widget = ctk.CTkTextbox(help_window)
        help_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")

def main():
    """Main function to run the application"""
    app = PVMATApp()
    app.mainloop()

if __name__ == "__main__":
    main()
