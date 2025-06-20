import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, List, Optional, Any


class MilitaryUIManager:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # Gruvbox Dark military color scheme
        self.colors = {
            "bg_primary": "#1d2021",  # Gruvbox dark background
            "bg_secondary": "#282828",  # Gruvbox dark0
            "bg_tertiary": "#3c3836",  # Gruvbox dark1
            "bg_quaternary": "#504945",  # Gruvbox dark2
            "accent": "#d79921",  # Gruvbox yellow/orange
            "accent_secondary": "#b57614",  # Gruvbox yellow dark
            "success": "#98971a",  # Gruvbox green
            "success_bright": "#b8bb26",  # Gruvbox bright green
            "warning": "#d65d0e",  # Gruvbox orange
            "danger": "#cc241d",  # Gruvbox red
            "text_primary": "#ebdbb2",  # Gruvbox light
            "text_secondary": "#d5c4a1",  # Gruvbox light1
            "text_accent": "#fabd2f",  # Gruvbox bright yellow
            "text_success": "#b8bb26",  # Gruvbox bright green
            "text_warning": "#fe8019",  # Gruvbox bright orange
            "text_danger": "#fb4934",  # Gruvbox bright red
            "border": "#665c54",  # Gruvbox dark3
            "button_active": "#d79921",  # Gruvbox yellow
            "button_hover": "#b57614",  # Gruvbox yellow dark
        }

        # Battalion info with Gruvbox colors
        self.battalion_info = {
            "CONDOR": {"icon": "🦅", "name": "CONDOR SQUADRON", "color": "#d79921"},  # Gruvbox yellow
            "YAGUARETE": {"icon": "🐆", "name": "YAGUARETE DIVISION", "color": "#d65d0e"},  # Gruvbox orange
            "CARPINCHO": {"icon": "🦫", "name": "CARPINCHO REGIMENT", "color": "#98971a"},  # Gruvbox green
        }

        # UI components
        self.notebook = None
        self.battalion_tree = None
        self.summary_tree = None
        self.players_tree = None
        self.status_label = None
        self.progress_bar = None
        self.refresh_btn = None

        # Current data
        self.current_data = {}

    def setup_ui(self):
        """Setup the military-themed UI"""
        self.setup_military_styles()

        # Main container
        main_container = tk.Frame(self.root, bg=self.colors["bg_primary"], relief="raised", bd=3)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Header
        self.create_classified_header(main_container)

        # Control panel
        self.create_military_control_panel(main_container)

        # Main content
        content_frame = tk.Frame(main_container, bg=self.colors["bg_secondary"], relief="sunken", bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_battalion_command_tab()
        self.create_intelligence_summary_tab()
        self.create_personnel_management_tab()
        self.create_operations_center_tab()

        # Status bar
        self.create_military_status_bar(main_container)

    def setup_military_styles(self):
        """Configure Gruvbox Dark military-themed ttk styles"""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure notebook tabs
        style.configure(
            "TNotebook.Tab",
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_secondary"],
            padding=[15, 8],
            font=("JetBrains Mono", 10, "bold"),
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", self.colors["bg_primary"])],
        )

        # Configure treeview
        style.configure(
            "Military.Treeview",
            background=self.colors["bg_secondary"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_secondary"],
            font=("JetBrains Mono", 12),
            rowheight=25,
        )

        style.configure(
            "Military.Treeview.Heading",
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_accent"],
            font=("JetBrains Mono", 10, "bold"),
        )

        style.map(
            "Military.Treeview",
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", self.colors["bg_primary"])],
        )

        # Configure combobox
        style.configure(
            "Military.TCombobox",
            fieldbackground=self.colors["bg_secondary"],
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_primary"],
            font=("JetBrains Mono", 10),
        )

        # Configure spinbox
        style.configure(
            "Military.TSpinbox",
            fieldbackground=self.colors["bg_secondary"],
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_primary"],
            font=("JetBrains Mono", 10),
        )

    def create_classified_header(self, parent):
        """Create classified military header with Gruvbox styling"""
        header_frame = tk.Frame(parent, bg=self.colors["bg_secondary"], relief="raised", bd=3, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Classification banner
        class_banner = tk.Frame(header_frame, bg=self.colors["danger"], height=20)
        class_banner.pack(fill=tk.X)
        class_banner.pack_propagate(False)

        tk.Label(
            class_banner,
            text="🔒 CLASSIFIED - MILITARY OPERATIONS 🔒",
            bg=self.colors["danger"],
            fg=self.colors["text_primary"],
            font=("JetBrains Mono", 10, "bold"),
        ).pack()

        # Main title
        title_label = tk.Label(
            header_frame,
            text="⚔️ WARERA TACTICAL COMMAND SYSTEM ⚔️",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_accent"],
            font=("JetBrains Mono", 12, "bold"),
            pady=6,
        )
        title_label.pack()

        # Current operation info
        current_week = self.app.get_current_week()
        op_label = tk.Label(
            header_frame,
            text=f"OPERATION: {current_week.upper()} | STATUS: ACTIVE",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("JetBrains Mono", 10),
        )
        op_label.pack()

    def create_military_control_panel(self, parent):
        """Create Gruvbox-styled military control panel"""
        control_frame = tk.Frame(parent, bg=self.colors["bg_tertiary"], relief="raised", bd=3)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Control header
        control_header = tk.Frame(control_frame, bg=self.colors["bg_quaternary"], height=30)
        control_header.pack(fill=tk.X)
        control_header.pack_propagate(False)

        tk.Label(
            control_header,
            text="🎯 TACTICAL CONTROL PANEL",
            bg=self.colors["bg_quaternary"],
            fg=self.colors["text_accent"],
            font=("JetBrains Mono", 11, "bold"),
            pady=5,
        ).pack()

        # Controls container
        controls_container = tk.Frame(control_frame, bg=self.colors["bg_tertiary"])
        controls_container.pack(fill=tk.X, padx=15, pady=15)

        # Left side controls
        left_controls = tk.Frame(controls_container, bg=self.colors["bg_tertiary"])
        left_controls.pack(side=tk.LEFT)

        # Country selection
        tk.Label(
            left_controls,
            text="🌍 COUNTRY:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_success"],
            font=("JetBrains Mono", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 5))

        country_combo = ttk.Combobox(
            left_controls,
            textvariable=self.app.current_country,
            values=self.app.available_countries,
            state="readonly",
            width=15,
            style="Military.TCombobox",
        )
        country_combo.pack(side=tk.LEFT, padx=(0, 20))
        country_combo.bind('<<ComboboxSelected>>', self.app.on_country_changed)

        # Max players
        tk.Label(
            left_controls,
            text="👥 MAX SOLDIERS:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_success"],
            font=("JetBrains Mono", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 5))

        players_spin = ttk.Spinbox(
            left_controls, from_=1, to=30, width=5, textvariable=self.app.max_players_shown, style="Military.TSpinbox"
        )
        players_spin.pack(side=tk.LEFT, padx=(0, 20))
        players_spin.bind('<Return>', lambda e: self.refresh_displays())

        # Right side controls
        right_controls = tk.Frame(controls_container, bg=self.colors["bg_tertiary"])
        right_controls.pack(side=tk.RIGHT)

        # Refresh button
        self.refresh_btn = tk.Button(
            right_controls,
            text="📡 INTEL UPDATE",
            command=self.app.refresh_data,
            bg=self.colors["accent"],
            fg=self.colors["bg_primary"],
            font=("JetBrains Mono", 10, "bold"),
            relief="raised",
            bd=3,
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=self.colors["button_hover"],
            activeforeground=self.colors["text_primary"],
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Export button
        export_btn = tk.Button(
            right_controls,
            text="📊 EXPORT INTEL",
            command=self.export_data,
            bg=self.colors["warning"],
            fg=self.colors["text_primary"],
            font=("JetBrains Mono", 10, "bold"),
            relief="raised",
            bd=3,
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=self.colors["accent_secondary"],
        )
        export_btn.pack(side=tk.LEFT)

    def create_battalion_command_tab(self):
        """Create battalion command tab"""
        self.battalion_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])
        self.notebook.add(self.battalion_frame, text="🏴 BATTALION COMMAND")

        # Command briefing header
        briefing_frame = tk.Frame(
            self.battalion_frame, bg=self.colors["bg_secondary"], relief="raised", bd=2, height=60
        )
        briefing_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        briefing_frame.pack_propagate(False)

        tk.Label(
            briefing_frame,
            text="⚔️ BATTALION TACTICAL ASSESSMENT ⚔️",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("Courier New", 12, "bold"),
            pady=20,
        ).pack()

        # Battalion control panel
        command_panel = tk.Frame(self.battalion_frame, bg=self.colors["bg_tertiary"], relief="raised", bd=2)
        command_panel.pack(fill=tk.X, padx=10, pady=5)

        panel_inner = tk.Frame(command_panel, bg=self.colors["bg_tertiary"])
        panel_inner.pack(fill=tk.X, padx=15, pady=15)

        # Battalion selection
        tk.Label(
            panel_inner,
            text="🏴 SELECT UNIT:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 5))

        battalion_combo = ttk.Combobox(
            panel_inner,
            textvariable=self.app.selected_battalion,
            values=["CONDOR", "YAGUARETE", "CARPINCHO"],
            state="readonly",
            style="Military.TCombobox",
        )
        battalion_combo.pack(side=tk.LEFT, padx=(0, 30))
        battalion_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_battalion_display())

        # Medal buttons with Gruvbox colors
        medal_frame = tk.Frame(panel_inner, bg=self.colors["bg_tertiary"])
        medal_frame.pack(side=tk.LEFT)

        tk.Label(
            medal_frame,
            text="🎖️ AWARD DECORATIONS:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_success"],
            font=("JetBrains Mono", 10, "bold"),
            # font=("Segoe UI Emoji", 9, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 10))

        decorations = [
            ("🥇 VALOR", "gold", self.colors["text_accent"], self.colors["bg_primary"]),
            ("🥈 HONOR", "silver", self.colors["border"], self.colors["text_primary"]),
            ("🥉 MERIT", "bronze", self.colors["warning"], self.colors["text_primary"]),
        ]

        for text, medal_type, bg_color, fg_color in decorations:
            btn = tk.Button(
                medal_frame,
                text=text,
                command=lambda mt=medal_type: self.assign_medal(mt),
                bg=bg_color,
                fg=fg_color,
                font=("JetBrains Mono", 9, "bold"),
                relief="raised",
                bd=3,
                padx=8,
                pady=4,
                cursor="hand2",
                activebackground=self.colors["button_hover"],
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Export button
        btn = tk.Button(
            medal_frame,
            text="Export",
            command=self.export_current_data,
            bg=self.colors["accent"],
            fg=self.colors["text_secondary"],
            font=("JetBrains Mono", 9, "bold"),
            relief="raised",
            bd=3,
            padx=8,
            pady=4,
            cursor="hand2",
            activebackground=self.colors["button_hover"],
        )
        btn.pack(side=tk.LEFT, padx=20)

        # Personnel roster
        roster_frame = tk.Frame(self.battalion_frame, bg=self.colors["bg_tertiary"], relief="sunken", bd=2)
        roster_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Roster header
        roster_header = tk.Frame(roster_frame, bg=self.colors["bg_secondary"], height=30)
        roster_header.pack(fill=tk.X)
        roster_header.pack_propagate(False)

        tk.Label(
            roster_header,
            text="📋 SOLDIERS ROSTER & COMBAT EFFECTIVENESS",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("Courier New", 11, "bold"),
            pady=5,
        ).pack()

        # Battalion treeview
        columns = ("OPERATIVE", "LVL", "DAMAGE", "GLOBAL RANK", "DECORATIONS")

        self.battalion_tree = ttk.Treeview(
            roster_frame, columns=columns, show="headings", height=20, style="Military.Treeview"
        )

        column_widths = {
            "CALLSIGN": 150,
            "LVL": 60,
            "DAMAGE OUTPUT": 120,
            "GLOBAL RANK": 100,
            "DECORATIONS": 150,
        }

        for col in columns:
            # aca no se ven bien las medallas
            self.battalion_tree.heading(col, text=col)
            self.battalion_tree.column(col, width=column_widths.get(col, 120), anchor="center")

        # Scrollbar
        battalion_scroll = ttk.Scrollbar(roster_frame, orient=tk.VERTICAL, command=self.battalion_tree.yview)
        self.battalion_tree.configure(yscrollcommand=battalion_scroll.set)

        self.battalion_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        battalion_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def create_intelligence_summary_tab(self):
        """Create intelligence summary tab"""
        self.summary_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])
        self.notebook.add(self.summary_frame, text="📊 INTELLIGENCE")

        # Intelligence header
        intel_header = tk.Frame(self.summary_frame, bg=self.colors["bg_secondary"], relief="raised", bd=2, height=60)
        intel_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        intel_header.pack_propagate(False)

        # Container for label and button side by side
        header_content = tk.Frame(intel_header, bg=self.colors["bg_secondary"])
        header_content.pack(fill=tk.X, padx=10, pady=5)

        # Strategic Intelligence label
        tk.Label(
            header_content,
            text="🔍 STRATEGIC INTELLIGENCE OVERVIEW",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("Courier New", 12, "bold"),
            pady=10,
        ).pack(side=tk.LEFT, anchor="w")

        # Export button
        tk.Button(
            header_content,
            text="Export",
            command=self.export_summary,
            bg=self.colors["accent"],
            fg=self.colors["text_secondary"],
            font=("JetBrains Mono", 9, "bold"),
            relief="raised",
            bd=3,
            padx=8,
            pady=4,
            cursor="hand2",
            activebackground=self.colors["button_hover"],
        ).pack(side=tk.RIGHT, anchor="e", padx=10)

        # Summary table
        summary_table_frame = tk.Frame(self.summary_frame, bg=self.colors["bg_tertiary"], relief="sunken", bd=2)
        summary_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Table header
        table_header = tk.Frame(summary_table_frame, bg=self.colors["bg_secondary"], height=30)
        table_header.pack(fill=tk.X)
        table_header.pack_propagate(False)

        tk.Label(
            table_header,
            text="📈 BATTALION COMBAT EFFECTIVENESS ANALYSIS",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("Courier New", 11, "bold"),
            pady=5,
        ).pack()

        # Summary treeview
        summary_columns = ("UNIT", "BATTALION", "SOLDIERS", "TOTAL DAMAGE", "%", "AVG PER SOLDIER")
        self.summary_tree = ttk.Treeview(
            summary_table_frame, columns=summary_columns, show="headings", height=15, style="Military.Treeview"
        )

        for col in summary_columns:
            self.summary_tree.heading(col, text=col)
            self.summary_tree.column(col, width=150, anchor="center")

        # Summary scrollbar
        summary_scroll = ttk.Scrollbar(summary_table_frame, orient=tk.VERTICAL, command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=summary_scroll.set)

        self.summary_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Intelligence briefing
        briefing_frame = tk.Frame(self.summary_frame, bg=self.colors["bg_secondary"], relief="raised", bd=2)
        briefing_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        self.summary_info = tk.Label(
            briefing_frame,
            text="",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("Courier New", 10),
            pady=10,
        )
        self.summary_info.pack()

    def create_personnel_management_tab(self):
        """Create personnel management tab"""
        self.players_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])
        self.notebook.add(self.players_frame, text="👥 SOLDIERS")

        # Personnel header
        personnel_header = tk.Frame(
            self.players_frame, bg=self.colors["bg_secondary"], relief="raised", bd=2, height=60
        )
        personnel_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        personnel_header.pack_propagate(False)

        tk.Label(
            personnel_header,
            text="👥 SOLDIER MANAGEMENT SYSTEM",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("Courier New", 12, "bold"),
            pady=20,
        ).pack()

        # Personnel control panel
        personnel_control = tk.Frame(self.players_frame, bg=self.colors["bg_tertiary"], relief="raised", bd=2)
        personnel_control.pack(fill=tk.X, padx=10, pady=5)

        control_inner = tk.Frame(personnel_control, bg=self.colors["bg_tertiary"])
        control_inner.pack(fill=tk.X, padx=15, pady=15)

        # Assignment controls
        left_controls = tk.Frame(control_inner, bg=self.colors["bg_tertiary"])
        left_controls.pack(side=tk.LEFT)

        tk.Label(
            left_controls,
            text="🏴 ASSIGN TO UNIT:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.assign_battalion = tk.StringVar(value="CONDOR")
        assign_combo = ttk.Combobox(
            left_controls,
            textvariable=self.assign_battalion,
            values=["CONDOR", "YAGUARETE", "CARPINCHO", "UNASSIGNED"],
            state="readonly",
            style="Military.TCombobox",
        )
        assign_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Assignment button
        assign_btn = tk.Button(
            left_controls,
            text="✅ EXECUTE ASSIGNMENT",
            command=self.assign_selected_players,
            bg=self.colors["accent"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 10, "bold"),
            relief="raised",
            bd=3,
            padx=10,
            pady=5,
            cursor="hand2",
        )
        assign_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Search controls
        right_controls = tk.Frame(control_inner, bg=self.colors["bg_tertiary"])
        right_controls.pack(side=tk.RIGHT)

        tk.Label(
            right_controls,
            text="🔍 SEARCH:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.player_filter = tk.StringVar()
        filter_entry = tk.Entry(
            right_controls,
            textvariable=self.player_filter,
            width=20,
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("Courier New", 10),
            relief="sunken",
            bd=2,
        )
        filter_entry.pack(side=tk.LEFT)
        filter_entry.bind('<KeyRelease>', lambda e: self.refresh_players_display())

        # Personnel database
        database_frame = tk.Frame(self.players_frame, bg=self.colors["bg_tertiary"], relief="sunken", bd=2)
        database_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Database header
        db_header = tk.Frame(database_frame, bg=self.colors["bg_secondary"], height=30)
        db_header.pack(fill=tk.X)
        db_header.pack_propagate(False)

        tk.Label(
            db_header,
            text="🗃️ SOLDIER DATABASE",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("Courier New", 11, "bold"),
            pady=5,
        ).pack()

        # Personnel treeview
        player_columns = ("CALLSIGN", "LEVEL", "DAMAGE OUTPUT", "GLOBAL RANK", "CURRENT UNIT", "DECORATIONS")
        self.players_tree = ttk.Treeview(
            database_frame, columns=player_columns, show="headings", height=25, style="Military.Treeview"
        )

        for col in player_columns:
            self.players_tree.heading(col, text=col)
            self.players_tree.column(col, width=120, anchor="center")

        # Personnel scrollbar
        players_scroll = ttk.Scrollbar(database_frame, orient=tk.VERTICAL, command=self.players_tree.yview)
        self.players_tree.configure(yscrollcommand=players_scroll.set)

        self.players_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        players_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def create_operations_center_tab(self):
        """Create operations center tab"""
        operations_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])
        self.notebook.add(operations_frame, text="⚙️ OPERATIONS")

        # Operations header
        ops_header = tk.Frame(operations_frame, bg=self.colors["bg_secondary"], relief="raised", bd=2, height=60)
        ops_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        ops_header.pack_propagate(False)

        tk.Label(
            ops_header,
            text="⚙️ OPERATIONS CENTER",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("Courier New", 12, "bold"),
            pady=20,
        ).pack()

        # API Configuration
        api_frame = tk.LabelFrame(
            operations_frame,
            text="📡 COMMUNICATION PROTOCOLS",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 11, "bold"),
            relief="raised",
            bd=2,
        )
        api_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            api_frame,
            text="🔐 AUTHORIZATION TOKEN:",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 10, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.token_var = tk.StringVar(value=self.app.get_bearer_token())
        token_entry = tk.Entry(
            api_frame,
            textvariable=self.token_var,
            width=60,
            show="*",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("Courier New", 10),
            relief="sunken",
            bd=2,
        )
        token_entry.pack(fill=tk.X, padx=10, pady=5)

        save_token_btn = tk.Button(
            api_frame,
            text="💾 SAVE CREDENTIALS",
            command=self.save_token,
            bg=self.colors["accent"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 10, "bold"),
            relief="raised",
            bd=3,
            padx=15,
            pady=5,
            cursor="hand2",
        )
        save_token_btn.pack(pady=10)

        # Data Operations
        data_frame = tk.LabelFrame(
            operations_frame,
            text="🗃️ DATA OPERATIONS",
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_secondary"],
            font=("Courier New", 11, "bold"),
            relief="raised",
            bd=2,
        )
        data_frame.pack(fill=tk.X, padx=20, pady=10)

        # Data operation buttons
        data_buttons_frame = tk.Frame(data_frame, bg=self.colors["bg_tertiary"])
        data_buttons_frame.pack(pady=15)

        operations = [("📥 IMPORT DATA", self.import_data, "#8B4513"), ("🗑️ CLEAR CACHE", self.clear_cache, "#8B0000")]

        for text, command, color in operations:
            btn = tk.Button(
                data_buttons_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Courier New", 10, "bold"),
                relief="raised",
                bd=3,
                padx=15,
                pady=8,
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=10)

    def create_military_status_bar(self, parent):
        """Create Gruvbox-styled military status bar"""
        status_frame = tk.Frame(parent, bg=self.colors["bg_quaternary"], relief="sunken", bd=2, height=35)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        # Status indicator
        self.status_label = tk.Label(
            status_frame,
            text="🎯 SYSTEM READY - AWAITING ORDERS",
            bg=self.colors["bg_quaternary"],
            fg=self.colors["text_success"],
            font=("JetBrains Mono", 10, "bold"),
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.Y)

        # Progress indicator
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, mode='indeterminate', length=250)

        # Current time
        self.time_label = tk.Label(
            status_frame,
            text="",
            bg=self.colors["bg_quaternary"],
            fg=self.colors["text_accent"],
            font=("JetBrains Mono", 9, "bold"),
        )
        self.time_label.pack(side=tk.RIGHT, padx=15)

        # Update time
        self.update_time()

    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%H:%M:%S ZULU")
        self.time_label.config(text=f"⏰ {current_time}")
        self.root.after(1000, self.update_time)

    def update_displays(self, data: Dict):
        """Update all displays with new data"""
        self.current_data = data
        self.refresh_battalion_display()
        self.refresh_summary_display()
        self.refresh_players_display()
        self.refresh_operations_display()

    def refresh_operations_display(self):
        self.token_var.set(self.app.get_bearer_token())

    def refresh_displays(self):
        """Refresh all displays"""
        if self.current_data:
            self.update_displays(self.current_data)

    def refresh_battalion_display(self):
        """Refresh battalion display"""
        if not self.battalion_tree or not self.current_data:
            return

        # Clear existing items
        for item in self.battalion_tree.get_children():
            self.battalion_tree.delete(item)

        users = self.current_data.get('users', [])
        assignments = self.current_data.get('assignments', {})
        selected_battalion = self.app.selected_battalion.get()

        # Filter users by battalion
        battalion_users = []
        for user in users:
            username_lower = user['name'].lower()
            user_battalion = assignments.get(username_lower, "UNASSIGNED")
            if user_battalion == selected_battalion:
                battalion_users.append(user)

        # Sort by weekly damage
        battalion_users.sort(key=lambda x: x.get('weeklyDamage', 0), reverse=True)

        # Limit to max players shown
        max_players = self.app.max_players_shown.get()
        battalion_users = battalion_users[:max_players]

        for i, user in enumerate(battalion_users, 1):
            username_lower = user['name'].lower()
            medals = self.get_medal_display(username_lower)

            self.battalion_tree.insert(
                "",
                "end",
                values=(
                    user['name'],
                    user.get('level', 1),
                    f"{user.get('weeklyDamage', 0):,}",
                    f"#{user.get('weeklyRankingPosition', 0)}",
                    medals,
                ),
            )

    def refresh_summary_display(self):
        """Refresh summary display"""
        if not self.summary_tree or not self.current_data:
            return

        # Clear existing items
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)

        users = self.current_data.get('users', [])
        assignments = self.current_data.get('assignments', {})
        total_damage = self.current_data.get('country_weekly_damage', 0)

        # Calculate battalion statistics
        battalion_stats = {}
        assigned_damage = 0

        for user in users:
            username_lower = user['name'].lower()
            battalion = assignments.get(username_lower, "UNASSIGNED")
            damage = user.get('weeklyDamage', 0)

            if battalion != "UNASSIGNED":
                if battalion not in battalion_stats:
                    battalion_stats[battalion] = {'soldiers': 0, 'total_damage': 0}
                battalion_stats[battalion]['soldiers'] += 1
                battalion_stats[battalion]['total_damage'] += damage
                assigned_damage += damage

        # Add battalion rows
        for battalion in ["CONDOR", "YAGUARETE", "CARPINCHO"]:
            if battalion in battalion_stats:
                stats = battalion_stats[battalion]
                percentage = (stats['total_damage'] / total_damage * 100) if total_damage > 0 else 0
                avg_damage = stats['total_damage'] // stats['soldiers'] if stats['soldiers'] > 0 else 0

                battalion_info = self.battalion_info.get(battalion, {"icon": "🏴", "name": battalion})

                self.summary_tree.insert(
                    "",
                    "end",
                    values=(
                        battalion_info["name"],
                        battalion_info["icon"],
                        f"{stats['soldiers']:,}",
                        f"{stats['total_damage']:,}",
                        f"{percentage:.1f}%",
                        f"{avg_damage:,}",
                    ),
                )

        # Add unassigned row
        unassigned_damage = total_damage - assigned_damage
        if unassigned_damage > 0:
            assigned_population = sum(stats['soldiers'] for stats in battalion_stats.values())
            unassigned_population = len(users) - assigned_population
            percentage = (unassigned_damage / total_damage * 100) if total_damage > 0 else 0
            avg_damage = unassigned_damage // unassigned_population if unassigned_population > 0 else 0

            self.summary_tree.insert(
                "",
                "end",
                values=(
                    "UNASSIGNED SOLDIERS",
                    "❓",
                    f"{unassigned_population:,}",
                    f"{unassigned_damage:,}",
                    f"{percentage:.1f}%",
                    f"{avg_damage:,}",
                ),
            )

        # Add total row
        active_population = self.current_data.get('active_population', len(users))
        country_avg = total_damage // active_population if active_population > 0 else 0
        self.summary_tree.insert(
            "",
            "end",
            values=("TOTAL FORCES", "🏴", f"{active_population:,}", f"{total_damage:,}", "100.0%", f"{country_avg:,}"),
        )

        # Update summary info
        current_week = self.app.get_current_week()
        theater = self.app.current_country.get().upper()
        info_text = f"COUNTRY: {theater} | OPERATION: {current_week.upper()} | TOTAL DAMAGE: {total_damage:,} | ACTIVE SOLDIERS: {active_population:,}"
        if hasattr(self, 'summary_info'):
            self.summary_info.config(text=info_text)

    def refresh_players_display(self):
        """Refresh players display"""
        if not self.players_tree or not self.current_data:
            return

        # Clear existing items
        for item in self.players_tree.get_children():
            self.players_tree.delete(item)

        users = self.current_data.get('users', [])
        assignments = self.current_data.get('assignments', {})

        # Apply filter
        filter_text = self.player_filter.get().lower() if hasattr(self, 'player_filter') else ""

        for user in users:
            username_lower = user['name'].lower()

            # Apply filter
            if filter_text and filter_text not in username_lower:
                continue

            battalion = assignments.get(username_lower, "UNASSIGNED")
            medals = self.get_medal_display(username_lower)

            # Get battalion display name
            if battalion in self.battalion_info:
                battalion_display = self.battalion_info[battalion]["name"]
            else:
                battalion_display = battalion or "UNASSIGNED"

            self.players_tree.insert(
                "",
                "end",
                values=(
                    user['name'],
                    user.get('level', 1),
                    f"{user.get('weeklyDamage', 0):,}",
                    f"#{user.get('weeklyRankingPosition', 0)}",
                    battalion_display,
                    medals,
                ),
            )

    def get_medal_display(self, username_lower: str) -> str:
        """Get medal display for a user"""
        if not self.current_data or 'user_data' not in self.current_data:
            return ""

        user_data = self.current_data['user_data']
        if username_lower not in user_data or "medals" not in user_data[username_lower]:
            return ""

        medals = user_data[username_lower]["medals"]
        medal_counts = {"gold": 0, "silver": 0, "bronze": 0}

        for week, medal_type in medals.items():
            if medal_type in medal_counts:
                medal_counts[medal_type] += 1

        display_parts = []
        medal_icons = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}

        for medal_type, count in medal_counts.items():
            if count > 0:
                icon = medal_icons[medal_type]
                if count > 1:
                    display_parts.append(f"{icon}x{count}")
                else:
                    display_parts.append(icon)

        return " ".join(display_parts)

    def assign_medal(self, medal_type: str):
        """Assign medal to selected player"""
        if not self.battalion_tree:
            return

        selected_items = self.battalion_tree.selection()
        if not selected_items:
            self.show_message("Warning", "Select personnel for decoration!", "warning")
            return

        for item in selected_items:
            player_name = self.battalion_tree.item(item)['values'][0]
            success = self.app.assign_medal(player_name, medal_type)

        if selected_items:
            self.show_message("Decoration Awarded", f"Awarded {medal_type} decoration!", "success")

    def assign_selected_players(self):
        """Assign selected players to battalion"""
        if not self.players_tree:
            return

        selected_items = self.players_tree.selection()
        if not selected_items:
            self.show_message("Warning", "Select personnel for assignment!", "warning")
            return

        battalion = self.assign_battalion.get()
        player_names = []

        for item in selected_items:
            player_name = self.players_tree.item(item)['values'][0]
            player_names.append(player_name)

        count = self.app.assign_players_to_battalion(player_names, battalion)
        self.show_message("Assignment Complete", f"Assigned {count} personnel to {battalion}", "success")

    def export_current_data(self):
        """Export selected players or all players to html"""

        if self.current_data is None:
            self.show_message("Export not completed", f"Export proccess uncompleted, missing data", "warning")
            return

        from export import export_summary_report, export_single_battalion_report, assign_battalion

        selected_battalion = self.app.selected_battalion.get()
        current_week = self.app.get_current_week()
        users = self.current_data.get("users")
        user_data = self.current_data.get("user_data")
        country_weekly_damage = self.current_data.get("country_weekly_damage", 1)
        active_population = self.current_data.get("active_population")
        country_name = self.current_data.get("country_info", {}).get("name", None)
        assignments = self.current_data.get("assignments")

        export_single_battalion_report(
            selected_battalion,
            users,
            assignments,
            user_data,
            country_weekly_damage,
            active_population,
            country_name,
            format_type="html",
        )

        # Separar a otro func

    def export_summary(self):
        """Export selected players or all players to html"""

        if self.current_data is None:
            self.show_message("Export not completed", f"Export proccess uncompleted, missing data", "warning")
            return

        from export import export_summary_report, export_single_battalion_report, assign_battalion

        selected_battalion = self.app.selected_battalion.get()
        current_week = self.app.get_current_week()
        users = self.current_data.get("users")
        user_data = self.current_data.get("user_data")
        country_weekly_damage = self.current_data.get("country_weekly_damage", 1)
        active_population = self.current_data.get("active_population")
        country_name = self.current_data.get("country_info", {}).get("name", None)
        assignments = self.current_data.get("assignments")

        battalions_data = {}
        battalion_assignments = assignments
        country_total_damage = country_weekly_damage
        assigned_damage = 0
        unassigned_users_found = 0

        # Calculate battalion statistics
        for user in users:
            battalion = assign_battalion(user['name'], battalion_assignments)
            if battalion == "UNASSIGNED":
                unassigned_users_found += 1
            else:
                if battalion not in battalions_data:
                    battalions_data[battalion] = {'total_damage': 0, 'soldier_count': 0, 'soldiers': []}
                battalions_data[battalion]['total_damage'] += user['weeklyDamage']
                battalions_data[battalion]['soldier_count'] += 1
                battalions_data[battalion]['soldiers'].append(user)
                assigned_damage += user['weeklyDamage']

        # Calculate unassigned damage
        unassigned_damage = country_total_damage - assigned_damage

        # Create and display summary panel
        export_summary_report(
            users,
            assignments,
            user_data,
            country_weekly_damage,
            active_population,
            country_name,
            format_type="html",
        )

        self.show_message("Export Complete", f"Export proccess completed", "success")

    def save_token(self):
        """Save API token"""
        token = self.token_var.get()
        self.app.set_bearer_token(token)
        self.show_message("Credentials Saved", "Authorization token updated!", "success")

    def export_data(self):
        """Export data"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Intelligence Data",
        )
        if filename:
            success = self.app.export_data(filename)
            if success:
                self.show_message("Export Complete", f"Intelligence data exported to {filename}", "success")
            else:
                self.show_message("Export Failed", "Export operation failed", "error")

    def import_data(self):
        """Import data"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="Import Intelligence Data"
        )
        if filename:
            success = self.app.import_data(filename)
            if success:
                self.show_message("Import Complete", f"Intelligence data imported from {filename}", "success")
            else:
                self.show_message("Import Failed", "Import operation failed", "error")

    def clear_cache(self):
        """Clear cache"""
        if self.show_confirmation("Confirm Operation", "Clear all cached intelligence for current theater?"):
            success = self.app.clear_cache()
            if success:
                self.show_message("Cache Cleared", "Intelligence cache cleared successfully!", "success")
            else:
                self.show_message("Clear Failed", "Cache clear operation failed", "error")

    def show_loading(self, message: str):
        """Show loading state"""
        if self.refresh_btn:
            self.refresh_btn.config(state="disabled", text="📡 GATHERING INTEL...")
        self.show_progress()
        self.update_status(message)

    def hide_loading(self):
        """Hide loading state"""
        if self.refresh_btn:
            self.refresh_btn.config(state="normal", text="📡 INTEL UPDATE")
        self.hide_progress()

    def show_progress(self):
        """Show progress indicator"""
        if self.progress_bar:
            self.progress_bar.pack(side=tk.RIGHT, padx=(0, 15))
            self.progress_bar.start()

    def hide_progress(self):
        """Hide progress indicator"""
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def update_status(self, message: str):
        """Update status with military terminology"""
        military_status = {
            "Ready": "🎯 SYSTEM READY - AWAITING ORDERS",
            "Fetching fresh data": "📡 GATHERING FIELD INTELLIGENCE...",
            "Data refreshed successfully": "✅ INTELLIGENCE UPDATE COMPLETE",
            "Error": "⚠️ COMMUNICATION ERROR - CHECK PROTOCOLS",
        }

        # Convert to military terminology
        for key, military_msg in military_status.items():
            if key.lower() in message.lower():
                message = military_msg
                break

        if self.status_label:
            self.status_label.config(text=message)
            self.root.update_idletasks()

    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Show styled message with larger font"""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x200")
        dialog.configure(bg=self.colors["bg_secondary"])
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        # Icon and color based on type
        icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}

        colors = {
            "info": self.colors["text_accent"],
            "warning": self.colors["text_warning"],
            "error": self.colors["text_danger"],
            "success": self.colors["text_success"],
        }

        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors["bg_secondary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Icon and title
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_secondary"])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        icon_label = tk.Label(
            header_frame,
            text=icons.get(msg_type, "ℹ️"),
            bg=self.colors["bg_secondary"],
            fg=colors.get(msg_type, self.colors["text_accent"]),
            font=("JetBrains Mono", 24),
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = tk.Label(
            header_frame,
            text=title,
            bg=self.colors["bg_secondary"],
            fg=colors.get(msg_type, self.colors["text_accent"]),
            font=("JetBrains Mono", 14, "bold"),
        )
        title_label.pack(side=tk.LEFT)

        # Message
        message_label = tk.Label(
            main_frame,
            text=message,
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("JetBrains Mono", 12),
            wraplength=450,
            justify=tk.LEFT,
        )
        message_label.pack(fill=tk.X, pady=(0, 20))

        # OK button
        ok_button = tk.Button(
            main_frame,
            text="ACKNOWLEDGED",
            command=dialog.destroy,
            bg=self.colors["accent"],
            fg=self.colors["bg_primary"],
            font=("JetBrains Mono", 12, "bold"),
            relief="raised",
            bd=3,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        ok_button.pack()

        # Center dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()

    def show_confirmation(self, title: str, message: str) -> bool:
        """Show confirmation dialog with larger font"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x220")
        dialog.configure(bg=self.colors["bg_secondary"])
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        result = [False]  # Use list to modify from inner function

        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors["bg_secondary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Icon and title
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_secondary"])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        icon_label = tk.Label(
            header_frame,
            text="❓",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("JetBrains Mono", 24),
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = tk.Label(
            header_frame,
            text=title,
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_warning"],
            font=("JetBrains Mono", 14, "bold"),
        )
        title_label.pack(side=tk.LEFT)

        # Message
        message_label = tk.Label(
            main_frame,
            text=message,
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            font=("JetBrains Mono", 12),
            wraplength=450,
            justify=tk.LEFT,
        )
        message_label.pack(fill=tk.X, pady=(0, 20))

        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=self.colors["bg_secondary"])
        buttons_frame.pack()

        def on_yes():
            result[0] = True
            dialog.destroy()

        def on_no():
            result[0] = False
            dialog.destroy()

        # Yes button
        yes_button = tk.Button(
            buttons_frame,
            text="✅ CONFIRM",
            command=on_yes,
            bg=self.colors["success"],
            fg=self.colors["text_primary"],
            font=("JetBrains Mono", 12, "bold"),
            relief="raised",
            bd=3,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        yes_button.pack(side=tk.LEFT, padx=(0, 10))

        # No button
        no_button = tk.Button(
            buttons_frame,
            text="❌ CANCEL",
            command=on_no,
            bg=self.colors["danger"],
            fg=self.colors["text_primary"],
            font=("JetBrains Mono", 12, "bold"),
            relief="raised",
            bd=3,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        no_button.pack(side=tk.LEFT)

        # Center dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()
        return result[0]
