import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv
from main import upload_to_youtube 
from utils.youtube_utils import upload_to_youtube
from utils.logging_utils import show_error, show_info

# Load environment variables
load_dotenv()

class VideoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Generator")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Topic Entry
        ttk.Label(self.main_frame, text="Topic:").pack(anchor=tk.W)
        self.topic_entry = ttk.Entry(self.main_frame, width=50)
        self.topic_entry.pack(fill=tk.X, pady=5)
        
        # Trending Topics Button
        ttk.Button(
            self.main_frame, 
            text="Get Trending Topics", 
            command=self.get_trending
        ).pack(pady=5)
        
        # Generate Button
        ttk.Button(
            self.main_frame, 
            text="Generate Video", 
            command=self.generate_video
        ).pack(pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            self.main_frame, 
            length=300, 
            mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self.main_frame, 
            textvariable=self.status_var
        ).pack(pady=5)
        
        # Save/Upload Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame, 
            text="Save Video", 
            command=self.save_video
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Upload to YouTube",
            command=self.upload_video
        ).pack(side=tk.LEFT, padx=5)

    def get_trending(self):
        """Get trending topics"""
        try:
            # Simulate getting trending topics for now
            topics = ["Ukraine News", "World Cup", "Climate Change"]
            self.show_topic_selection(topics)
        except Exception as e:
            show_error("Error", f"Failed to get trending topics: {str(e)}")

    def show_topic_selection(self, topics):
        """Show topic selection window"""
        window = tk.Toplevel(self.root)
        window.title("Select Topic")
        for topic in topics:
            ttk.Button(
                window,
                text=topic,
                command=lambda t=topic: self.select_topic(t, window)
            ).pack(pady=2, padx=5, fill=tk.X)

    def select_topic(self, topic, window):
        """Select a topic from the list"""
        self.topic_entry.delete(0, tk.END)
        self.topic_entry.insert(0, topic)
        window.destroy()

    def generate_video(self):
        """Generate the video"""
        topic = self.topic_entry.get()
        if not topic:
            show_error("Error", "Please enter a topic first!")
            return
        
        try:
            self.status_var.set("Generating video...")
            self.progress['value'] = 0
            # Simulate video generation steps
            self.simulate_progress("Generating script...", 0, 25)
            self.simulate_progress("Creating voiceover...", 25, 50)
            self.simulate_progress("Generating images...", 50, 75)
            self.simulate_progress("Assembling video...", 75, 100)
            self.status_var.set("Video generated successfully!")
            show_info("Success", "Video has been generated!")
        except Exception as e:
            show_error("Error", str(e))

    def simulate_progress(self, status, start, end):
        """Simulate progress for demonstration"""
        self.status_var.set(status)
        for i in range(start, end):
            self.progress['value'] = i
            self.root.update_idletasks()
            self.root.after(50)  # Small delay to show progress

    def save_video(self):
        """Save the video locally"""
        show_info("Save", "Video saved successfully!")

    def upload_video(self):
        """Upload the video to YouTube"""
        if not self.generated_video:
            show_error("Error", "Please generate a video first!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to upload to YouTube?"):
            try:
                self.status_var.set("Uploading to YouTube...")
                title = f"Video about {self.topic_entry.get()}"
                description = "Generated using AI"
                upload_to_youtube(self.generated_video, title, description)
                show_info("Success", "Video uploaded to YouTube!")
            except Exception as e:
                show_error("Error", f"Failed to upload: {str(e)}")

def main():
    root = tk.Tk()
    app = VideoGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()