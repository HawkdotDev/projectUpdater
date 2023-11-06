import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import concurrent.futures
from functools import partial

from utils.git_pull import git_pull_in_subfolders

path_presets = {}  # dictionary to store path presets
selected_folder_path = ""

def start_git_pull(root_path, status_label, progress_bar):
    def update_status(status):
        status_label.config(text=status)
        progress_bar.stop()

    if(selected_folder_path):
        try:
            git_pull_in_subfolders(selected_folder_path, update_status)
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")
    else:
        try:
            git_pull_in_subfolders(root_path, update_status)
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")

def browse_file():
    global selected_folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder_path = folder_path


def save_preset(entry_path):
    root_path = entry_path.get()
    preset_name = simpledialog.askstring("Save Preset", "Enter a name for the preset:")
    if preset_name:
        path_presets[preset_name] = root_path
        save_presets_to_file(path_presets)

def delete_preset(listbox):
    selected_presets = listbox.curselection()
    for index in reversed(selected_presets):
        preset_name = listbox.get(index)
        listbox.delete(index)
        path_presets.pop(preset_name, None)
    save_presets_to_file(path_presets)

def load_presets():
    if os.path.exists('path_presets.txt'):
        with open('path_presets.txt', 'r') as file:
            presets = file.read().splitlines()
            for preset in presets:
                name, path = preset.split(': ')
                path_presets[name] = path

def save_presets_to_file(presets):
    with open('path_presets.txt', 'w') as file:
        for name, path in presets.items():
            file.write(f"{name}: {path}\n")

def run_selected_presets(listbox, status_label, progress_bar, frame):
    selected_presets = listbox.curselection()
    if not selected_presets:
        return
    
    with concurrent,futures.ThreadPoolExecutor() as executor:
        futures = []
        for index in selected_presets:
            preset_name = listbox.get(index)
            root_path = path_presets[preset_name]
            status_label = tk.Label(frame, text=f"Running Git pull for {preset_name}...")
            progress_bar = ttk.Progressbar(frame, mode="indeterminate")
            status_label.grid(row=3 + index, column=1, padx=10, pady=10)
            progress_bar.grid(row=4 + index, column=1, padx=10, pady=10)
            futures.append(executor.submit(start_git_pull, root_path, status_label, progress_bar))
        
        for future in concurrent.futures.as_completed(futures):
            future.result()

def run_git_pull_gui():
    
    app = tk.Tk()  # main application window
    app.title("Git Pull GUI")

    load_presets()

    # The input elements
    frame = tk.Frame(app)
    frame.pack(padx=20, pady=20)

    label_path = tk.Label(frame, text="Enter Root Path:")
    label_path.grid(row=0, column=0, padx=10, pady=10)

    entry_path = tk.Entry(frame)
    entry_path.grid(row=0, column=1, padx=10, pady=10)

    start_button = tk.Button(frame, text="Start Git Pull", command=lambda: start_git_pull(entry_path.get(), status_label, progress_bar))
    start_button.grid(row=1, column=1, padx=10, pady=10)

    browse_button = tk.Button(frame, text="Browse", command=browse_file)
    browse_button.grid(row=0, column=2, padx=10, pady=10)   

    save_preset_func = partial(save_preset, entry_path)
    save_preset_button = tk.Button(frame, text="Save Preset", command=save_preset_func)
    save_preset_button.grid(row=2, column=1, padx=10, pady=10)

    listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE)
    listbox.grid(row=3, column=0, padx=10, pady=10)

    delete_preset_func = partial(delete_preset, listbox)
    delete_preset_button = tk.Button(frame, text="Delete Preset", command=delete_preset_func)
    delete_preset_button.grid(row=2, column=2, padx=10, pady=10)

    for preset_name in path_presets:
        listbox.insert(tk.END, preset_name)

    status_label = tk.Label(frame, text="")
    status_label.grid(row=4, column=1, padx=10, pady=10)

    progress_bar = ttk.Progressbar(frame, mode="indeterminate")
    progress_bar.grid(row=5, column=1, padx=10, pady=10)

    run_selected_button = tk.Button(frame, text="Run Selected Presets", command=lambda: run_selected_presets(listbox, status_label, progress_bar, frame))
    run_selected_button.grid(row=6, column=1, padx=10, pady=10)

    app.mainloop()

