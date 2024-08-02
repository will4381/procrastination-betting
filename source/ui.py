import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from source.algo import Procrast, Assignment, User, Bet
import sys

def setup_styles(style):
    style.configure("Sidebar.TFrame", background="#F2F2F7")
    style.configure("Main.TFrame", background="white")
    style.configure("Content.TFrame", background="white")
    style.configure("Sidebar.TLabel", background="#F2F2F7", foreground="black")
    
    style.configure("TButton", 
                    font=("SF Pro Text", 13),
                    padding=(10, 5))
    
    style.configure("Accent.TButton", 
                    font=("SF Pro Text", 13, "bold"))
    
    style.configure("Content.TFrame", padding=(20, 20))
    
    style.configure("TLabel", anchor="w", padding=(0, 5))
    style.configure("TEntry", padding=(5, 5))

    style.configure("Card.TFrame", 
                    background="#FFFFFF", 
                    relief="flat", 
                    borderwidth=1)

    for widget in ['TEntry', 'TCombobox']:
        style.configure(widget, padding=(5, 5))

    style.configure("Treeview", font=("SF Pro Text", 13))
    style.configure("Treeview.Heading", font=("SF Pro Text", 13, "bold"))

    style.configure("Sidebar.TButton.Active",
                    background="#0E7AFE",
                    foreground="white")

def create_button(parent, text, command, width, **kwargs):
    button = ttk.Button(parent, text=text, command=command, width=width, **kwargs)
    return button

class ProcrastUI(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("🎲 Procrast")
        self.geometry("1200x800")
        self.procrast = Procrast()

        setup_styles(self.style)

        # Set app icon
        if sys.platform == 'darwin':  # macOS
            from PIL import Image, ImageTk
            icon = Image.open("assets/dice.png")
            icon_tk = ImageTk.PhotoImage(icon)
            self.iconphoto(True, icon_tk)
            self.createcommand('tk::mac::Quit', self.quit)

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, width=190)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.divider = ttk.Separator(self, orient="vertical")
        self.divider.grid(row=0, column=1, sticky="ns")

        self.main_frame = ttk.Frame(self, style="Main.TFrame")
        self.main_frame.grid(row=0, column=2, sticky="nsew", padx=(20, 0))
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.content_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DashboardFrame, AssignmentsFrame, BettingFrame, UsersFrame, SimulationFrame, SimulationResultsFrame):
            frame = F(self.content_frame, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        self.sidebar.set_active(page_name)

class Sidebar(ttk.Frame):
    def __init__(self, parent, width):
        super().__init__(parent, width=width, style='Sidebar.TFrame')
        self.parent = parent

        # Logo
        logo_frame = ttk.Frame(self, style='Sidebar.TFrame')
        logo_frame.pack(pady=(20, 30), padx=10)
        
        logo_label = ttk.Label(logo_frame, text="🎲", font=("SF Pro Display", 24), style="Sidebar.TLabel")
        logo_label.pack(side="left", padx=(0, 5))
        
        app_name = ttk.Label(logo_frame, text="Procrast", font=("SF Pro Display", 18, "bold"), style="Sidebar.TLabel")
        app_name.pack(side="left")

        self.buttons = {}
        options = [
            ("Dashboard", "📊", "DashboardFrame"),
            ("Assignments", "📝", "AssignmentsFrame"),
            ("Betting", "🎲", "BettingFrame"),
            ("Users", "👥", "UsersFrame"),
            ("Simulation", "🔬", "SimulationFrame"),
            ("Results", "📈", "SimulationResultsFrame")
        ]

        for text, emoji, frame in options:
            btn = ttk.Button(
                self, 
                text=f"{emoji} {text}", 
                command=lambda f=frame: parent.show_frame(f),
                bootstyle="light",
                padding=(10, 8)
            )
            btn.pack(padx=10, pady=5, fill="x")
            self.buttons[frame] = btn

    def set_active(self, active_frame):
        for frame, btn in self.buttons.items():
            if frame == active_frame:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="light")
        self.parent.update_idletasks()

