import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from charts import ChartView
from report_generator import generate_report_for_player
import pandas as pd

class SportAnalyzerUI:
    def __init__(self, root, data_manager):
        self.root = root
        self.data = data_manager
        self.root.title("Sport Performance Analyzer")
        self.root.geometry("1100x720")
        self.root.configure(bg="#e8f5e9")
        
        # Initialize player variables for each sport
        self.running_player_var = tk.StringVar()
        self.swimming_player_var = tk.StringVar()
        self.football_player_var = tk.StringVar()

        self.create_layout()
        self.show_dashboard()

    def create_layout(self):
        sidebar = tk.Frame(self.root, bg="#2e7d32", width=200)
        sidebar.pack(side="left", fill="y")

        btn_specs = [
            ("🏠 Dashboard", self.show_dashboard),
            ("➕ Add Performance", self.show_add_form),
            ("📈 Charts", self.show_charts_menu),
            ("❌ Exit", self.root.quit)
        ]
        for text, cmd in btn_specs:
            b = tk.Button(sidebar, text=text, bg="#2e7d32", fg="white",
                          font=("Arial", 11, "bold"), relief="flat",
                          activebackground="#1b5e20", command=cmd)
            b.pack(fill="x", pady=6, ipady=10, padx=8)

        self.main = tk.Frame(self.root, bg="white")
        self.main.pack(side="right", fill="both", expand=True, padx=12, pady=12)

    def show_dashboard(self):
        # Force refresh data to ensure we have latest records
        self.data.refresh_data()
        
        self._clear_main()
        tk.Label(self.main, text="Dashboard — Sport-specific player summary",
                 font=("Arial", 18, "bold"), bg="white", fg="#2e7d32").pack(pady=8)

        # Get all players
        all_players = self.data.get_players()
        
        # Get players who have data for each sport
        running_players = []
        swimming_players = []
        football_players = []
        
        for player in all_players:
            running_df = self.data.get_player_sport_df(player, "Running")
            swimming_df = self.data.get_player_sport_df(player, "Swimming")
            football_df = self.data.get_player_sport_df(player, "Football")
            
            if not running_df.empty:
                running_players.append(player)
            if not swimming_df.empty:
                swimming_players.append(player)
            if not football_df.empty:
                football_players.append(player)
        
        # If no sport-specific players found, show all players as options
        if not running_players:
            running_players = all_players
        if not swimming_players:
            swimming_players = all_players
        if not football_players:
            football_players = all_players

        cards = tk.Frame(self.main, bg="white")
        cards.pack(fill="x", pady=10)

        sports_config = [
            {
                "sport": "Running",
                "players": running_players,
                "player_var": self.running_player_var,
                "default_label": "Select Runner"
            },
            {
                "sport": "Swimming", 
                "players": swimming_players,
                "player_var": self.swimming_player_var,
                "default_label": "Select Swimmer"
            },
            {
                "sport": "Football",
                "players": football_players,
                "player_var": self.football_player_var,
                "default_label": "Select Footballer"
            }
        ]

        # Display cards for each sport with their own player selection
        for config in sports_config:
            sport = config["sport"]
            players = config["players"]
            player_var = config["player_var"]
            default_label = config["default_label"]
            
            # Create card with scrollable area for sessions
            card = tk.Frame(cards, bg="#f1f8f2", bd=1, relief="solid", width=350, height=400)
            card.pack(side="left", padx=10, pady=8, ipadx=10, ipady=10)
            card.pack_propagate(False)  # Prevent card from resizing
            
            # Sport title
            title_frame = tk.Frame(card, bg="#f1f8f2")
            title_frame.pack(fill="x", padx=8, pady=6)
            tk.Label(title_frame, text=sport, font=("Arial", 12, "bold"), bg="#f1f8f2", fg="#2e7d32").pack(anchor="nw")
            
            # Player selection for this sport
            player_frame = tk.Frame(card, bg="#f1f8f2")
            player_frame.pack(fill="x", padx=8, pady=4)
            tk.Label(player_frame, text="Player:", bg="#f1f8f2").pack(side="left")
            #DROPDOWN COMBOBOX - This is the actual dropdown
            player_combo = ttk.Combobox(player_frame, textvariable=player_var, values=players, state="readonly", width=20)
            player_combo.pack(side="left", padx=6)
            
            # Set default selection if not already set
            if players:
                current_selection = player_var.get()
                if current_selection in players:
                    player_combo.set(current_selection)
                else:
                    player_combo.current(0)
                    player_var.set(players[0])
            else:
                player_combo.set("")
                player_var.set("")
            
            # Bind selection change to update this card only
            def on_player_selected(event, sport_name=sport, p_var=player_var):
                self._update_sport_card(sport_name, p_var.get())
            
            player_combo.bind('<<ComboboxSelected>>', on_player_selected)
            
            # Create scrollable frame for sessions
            sessions_frame = tk.Frame(card, bg="#f1f8f2")
            sessions_frame.pack(fill="both", expand=True, padx=8, pady=4)
            
            # Add scrollbar
            canvas = tk.Canvas(sessions_frame, bg="#f1f8f2", height=250)
            scrollbar = ttk.Scrollbar(sessions_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f1f8f2")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Store the scrollable frame for later updates
            setattr(self, f"{sport.lower()}_sessions_frame", scrollable_frame)
            
            # Display stats and sessions for selected player in this sport
            self._display_sport_stats(card, sport, player_var.get(), scrollable_frame)

        # Refresh button
        refresh_frame = tk.Frame(self.main, bg="white")
        refresh_frame.pack(pady=10)
        ttk.Button(refresh_frame, text="Refresh All", command=self.show_dashboard).pack(side="left", padx=6)
        
        # New Player button
        ttk.Button(refresh_frame, text="New Player", command=self._prompt_new_player).pack(side="left", padx=6)

        # REMOVED: Chart area from dashboard

    def _display_sport_stats(self, card, sport, player, sessions_frame):
        """Display statistics and sessions for a specific player and sport"""
        # Clear existing sessions
        for widget in sessions_frame.winfo_children():
            widget.destroy()
        
        if player:
            # Get all sessions for this player and sport
            df = self.data.get_player_sport_df(player, sport)
            stats = self.data.aggregate_stats_for_player_sport(player, sport)
            
            # Display summary statistics
            summary_frame = tk.Frame(sessions_frame, bg="#f1f8f2")
            summary_frame.pack(fill="x", pady=4)
            
            tk.Label(summary_frame, text=f"Total Sessions: {stats['sessions']}", 
                    bg="#f1f8f2", font=("Arial", 9, "bold")).pack(anchor="w")
            tk.Label(summary_frame, text=f"Total Duration: {stats['total_duration']:.1f} min", 
                    bg="#f1f8f2", font=("Arial", 9)).pack(anchor="w")
            tk.Label(summary_frame, text=f"Total Distance: {stats['total_distance']:.2f} km", 
                    bg="#f1f8f2", font=("Arial", 9)).pack(anchor="w")
            
            if sport in ["Running", "Swimming"]:
                tk.Label(summary_frame, text=f"Avg Speed: {stats['avg_speed']:.2f} km/h", 
                        bg="#f1f8f2", font=("Arial", 9)).pack(anchor="w")
            
            # Display individual sessions
            if not df.empty:
                sessions_label = tk.Label(sessions_frame, text="Individual Sessions:", 
                                        bg="#f1f8f2", font=("Arial", 9, "bold"))
                sessions_label.pack(anchor="w", pady=(10, 5))
                
                # Display each session
                for i, session in df.iterrows():
                    session_frame = tk.Frame(sessions_frame, bg="#e8f5e9", relief="raised", bd=1)
                    session_frame.pack(fill="x", pady=2, padx=5)
                    
                    date_str = session["Date"].strftime("%Y-%m-%d") if not pd.isna(session["Date"]) else "Unknown"
                    
                    session_text = f"Date: {date_str} | "
                    session_text += f"Dur: {session['Duration']}min | "
                    session_text += f"Dist: {session['Distance']}km"
                    
                    if sport in ["Running", "Swimming"] and session['Speed']:
                        session_text += f" | Speed: {session['Speed']}km/h"
                    
                    if sport == "Football":
                        if session['Goals']:
                            session_text += f" | Goals: {session['Goals']}"
                        if session['Assists']:
                            session_text += f" | Assists: {session['Assists']}"
                    
                    tk.Label(session_frame, text=session_text, bg="#e8f5e9", 
                            font=("Arial", 8), wraplength=300, justify="left").pack(anchor="w", padx=5, pady=2)

            # Generate Report button at the bottom of the card
            btn_frame = tk.Frame(card, bg="#f1f8f2")
            btn_frame.pack(fill="x", padx=8, pady=4, anchor="s")
            ttk.Button(btn_frame, text="📄 Generate Report",
                      command=lambda p=player, s=sport: self._generate_player_sport_report(p, s)).pack(anchor="se")
        else:
            # No player selected
            tk.Label(sessions_frame, text="No player selected", bg="#f1f8f2").pack()

    def _update_sport_card(self, sport, player):
        """Update a specific sport card when player selection changes"""
        # Find the sessions frame for this sport and update it
        sessions_frame = getattr(self, f"{sport.lower()}_sessions_frame")
        self._display_sport_stats(None, sport, player, sessions_frame)

    def show_add_form(self):
        self._clear_main()
        tk.Label(self.main, text="Add Performance", font=("Arial", 16, "bold"), bg="white", fg="#2e7d32").pack(pady=8)

        form = tk.Frame(self.main, bg="white")
        form.pack(pady=10, padx=10, anchor="nw")

        tk.Label(form, text="Date (YYYY-MM-DD):", bg="white").grid(row=0, column=0, sticky="w", pady=4)
        self.date_e = ttk.Entry(form, width=20); self.date_e.grid(row=0, column=1, pady=4, padx=6); self.date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Label(form, text="Player Name:", bg="white").grid(row=1, column=0, sticky="w", pady=4)
        self.player_e = ttk.Entry(form, width=30); self.player_e.grid(row=1, column=1, pady=4, padx=6)
        tk.Label(form, text="Sport:", bg="white").grid(row=2, column=0, sticky="w", pady=4)
        self.sport_e = ttk.Combobox(form, values=["Running","Swimming","Football"], state="readonly", width=28); self.sport_e.grid(row=2, column=1, pady=4, padx=6); self.sport_e.current(0)
        tk.Label(form, text="Duration (min):", bg="white").grid(row=3, column=0, sticky="w", pady=4)
        self.duration_e = ttk.Entry(form, width=20); self.duration_e.grid(row=3, column=1, pady=4, padx=6)
        tk.Label(form, text="Distance (km):", bg="white").grid(row=4, column=0, sticky="w", pady=4)
        self.distance_e = ttk.Entry(form, width=20); self.distance_e.grid(row=4, column=1, pady=4, padx=6)
        tk.Label(form, text="Speed (km/h) - optional:", bg="white").grid(row=5, column=0, sticky="w", pady=4)
        self.speed_e = ttk.Entry(form, width=20); self.speed_e.grid(row=5, column=1, pady=4, padx=6)
        tk.Label(form, text="Calories:", bg="white").grid(row=6, column=0, sticky="w", pady=4)
        self.calories_e = ttk.Entry(form, width=20); self.calories_e.grid(row=6, column=1, pady=4, padx=6)

        self.football_frame = tk.Frame(form, bg="white"); self.football_frame.grid(row=7, column=0, columnspan=2, pady=4, sticky="w")
        tk.Label(self.football_frame, text="(Football only) Goals:", bg="white").grid(row=0, column=0)
        self.goals_e = ttk.Entry(self.football_frame, width=8); self.goals_e.grid(row=0, column=1, padx=6)
        tk.Label(self.football_frame, text="Assists:", bg="white").grid(row=0, column=2)
        self.assists_e = ttk.Entry(self.football_frame, width=8); self.assists_e.grid(row=0, column=3, padx=6)
        tk.Label(self.football_frame, text="Stamina (1-10):", bg="white").grid(row=0, column=4)
        self.stamina_e = ttk.Entry(self.football_frame, width=6); self.stamina_e.grid(row=0, column=5, padx=6)

        tk.Label(form, text="Notes:", bg="white").grid(row=8, column=0, sticky="w", pady=6)
        self.notes_e = ttk.Entry(form, width=60); self.notes_e.grid(row=8, column=1, pady=6, padx=6, columnspan=2, sticky="w")

        ttk.Button(form, text="Save Performance", command=self._save_performance).grid(row=9, column=0, columnspan=2, pady=12)

        def on_sport_change(event=None):
            if self.sport_e.get() == "Football":
                self.football_frame.grid()
            else:
                self.football_frame.grid_remove()
        self.sport_e.bind("<<ComboboxSelected>>", on_sport_change)
        on_sport_change()

    def show_charts_menu(self):
        self._clear_main()
        tk.Label(self.main, text="Charts — Choose player & sport", font=("Arial",14,"bold"), bg="white", fg="#2e7d32").pack(pady=6)
        frame = tk.Frame(self.main, bg="white"); frame.pack(pady=8)
        players = self.data.get_players()
        tk.Label(frame, text="Player:", bg="white").grid(row=0, column=0, padx=6, pady=4)
        pvar = tk.StringVar(); pcomb = ttk.Combobox(frame, textvariable=pvar, values=players, state="readonly", width=30); pcomb.grid(row=0,column=1)
        if players: pcomb.current(0)
        tk.Label(frame, text="Sport:", bg="white").grid(row=1, column=0, padx=6, pady=4)
        svar = tk.StringVar(); scomb = ttk.Combobox(frame, textvariable=svar, values=["Running","Swimming","Football"], state="readonly", width=30); scomb.grid(row=1,column=1); scomb.current(0)

        chart_area = tk.Frame(self.main, bg="white"); chart_area.pack(fill="both", expand=True, pady=10)
        chart_view = ChartView(chart_area)

        def plot_choice():
            player = pvar.get()
            sport = svar.get()
            if not player:
                messagebox.showinfo("Select player", "Please select a player")
                return
            df = self.data.get_player_sport_df(player, sport)
            metric = "Speed" if sport in ("Running","Swimming") else "Duration"
            chart_view.show_player_sport_trend(df, metric=metric)

        ttk.Button(frame, text="Show Chart", command=plot_choice).grid(row=0, column=2, rowspan=2, padx=10)

    def _generate_player_sport_report(self, player, sport):
        """Generate PDF report for all sessions of a player in a specific sport"""
        if not player:
            messagebox.showinfo("No player", "Please select a player first.")
            return
        
        # Get all sessions for this player and sport
        df = self.data.get_player_sport_df(player, sport)
        stats = self.data.aggregate_stats_for_player_sport(player, sport)
        
        if df.empty:
            messagebox.showinfo("No data", "No records to generate report for this player/sport.")
            return
            
        # Generate the report
        path = generate_report_for_player(player, sport, df, stats)
        if path:
            messagebox.showinfo("Report saved", f"Report saved at:\n{path}")
        else:
            messagebox.showinfo("Error", "Failed to generate report.")

    def _save_performance(self):
        try:
            rec = {
                "Date": self.date_e.get(),
                "Player": self.player_e.get().strip(),
                "Sport": self.sport_e.get(),
                "Duration": float(self.duration_e.get() or 0),
                "Distance": float(self.distance_e.get() or 0),
                "Speed": float(self.speed_e.get()) if self.speed_e.get().strip() else None,
                "Calories": float(self.calories_e.get() or 0),
                "Notes": self.notes_e.get().strip()
            }
            if self.sport_e.get() == "Football":
                rec["Goals"] = int(self.goals_e.get() or 0)
                rec["Assists"] = int(self.assists_e.get() or 0)
                rec["Stamina"] = float(self.stamina_e.get() or 0)
                rec["Sport"] = "Football"
            if not rec["Player"]:
                messagebox.showerror("Error", "Please enter Player Name.")
                return
            added = self.data.add_performance(rec)
            if added:
                messagebox.showinfo("Saved", "Performance saved.")
                self.show_dashboard()  # Refresh dashboard to show updated data
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def _prompt_new_player(self):
        name = simpledialog.askstring("New player", "Enter player name:")
        if name:
            # After adding a new player, refresh the dashboard
            self.data.refresh_data()
            self.show_dashboard()

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()