import sys
import os
import threading
import time
import requests
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

# Colors for Dark Theme
BG_MAIN = "#121214"        # Very dark gray-blue background
BG_PANEL = "#1a1a24"       # Slate card/panel background
BG_INPUT = "#252538"       # Dark text entries/dropdowns
FG_PRIMARY = "#ffffff"     # White text
FG_SECONDARY = "#a9a9b3"   # Gray subtext
COLOR_ACCENT = "#1082DD"   # Blue accent
COLOR_ACCENT_HOVER = "#0d68b1"
COLOR_SUCCESS = "#2ecc71"  # Green
COLOR_ERROR = "#e74c3c"    # Red
COLOR_CONSOLE_BG = "#0c0c0e" # Dark terminal background

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Universitaly Course Scraper")
        self.root.geometry("850x650")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(800, 600)
        
        # Thread controller
        self.scraping_thread = None
        self.stop_requested = False
        
        self.setup_styles()
        self.create_widgets()
        self.set_defaults()

    def setup_styles(self):
        # Configure TTK styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Style Comboboxes
        self.style.configure("TCombobox", 
                             fieldbackground=BG_INPUT, 
                             background=BG_INPUT, 
                             foreground=FG_PRIMARY, 
                             arrowcolor=FG_PRIMARY,
                             bordercolor=BG_PANEL,
                             lightcolor=BG_PANEL,
                             darkcolor=BG_PANEL)
        self.style.map("TCombobox", 
                       fieldbackground=[("readonly", BG_INPUT)],
                       foreground=[("readonly", FG_PRIMARY)])
        
        # Style Progressbar
        self.style.configure("Custom.Horizontal.TProgressbar", 
                             troughcolor=BG_INPUT, 
                             background=COLOR_ACCENT, 
                             bordercolor=BG_MAIN, 
                             lightcolor=BG_MAIN, 
                             darkcolor=BG_MAIN)

    def create_widgets(self):
        # Main Layout: Two Columns (Left: Filters, Right: Logs & Actions)
        self.root.grid_columnconfigure(0, weight=4, minsize=350)
        self.root.grid_columnconfigure(1, weight=5, minsize=450)
        self.root.grid_rowconfigure(0, weight=1)
        
        # LEFT COLUMN: Filters Panel
        left_panel = tk.Frame(self.root, bg=BG_PANEL, padx=20, pady=20, bd=0)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_rowconfigure(9, weight=1) # spacer
        
        # Title Block
        title_label = tk.Label(left_panel, text="UNIVERSITALY", font=("Segoe UI", 20, "bold"), fg=COLOR_ACCENT, bg=BG_PANEL)
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 2))
        subtitle_label = tk.Label(left_panel, text="Course Database Scraper", font=("Segoe UI", 11), fg=FG_SECONDARY, bg=BG_PANEL)
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Accent separator line
        sep = tk.Frame(left_panel, height=2, bg=COLOR_ACCENT, bd=0)
        sep.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Filter Fields Grid
        filter_grid = tk.Frame(left_panel, bg=BG_PANEL)
        filter_grid.grid(row=3, column=0, sticky="nsew")
        filter_grid.grid_columnconfigure(1, weight=1)
        
        row_idx = 0
        
        # Keyword Search
        tk.Label(filter_grid, text="Search Keyword:", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_PANEL).grid(row=row_idx, column=0, sticky="w", pady=8)
        self.entry_keyword = tk.Entry(filter_grid, font=("Segoe UI", 10), bg=BG_INPUT, fg=FG_PRIMARY, insertbackground=FG_PRIMARY, bd=0, highlightthickness=1, highlightbackground=BG_INPUT, highlightcolor=COLOR_ACCENT)
        self.entry_keyword.grid(row=row_idx, column=1, sticky="ew", padx=(10, 0), pady=8)
        row_idx += 1
        
        # Language
        tk.Label(filter_grid, text="Course Language:", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_PANEL).grid(row=row_idx, column=0, sticky="w", pady=8)
        self.combo_lang = ttk.Combobox(filter_grid, values=["All Languages", "English", "Italian"], state="readonly", font=("Segoe UI", 10))
        self.combo_lang.grid(row=row_idx, column=1, sticky="ew", padx=(10, 0), pady=8)
        row_idx += 1
        
        # Degree Type
        tk.Label(filter_grid, text="Degree Level:", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_PANEL).grid(row=row_idx, column=0, sticky="w", pady=8)
        self.combo_degree = ttk.Combobox(filter_grid, values=[
            "All Levels", 
            "2nd Level - Master's (Magistrale)", 
            "1st Level - Bachelor's (Triennale)", 
            "Single cycle - 5 years", 
            "Single cycle - 6 years"
        ], state="readonly", font=("Segoe UI", 10))
        self.combo_degree.grid(row=row_idx, column=1, sticky="ew", padx=(10, 0), pady=8)
        row_idx += 1
        
        # Delivery Mode
        tk.Label(filter_grid, text="Delivery Mode:", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_PANEL).grid(row=row_idx, column=0, sticky="w", pady=8)
        self.combo_delivery = ttk.Combobox(filter_grid, values=[
            "All Modes", 
            "In Presence (Convenzionale)", 
            "Mixed (Mista)", 
            "Mostly Remote (Prevalentemente a distanza)", 
            "Fully Remote (A distanza)"
        ], state="readonly", font=("Segoe UI", 10))
        self.combo_delivery.grid(row=row_idx, column=1, sticky="ew", padx=(10, 0), pady=8)
        row_idx += 1
        
        # Access Type
        tk.Label(filter_grid, text="Access Type:", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_PANEL).grid(row=row_idx, column=0, sticky="w", pady=8)
        self.combo_access = ttk.Combobox(filter_grid, values=[
            "All Access Types", 
            "Open (Libero)", 
            "Entry Test (Accesso con laurea/diploma)", 
            "Programmed Number (Programmato)"
        ], state="readonly", font=("Segoe UI", 10))
        self.combo_access.grid(row=row_idx, column=1, sticky="ew", padx=(10, 0), pady=8)
        row_idx += 1
        
        # Duration Option
        tk.Label(filter_grid, text="Duration (Years):", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_PANEL).grid(row=row_idx, column=0, sticky="w", pady=8)
        self.combo_duration = ttk.Combobox(filter_grid, values=["All", "1", "2", "3", "5", "6"], state="readonly", font=("Segoe UI", 10))
        self.combo_duration.grid(row=row_idx, column=1, sticky="ew", padx=(10, 0), pady=8)
        row_idx += 1

        # Helpful explanation box
        info_box = tk.Label(left_panel, text="* Preconfigured Defaults:\nEnglish, Master's (2 Years), In Presence.\nThis matches your specific filter target.", 
                            font=("Segoe UI", 9, "italic"), fg=FG_SECONDARY, bg=BG_PANEL, justify="left", anchor="w")
        info_box.grid(row=8, column=0, sticky="w", pady=(20, 0))

        # Bottom logo placeholder/decor
        decor_label = tk.Label(left_panel, text="Universitaly Scraper v1.0", font=("Segoe UI", 8), fg=FG_SECONDARY, bg=BG_PANEL)
        decor_label.grid(row=10, column=0, sticky="sw")
        
        # RIGHT COLUMN: Actions & Scroller Panel
        right_panel = tk.Frame(self.root, bg=BG_MAIN, padx=10, pady=10)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Controls Frame (Start/Stop Buttons)
        controls_frame = tk.Frame(right_panel, bg=BG_MAIN)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.btn_scrape = tk.Button(controls_frame, text="Scrape & Export to Excel", font=("Segoe UI", 12, "bold"), 
                                    bg=COLOR_ACCENT, fg=FG_PRIMARY, activebackground=COLOR_ACCENT_HOVER, 
                                    activeforeground=FG_PRIMARY, bd=0, cursor="hand2", padx=20, pady=8, command=self.start_scraping)
        self.btn_scrape.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.btn_stop = tk.Button(controls_frame, text="Stop", font=("Segoe UI", 12, "bold"), 
                                  bg=BG_INPUT, fg=FG_PRIMARY, activebackground=COLOR_ERROR, 
                                  activeforeground=FG_PRIMARY, bd=0, cursor="hand2", padx=20, pady=8, state="disabled", command=self.stop_scraping)
        self.btn_stop.grid(row=0, column=1, sticky="w")
        
        # Progress Display
        progress_frame = tk.Frame(right_panel, bg=BG_MAIN)
        progress_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, style="Custom.Horizontal.TProgressbar", mode="determinate")
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(5, 2))
        
        self.lbl_progress = tk.Label(progress_frame, text="Ready to scrape.", font=("Segoe UI", 10), fg=FG_SECONDARY, bg=BG_MAIN)
        self.lbl_progress.grid(row=1, column=0, sticky="w")
        
        # Console Log
        tk.Label(right_panel, text="Real-time Execution Output Logs:", font=("Segoe UI", 10, "bold"), fg=FG_PRIMARY, bg=BG_MAIN).grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.txt_console = ScrolledText(right_panel, bg=COLOR_CONSOLE_BG, fg="#2ecc71", font=("Consolas", 10), bd=0, highlightthickness=1, highlightbackground=BG_INPUT)
        self.txt_console.grid(row=3, column=0, sticky="nsew", pady=(0, 5))
        self.txt_console.insert(tk.END, ">>> Welcome to Universitaly Database Scraper!\n")
        self.txt_console.insert(tk.END, ">>> Set your filters on the left and click 'Scrape & Export to Excel' to begin.\n")
        self.txt_console.configure(state="disabled")

    def set_defaults(self):
        # Set default selections to user's targeted filters
        self.entry_keyword.insert(0, "")
        self.combo_lang.set("English")
        self.combo_degree.set("2nd Level - Master's (Magistrale)")
        self.combo_delivery.set("In Presence (Convenzionale)")
        self.combo_access.set("All Access Types")
        self.combo_duration.set("2")

    def log(self, message):
        """Append log to console in a thread-safe way."""
        def append():
            self.txt_console.configure(state="normal")
            self.txt_console.insert(tk.END, message + "\n")
            self.txt_console.see(tk.END)
            self.txt_console.configure(state="disabled")
        self.root.after(0, append)

    def update_progress(self, progress_val, text_val):
        """Update progress bar and status label in a thread-safe way."""
        def update():
            self.progress_bar["value"] = progress_val
            self.lbl_progress.config(text=text_val)
        self.root.after(0, update)

    def start_scraping(self):
        if self.scraping_thread and self.scraping_thread.is_alive():
            return
        
        # Reset state
        self.stop_requested = False
        self.btn_scrape.config(state="disabled", bg=BG_INPUT)
        self.btn_stop.config(state="normal", bg=COLOR_ERROR)
        
        # Build API Query Parameters
        filters = self.get_active_filters()
        
        # Spawns file dialog BEFORE starting background thread
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            title="Save Scraped Courses Excel File As",
            initialfile="universitaly_courses.xlsx"
        )
        
        if not file_path:
            # User cancelled
            self.btn_scrape.config(state="normal", bg=COLOR_ACCENT)
            self.btn_stop.config(state="disabled", bg=BG_INPUT)
            self.log("[SYSTEM] Scraping cancelled: No save destination selected.")
            return

        self.log(f"[SYSTEM] Starting scraper with filters: {filters}")
        self.log(f"[SYSTEM] Export location: {file_path}")
        
        # Start thread
        self.scraping_thread = threading.Thread(target=self.scrape_thread_process, args=(filters, file_path))
        self.scraping_thread.daemon = True
        self.scraping_thread.start()

    def stop_scraping(self):
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.stop_requested = True
            self.log("[SYSTEM] Stop request received. Cleanly exiting on next page cycle...")
            self.btn_stop.config(state="disabled")

    def get_active_filters(self):
        # Mappings of UI values to API parameters
        lang_map = {"All Languages": "", "English": "EN", "Italian": "IT"}
        degree_map = {
            "All Levels": "", 
            "2nd Level - Master's (Magistrale)": "2", 
            "1st Level - Bachelor's (Triennale)": "3", 
            "Single cycle - 5 years": "5", 
            "Single cycle - 6 years": "6"
        }
        delivery_map = {
            "All Modes": "", 
            "In Presence (Convenzionale)": "C", 
            "Mixed (Mista)": "B", 
            "Mostly Remote (Prevalentemente a distanza)": "P", 
            "Fully Remote (A distanza)": "T"
        }
        access_map = {
            "All Access Types": "", 
            "Open (Libero)": "1", 
            "Entry Test (Accesso con laurea/diploma)": "2", 
            "Programmed Number (Programmato)": "3"
        }
        
        dur_val = self.combo_duration.get()
        duration = "" if dur_val == "All" else dur_val
        
        return {
            "searchType": "u",
            "tipoLaurea": degree_map.get(self.combo_degree.get(), ""),
            "tipoClasse": "0",
            "durata": duration,
            "lingua": lang_map.get(self.combo_lang.get(), ""),
            "tipoAccesso": access_map.get(self.combo_access.get(), ""),
            "modalitaErogazione": delivery_map.get(self.combo_delivery.get(), ""),
            "searchText": self.entry_keyword.get().strip(),
            "order": "ASC"
        }

    def flatten_course(self, item):
        """Extract and clean nested fields into a flat dictionary."""
        row = {
            "Course ID": item.get("id"),
            "Academic Year": item.get("anno", {}).get("descrizione"),
            "University": item.get("nomeStruttura"),
            "Course Name (IT)": item.get("nomeCorso"),
            "Course Name (EN)": item.get("nomeCorsoEn"),
            "URL": item.get("url"),
            "Language": item.get("lingua"),
            "Duration (Years)": item.get("durataAnni"),
            "Degree Type": item.get("tipoLaurea", {}).get("descrizioneEn") or item.get("tipoLaurea", {}).get("descrizione"),
            "Delivery Mode": item.get("modalitaErogazione", {}).get("descrizioneEn") or item.get("modalitaErogazione", {}).get("descrizione"),
            "Access Mode": item.get("modalitaAccesso", {}).get("descrizioneEn") or item.get("modalitaAccesso", {}).get("descrizione"),
            "Program Admission": item.get("programmazione", {}).get("descrizioneEn") or item.get("programmazione", {}).get("descrizione"),
            "Subject Area": item.get("area"),
            "Subject Class Code": item.get("classe", {}).get("codice") if item.get("classe") else None,
            "Subject Class Description": item.get("classe", {}).get("descrizione") if item.get("classe") else None,
            "CFU Credits": item.get("classe", {}).get("totaleCfu") if item.get("classe") else None,
            "Interclass Class Code": item.get("classeInterclasse", {}).get("codice") if item.get("classeInterclasse") else None,
            "Interclass Class Description": item.get("classeInterclasse", {}).get("descrizione") if item.get("classeInterclasse") else None,
            "Date Inserted": item.get("dataInserimento"),
        }
        # Clean EN prefixes (some descriptions are returned as 'EN in presenza' or similar)
        for key in ["Degree Type", "Delivery Mode", "Access Mode", "Program Admission"]:
            if isinstance(row[key], str) and row[key].startswith("EN "):
                row[key] = row[key][3:].capitalize()
        return row

    def scrape_thread_process(self, filters, file_path):
        base_url = "https://universitaly-backend.cineca.it/api/offerta-formativa/cerca-corsi"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        all_courses = []
        start_time = time.time()
        
        try:
            # 1. Fetch Page 1 first to read pagination metadata
            params = filters.copy()
            params["page"] = 1
            self.log("[NETWORK] Fetching page 1 metadata...")
            
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            if response.status_code != 200:
                raise Exception(f"Backend API returned status code {response.status_code}")
            
            data = response.json()
            total_results = data.get("totalResults", 0)
            total_pages = data.get("totalPages", 0)
            
            self.log(f"[INFO] Found {total_results} matching courses across {total_pages} pages.")
            
            if total_results == 0:
                self.log("[SYSTEM] No matching courses found with current filter configuration.")
                self.update_progress(100, "Done. No results found.")
                self.reset_gui_buttons()
                messagebox.showinfo("Scraping Completed", "No courses match the selected filters.")
                return

            # Append courses from page 1
            for course in data.get("corsi", []):
                all_courses.append(self.flatten_course(course))
            
            self.log(f"[SCRAPER] Page 1/{total_pages} done. Collected {len(all_courses)} courses.")
            progress = (1 / total_pages) * 100
            self.update_progress(progress, f"Scraped page 1/{total_pages} ({len(all_courses)} courses)")
            
            # 2. Iterate pages 2 to total_pages
            for page in range(2, total_pages + 1):
                if self.stop_requested:
                    self.log("[SYSTEM] Scraping stopped early by user request.")
                    break
                
                # Small polite throttle delay to be gentle on servers
                time.sleep(0.2)
                
                params["page"] = page
                self.log(f"[NETWORK] Fetching page {page}/{total_pages}...")
                
                try:
                    response = requests.get(base_url, params=params, headers=headers, timeout=15)
                    if response.status_code != 200:
                        self.log(f"[WARNING] Failed to fetch page {page}. Code: {response.status_code}. Retrying in 1s...")
                        time.sleep(1.0)
                        response = requests.get(base_url, params=params, headers=headers, timeout=15)
                        if response.status_code != 200:
                            self.log(f"[ERROR] Skipping page {page} due to persistent connection issue.")
                            continue
                    
                    page_data = response.json()
                    page_courses = page_data.get("corsi", [])
                    for course in page_courses:
                        all_courses.append(self.flatten_course(course))
                    
                    self.log(f"[SCRAPER] Page {page}/{total_pages} done. Collected {len(all_courses)} courses total.")
                    progress = (page / total_pages) * 100
                    self.update_progress(progress, f"Scraped page {page}/{total_pages} ({len(all_courses)} courses)")
                except Exception as e:
                    self.log(f"[ERROR] Network error on page {page}: {str(e)}. Skipping page.")
            
            # 3. Export to Excel
            if all_courses:
                self.log("[SYSTEM] Processing data and exporting to Excel...")
                df = pd.DataFrame(all_courses)
                
                # Excel Column Ordering
                column_order = [
                    "Course ID", "Course Name (IT)", "Course Name (EN)", "University", 
                    "Degree Type", "Duration (Years)", "CFU Credits", "Language", 
                    "Delivery Mode", "Access Mode", "Program Admission", "Subject Area", 
                    "Subject Class Code", "Subject Class Description", 
                    "Interclass Class Code", "Interclass Class Description",
                    "Academic Year", "URL", "Date Inserted"
                ]
                
                # Check which columns exist in data and order them
                cols_to_use = [col for col in column_order if col in df.columns]
                # Add any missing keys that weren't in column_order
                remaining_cols = [col for col in df.columns if col not in cols_to_use]
                df = df[cols_to_use + remaining_cols]
                
                # Save using pandas and openpyxl
                df.to_excel(file_path, index=False, sheet_name="Universitaly Courses")
                
                elapsed = time.time() - start_time
                self.log(f"[SUCCESS] Exported {len(all_courses)} courses in {elapsed:.1f} seconds!")
                self.update_progress(100, f"Completed. Exported {len(all_courses)} courses.")
                self.root.after(0, lambda: messagebox.showinfo("Scraping Completed", 
                                                              f"Successfully scraped {len(all_courses)} courses.\n"
                                                              f"File saved to:\n{file_path}"))
            else:
                self.log("[SYSTEM] No courses collected. Excel file not created.")
                self.update_progress(100, "Done. No records to export.")
                
        except Exception as e:
            self.log(f"[FATAL ERROR] Scraping failed: {str(e)}")
            self.update_progress(100, "Failed due to error.")
            self.root.after(0, lambda: messagebox.showerror("Scraping Error", f"Scraping failed with error:\n{str(e)}"))
        
        finally:
            self.reset_gui_buttons()

    def reset_gui_buttons(self):
        """Restore buttons status back to default state."""
        def reset():
            self.btn_scrape.config(state="normal", bg=COLOR_ACCENT)
            self.btn_stop.config(state="disabled", bg=BG_INPUT)
        self.root.after(0, reset)

if __name__ == "__main__":
    # If running with CLI help options
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Universitaly Scraper GUI App")
        print("Run without arguments to launch the graphical user interface.")
        sys.exit(0)
        
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()