class Header(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.back_button = ttk.Button(self, text="<", width=3, style="Header.TButton")
        self.back_button.pack(side="left", padx=10)
        self.forward_button = ttk.Button(self, text=">", width=3, style="Header.TButton")
        self.forward_button.pack(side="left", padx=10)
        self.title_label = ttk.Label(self, text="", font=("SF Pro Display", 20, "bold"))
        self.title_label.pack(side="left", padx=20)

    def set_title(self, title):
        self.title_label.config(text=title)

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        label = ttk.Label(self, text="Dashboard Overview", font=("SF Pro Display", 24, "bold"))
        label.pack(anchor="w", pady=(0, 20))

        stats_frame = ttk.Frame(self, style="Card.TFrame")
        stats_frame.pack(fill="x", pady=10)

        stats = [
            ("Total Users", len(self.controller.procrast.users)),
            ("Total Assignments", len(self.controller.procrast.assignments)),
            ("Total Bets", sum(len(user.bets) for user in self.controller.procrast.users)),
            ("House Take", f"{self.controller.procrast.house_take:.2%}")
        ]

        for i, (title, value) in enumerate(stats):
            frame = ttk.Frame(stats_frame, style="TFrame")
            frame.grid(row=0, column=i, padx=20, pady=20, sticky="nsew")
            ttk.Label(frame, text=title, font=("SF Pro Text", 14)).grid(row=0, column=0, pady=5)
            ttk.Label(frame, text=str(value), font=("SF Pro Display", 24, "bold")).grid(row=1, column=0, pady=5)

        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

        note_label = ttk.Label(self, text="Note: Betting odds are predictions based on current bets and not guaranteed. House take is applied to all bets with ample bettors.", 
                               font=("SF Pro Text", 12), wraplength=600, justify="left")
        note_label.pack(anchor="w", pady=(20, 0))

        reset_button = create_button(
            self,
            "Reset Simulation",
            self.reset_simulation,
            width=15
        )
        reset_button.pack(anchor="w", pady=(20, 0))

    def reset_simulation(self):
        self.controller.procrast.reset()
        self.controller.frames['AssignmentsFrame'].update_assignment_list()
        self.controller.frames['BettingFrame'].update_user_menu()
        self.controller.frames['BettingFrame'].update_assignment_menu()
        self.controller.frames['UsersFrame'].update_user_list()
        self.controller.frames['SimulationResultsFrame'].clear_results()
        Messagebox.show_info("Reset Complete", "The simulation has been reset.")

class AssignmentsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        label = ttk.Label(self, text="Manage Assignments", font=("SF Pro Display", 24, "bold"))
        label.pack(anchor="w", pady=(0, 20))

        ttk.Label(self, text="Assignment Name:").pack(anchor="w", padx=10, pady=(10, 5))
        self.assignment_name = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.assignment_name.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(self, text="Due Date (MM-DD-YYYY):").pack(anchor="w", padx=10, pady=(10, 5))
        self.due_date = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.due_date.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(self, text="Format: MM-DD-YYYY", font=("SF Pro Text", 10), foreground="gray").pack(anchor="w", padx=10)

        add_button = create_button(
            self, 
            "Add Assignment", 
            self.add_assignment,
            width=15
        )
        add_button.pack(anchor="w", padx=10, pady=20)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=20)

        self.assignment_tree = ttk.Treeview(tree_frame, columns=("name", "due_date"), show="headings")
        self.assignment_tree.heading("name", text="Assignment Name")
        self.assignment_tree.heading("due_date", text="Due Date")
        self.assignment_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.assignment_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.assignment_tree.configure(yscrollcommand=scrollbar.set)

        self.update_assignment_list()

    def add_assignment(self):
        name = self.assignment_name.get()
        due_date = datetime.strptime(self.due_date.get(), "%m-%d-%Y")
        assignment = Assignment(str(len(self.controller.procrast.assignments)), name, datetime.now(), due_date)
        self.controller.procrast.add_assignment(assignment)
        self.update_assignment_list()
        self.assignment_name.delete(0, 'end')
        self.due_date.delete(0, 'end')

    def update_assignment_list(self):
        for item in self.assignment_tree.get_children():
            self.assignment_tree.delete(item)
        for assignment in self.controller.procrast.assignments:
            self.assignment_tree.insert("", "end", values=(assignment.name, assignment.due_date.strftime('%Y-%m-%d')))

class BettingFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        label = ttk.Label(self, text="Place Your Bets", font=("SF Pro Display", 24, "bold"))
        label.pack(anchor="w", pady=(0, 20))

        ttk.Label(self, text="User:").pack(anchor="w", padx=10, pady=(10, 5))
        self.user_var = tk.StringVar()
        self.user_menu = ttk.Combobox(self, textvariable=self.user_var, state="readonly", 
                                      font=("SF Pro Text", 13))
        self.user_menu.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(self, text="Assignment:").pack(anchor="w", padx=10, pady=(10, 5))
        self.assignment_var = tk.StringVar()
        self.assignment_menu = ttk.Combobox(self, textvariable=self.assignment_var, state="readonly", 
                                            font=("SF Pro Text", 13))
        self.assignment_menu.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(self, text="Bet Amount:").pack(anchor="w", padx=10, pady=(10, 5))
        self.bet_amount = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.bet_amount.pack(fill="x", padx=10, pady=(0, 10))

        place_bet_button = create_button(
            self, 
            "Place Bet", 
            self.place_bet,
            width=15
        )
        place_bet_button.pack(anchor="w", padx=10, pady=20)

        self.odds_frame = ttk.Frame(self, style="TFrame")
        self.odds_frame.pack(fill="both", expand=True, padx=10, pady=20)

        self.update_user_menu()
        self.update_assignment_menu()

    def update_user_menu(self):
        self.user_menu['values'] = [user.name for user in self.controller.procrast.users]
        if self.user_menu['values']:
            self.user_menu.set(self.user_menu['values'][0])

    def update_assignment_menu(self):
        self.assignment_menu['values'] = [a.name for a in self.controller.procrast.assignments]
        if self.assignment_menu['values']:
            self.assignment_menu.set(self.assignment_menu['values'][0])

    def place_bet(self):
        user = next((u for u in self.controller.procrast.users if u.name == self.user_var.get()), None)
        assignment = next((a for a in self.controller.procrast.assignments if a.name == self.assignment_var.get()), None)
        amount = float(self.bet_amount.get())

        if user and assignment:
            current_date = self.controller.procrast.current_date
            bet = self.controller.procrast.place_bet(user, amount, current_date, [assignment])
            if bet:
                Messagebox.show_info("Bet Placed", f"Bet of ${amount} placed on {assignment.name}")
                self.update_odds_chart()
            else:
                Messagebox.show_error("Error", "Insufficient balance or invalid bet")
        else:
            Messagebox.show_error("Error", "Invalid user or assignment")

    def update_odds_chart(self):
        for widget in self.odds_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        for assignment in self.controller.procrast.assignments:
            odds = self.controller.procrast.get_calendar_odds(assignment)
            dates = list(odds.keys())
            values = list(odds.values())
            ax.plot(dates, values, label=assignment.name)

        ax.set_xlabel("Date")
        ax.set_ylabel("Odds")
        ax.legend()
        ax.set_title("Odds Over Time")
        ax.tick_params(axis='x', labelrotation=45)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.odds_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

class UsersFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        label = ttk.Label(self, text="Manage Users", font=("SF Pro Display", 24, "bold"))
        label.pack(anchor="w", pady=(0, 20))

        ttk.Label(self, text="Username:").pack(anchor="w", padx=10, pady=(10, 5))
        self.username = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.username.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(self, text="Initial Balance:").pack(anchor="w", padx=10, pady=(10, 5))
        self.initial_balance = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.initial_balance.pack(fill="x", padx=10, pady=(0, 10))

        add_user_button = create_button(
            self, 
            "Add User", 
            self.add_user,
            width=15
        )
        add_user_button.pack(anchor="w", padx=10, pady=20)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=20)

        self.user_list = ttk.Treeview(tree_frame, columns=("username", "balance"), show="headings")
        self.user_list.heading("username", text="Username")
        self.user_list.heading("balance", text="Balance")
        self.user_list.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.user_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.user_list.configure(yscrollcommand=scrollbar.set)

        self.update_user_list()

    def add_user(self):
        username = self.username.get()
        try:
            balance = float(self.initial_balance.get())
        except ValueError:
            Messagebox.show_error("Invalid Balance", "Please enter a valid number for the initial balance.")
            return

        user = User(username, balance)
        self.controller.procrast.add_user(user)
        self.update_user_list()
        self.username.delete(0, 'end')
        self.initial_balance.delete(0, 'end')
        Messagebox.show_info("User Added", f"User {username} has been added with an initial balance of ${balance:.2f}")

    def update_user_list(self):
        for item in self.user_list.get_children():
            self.user_list.delete(item)
        for user in self.controller.procrast.users:
            self.user_list.insert("", "end", values=(user.name, f"${user.balance:.2f}"))

class SimulationFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        label = ttk.Label(self, text="Run Simulation", font=("SF Pro Display", 24, "bold"))
        label.pack(anchor="w", pady=(0, 20))

        ttk.Label(self, text="Number of Users:").pack(anchor="w", padx=10, pady=(10, 5))
        self.num_users = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.num_users.pack(fill="x", padx=10, pady=(0, 10))
        self.num_users.insert(0, "100")

        ttk.Label(self, text="Number of Assignments:").pack(anchor="w", padx=10, pady=(10, 5))
        self.num_assignments = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.num_assignments.pack(fill="x", padx=10, pady=(0, 10))
        self.num_assignments.insert(0, "50")

        ttk.Label(self, text="Simulation Duration:").pack(anchor="w", padx=10, pady=(10, 5))
        self.sim_duration = ttk.Combobox(self, values=['week', 'month', '3month', 'year'], 
                                         state="readonly", font=("SF Pro Text", 13))
        self.sim_duration.pack(fill="x", padx=10, pady=(0, 10))
        self.sim_duration.set('month')

        ttk.Label(self, text="Mean Completion Rate (0-1):").pack(anchor="w", padx=10, pady=(10, 5))
        self.completion_rate_mean = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.completion_rate_mean.pack(fill="x", padx=10, pady=(0, 10))
        self.completion_rate_mean.insert(0, "0.7")

        ttk.Label(self, text="Completion Rate Std Dev:").pack(anchor="w", padx=10, pady=(10, 5))
        self.completion_rate_std = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.completion_rate_std.pack(fill="x", padx=10, pady=(0, 10))
        self.completion_rate_std.insert(0, "0.1")

        ttk.Label(self, text="House Take Percentage (0-100):").pack(anchor="w", padx=10, pady=(10, 5))
        self.house_take = ttk.Entry(self, width=30, font=("SF Pro Text", 13))
        self.house_take.pack(fill="x", padx=10, pady=(0, 10))
        self.house_take.insert(0, str(self.controller.procrast.house_take * 100))

        run_simulation_button = create_button(
            self, 
            "Run Simulation", 
            self.run_simulation,
            width=15
        )
        run_simulation_button.pack(anchor="w", padx=10, pady=20)

    def run_simulation(self):
        num_users = int(self.num_users.get())
        num_assignments = int(self.num_assignments.get())
        duration = self.sim_duration.get()
        completion_rate_mean = float(self.completion_rate_mean.get())
        completion_rate_std = float(self.completion_rate_std.get())
        house_take = float(self.house_take.get()) / 100

        self.controller.procrast.house_take = house_take
        self.controller.procrast.generate_random_data(num_users, num_assignments, 100, 1000, 1, 30)

        if duration == 'week':
            days = 7
        elif duration == 'month':
            days = 30
        elif duration == '3month':
            days = 90
        elif duration == 'year':
            days = 365

        for day in range(days):
            self.controller.procrast.simulate_day(completion_rate_mean, completion_rate_std)

        house_take, remaining_pool = self.controller.procrast.finalize_simulation()
        daily_stats = self.controller.procrast.get_daily_stats()

        self.controller.frames['SimulationResultsFrame'].display_results(house_take, remaining_pool, daily_stats)
        self.controller.show_frame("SimulationResultsFrame")
        
        self.controller.frames['UsersFrame'].update_user_list()
        self.controller.frames['AssignmentsFrame'].update_assignment_list()
        self.controller.frames['BettingFrame'].update_user_menu()
        self.controller.frames['BettingFrame'].update_assignment_menu()

class SimulationResultsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = ttk.Label(self, text="Simulation Results", font=("SF Pro Display", 24, "bold"))
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 20), padx=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def display_results(self, house_take, remaining_pool, daily_stats):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        results_text = tk.Text(self.scrollable_frame, height=10, width=80, font=("SF Pro Text", 13), 
                               bg="white", highlightthickness=0, bd=0)
        results_text.pack(fill="x", padx=10, pady=10)

        results = f"Simulation Results:\n"
        results += f"House Take: ${house_take:.2f}\n"
        results += f"Remaining Pool: ${remaining_pool:.2f}\n\n"
        results += "Top 5 Users by Balance:\n"
        for user in sorted(self.controller.procrast.users, key=lambda x: x.balance, reverse=True)[:5]:
            results += f"{user.name}: ${user.balance:.2f}\n"

        detailed_stats = self.controller.procrast.get_detailed_statistics()
        results += f"\nDetailed Statistics:\n"
        for key, value in detailed_stats.items():
            results += f"{key.replace('_', ' ').title()}: {value:.2f}\n"

        results_text.insert("1.0", results)

        fig = Figure(figsize=(16, 24), dpi=100)
        gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1])

        # Completion rate over time
        ax1 = fig.add_subplot(gs[0, 0])
        dates = [stat['date'] for stat in daily_stats]
        completion_rates = [stat['completion_rate'] for stat in daily_stats]
        ax1.plot(dates, completion_rates, color='#007AFF')
        ax1.set_title("Completion Rate Over Time")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Completion Rate")
        ax1.tick_params(axis='x', rotation=45)

        # Total bets vs Completed bets
        ax2 = fig.add_subplot(gs[1, 0])
        total_bets = [stat['total_bets'] for stat in daily_stats]
        completed_bets = [stat['completed_bets'] for stat in daily_stats]
        ax2.bar(dates, total_bets, label="Total Bets", alpha=0.5, color='#5AC8FA')
        ax2.bar(dates, completed_bets, label="Completed Bets", alpha=0.5, color='#4CD964')
        ax2.set_title("Total vs Completed Bets")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Number of Bets")
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)

        # User balance distribution
        ax3 = fig.add_subplot(gs[2, 0])
        balances = [user.balance for user in self.controller.procrast.users]
        ax3.hist(balances, bins=30, color='#FF9500')
        ax3.set_title("User Balance Distribution")
        ax3.set_xlabel("Balance")
        ax3.set_ylabel("Number of Users")

        fig.tight_layout(pad=4.0)

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def main():
    app = ProcrastUI()
    app.mainloop()

if __name__ == "__main__":
    main()