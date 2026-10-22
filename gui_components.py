# ==============================================================================
# File: .//Description-of-file/gui_components.md
# Overview: Tkinter/TTK Desktop Graphical User Interface implementation containing layout, presets, sliders, and queue management.
# ==============================================================================

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional

from config import (
    APP_TITLE,
    APP_WINDOW_SIZE,
    APP_MIN_SIZE,
    PRESETS,
    SUPPORTED_EXTENSIONS,
    DEFAULT_SILENCE_THRESHOLD_DB,
    DEFAULT_MIN_SILENCE_DURATION,
    DEFAULT_MARGIN_PADDING,
    DEFAULT_TARGET_PAUSE,
    DEFAULT_CUT_MODE,
    DEFAULT_OUTPUT_SUFFIX,
    DEFAULT_VIDEO_PRESET,
    DEFAULT_VIDEO_CRF,
    DEFAULT_EXPORT_AUDIO_ONLY,
    SUPPORTED_AUDIO_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    SOUND_POWER_MIN_DB,
    SOUND_POWER_MAX_DB,
    ZONE_DURATION_MIN_S,
    ZONE_DURATION_MAX_S,
)
from domain_models import ProcessingSettings, AudioScanResult, ProcessSummary
from scan_audio import scan_audio
from batch_processor import process_batch


