import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from tkinter import filedialog, messagebox
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import numpy as np
import os  # Added for file name handling
import json # Added for custom job roles

# --- NEW: Import for PDF Preview and Treemap ---
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow not found. PDF Preview will be disabled.")
    print("Please run: pip install pillow")
    Image = None
    ImageTk = None

try:
    import squarify
except ImportError:
    print("squarify not found. Treemap visualization will be disabled.")
    print("Please run: pip install squarify")
    squarify = None
# -----------------------------------------------


# --- Import file-reading libraries (handle errors if not installed) ---
try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. PDF support will be disabled.")
    print("Please run: pip install PyMuPDF")
    fitz = None

try:
    from docx import Document
except ImportError:
    print("python-docx not found. DOCX support will be disabled.")
    print("Please run: pip install python-docx")
    Document = None
# ---------------------------------------------------------------------


class ResumeAnalyzer:
    def __init__(self):
        # Default job roles, in case JSON load fails
        self.default_job_roles = {
            "Data Scientist": {
                "keywords": {
                    "python": 3, "machine learning": 3, "data analysis": 3, "sql": 2,
                    "statistics": 2, "pandas": 2, "numpy": 2, "scikit-learn": 2,
                    "tensorflow": 2, "pytorch": 2, "deep learning": 2, "data visualization": 2,
                    "big data": 1, "hadoop": 1, "spark": 1, "aws": 1, "azure": 1
                },
                "experience_keywords": {
                    "years": 2, "experience": 2, "developed": 1, "implemented": 1,
                    "managed": 1, "led": 1, "created": 1, "built": 1
                }
            },
            "Software Engineer": {
                "keywords": {
                    "java": 3, "python": 3, "c++": 3, "javascript": 2, "html": 2,
                    "css": 2, "react": 2, "angular": 2, "node.js": 2, "git": 2,
                    "agile": 2, "software development": 3, "api": 2, "rest": 2,
                    "docker": 1, "kubernetes": 1, "ci/cd": 1, "testing": 1, "debugging": 1
                },
                "experience_keywords": {
                    "years": 2, "experience": 2, "developed": 1, "implemented": 1,
                    "managed": 1, "led": 1, "created": 1, "built": 1, "designed": 1
                }
            },
            "Data Analyst": {
                "keywords": {
                    "sql": 3, "excel": 3, "tableau": 3, "power bi": 3, "python": 2,
                    "r": 2, "data visualization": 2, "statistics": 2, "reporting": 2,
                    "dashboard": 2, "data cleaning": 2, "etl": 1, "business intelligence": 1
                },
                "experience_keywords": {
                    "years": 2, "experience": 2, "analyzed": 1, "reported": 1,
                    "presented": 1, "created": 1, "developed": 1, "managed": 1
                }
            },
            "Product Manager": {
                "keywords": {
                    "product strategy": 3, "roadmap": 3, "user stories": 3, "agile": 2,
                    "scrum": 2, "market research": 2, "customer development": 2,
                    "prioritization": 2, "kpis": 2, "metrics": 2, "stakeholder management": 2,
                    "wireframes": 1, "prototyping": 1, "a/b testing": 1, "jira": 1
                },
                "experience_keywords": {
                    "years": 2, "experience": 2, "managed": 1, "led": 1, "developed": 1,
                    "launched": 1, "strategized": 1, "coordinated": 1, "oversaw": 1
                }
            }
        }
        
        # --- NEW: Load roles from JSON ---
        self.roles_file = 'job_roles.json'
        self.job_roles = self.load_roles()
        # ---------------------------------

        # Initialize main window using ttkbootstrap
        # --- NEW: Changed theme to "darkly" ---
        self.root = ttk.Window() # Removed themename
        self.style = self.root.style
        self.style.theme_use('darkly') # Set theme manually
        self.root.title("AI Resume Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600) # Set a minimum size

        # Initialize data
        self.resume_text = ""
        self.analysis_results = {}
        self.preview_photo = None # For PDF preview

        self.setup_gui()

    # --- NEW: Load roles from JSON file ---
    def load_roles(self):
        try:
            with open(self.roles_file, 'r') as f:
                roles = json.load(f)
            if not roles:
                # File is empty, use default and save
                self.save_roles(self.default_job_roles)
                return self.default_job_roles
            return roles
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is invalid, create it with defaults
            self.save_roles(self.default_job_roles)
            return self.default_job_roles
        except Exception as e:
            print(f"Error loading roles: {e}")
            return self.default_job_roles

    # --- NEW: Save roles to JSON file ---
    def save_roles(self, roles_data):
        try:
            with open(self.roles_file, 'w') as f:
                json.dump(roles_data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save roles to {self.roles_file}: {e}")
    # ------------------------------------

    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # --- NEW: Added icons to tabs (using unicode) ---
        # You can use ttk.PhotoImage for custom images
        
        # Upload Tab
        self.upload_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.upload_frame, text=" ⬆ Upload Resume ")
        self.setup_upload_tab()

        # Analysis Tab
        self.analysis_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.analysis_frame, text=" 📊 Analysis Results ")
        self.setup_analysis_tab()

        # Visualization Tab
        self.viz_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.viz_frame, text=" 📈 Visualizations ")
        self.setup_viz_tab()

        # --- NEW: Manage Roles Tab ---
        self.manage_roles_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.manage_roles_frame, text=" ⚙ Manage Roles ")
        self.setup_manage_roles_tab()
        # -----------------------------

        # --- NEW: Theme Toggle Button ---
        theme_frame = ttk.Frame(self.root)
        theme_frame.pack(side='bottom', fill='x', padx=10, pady=(0, 5), anchor='e')
        
        self.theme_toggle = ttk.Checkbutton(
            theme_frame, 
            text='🌙 Dark Mode', 
            command=self.toggle_theme, 
            bootstyle="round-toggle"
        )
        self.theme_toggle.pack(side='right')
        self.theme_toggle.invoke() # Start in Dark Mode
        # ------------------------------

    def setup_upload_tab(self):
        # Title
        title_label = ttk.Label(self.upload_frame, text="AI Resume Analyzer",
                                font=("", 20, "bold"), bootstyle="primary")
        title_label.pack(pady=10)

        # Instructions
        instructions = ttk.Label(self.upload_frame,
                                 text="Upload or paste your resume, then click 'Analyze' to see your job match scores.",
                                 font=("", 12), wraplength=800, justify="center",
                                 bootstyle="secondary")
        instructions.pack(pady=10)

        # Main content frame to hold two columns
        main_content_frame = ttk.Frame(self.upload_frame)
        main_content_frame.pack(fill='both', expand=True, pady=10, padx=20)

        # --- MODIFICATION: Left Column is now Scrollable ---
        
        # 1. Create a Canvas and a Scrollbar for the left side
        # --- FIX: Move 'width=280' from .pack() to the constructor ---
        self.left_canvas = tk.Canvas(main_content_frame, highlightthickness=0, bg=self.root.style.colors.bg, width=280)
        left_scrollbar = ttk.Scrollbar(main_content_frame, orient="vertical", command=self.left_canvas.yview)
        
        # 2. Create the frame that will hold the content
        self.left_column = ttk.Frame(self.left_canvas, bootstyle="dark")
        self.left_column.columnconfigure(0, weight=1) # Make content inside fill the frame

        # 3. Bind the frame's <Configure> event to update the canvas scrollregion
        self.left_column.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )

        # 4. Put the scrollable_frame into the canvas
        # --- FIX: Use self.left_canvas ---
        left_canvas_frame_id = self.left_canvas.create_window((0, 0), window=self.left_column, anchor="nw")

        # 5. Bind the canvas's <Configure> event to update the frame's width
        def on_left_canvas_configure(event):
            # --- FIX: Use self.left_canvas ---
            self.left_canvas.itemconfig(left_canvas_frame_id, width=event.width)

        # --- FIX: Use self.left_canvas ---
        self.left_canvas.bind("<Configure>", on_left_canvas_configure)
        
        # 6. Configure the canvas to use the scrollbar
        # --- FIX: Use self.left_canvas ---
        self.left_canvas.configure(yscrollcommand=left_scrollbar.set)

        # 7. Pack the canvas and scrollbar (canvas has fixed width, scrollbar appears as needed)
        # --- FIX: Remove 'width=280' from .pack() ---
        self.left_canvas.pack(side="left", fill="y", expand=False) # Give it a fixed width
        left_scrollbar.pack(side="left", fill="y")
        
        # --- END MODIFICATION ---

        # Right Column (Text Area)
        right_column = ttk.Frame(main_content_frame)
        right_column.pack(side='right', fill='both', expand=True, padx=(15, 0))

        # --- Populate Left Column (in NEW ORDER) ---
        
        # --- 1. PDF Preview Frame (MOVED TO TOP) ---
        self.preview_frame = ttk.Labelframe(self.left_column, text="PDF Preview", padding=10)
        self.preview_frame.pack(fill='x', pady=15, padx=10)
        
        self.preview_image_label = ttk.Label(self.preview_frame, text="Upload a PDF to see a preview", bootstyle="secondary", justify="center")
        self.preview_image_label.pack(fill='x')
        # -----------------------------
        
        # --- 2. Load Resume ---
        upload_options_frame = ttk.Labelframe(self.left_column, text="Option 1: Load Resume", padding=15)
        upload_options_frame.pack(fill='x', pady=(0, 15), padx=10)

        upload_btn = ttk.Button(upload_options_frame, text="Upload File (.pdf, .docx, .txt)",
                                command=self.upload_file, bootstyle="primary",
                                padding=(10, 8))
        upload_btn.pack(fill='x', pady=5)

        sample_btn = ttk.Button(upload_options_frame, text="Load Sample Resume",
                                command=self.load_sample, bootstyle="info-outline",
                                padding=(10, 8))
        sample_btn.pack(fill='x', pady=5)

        # --- 3. Analyze ---
        analyze_controls_frame = ttk.Labelframe(self.left_column, text="Option 2: Analyze", padding=15)
        analyze_controls_frame.pack(fill='x', padx=10, pady=(0, 15))

        analyze_btn = ttk.Button(analyze_controls_frame, text="Analyze Resume",
                                 command=self.analyze_resume, bootstyle="success",
                                 padding=(10, 8))
        analyze_btn.pack(fill='x', pady=5)

        clear_btn = ttk.Button(analyze_controls_frame, text="Clear Text",
                               command=self.clear_text, bootstyle="danger-outline",
                               padding=(10, 8))
        clear_btn.pack(fill='x', pady=5)

        # --- Populate Right Column ---

        paste_text_frame = ttk.Labelframe(right_column, text="Resume Content", padding=15)
        paste_text_frame.pack(fill='both', expand=True)

        # Use a StringVar to update the label
        self.file_status_var = tk.StringVar()
        self.file_status_var.set("Paste your resume text below or upload a file")
        
        text_label = ttk.Label(paste_text_frame, textvariable=self.file_status_var,
                               font=("", 10, "bold"), anchor="w",
                               bootstyle="secondary")
        text_label.pack(fill='x', pady=(0, 5))

        # Use ttkbootstrap's ScrolledText for a themed look
        self.resume_text_area = ScrolledText(paste_text_frame, height=15,
                                             font=("", 10), wrap=tk.WORD,
                                             autohide=True,
                                             relief="solid", borderwidth=1)
        self.resume_text_area.pack(fill='both', expand=True, pady=5)

    def setup_analysis_tab(self):
        # Results frame
        self.results_frame = ttk.Frame(self.analysis_frame)
        self.results_frame.pack(fill='both', expand=True)

        # Initially show placeholder
        placeholder = ttk.Label(self.results_frame, text="Upload Your Resume and Click 'Analyze Resume' to see results",
                                font=("", 14), bootstyle="secondary", anchor="center")
        placeholder.pack(expand=True, fill='both')
        self.analysis_placeholder = placeholder

    def setup_viz_tab(self):
        # Visualization frame
        self.viz_container = ttk.Frame(self.viz_frame)
        self.viz_container.pack(fill='both', expand=True)

        # Initially show placeholder
        viz_placeholder = ttk.Label(self.viz_container, text="Visualizations will appear here after analysis",
                                    font=("", 14), bootstyle="secondary", anchor="center")
        viz_placeholder.pack(expand=True, fill='both')
        self.viz_placeholder = viz_placeholder

    # --- NEW: Manage Roles Tab UI ---
    def setup_manage_roles_tab(self):
        # Top frame for selection
        top_frame = ttk.Frame(self.manage_roles_frame)
        top_frame.pack(fill='x', pady=(5, 10))

        select_label = ttk.Label(top_frame, text="Select Role to Edit:", font=("", 10, "bold"))
        select_label.pack(side='left', padx=(0, 10))

        self.role_combobox = ttk.Combobox(top_frame, state="readonly")
        self.role_combobox.pack(side='left', fill='x', expand=True)
        self.update_role_combobox() # Populate
        
        # Bind selection event
        self.role_combobox.bind("<<ComboboxSelected>>", self.on_role_select)

        # Main frame for editing
        edit_frame = ttk.Frame(self.manage_roles_frame)
        edit_frame.pack(fill='both', expand=True)
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.rowconfigure(3, weight=1) # Updated row index
        
        # Role Name
        role_name_label = ttk.Label(edit_frame, text="Role Name:", font=("", 10, "bold"))
        role_name_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(10,0))
        
        self.role_name_entry = ttk.Entry(edit_frame)
        self.role_name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        # Keywords
        keywords_label = ttk.Label(edit_frame, text="Skill Keywords (format: skill:weight):", font=("", 10, "bold"))
        keywords_label.grid(row=2, column=0, sticky='nw', pady=(5,0))
        
        self.keywords_text = ScrolledText(edit_frame, wrap=tk.WORD, height=10, autohide=True, relief="solid", borderwidth=1)
        self.keywords_text.grid(row=3, column=0, sticky='nsew', pady=5, padx=(0, 5))

        # Experience Keywords
        exp_keywords_label = ttk.Label(edit_frame, text="Experience Keywords (format: keyword:weight):", font=("", 10, "bold"))
        exp_keywords_label.grid(row=2, column=1, sticky='nw', pady=(5,0))
        
        self.exp_keywords_text = ScrolledText(edit_frame, wrap=tk.WORD, height=10, autohide=True, relief="solid", borderwidth=1)
        self.exp_keywords_text.grid(row=3, column=1, sticky='nsew', pady=5, padx=(5, 0))

        # Buttons
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')
        button_frame.columnconfigure((0, 1), weight=1)

        save_btn = ttk.Button(button_frame, text="Save Role", command=self.save_role, bootstyle="success")
        save_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        delete_btn = ttk.Button(button_frame, text="Delete Selected Role", command=self.delete_role, bootstyle="danger-outline")
        delete_btn.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        # Set initial state
        self.role_combobox.set("Select a role or type a new name")

    # --- NEW: Helper for Manage Roles Tab ---
    def update_role_combobox(self):
        """Refreshes the role combobox list from self.job_roles."""
        roles = list(self.job_roles.keys())
        self.role_combobox['values'] = roles
        if roles:
            self.role_combobox.set("Select a role to edit")
        else:
            self.role_combobox.set("No roles found. Add one!")

    # --- NEW: Helper for Manage Roles Tab ---
    def on_role_select(self, event=None):
        """Populates the edit fields when a role is selected."""
        role_name = self.role_combobox.get()
        if role_name not in self.job_roles:
            self.clear_role_fields()
            return
            
        role_data = self.job_roles[role_name]
        
        # Populate fields
        self.role_name_entry.delete(0, tk.END)
        self.role_name_entry.insert(0, role_name)
        
        self.keywords_text.delete(1.0, tk.END)
        keywords_str = "\n".join([f"{k}:{v}" for k, v in role_data.get("keywords", {}).items()])
        self.keywords_text.insert(1.0, keywords_str)
        
        self.exp_keywords_text.delete(1.0, tk.END)
        exp_keywords_str = "\n".join([f"{k}:{v}" for k, v in role_data.get("experience_keywords", {}).items()])
        self.exp_keywords_text.insert(1.0, exp_keywords_str)

    # --- NEW: Helper for Manage Roles Tab ---
    def clear_role_fields(self):
        """Clears all fields in the manage roles tab."""
        self.role_name_entry.delete(0, tk.END)
        self.keywords_text.delete(1.0, tk.END)
        self.exp_keywords_text.delete(1.0, tk.END)
        self.role_combobox.set("Select a role or type a new name")

    # --- NEW: Helper for Manage Roles Tab ---
    def save_role(self):
        """Saves the role data from the UI."""
        role_name = self.role_name_entry.get().strip()
        if not role_name:
            messagebox.showwarning("Input Error", "Role Name cannot be empty.")
            return

        def parse_keywords(text_widget):
            """Helper to parse keyword text boxes."""
            keywords = {}
            text = text_widget.get(1.0, tk.END).strip()
            if not text:
                return keywords # Allow empty
            lines = text.split("\n")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                if ':' not in line:
                    raise ValueError(f"Invalid format on line {i}: '{line}'. Must be 'skill:weight'.")
                
                parts = line.split(':', 1)
                skill = parts[0].strip().lower()
                weight_str = parts[1].strip()
                
                if not skill:
                    raise ValueError(f"Missing skill name on line {i}.")
                try:
                    weight = int(weight_str)
                except ValueError:
                    raise ValueError(f"Invalid weight '{weight_str}' on line {i}. Must be an integer.")
                
                if weight <= 0:
                    raise ValueError(f"Weight for '{skill}' must be positive.")
                
                keywords[skill] = weight
            return keywords

        try:
            keywords_dict = parse_keywords(self.keywords_text)
            exp_keywords_dict = parse_keywords(self.exp_keywords_text)
            
            # Create new role data
            new_role_data = {
                "keywords": keywords_dict,
                "experience_keywords": exp_keywords_dict
            }
            
            # Add or update in main dict
            self.job_roles[role_name] = new_role_data
            
            # Save to file
            self.save_roles(self.job_roles)
            
            # Update UI
            self.update_role_combobox()
            self.role_combobox.set(role_name) # Select the saved role
            
            messagebox.showinfo("Success", f"Role '{role_name}' saved successfully!")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    # --- NEW: Helper for Manage Roles Tab ---
    def delete_role(self):
        """Deletes the selected role."""
        role_name = self.role_combobox.get()
        if role_name not in self.job_roles:
            messagebox.showwarning("Selection Error", "Please select a valid role to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the role '{role_name}'?"):
            return
            
        try:
            # Delete from dict
            del self.job_roles[role_name]
            
            # Save changes to file
            self.save_roles(self.job_roles)
            
            # Update UI
            self.clear_role_fields()
            self.update_role_combobox()
            
            messagebox.showinfo("Success", f"Role '{role_name}' deleted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete role: {e}")
    # ------------------------------------

    # --- NEW: Theme Toggle Functions ---
    def toggle_theme(self):
        """Switches the application theme between light and dark."""
        if self.theme_toggle.instate(['selected']):
            # Switch to Dark Mode
            self.style.theme_use('darkly')
            self.theme_toggle.configure(text='🌙 Dark Mode')
        else:
            # Switch to Light Mode
            self.style.theme_use('litera')
            self.theme_toggle.configure(text='☀️ Light Mode')
        
        # Update custom widgets that don't auto-refresh
        self.update_widget_colors()
        
        # Redraw data-driven tabs if they exist
        if self.analysis_results:
            self.display_analysis_results()
            self.generate_visualizations()

    def update_widget_colors(self):
        """Manually updates the background colors of canvas widgets."""
        new_bg = self.style.colors.bg
        is_dark = self.style.theme.name == "darkly"
        new_bootstyle = "dark" if is_dark else "light"

        # Update Upload Tab
        self.left_canvas.configure(bg=new_bg)
        self.left_column.configure(bootstyle=new_bootstyle)

        # Update Viz Tab (if it has been drawn)
        if hasattr(self, 'viz_canvas'):
            self.viz_canvas.configure(bg=new_bg)
        if hasattr(self, 'viz_scrollable_frame'):
            self.viz_scrollable_frame.configure(bootstyle=new_bootstyle)
    # ---------------------------------

    # --- NEW: Helper for PDF Preview ---
    def show_pdf_preview(self, file_path):
        """Renders the first page of a PDF in the preview label."""
        if fitz is None or Image is None or ImageTk is None:
            self.clear_pdf_preview("PDF libraries not loaded.")
            return

        try:
            doc = fitz.open(file_path)
            page = doc.load_page(0) # Get first page

            # Render page to pixels
            pix = page.get_pixmap()
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            
            # Resize image to fit label (max width of the left column)
            max_w = 250 # Should match the canvas width minus padding
            if img.width > max_w:
                w_percent = (max_w / float(img.width))
                h_size = int((float(img.height) * float(w_percent)))
                img = img.resize((max_w, h_size), Image.LANCZOS)

            # Convert to PhotoImage and display
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_image_label.configure(image=self.preview_photo, text="")
            doc.close()

        except Exception as e:
            self.clear_pdf_preview(f"Error: {e}")
            print(f"Failed to preview PDF: {e}")

    # --- NEW: Helper for PDF Preview ---
    def clear_pdf_preview(self, text="Upload a PDF to see a preview"):
        """Clears the PDF preview label."""
        self.preview_image_label.configure(image="", text=text)
        self.preview_photo = None
    # ---------------------------------

    def upload_file(self):
        # Check if file reading libraries are available
        if fitz is None or Document is None:
            messagebox.showerror("Missing Libraries", 
                                 "PDF or DOCX reading libraries are not installed. Please check the console for installation instructions.")
            return

        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[
                ("Supported Files", "*.pdf;*.docx;*.txt"),
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                content = ""
                
                # --- NEW: Handle PDF Preview ---
                if file_path.endswith('.pdf'):
                    self.show_pdf_preview(file_path)
                else:
                    self.clear_pdf_preview("Preview only for PDF files.")
                # -------------------------------

                # TXT file
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()

                # PDF file
                elif file_path.endswith('.pdf'):
                    pdf_doc = fitz.open(file_path)
                    for page in pdf_doc:
                        content += page.get_text()
                    pdf_doc.close()

                # Word file (.docx)
                elif file_path.endswith('.docx'):
                    doc = Document(file_path)
                    for para in doc.paragraphs:
                        content += para.text + "\n"

                else:
                    messagebox.showwarning("Unsupported Format", "Please upload a .txt, .pdf, or .docx file.")
                    return

                if not content.strip():
                    messagebox.showwarning("Empty File", "The file seems to be empty.")
                    return

                # Paste content into text area
                self.resume_text_area.delete(1.0, tk.END)
                self.resume_text_area.insert(1.0, content)

                # Update the status label with the file name
                file_name = os.path.basename(file_path)
                self.file_status_var.set(f"Successfully loaded: {file_name}")

                messagebox.showinfo("Success", "Resume uploaded successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")

    def clear_text(self):
        self.resume_text_area.delete(1.0, tk.END)
        # Reset the status label
        self.file_status_var.set("Paste your resume text below or upload a file")
        # --- NEW: Clear preview ---
        self.clear_pdf_preview()
    
    def load_sample(self):
        sample_resume = """
        John Doe
        Data Scientist
        john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe
        
        SUMMARY
        Experienced Data Scientist with 5+ years of expertise in machine learning, data analysis, and predictive modeling. 
        Proficient in Python, SQL, and various ML frameworks including TensorFlow and Scikit-learn.
        
        EXPERIENCE
        Senior Data Scientist, Tech Company Inc. (2019 - Present)
        - Developed and deployed machine learning models for customer segmentation
        - Implemented natural language processing algorithms for text classification
        - Built data pipelines using Python, Pandas, and SQL
        - Created interactive dashboards using Tableau and Power BI
        
        Data Analyst, Analytics Firm (2017 - 2019)
        - Analyzed large datasets to derive business insights
        - Created statistical models for forecasting sales
        - Developed ETL processes for data cleaning and transformation
        
        SKILLS
        Programming: Python, R, SQL, Java
        Machine Learning: Scikit-learn, TensorFlow, PyTorch, Keras
        Data Analysis: Pandas, NumPy, Matplotlib, Seaborn
        Tools: Git, Docker, AWS, Azure, Tableau, Power BI
        """
        
        self.resume_text_area.delete(1.0, tk.END)
        self.resume_text_area.insert(1.0, sample_resume)
        # Update the status label
        self.file_status_var.set("Sample Resume Loaded")
        # --- NEW: Clear preview ---
        self.clear_pdf_preview("Preview only for PDF files.")

    def analyze_resume(self):
        self.resume_text = self.resume_text_area.get(1.0, tk.END).strip()

        if not self.resume_text:
            messagebox.showwarning("Input Error", "Please enter or upload resume text.")
            return

        # Perform analysis
        try:
            # --- RELOAD ROLES IN CASE THEY WERE EDITED ---
            self.job_roles = self.load_roles()
            # -------------------------------------------

            self.analysis_results = self.analyze_resume_text(self.resume_text)
            
            # Switch to analysis tab and display results
            self.notebook.select(1)  # Switch to Analysis Results tab
            self.display_analysis_results()

            # Generate visualizations
            self.generate_visualizations()

            messagebox.showinfo("Analysis Complete", "Resume analysis completed successfully!")
        
        except Exception as e:
            messagebox.showerror("Analysis Error", f"An unexpected error occurred during analysis: {e}")


    def analyze_resume_text(self, text):
        results = {}
        text_lower = text.lower()
        
        if not self.job_roles:
            messagebox.showwarning("No Roles", "No job roles are defined. Please add one in the 'Manage Roles' tab.")
            return {}

        for role, role_data in self.job_roles.items():
            # Calculate skill match
            skill_score = 0
            # Use sum of weights as max score
            max_skill_score = sum(role_data.get("keywords", {}).values())
            
            found_skills = {}
            for skill, weight in role_data.get("keywords", {}).items():
                pattern = r'\b' + re.escape(skill) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Score based on weight * occurrences
                    skill_score += weight * len(matches) 
                    found_skills[skill] = len(matches)
            
            # Normalize the score against the max possible score (if all skills found once)
            skill_match_percentage = (skill_score / max_skill_score) * 100 if max_skill_score > 0 else 0
            
            # --- Better approach: Cap score at max_skill_score ---
            skill_score_capped = 0
            for skill, weight in role_data.get("keywords", {}).items():
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    skill_score_capped += weight # Add weight only once per skill
                    
            # Recalculate percentage based on finding the skill *at all*
            skill_match_percentage = (skill_score_capped / max_skill_score) * 100 if max_skill_score > 0 else 0


            # Calculate experience indicators
            exp_score = 0
            max_exp_score = sum(role_data.get("experience_keywords", {}).values())
            
            found_exp = {}
            for exp_keyword, weight in role_data.get("experience_keywords", {}).items():
                pattern = r'\b' + re.escape(exp_keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    exp_score += weight * len(matches)
                    found_exp[exp_keyword] = len(matches)
            
            # Same cap logic for experience
            exp_score_capped = 0
            for exp_keyword, weight in role_data.get("experience_keywords", {}).items():
                pattern = r'\b' + re.escape(exp_keyword) + r'\b'
                if re.search(pattern, text_lower):
                    exp_score_capped += weight
            
            exp_match_percentage = (exp_score_capped / max_exp_score) * 100 if max_exp_score > 0 else 0

            # Calculate overall match (weighted average)
            overall_match = (skill_match_percentage * 0.7) + (exp_match_percentage * 0.3)
            
            results[role] = {
                "skill_match": skill_match_percentage,
                "experience_match": exp_match_percentage,
                "overall_match": overall_match,
                "found_skills": found_skills, # Keep original count here for user info
                "found_experience": found_exp,
                "missing_skills": [skill for skill in role_data.get("keywords", {}) if skill not in found_skills]
            }

        return results

    def display_analysis_results(self):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not self.analysis_results:
            no_results = ttk.Label(self.results_frame, text="No analysis results available",
                                   font=("", 14), bootstyle="secondary")
            no_results.pack(expand=True)
            return

        # Create a scrollable frame for results
        # Use ttkbootstrap's ScrolledFrame for simplicity
        scrollable_frame = ScrolledText(self.results_frame, autohide=True, padding=10)
        scrollable_frame.pack(fill='both', expand=True)
        
        # We must use a sub-frame inside the ScrolledText 'window'
        results_container = ttk.Frame(scrollable_frame)
        scrollable_frame.window_create(tk.END, window=results_container)


        # Title
        title = ttk.Label(results_container, text="Resume Analysis Results",
                            font=("", 18, "bold"), bootstyle="secondary")
        title.pack(pady=10)

        # --- NEW: Recommendations Section ---
        try:
            self.create_recommendations(results_container)
        except Exception as e:
            print(f"Error creating recommendations: {e}")
        # ------------------------------------


        # Sort results by overall match
        sorted_results = sorted(self.analysis_results.items(), key=lambda item: item[1]['overall_match'], reverse=True)

        # --- NEW: Get theme-aware bootstyles ---
        theme_bootstyle = "light" if self.style.theme.name == "litera" else "dark"
        label_bootstyle = "dark" if self.style.theme.name == "litera" else "light"
        # ---------------------------------------

        # Create results for each job role
        for role, data in sorted_results:
            role_frame = ttk.Frame(results_container, bootstyle=theme_bootstyle, relief="solid", borderwidth=1)
            role_frame.pack(fill='x', padx=10, pady=10)

            # Role header
            header_frame = ttk.Frame(role_frame, bootstyle="primary", padding=10)
            header_frame.pack(fill='x')

            role_label = ttk.Label(header_frame, text=role, font=("", 16, "bold"),
                                   bootstyle="primary-inverse")
            role_label.pack(side='left')

            match_label = ttk.Label(header_frame,
                                    text=f"Overall Match: {data['overall_match']:.1f}%",
                                    font=("", 14, "bold"), bootstyle="primary-inverse",
                                    padding=5)
            match_label.pack(side='right')

            # Match details
            details_frame = ttk.Frame(role_frame, bootstyle=theme_bootstyle, padding=10)
            details_frame.pack(fill='x')

            # --- NEW: Use ttk.Meter widgets ---
            meters_frame = ttk.Frame(details_frame, bootstyle=theme_bootstyle)
            meters_frame.pack(fill='x', pady=10)

            skills_meter = ttk.Meter(
                meters_frame,
                metersize=160,
                amountused=data['skill_match'],
                textright="%",
                subtext="Skills Match",
                bootstyle="success"
            )
            skills_meter.pack(side='left', expand=True, padx=20)

            exp_meter = ttk.Meter(
                meters_frame,
                metersize=160,
                amountused=data['experience_match'],
                textright="%",
                subtext="Experience Indicators",
                bootstyle="info"
            )
            exp_meter.pack(side='right', expand=True, padx=20)
            # ------------------------------------

            # Found skills
            if data['found_skills']:
                found_skills_frame = ttk.Frame(details_frame, bootstyle=theme_bootstyle)
                found_skills_frame.pack(fill='x', pady=5)

                found_label = ttk.Label(found_skills_frame, text="Found Skills:",
                                        font=("", 11, "bold"), bootstyle=label_bootstyle)
                found_label.pack(anchor='w')

                skills_text = ", ".join([f"{skill} ({count}x)" for skill, count in data['found_skills'].items()])
                skills_display = ttk.Label(found_skills_frame, text=skills_text,
                                           font=("", 10), bootstyle=label_bootstyle,
                                           wraplength=800, justify="left")
                skills_display.pack(anchor='w')

            # Missing skills
            if data['missing_skills']:
                missing_skills_frame = ttk.Frame(details_frame, bootstyle=theme_bootstyle)
                missing_skills_frame.pack(fill='x', pady=5)

                missing_label = ttk.Label(missing_skills_frame, text="Missing Skills:",
                                          font=("", 11, "bold"), bootstyle="danger")
                missing_label.pack(anchor='w')

                missing_text = ", ".join(data['missing_skills'])
                missing_display = ttk.Label(missing_skills_frame, text=missing_text,
                                            font=("", 10), bootstyle="danger",
                                            wraplength=800, justify="left")
                missing_display.pack(anchor='w')

    # --- NEW: Recommendations Helper ---
    def create_recommendations(self, parent):
        """Finds the best role and recommends missing keywords."""
        if not self.analysis_results:
            return

        # Find best role
        best_role_name = max(self.analysis_results, key=lambda r: self.analysis_results[r]['overall_match'])
        best_role_data = self.analysis_results[best_role_name]
        
        if best_role_data['overall_match'] < 10: # Don't recommend if match is too low
            return

        missing_skills = best_role_data['missing_skills']
        if not missing_skills:
            rec_text = f"Congratulations! You're an excellent match for {best_role_name} and aren't missing any key skills."
        else:
            # Get the *weights* for the missing skills
            role_keywords = self.job_roles[best_role_name].get("keywords", {})
            weighted_missing = [(skill, role_keywords.get(skill, 0)) for skill in missing_skills]
            
            # Sort by weight (highest first)
            weighted_missing.sort(key=lambda x: x[1], reverse=True)
            
            # Get top 5 missing keywords
            top_missing = [skill[0] for skill in weighted_missing[:5]]
            
            rec_text = (f"Your top match is {best_role_name} ({best_role_data['overall_match']:.1f}%).\n\n"
                        f"To improve your score:\nTry to include some of these high-value keywords you're missing:\n"
                        f"• {', '.join(top_missing)}")

        rec_frame = ttk.Labelframe(parent, text=" 💡 Top Recommendations ", padding=15, bootstyle="success")
        rec_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        rec_label = ttk.Label(rec_frame, text=rec_text, wraplength=750, justify='left', font=("", 11), bootstyle="inverse-success")
        rec_label.pack(fill='x')
    # -----------------------------------

    def generate_visualizations(self):
        # Clear previous visualizations
        for widget in self.viz_container.winfo_children():
            widget.destroy()

        if not self.analysis_results:
            no_viz = ttk.Label(self.viz_container, text="No data available for visualization",
                               font=("", 14), bootstyle="secondary")
            no_viz.pack(expand=True)
            return
        
        # --- ROBUST SCROLLABLE FRAME (THE CORRECT FIX) ---
        
        # 1. Create a Canvas and a Scrollbar
        self.viz_canvas = tk.Canvas(self.viz_container, highlightthickness=0, bg=self.root.style.colors.bg) # remove canvas border
        scrollbar = ttk.Scrollbar(self.viz_container, orient="vertical", command=self.viz_canvas.yview)
        
        # 2. Create the frame that will hold the content
        viz_bootstyle = "dark" if self.style.theme.name == "darkly" else "light"
        self.viz_scrollable_frame = ttk.Frame(self.viz_canvas, bootstyle=viz_bootstyle)
        self.viz_canvas.configure(bg=self.root.style.colors.bg)
        
        # 3. Bind the frame's <Configure> event to update the canvas scrollregion
        self.viz_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        )

        # 4. Put the scrollable_frame into the canvas using a canvas "window"
        canvas_frame_id = self.viz_canvas.create_window((0, 0), window=self.viz_scrollable_frame, anchor="nw")

        # 5. CRITICAL FIX: Bind the canvas's <Configure> event to update the frame's width
        # This makes the content frame fill the width of the canvas
        def on_canvas_configure(event):
            self.viz_canvas.itemconfig(canvas_frame_id, width=event.width)

        self.viz_canvas.bind("<Configure>", on_canvas_configure)
        
        # 6. Configure the canvas to use the scrollbar
        self.viz_canvas.configure(yscrollcommand=scrollbar.set)

        # 7. Pack the canvas and scrollbar into the main container
        self.viz_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- END ROBUST SCROLLABLE FRAME ---


        # Title (pack into the scrollable_frame)
        title_bootstyle = "inverse-dark" if self.style.theme.name == "darkly" else "inverse-light"
        title = ttk.Label(self.viz_scrollable_frame, text="Resume Analysis Visualizations",
                          font=("", 18, "bold"), bootstyle=title_bootstyle)
        title.pack(pady=10, fill='x', padx=10)

        # Create visualizations (pack into the scrollable_frame)
        self.create_match_comparison_chart(self.viz_scrollable_frame)
        # --- NEW: Add Treemap ---
        if squarify:
            self.create_skill_treemap(self.viz_scrollable_frame)
        # ------------------------
        self.create_skill_breakdown_chart(self.viz_scrollable_frame)
        self.create_radar_chart(self.viz_scrollable_frame)

    def create_match_comparison_chart(self, parent):
        # Prepare data for bar chart
        roles = list(self.analysis_results.keys())
        if not roles: return # Nothing to plot
        
        overall_matches = [self.analysis_results[role]['overall_match'] for role in roles]
        skill_matches = [self.analysis_results[role]['skill_match'] for role in roles]
        exp_matches = [self.analysis_results[role]['experience_match'] for role in roles]

        # Create DataFrame for seaborn
        df = pd.DataFrame({
            'Role': roles * 3,
            'Match Type': ['Overall'] * len(roles) + ['Skills'] * len(roles) + ['Experience'] * len(roles),
            'Percentage': overall_matches + skill_matches + exp_matches
        })

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.root.style.colors.bg) # Match fig background to app
        ax.set_facecolor(self.root.style.colors.bg) # Match plot background to app

        # --- Set text color for dark theme ---
        text_color = self.root.style.colors.fg
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        # -----------------------------------

        # Create bar plot
        sns.barplot(data=df, x='Role', y='Percentage', hue='Match Type', ax=ax, palette='viridis')

        ax.set_title('Resume Match Percentage by Job Role', fontsize=16, fontweight='bold')
        ax.set_ylabel('Match Percentage (%)', fontsize=12)
        ax.set_xlabel('Job Role', fontsize=12)
        ax.tick_params(axis='x', rotation=25) # Less rotation is cleaner
        
        legend = ax.legend(title='Match Type')
        plt.setp(legend.get_texts(), color=text_color)
        plt.setp(legend.get_title(), color=text_color)
        
        ax.set_ylim(0, 100) # Ensure y-axis is 0-100

        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3, fontsize=9, color=text_color)

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    # --- NEW: Treemap Visualization ---
    def create_skill_treemap(self, parent):
        all_found_skills = {}
        for role, data in self.analysis_results.items():
            for skill, count in data.get('found_skills', {}).items():
                if skill in all_found_skills:
                    all_found_skills[skill] += count
                else:
                    all_found_skills[skill] = count

        if not all_found_skills: # Skip if no skills
            return
            
        # Get counts and labels
        counts = list(all_found_skills.values())
        labels = [f"{skill}\n({count}x)" for skill, count in all_found_skills.items()]
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.root.style.colors.bg)
        ax.set_facecolor(self.root.style.colors.bg)
        
        text_color = self.root.style.colors.fg
        ax.title.set_color(text_color)

        # Create treemap
        try:
            squarify.plot(sizes=counts, label=labels, ax=ax,
                          color=sns.color_palette("viridis", len(counts)),
                          text_kwargs={'color': 'white', 'fontsize': 10})
            
            ax.set_title('Overall Skill Frequency Treemap', fontsize=16, fontweight='bold')
            ax.axis('off')
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Failed to create treemap: {e}")
    # ---------------------------------

    def create_skill_breakdown_chart(self, parent):
        # Prepare data for horizontal bar chart of found skills
        all_found_skills = {}
        for role, data in self.analysis_results.items():
            for skill, count in data.get('found_skills', {}).items():
                if skill in all_found_skills:
                    all_found_skills[skill] += count
                else:
                    all_found_skills[skill] = count

        if not all_found_skills: # Skip if no skills were found
            return

        # Sort skills by frequency
        sorted_skills = sorted(all_found_skills.items(), key=lambda x: x[1], reverse=True)
        skills = [item[0] for item in sorted_skills[:15]]  # Top 15 skills
        counts = [item[1] for item in sorted_skills[:15]]

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor(self.root.style.colors.bg)
        ax.set_facecolor(self.root.style.colors.bg)
        
        text_color = self.root.style.colors.fg
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        
        # Create horizontal bar plot
        y_pos = np.arange(len(skills))
        
        # Use a ttkbootstrap-friendly color
        primary_color = self.root.style.colors.primary
        ax.barh(y_pos, counts, color=primary_color)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(skills)
        ax.invert_yaxis()  # Highest values at the top
        ax.set_xlabel('Frequency in Resume', fontsize=12)
        ax.set_title('Top Skills Found in Resume', fontsize=16, fontweight='bold')

        # Add value labels on bars
        for i, v in enumerate(counts):
            ax.text(v + 0.1, i, str(v), va='center', color=text_color)

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_radar_chart(self, parent):
        # Prepare data for radar chart
        categories = list(self.analysis_results.keys())
        N = len(categories)
        if N < 3: # Radar charts need at least 3 points
            return 

        # Values for each category (overall match percentages)
        values = [self.analysis_results[role]['overall_match'] for role in categories]
        values += values[:1]  # Complete the circle

        # Compute angles for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        fig.patch.set_facecolor(self.root.style.colors.bg)
        ax.set_facecolor(self.root.style.colors.bg)

        text_color = self.root.style.colors.fg
        ax.title.set_color(text_color)

        primary_color = self.root.style.colors.primary

        # Plot data
        ax.plot(angles, values, 'o-', linewidth=2, label='Overall Match', color=primary_color)
        ax.fill(angles, values, color=primary_color, alpha=0.25)
        
        ax.tick_params(colors=text_color) # Ticks
        ax.set_yticklabels([f"{i}%" for i in range(0, 101, 20)], color=text_color)

        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, color=text_color)
        
        ax.set_ylim(0, 100)

        # Add title
        ax.set_title('Resume Match Radar Chart', size=16, fontweight='bold', pad=20)

        # Add grid
        ax.grid(color=text_color, linestyle='--', linewidth=0.5, alpha=0.3)
        
        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def run(self):
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    # Check if all modules are available before starting
    if fitz is None or Document is None:
        print("\nApplication cannot start due to missing dependencies (PyMuPDF or python-docx).")
        print("Please install them and try give again.")
    elif Image is None or ImageTk is None:
        print("\nApplication cannot start due to missing dependency (Pillow).")
        print("Please install it and try again: pip install pillow")
    elif squarify is None:
        print("\nApplication cannot start due to missing dependency (squarify).")
        print("Please install it and try again: pip install squarify")
    else:
        app = ResumeAnalyzer()
        app.run()





