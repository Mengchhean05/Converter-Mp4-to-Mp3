import os
import threading  # ប្រើសម្រាប់ការពារកុំឱ្យកម្មវិធីគាំង (Not Responding)
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # សម្រាប់ប្រើប្រាស់ Progress Bar
from moviepy.video.io.VideoFileClip import VideoFileClip
from proglog import ProgressBarLogger

# បង្កើត Custom Logger សម្រាប់ចាប់យកភាគរយពី MoviePy
class MyBarLogger(ProgressBarLogger):
    def callback(self, **changes):
        if self.state.get('bars'):
            bar = list(self.state['bars'].values())[0]
            # បង្ការការចែកនឹងសូន្យ (ZeroDivisionError)
            if bar['total'] > 0:
                percentage = int((bar['index'] / bar['total']) * 100)
                progress_bar['value'] = percentage
                lbl_percentage.config(text=f"{percentage}%")
                root.update_idletasks()

# បញ្ជីសម្រាប់រក្សាទុកទីតាំង File ទាំងអស់ដែលបានជ្រើសរើស
selected_files = []

def select_files():
    global selected_files
    # ថែមគន្លឹះ multiple=True ដើម្បីអាចរើសបានច្រើន File ក្នុងពេលតែមួយ
    file_paths = filedialog.askopenfilenames(
        title="ជ្រើសរើស File MP4 (អាចរើសបានច្រើន)",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    
    if file_paths:
        selected_files = list(file_paths)
        # បង្ហាញឈ្មោះ File ដំបូង និងចំនួន File ផ្សេងទៀតដែលបានរើស
        entry_video_path.delete(0, tk.END)
        if len(selected_files) == 1:
            entry_video_path.insert(0, os.path.basename(selected_files[0]))
        else:
            entry_video_path.insert(0, f"បានជ្រើសរើសវីដេអូចំនួន {len(selected_files)} File")
        
        # Reset ភាគរយ
        progress_bar['value'] = 0
        lbl_percentage.config(text="0%")
        lbl_status.config(text=f"បានជ្រើសរើសរួចរាល់។ រង់ចាំចុច Convert...", fg="blue")

# មុខងាររត់នៅ Background (Background Thread) ដើម្បីដំណើរការ Convert មិនឱ្យទើស GUI
def run_conversion_thread(output_folder):
    btn_convert.config(state=tk.DISABLED)
    btn_browse.config(state=tk.DISABLED)
    
    total_files = len(selected_files)
    success_count = 0
    
    # រង្វិលជុំដំណើរការម្ដងមួយ File ៗ
    for index, mp4_path in enumerate(selected_files):
        file_name = os.path.basename(mp4_path)
        # បង្ហាញស្ថានភាពថាបច្ចុប្បន្នកំពុងធ្វើដល់ File ណា
        lbl_status.config(text=f"កំពុងធ្វើ ({index + 1}/{total_files}): {file_name}", fg="orange")
        progress_bar['value'] = 0
        lbl_percentage.config(text="0%")
        root.update()
        
        try:
            base_name = os.path.basename(mp4_path)
            f_name, _ = os.path.splitext(base_name)
            mp3_path = os.path.join(output_folder, f"{f_name}.mp3")
            
            video = VideoFileClip(mp4_path)
            logger = MyBarLogger()
            video.audio.write_audiofile(mp3_path, logger=logger)
            video.close()
            
            success_count += 1
        except Exception as e:
            print(f"មានបញ្ហានៅលើ File {file_name}: {str(e)}")
            
    # បើកប៊ូតុងឡើងវិញក្រោយធ្វើចប់
    btn_convert.config(state=tk.NORMAL)
    btn_browse.config(state=tk.NORMAL)
    
    # បង្ហាញលទ្ធផលរួម
    progress_bar['value'] = 100
    lbl_percentage.config(text="100%")
    lbl_status.config(text=f"បាន Convert ជោគជ័យ {success_count}/{total_files} File!", fg="green")
    messagebox.showinfo("ជោគជ័យ", f"ការបំប្លែងជាក្រុមត្រូវបានបញ្ចប់!\nជោគជ័យ៖ {success_count}/{total_files} File")

def start_batch_conversion():
    if not selected_files:
        messagebox.showwarning("ការព្រមាន", "សូមជ្រើសរើស File MP4 យ៉ាងហោចណាស់មួយ!")
        return
    
    # ជ្រើសរើសទីតាំងរក្សាទុក
    output_folder = filedialog.askdirectory(title="ជ្រើសរើសទីតាំងរក្សាទុក File MP3")
    
    if output_folder:
        # បង្កើត Thread ថ្មីដើម្បីរត់មុខងារ Convert នៅ Background ការពារ App គាំង
        conversion_thread = threading.Thread(target=run_conversion_thread, args=(output_folder,))
        conversion_thread.start()

# បង្កើតផ្ទាំងកម្មវិធី GUI
root = tk.Tk()
root.title("Multi MP4 to MP3 Converter")
root.geometry("520x320")
root.resizable(False, False)

# ស្លាកបង្ហាញចំណងជើង
lbl_title = tk.Label(root, text="កម្មវិធីបំប្លែងវីដេអូ MP4 ទៅជា MP3 (រើសបានច្រើន)", font=("Arial", 13, "bold"))
lbl_title.pack(pady=15)

# ប្រអប់ជ្រើសរើស File
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

entry_video_path = tk.Entry(frame_input, width=42, font=("Arial", 10))
entry_video_path.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame_input, text="ជ្រើសរើសវីដេអូ", command=select_files, bg="#0078D4", fg="white")
btn_browse.pack(side=tk.LEFT, padx=5)

# ប៊ូតុង Convert
btn_convert = tk.Button(root, text="ចាប់ផ្តើម Convert ទាំងអស់", command=start_batch_conversion, font=("Arial", 11, "bold"), bg="#107C41", fg="white", width=22)
btn_convert.pack(pady=10)

# របារបង្ហាញភាគរយ (Progress Bar សម្រាប់ File នីមួយៗ)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=370, mode="determinate")
progress_bar.pack(pady=5)

# អក្សរបង្ហាញលេខភាគរយ %
lbl_percentage = tk.Label(root, text="0%", font=("Arial", 10, "bold"))
lbl_percentage.pack()

# បង្ហាញស្ថានភាពទូទៅ
lbl_status = tk.Label(root, text="សូមជ្រើសរើស File វីដេអូដើម្បីចាប់ផ្ដើម", font=("Arial", 10, "italic"), fg="gray")
lbl_status.pack(pady=5)

root.mainloop()