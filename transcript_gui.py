import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
from transcript_grid import TranscriptSummarizer

# Import configuration
try:
    from config import get_output_path, OUTPUT_FILES

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("Warning: config.py not found, using default output directory")


class TranscriptAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimized Transcript Summarizer")
        self.root.geometry("900x700")

        # Variables
        self.directory_path = tk.StringVar()
        self.api_key = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        self.max_workers_var = tk.IntVar(value=3)

        # Load API key from environment if available
        if os.getenv("OPENAI_API_KEY"):
            self.api_key.set(os.getenv("OPENAI_API_KEY"))

        # Set default directory to "FlexXray Transcripts"
        default_directory = "FlexXray Transcripts"
        if os.path.exists(default_directory):
            self.directory_path.set(default_directory)

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Optimized Transcript Summarizer",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # API Key Section
        ttk.Label(main_frame, text="OpenAI API Key:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        api_entry = ttk.Entry(main_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        # Directory Selection
        ttk.Label(main_frame, text="Transcript Directory:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        dir_entry = ttk.Entry(main_frame, textvariable=self.directory_path, width=50)
        dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        browse_btn = ttk.Button(
            main_frame, text="Browse", command=self.browse_directory
        )
        browse_btn.grid(row=2, column=2, pady=5, padx=(5, 0))

        # Performance Settings
        performance_frame = ttk.LabelFrame(
            main_frame, text="Performance Settings", padding="10"
        )
        performance_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        performance_frame.columnconfigure(1, weight=1)

        ttk.Label(performance_frame, text="Max Concurrent API Calls:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        workers_spinbox = ttk.Spinbox(
            performance_frame,
            from_=1,
            to=5,
            textvariable=self.max_workers_var,
            width=10,
        )
        workers_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        ttk.Label(
            performance_frame, text="(Higher = faster but may hit rate limits)"
        ).grid(row=0, column=2, sticky=tk.W, pady=5, padx=(5, 0))

        # Analysis Options
        options_frame = ttk.LabelFrame(
            main_frame, text="Analysis Options", padding="10"
        )
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(0, weight=1)

        # Checkboxes for each analysis section
        self.section_vars = {}
        row = 0
        # Get questions from the TranscriptSummarizer class
        from transcript_grid import TranscriptSummarizer

        temp_analyzer = TranscriptSummarizer("temp")
        for section_key, section_data in temp_analyzer.questions.items():
            var = tk.BooleanVar(value=True)
            self.section_vars[section_key] = var
            cb = ttk.Checkbutton(
                options_frame, text=section_data["title"], variable=var
            )
            cb.grid(row=row, column=0, sticky=tk.W, pady=2)
            row += 1

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        # Time tracking
        self.time_label = ttk.Label(progress_frame, text="")
        self.time_label.grid(row=2, column=0, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)

        self.analyze_btn = ttk.Button(
            button_frame, text="Start Optimized Analysis", command=self.start_analysis
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.view_results_btn = ttk.Button(
            button_frame,
            text="View Results",
            command=self.view_results,
            state=tk.DISABLED,
        )
        self.view_results_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(
            button_frame,
            text="Stop Analysis",
            command=self.stop_analysis,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(
            row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10
        )
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=90)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Analysis control
        self.analysis_running = False
        self.start_time = None

    def browse_directory(self):
        directory = filedialog.askdirectory(
            initialdir=(
                "FlexXray Transcripts"
                if os.path.exists("FlexXray Transcripts")
                else "."
            )
        )
        if directory:
            self.directory_path.set(directory)
            # Update status to show selected directory
            self.status_var.set(f"Selected: {os.path.basename(directory)}")

    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, message, progress):
        self.root.after(0, lambda: self.status_var.set(message))
        self.root.after(0, lambda: self.progress_var.set(progress))

        # Update time elapsed
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.root.after(
                0,
                lambda: self.time_label.config(
                    text=f"Time elapsed: {elapsed:.1f} seconds"
                ),
            )

    def start_analysis(self):
        # Validate inputs
        if not self.api_key.get().strip():
            messagebox.showerror("Error", "Please enter your OpenAI API key.")
            return

        if not self.directory_path.get().strip():
            messagebox.showerror(
                "Error",
                "Please select a directory containing Word document transcripts.",
            )
            return

        if not os.path.exists(self.directory_path.get()):
            messagebox.showerror("Error", "Selected directory does not exist.")
            return

        # Check if any sections are selected
        selected_sections = [key for key, var in self.section_vars.items() if var.get()]
        if not selected_sections:
            messagebox.showerror(
                "Error", "Please select at least one analysis section."
            )
            return

        # Disable UI during analysis
        self.analyze_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Starting optimized analysis...")
        self.time_label.config(text="")
        self.log_text.delete(1.0, tk.END)
        self.analysis_running = True
        self.start_time = time.time()

        # Start analysis in separate thread
        thread = threading.Thread(
            target=self.run_optimized_analysis, args=(selected_sections,)
        )
        thread.daemon = True
        thread.start()

    def stop_analysis(self):
        self.analysis_running = False
        self.log_message("Stopping analysis... (this may take a moment)")
        self.stop_btn.config(state=tk.DISABLED)

    def run_optimized_analysis(self, selected_sections):
        try:
            self.log_message("Initializing optimized transcript analyzer...")

            # Initialize analyzer with performance settings
            analyzer = TranscriptSummarizer(
                self.api_key.get().strip(), max_workers=self.max_workers_var.get()
            )

            # Update questions to only include selected sections
            temp_analyzer = TranscriptSummarizer("temp")
            analyzer.questions = {
                key: temp_analyzer.questions[key] for key in selected_sections
            }

            self.log_message(f"Processing transcripts in: {self.directory_path.get()}")
            self.log_message(
                f"Using {self.max_workers_var.get()} concurrent API calls for optimal performance"
            )

            # Process transcripts with progress tracking
            results = analyzer.process_transcripts_directory(
                self.directory_path.get(), self.update_progress
            )

            if not self.analysis_running:
                self.log_message("Analysis stopped by user")
                return

            if results:
                self.log_message("Saving results...")
                analyzer.save_results(results)
                analyzer.generate_summary_report(results)

                self.log_message("Creating optimized Word document...")
                analyzer.export_to_word(results)

                end_time = time.time()
                total_time = end_time - self.start_time

                self.log_message(
                    f"Optimized analysis complete! Processed {len(results)} transcripts in {total_time:.2f} seconds."
                )
                self.log_message("Files created:")
                if CONFIG_AVAILABLE:
                    self.log_message(
                        f"- {OUTPUT_FILES['transcript_analysis_json']} (structured data)"
                    )
                    self.log_message(
                        f"- {OUTPUT_FILES['transcript_analysis_txt']} (human-readable report)"
                    )
                    self.log_message(
                        f"- {OUTPUT_FILES['transcript_analysis_docx']} (optimized Word document)"
                    )
                    self.log_message(
                        f"All files have been saved to: {get_output_path('')}"
                    )
                else:
                    self.log_message(
                        "- FlexXray_transcript_analysis_results.json (structured data)"
                    )
                    self.log_message(
                        "- FlexXray_transcript_analysis_results.txt (human-readable report)"
                    )
                    self.log_message(
                        "- FlexXray_transcript_analysis_results.docx (optimized Word document)"
                    )
                    self.log_message(
                        "All files have been saved to the current directory."
                    )

                # Enable view results button
                self.root.after(
                    0, lambda: self.view_results_btn.config(state=tk.NORMAL)
                )
                self.root.after(
                    0,
                    lambda: self.status_var.set(
                        f"Analysis complete! ({total_time:.2f}s)"
                    ),
                )
                self.root.after(0, lambda: self.progress_var.set(100))
            else:
                self.log_message("No transcripts were successfully processed.")
                self.root.after(
                    0, lambda: self.status_var.set("No transcripts processed")
                )

        except Exception as e:
            error_msg = f"An error occurred: {e}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
        finally:
            self.analysis_running = False
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))

    def view_results(self):
        # Open the results file in default application
        if CONFIG_AVAILABLE:
            word_file = get_output_path(OUTPUT_FILES["transcript_analysis_docx"])
            report_file = get_output_path(OUTPUT_FILES["transcript_analysis_txt"])
        else:
            word_file = "FlexXray_transcript_analysis_results.docx"
            report_file = "FlexXray_transcript_analysis_results.txt"

        if os.path.exists(word_file):
            os.startfile(word_file)  # Windows - opens Word document
        elif os.path.exists(report_file):
            os.startfile(report_file)  # Windows - opens text file
        else:
            messagebox.showinfo(
                "Info", "No results file found. Please run the analysis first."
            )


def main():
    root = tk.Tk()
    app = TranscriptAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