class DeadAirCutterGUI:
    """Main Desktop GUI application window for the Dead Air Audio Cutter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(APP_WINDOW_SIZE)
        self.root.minsize(*APP_MIN_SIZE)

        # State tracking
        self.file_queue: List[str] = []
        self.cached_scans: Dict[str, AudioScanResult] = {}
        self.is_processing: bool = False
        self.cancel_requested: bool = False

        self._configure_styles()
        self._build_layout()
        self._load_preset("Podcast / Voiceover")

    def _configure_styles(self) -> None:
        """Configures ttk widget styles for a clean, modern aesthetic."""
        style = ttk.Style()
        style.theme_use("clam")

        # General styling enhancements
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Subheader.TLabel", font=("Segoe UI", 9, "italic"), foreground="#555")
        style.configure("Status.TLabel", font=("Segoe UI", 9))
        style.configure("Highlight.TLabel", font=("Segoe UI", 10, "bold"), foreground="#0066cc")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        """Constructs two-column and bottom paned layout."""
        # Top banner
        header_frame = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Dead Air & Silence Cutter", font=("Segoe UI", 15, "bold")).pack(anchor=tk.W)
        ttk.Label(
            header_frame,
            text="Automatically eliminate awkward pauses or shorten dead air to natural room-tone pauses.",
            style="Subheader.TLabel",
        ).pack(anchor=tk.W)

        # Main splitter / container
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel: Settings, Presets, and Controls
        left_frame = ttk.Frame(main_paned, padding=8)
        main_paned.add(left_frame, weight=1)

        # Right panel: Queue, Scan Preview, and Output options
        right_frame = ttk.Frame(main_paned, padding=8)
        main_paned.add(right_frame, weight=2)

        self._build_settings_panel(left_frame)
        self._build_queue_panel(right_frame)
        self._build_bottom_panel()

    def _build_settings_panel(self, parent: ttk.Frame) -> None:
        """Creates preset dropdown, threshold sliders, and mode selectors."""
        # Presets Group
        preset_group = ttk.LabelFrame(parent, text="Presets", padding=8)
        preset_group.pack(fill=tk.X, pady=(0, 8))

        self.preset_var = tk.StringVar(value="Podcast / Voiceover")
        preset_names = list(PRESETS.keys()) + ["Custom"]
        self.preset_dropdown = ttk.Combobox(
            preset_group, textvariable=self.preset_var, values=preset_names, state="readonly"
        )
        self.preset_dropdown.pack(fill=tk.X, pady=2)
        self.preset_dropdown.bind("<<ComboboxSelected>>", lambda e: self._on_preset_change())

        self.preset_desc_var = tk.StringVar()
        ttk.Label(preset_group, textvariable=self.preset_desc_var, wraplength=260, style="Subheader.TLabel").pack(
            fill=tk.X, pady=(2, 4)
        )

        # Sliders Group
        param_group = ttk.LabelFrame(parent, text="Detection & Cut Settings", padding=8)
        param_group.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Sound Power Cutoff slider (Cuts zones where sound power <= slider)
        self.threshold_var = tk.DoubleVar(value=DEFAULT_SILENCE_THRESHOLD_DB)
        self._create_slider(
            parent=param_group,
            label="Sound Power Cutoff (dB):",
            subtitle="If sound power <= this slider, cut that zone",
            variable=self.threshold_var,
            from_=SOUND_POWER_MIN_DB,
            to=SOUND_POWER_MAX_DB,
            resolution=0.5,
            format_str="{:.1f} dB",
        )

        # Min silence duration slider
        self.min_duration_var = tk.DoubleVar(value=DEFAULT_MIN_SILENCE_DURATION)
        self._create_slider(
            parent=param_group,
            label="Min Zone Duration (s):",
            subtitle="Minimum duration for a low-power zone to be cut",
            variable=self.min_duration_var,
            from_=ZONE_DURATION_MIN_S,
            to=ZONE_DURATION_MAX_S,
            resolution=0.05,
            format_str="{:.2f} s",
        )

        # Margin padding slider
        self.margin_var = tk.DoubleVar(value=DEFAULT_MARGIN_PADDING)
        self._create_slider(
            parent=param_group,
            label="Speech Buffer / Margin (s):",
            subtitle="Safety buffer kept around spoken words",
            variable=self.margin_var,
            from_=0.0,
            to=0.5,
            resolution=0.02,
            format_str="{:.2f} s",
        )

        # Mode Selection
        mode_group = ttk.LabelFrame(param_group, text="Dead Air Action", padding=6)
        mode_group.pack(fill=tk.X, pady=(8, 4))

        self.mode_var = tk.StringVar(value=DEFAULT_CUT_MODE)
        ttk.Radiobutton(
            mode_group,
            text="Shorten dead air to natural pause",
            value="shorten",
            variable=self.mode_var,
            command=self._on_mode_change,
        ).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            mode_group,
            text="Completely cut and remove dead air",
            value="cut",
            variable=self.mode_var,
            command=self._on_mode_change,
        ).pack(anchor=tk.W, pady=2)

        # Target pause slider (applicable when shortening)
        self.target_pause_var = tk.DoubleVar(value=DEFAULT_TARGET_PAUSE)
        self.pause_slider_container = ttk.Frame(param_group)
        self.pause_slider_container.pack(fill=tk.X, pady=(4, 0))
        self._create_slider(
            parent=self.pause_slider_container,
            label="Target Pause Length (s):",
            subtitle="Duration of retained room tone between speech",
            variable=self.target_pause_var,
            from_=0.05,
            to=0.8,
            resolution=0.05,
            format_str="{:.2f} s",
        )

        # Video Mode Settings Group
        video_group = ttk.LabelFrame(parent, text="🎬 Video Mode Settings", padding=8)
        video_group.pack(fill=tk.X, pady=(4, 0))

        self.video_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            video_group,
            text="Enable Video Mode (Sync video frames with audio cuts)",
            variable=self.video_mode_var,
        ).pack(anchor=tk.W, pady=2)

        self.audio_only_from_video_var = tk.BooleanVar(value=DEFAULT_EXPORT_AUDIO_ONLY)
        ttk.Checkbutton(
            video_group,
            text="Extract Audio Only (.mp3) from video inputs",
            variable=self.audio_only_from_video_var,
        ).pack(anchor=tk.W, pady=2)

        quality_frame = ttk.Frame(video_group)
        quality_frame.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(quality_frame, text="Video Quality / Speed:").pack(side=tk.LEFT)
        self.video_quality_var = tk.StringVar(value="Fast (CRF 22)")
        self.video_quality_dropdown = ttk.Combobox(
            quality_frame,
            textvariable=self.video_quality_var,
            values=["High Quality (CRF 18)", "Fast (CRF 22)", "Compact (CRF 26)", "Draft (Ultrafast)"],
            state="readonly",
            width=18,
        )
        self.video_quality_dropdown.pack(side=tk.RIGHT)

    def _create_slider(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.DoubleVar,
        from_: float,
        to: float,
        resolution: float,
        format_str: str,
        subtitle: str = "",
    ) -> None:
        """Helper to create a labelled slider with linked dynamic value text and explanatory subtitle."""
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=3)

        val_label = ttk.Label(container, text="", width=9, anchor=tk.E, font=("Segoe UI", 9, "bold"))

        def update_val_display(*_):
            val_label.config(text=format_str.format(variable.get()))

        variable.trace_add("write", update_val_display)

        header = ttk.Frame(container)
        header.pack(fill=tk.X)
        ttk.Label(header, text=label, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        val_label.pack(side=tk.RIGHT)

        if subtitle:
            ttk.Label(container, text=subtitle, style="Subheader.TLabel").pack(anchor=tk.W)

        slider = ttk.Scale(
            container,
            from_=from_,
            to=to,
            variable=variable,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_manual_param_change(),
        )
        slider.pack(fill=tk.X, pady=(2, 0))
        update_val_display()

    def _build_queue_panel(self, parent: ttk.Frame) -> None:
        """Builds file queue, file selection buttons, and scan preview box."""
        # Actions bar
        btn_bar = ttk.Frame(parent)
        btn_bar.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(btn_bar, text="+ Add Files", command=self._add_files).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_bar, text="+ Add Folder", command=self._add_folder).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Clear Queue", command=self._clear_queue).pack(side=tk.LEFT, padx=4)

        # File Listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        self.queue_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Segoe UI", 9),
            activestyle="none",
        )
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.queue_listbox.yview)
        self.queue_listbox.configure(yscrollcommand=scrollbar.set)
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue_listbox.bind("<<ListboxSelect>>", lambda e: self._on_file_selected())

        # Scan Preview & Statistics Frame
        preview_frame = ttk.LabelFrame(parent, text="Scan / Preview Statistics", padding=8)
        preview_frame.pack(fill=tk.X, pady=(0, 6))

        stats_grid = ttk.Frame(preview_frame)
        stats_grid.pack(fill=tk.X)

        self.stat_orig_var = tk.StringVar(value="-")
        self.stat_silence_var = tk.StringVar(value="-")
        self.stat_est_var = tk.StringVar(value="-")
        self.stat_saved_var = tk.StringVar(value="-")
        self.stat_mean_power_var = tk.StringVar(value="-")
        self.stat_max_power_var = tk.StringVar(value="-")
        self.stat_media_type_var = tk.StringVar(value="-")
        self.stat_video_mode_var = tk.StringVar(value="-")

        self._add_stat_cell(stats_grid, 0, 0, "Original Duration:", self.stat_orig_var)
        self._add_stat_cell(stats_grid, 0, 1, "Dead Air Detected:", self.stat_silence_var)
        self._add_stat_cell(stats_grid, 1, 0, "Estimated New Duration:", self.stat_est_var)
        self._add_stat_cell(stats_grid, 1, 1, "Time Saved:", self.stat_saved_var, highlight=True)
        self._add_stat_cell(stats_grid, 2, 0, "Mean Sound Power:", self.stat_mean_power_var)
        self._add_stat_cell(stats_grid, 2, 1, "Peak Sound Power:", self.stat_max_power_var)
        self._add_stat_cell(stats_grid, 3, 0, "Media Type:", self.stat_media_type_var)
        self._add_stat_cell(stats_grid, 3, 1, "Sync Mode:", self.stat_video_mode_var)

        preview_btn_bar = ttk.Frame(preview_frame)
        preview_btn_bar.pack(fill=tk.X, pady=(6, 0))
        self.scan_btn = ttk.Button(
            preview_btn_bar, text="🔍 Scan Selected File", command=self._scan_selected_file
        )
        self.scan_btn.pack(side=tk.LEFT)

        # Destination Output Settings
        dest_frame = ttk.LabelFrame(parent, text="Output Destination", padding=8)
        dest_frame.pack(fill=tk.X)

        row1 = ttk.Frame(dest_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Save To:").pack(side=tk.LEFT, padx=(0, 4))
        self.out_dir_var = tk.StringVar(value="")
        ttk.Entry(row1, textvariable=self.out_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(row1, text="Browse...", command=self._browse_output_dir).pack(side=tk.RIGHT)

        row2 = ttk.Frame(dest_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Filename Suffix:").pack(side=tk.LEFT, padx=(0, 4))
        self.suffix_var = tk.StringVar(value=DEFAULT_OUTPUT_SUFFIX)
        ttk.Entry(row2, textvariable=self.suffix_var, width=12).pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="(Leave folder blank to create 'processed' subfolder in source directory)", style="Subheader.TLabel").pack(side=tk.LEFT, padx=6)

    def _add_stat_cell(
        self, parent: ttk.Frame, row: int, col: int, label: str, variable: tk.StringVar, highlight: bool = False
    ) -> None:
        """Helper to create a compact stat metric display cell."""
        f = ttk.Frame(parent)
        f.grid(row=row, column=col, sticky="w", padx=6, pady=2)
        ttk.Label(f, text=label, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        style_name = "Highlight.TLabel" if highlight else "Status.TLabel"
        ttk.Label(f, textvariable=variable, style=style_name).pack(side=tk.LEFT, padx=4)

    def _build_bottom_panel(self) -> None:
        """Builds action buttons, dual progress bars, and execution log."""
        bottom_frame = ttk.Frame(self.root, padding=(10, 4, 10, 10))
        bottom_frame.pack(fill=tk.X)

        # Progress bar
        self.progress_bar = ttk.Progressbar(bottom_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 6))

        # Bottom button bar
        bar = ttk.Frame(bottom_frame)
        bar.pack(fill=tk.X)

        self.status_msg_var = tk.StringVar(value="Ready. Add audio files to begin.")
        ttk.Label(bar, textvariable=self.status_msg_var, style="Status.TLabel").pack(side=tk.LEFT)

        self.cancel_btn = ttk.Button(bar, text="Cancel", command=self._request_cancel, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.start_btn = ttk.Button(
            bar, text="🚀 Cut Dead Air (Process Queue)", style="Accent.TButton", command=self._start_processing
        )
        self.start_btn.pack(side=tk.RIGHT, padx=4)

    # --------------------------------------------------------------------------
    # Event Handlers & User Interactions
    # --------------------------------------------------------------------------

    def _load_preset(self, name: str) -> None:
        """Applies values from a selected preset profile."""
        if name in PRESETS:
            cfg = PRESETS[name]
            self.preset_var.set(name)
            self.preset_desc_var.set(cfg["description"])
            self.threshold_var.set(cfg["silence_threshold_db"])
            self.min_duration_var.set(cfg["min_silence_duration"])
            self.margin_var.set(cfg["margin_padding"])
            self.target_pause_var.set(cfg["target_pause"])
            self.mode_var.set(cfg["mode"])
            self._on_mode_change()

    def _on_preset_change(self) -> None:
        """Triggered when preset dropdown changes."""
        preset = self.preset_var.get()
        if preset in PRESETS:
            self._load_preset(preset)

    def _on_manual_param_change(self) -> None:
        """Sets preset dropdown to 'Custom' when sliders are manipulated."""
        if self.preset_var.get() != "Custom":
            self.preset_var.set("Custom")
            self.preset_desc_var.set("Customized user parameters.")

    def _on_mode_change(self) -> None:
        """Toggles visibility of the target pause slider based on mode."""
        if self.mode_var.get() == "shorten":
            self.pause_slider_container.pack(fill=tk.X, pady=(4, 0))
        else:
            self.pause_slider_container.pack_forget()

    def _format_queue_item(self, file_path: str) -> str:
        """Helper to prefix filename with [VIDEO] or [AUDIO] badge."""
        ext = os.path.splitext(file_path)[1].lower()
        badge = "[VIDEO] " if ext in SUPPORTED_VIDEO_EXTENSIONS else "[AUDIO] "
        return f"{badge}{os.path.basename(file_path)}"

    def _add_files(self) -> None:
        """Opens file dialog to select multiple video or audio files."""
        all_exts = " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)
        video_exts = " ".join(f"*{ext}" for ext in SUPPORTED_VIDEO_EXTENSIONS)
        audio_exts = " ".join(f"*{ext}" for ext in SUPPORTED_AUDIO_EXTENSIONS)
        file_types = [
            ("All Supported Media (Video & Audio)", all_exts),
            ("Video Files", video_exts),
            ("Audio Files", audio_exts),
            ("All Files", "*.*"),
        ]
        chosen = filedialog.askopenfilenames(
            title="Select Video or Audio Files",
            filetypes=file_types,
        )
        for f in chosen:
            if f not in self.file_queue:
                self.file_queue.append(f)
                self.queue_listbox.insert(tk.END, self._format_queue_item(f))
        self._update_queue_status()

    def _add_folder(self) -> None:
        """Opens directory picker and collects all supported video and audio files."""
        chosen_dir = filedialog.askdirectory(title="Select Folder Containing Media Files")
        if not chosen_dir:
            return
        added_count = 0
        for root_path, _, filenames in os.walk(chosen_dir):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(root_path, fname)
                    if full_path not in self.file_queue:
                        self.file_queue.append(full_path)
                        self.queue_listbox.insert(tk.END, self._format_queue_item(full_path))
                        added_count += 1
        self._update_queue_status()
        if added_count > 0:
            self.status_msg_var.set(f"Added {added_count} media file(s) from folder.")

    def _remove_selected(self) -> None:
        """Removes selected files from listbox and internal queue."""
        selected_indices = list(self.queue_listbox.curselection())
        selected_indices.sort(reverse=True)
        for idx in selected_indices:
            path = self.file_queue.pop(idx)
            self.cached_scans.pop(path, None)
            self.queue_listbox.delete(idx)
        self._update_queue_status()

    def _clear_queue(self) -> None:
        """Empties the file queue."""
        self.file_queue.clear()
        self.cached_scans.clear()
        self.queue_listbox.delete(0, tk.END)
        self._reset_stats_display()
        self._update_queue_status()

    def _browse_output_dir(self) -> None:
        """Selects target export directory."""
        chosen = filedialog.askdirectory(title="Select Destination Output Directory")
        if chosen:
            self.out_dir_var.set(chosen)

    def _update_queue_status(self) -> None:
        """Updates status banner with current queue count."""
        count = len(self.file_queue)
        if count == 0:
            self.status_msg_var.set("Queue is empty. Click '+ Add Files' or '+ Add Folder'.")
        else:
            self.status_msg_var.set(f"{count} file(s) in queue ready for processing.")

    def _reset_stats_display(self) -> None:
        """Resets the statistics labels."""
        self.stat_orig_var.set("-")
        self.stat_silence_var.set("-")
        self.stat_est_var.set("-")
        self.stat_saved_var.set("-")
        self.stat_mean_power_var.set("-")
        self.stat_max_power_var.set("-")
        self.stat_media_type_var.set("-")
        self.stat_video_mode_var.set("-")

    def _format_time(self, seconds: float) -> str:
        """Formats seconds into mm:ss or hh:mm:ss string."""
        mins, secs = divmod(int(round(seconds)), 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def _on_file_selected(self) -> None:
        """Displays cached scan statistics when user clicks a file in the queue."""
        selection = self.queue_listbox.curselection()
        if not selection:
            return
        file_path = self.file_queue[selection[0]]
        scan = self.cached_scans.get(file_path)
        if scan:
            self._display_scan_stats(scan)
        else:
            self._reset_stats_display()

    def _display_scan_stats(self, scan: AudioScanResult) -> None:
        """Populates the scan preview panel with calculated numbers."""
        orig_str = self._format_time(scan.total_duration)
        silence_count = len(scan.silence_intervals)
        silence_str = f"{self._format_time(scan.total_silence_duration)} ({silence_count} pauses)"
        est_str = self._format_time(scan.estimated_output_duration)
        saved_str = f"{self._format_time(scan.time_saved)} (-{scan.percentage_saved:.1f}%)"

        self.stat_orig_var.set(orig_str)
        self.stat_silence_var.set(silence_str)
        self.stat_est_var.set(est_str)
        self.stat_saved_var.set(saved_str)

        mean_str = f"{scan.mean_power_db:.1f} dB" if scan.mean_power_db is not None else "N/A"
        max_str = f"{scan.max_power_db:.1f} dB" if scan.max_power_db is not None else "N/A"
        self.stat_mean_power_var.set(mean_str)
        self.stat_max_power_var.set(max_str)

        if scan.is_video:
            self.stat_media_type_var.set("[VIDEO] Video Media")
            if self.audio_only_from_video_var.get():
                self.stat_video_mode_var.set("Extract Audio (.mp3)")
            else:
                self.stat_video_mode_var.set("Sync Video + Audio")
        else:
            self.stat_media_type_var.set("[AUDIO] Pure Sound")
            self.stat_video_mode_var.set("Audio Processing")

    def _get_current_settings(self) -> ProcessingSettings:
        """Gathers values from UI controls into a ProcessingSettings object."""
        out_dir = self.out_dir_var.get().strip() or None
        suffix = self.suffix_var.get()

        quality_map = {
            "High Quality (CRF 18)": ("medium", 18),
            "Fast (CRF 22)": ("fast", 22),
            "Compact (CRF 26)": ("fast", 26),
            "Draft (Ultrafast)": ("ultrafast", 24),
        }
        preset, crf = quality_map.get(self.video_quality_var.get(), ("fast", 22))

        return ProcessingSettings(
            threshold_db=self.threshold_var.get(),
            min_silence_duration=self.min_duration_var.get(),
            margin_padding=self.margin_var.get(),
            target_pause=self.target_pause_var.get(),
            mode=self.mode_var.get(),
            output_dir=out_dir,
            output_suffix=suffix,
            is_video_mode=self.video_mode_var.get(),
            export_audio_only=self.audio_only_from_video_var.get(),
            video_preset=preset,
            video_crf=crf,
        )

    # --------------------------------------------------------------------------
    # Background Processing: Pre-flight Scan & Execution
    # --------------------------------------------------------------------------

    def _scan_selected_file(self) -> None:
        """Initiates a background scan on the selected file."""
        selection = self.queue_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select a File", "Please select a file from the queue to scan.")
            return

        target_file = self.file_queue[selection[0]]
        settings = self._get_current_settings()

        self.scan_btn.configure(state=tk.DISABLED)
        self.status_msg_var.set(f"Scanning '{os.path.basename(target_file)}' for dead air...")

        def run_scan():
            try:
                result = scan_audio(target_file, settings)
                self.cached_scans[target_file] = result

                def update_ui():
                    self._display_scan_stats(result)
                    self.status_msg_var.set(
                        f"Scan complete: {result.time_saved:.1f}s dead air cut ({result.percentage_saved:.1f}% saved)."
                    )
                    self.scan_btn.configure(state=tk.NORMAL)

                self.root.after(0, update_ui)
            except Exception as err:
                def show_err():
                    self.status_msg_var.set(f"Scan failed: {err}")
                    messagebox.showerror("Scan Error", str(err))
                    self.scan_btn.configure(state=tk.NORMAL)

                self.root.after(0, show_err)

        threading.Thread(target=run_scan, daemon=True).start()

    def _start_processing(self) -> None:
        """Begins processing the entire queue on a background worker thread."""
        if not self.file_queue:
            messagebox.showinfo("Queue Empty", "Please add at least one audio file to process.")
            return

        if self.is_processing:
            return

        self.is_processing = True
        self.cancel_requested = False
        self.start_btn.configure(state=tk.DISABLED)
        self.scan_btn.configure(state=tk.DISABLED)
        self.cancel_btn.configure(state=tk.NORMAL)
        self.progress_bar.configure(value=0)

        settings = self._get_current_settings()
        files = list(self.file_queue)

        def worker():
            total = len(files)

            def on_start(idx: int, tot: int, path: str):
                msg = f"[{idx}/{tot}] Processing '{os.path.basename(path)}'..."
                self.root.after(0, lambda: self.status_msg_var.set(msg))

            def on_progress(idx: int, tot: int, fraction: float, msg: str):
                overall_fraction = ((idx - 1) + fraction) / tot
                pct = int(overall_fraction * 100)
                display_text = f"[{idx}/{tot}] {msg}"
                self.root.after(
                    0,
                    lambda: (
                        self.progress_bar.configure(value=pct),
                        self.status_msg_var.set(display_text),
                    ),
                )

            def on_complete(idx: int, tot: int, summary: ProcessSummary):
                pass

            def check_cancel() -> bool:
                return self.cancel_requested

            summaries = process_batch(
                files=files,
                settings=settings,
                on_file_start=on_start,
                on_file_progress=on_progress,
                on_file_complete=on_complete,
                is_cancelled=check_cancel,
            )

            def finish():
                self.is_processing = False
                self.start_btn.configure(state=tk.NORMAL)
                self.scan_btn.configure(state=tk.NORMAL)
                self.cancel_btn.configure(state=tk.DISABLED)
                self.progress_bar.configure(value=100)

                successes = sum(1 for s in summaries if s.success)
                total_saved = sum(s.time_saved for s in summaries if s.success)
                saved_str = self._format_time(total_saved)

                if self.cancel_requested:
                    self.status_msg_var.set(f"Cancelled by user. Processed {successes}/{total} files.")
                    messagebox.showwarning("Cancelled", f"Batch processing was cancelled.\n{successes}/{total} completed.")
                else:
                    self.status_msg_var.set(f"Completed! {successes}/{total} files processed. Total time saved: {saved_str}")
                    messagebox.showinfo(
                        "Processing Complete",
                        f"Successfully cut dead air in {successes} of {total} files!\nTotal duration saved: {saved_str}.",
                    )

            self.root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _request_cancel(self) -> None:
        """Sets cancellation flag when user clicks Cancel button."""
        self.cancel_requested = True
        self.status_msg_var.set("Cancelling batch processing after current operation...")
        self.cancel_btn.configure(state=tk.DISABLED)
