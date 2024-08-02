from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Assignment:
    def __init__(self, id: str, name: str, open_date: datetime, due_date: datetime):
        self.id = id
        self.name = name
        self.open_date = open_date
        self.due_date = due_date
        self.bets = []

class Bet:
    def __init__(self, user, amount: float, selected_date: datetime, assignments):
        self.user = user
        self.amount = amount
        self.selected_date = selected_date
        self.assignments = assignments
        self.completed = False
        self.potential_return = None

class User:
    def __init__(self, name: str, balance: float):
        self.name = name
        self.balance = balance
        self.bets = []

class Procrast:
    def __init__(self):
        self.assignments = []
        self.users = []
        self.current_date = datetime.now()
        self.house_take = 0.05  # 5% house take by default
        self.daily_stats = []

    def add_user(self, user):
        self.users.append(user)
        logging.info(f"Added user: {user.name}")

    def add_assignment(self, assignment):
        self.assignments.append(assignment)
        logging.info(f"Added assignment: {assignment.name}")

    def reset(self):
        self.assignments = []
        self.users = []
        self.current_date = datetime.now()
        self.daily_stats = []
        logging.info("Reset Procrast instance")

    def generate_random_data(self, num_users, num_assignments, min_balance, max_balance, min_duration, max_duration):
        existing_users_count = len(self.users)
        for i in range(existing_users_count, num_users):
            self.users.append(User(f"User_{i}", random.uniform(min_balance, max_balance)))
        
        for i in range(num_assignments):
            open_date = self.current_date + timedelta(days=random.randint(0, 30))
            due_date = open_date + timedelta(days=random.randint(min_duration, max_duration))
            self.assignments.append(Assignment(str(i), f"Assignment_{i}", open_date, due_date))

        # Generate random bets
        for user in self.users:
            for _ in range(random.randint(1, 5)):  # Each user places 1-5 bets
                assignment = random.choice(self.assignments)
                bet_amount = random.uniform(10, 100)
                bet_date = assignment.open_date + timedelta(days=random.randint(0, (assignment.due_date - assignment.open_date).days))
                self.place_bet(user, bet_amount, bet_date, [assignment])

    def place_bet(self, user, amount, selected_date, assignments):
        if user.balance < amount:
            logging.warning(f"Insufficient balance for user {user.name}")
            return None
        bet = Bet(user, amount, selected_date, assignments)
        user.balance -= amount
        user.bets.append(bet)
        for assignment in assignments:
            assignment.bets.append(bet)
        logging.info(f"Placed bet: User {user.name}, Amount ${amount:.2f}, Assignments: {[a.name for a in assignments]}")
        return bet

    def calculate_odds(self, assignment, date):
        # Calculate total bet amount for this assignment up to the given date
        total_bet = sum(bet.amount for bet in assignment.bets if bet.selected_date <= date)
        
        # Calculate time factor: closer to due date means lower odds
        time_factor = (assignment.due_date - date).days / (assignment.due_date - assignment.open_date).days
        
        # Base odds start at 1.5 and decrease as we get closer to the due date
        base_odds = 1 + (0.5 * time_factor)
        
        # If there are bets, adjust odds based on total bet amount and house take
        if total_bet > 0:
            adjusted_odds = (total_bet * (1 - self.house_take)) / total_bet
            return max(base_odds, adjusted_odds)
        else:
            return base_odds

    def simulate_day(self, completion_rate_mean=0.7, completion_rate_std=0.1):
        daily_completion_rate = min(max(random.gauss(completion_rate_mean, completion_rate_std), 0), 1)
        completed_bets = 0
        total_bets = 0

        for assignment in self.assignments:
            if assignment.due_date == self.current_date:
                for bet in assignment.bets:
                    bet.completed = random.random() < daily_completion_rate
                    if bet.completed:
                        completed_bets += 1
                    total_bets += 1
        
        self.daily_stats.append({
            'date': self.current_date,
            'completion_rate': daily_completion_rate,
            'total_bets': total_bets,
            'completed_bets': completed_bets
        })
        
        self.current_date += timedelta(days=1)
        logging.info(f"Simulated day: {self.current_date}, Completion rate: {daily_completion_rate:.2f}")

    def finalize_simulation(self):
        total_pool = sum(bet.amount for assignment in self.assignments for bet in assignment.bets)
        house_take = total_pool * self.house_take
        prize_pool = total_pool - house_take

        for user in self.users:
            for bet in user.bets:
                if bet.completed:
                    odds = self.calculate_odds(bet.assignments[0], bet.selected_date)
                    bet.potential_return = bet.amount * odds
                    actual_return = min(bet.potential_return, prize_pool)
                    user.balance += actual_return
                    prize_pool -= actual_return
                    logging.info(f"User {user.name} won ${actual_return:.2f}")

        return house_take, prize_pool

    def get_calendar_odds(self, assignment):
        calendar = {}
        current = assignment.open_date
        while current <= assignment.due_date:
            calendar[current] = self.calculate_odds(assignment, current)
            current += timedelta(days=1)
        return calendar

    def get_detailed_statistics(self):
        stats = {
            "total_users": len(self.users),
            "total_assignments": len(self.assignments),
            "total_bets": sum(len(user.bets) for user in self.users),
            "total_bet_amount": sum(bet.amount for user in self.users for bet in user.bets),
            "average_bet_amount": sum(bet.amount for user in self.users for bet in user.bets) / sum(len(user.bets) for user in self.users) if sum(len(user.bets) for user in self.users) > 0 else 0,
            "completed_bets": sum(1 for user in self.users for bet in user.bets if bet.completed),
            "completion_rate": sum(1 for user in self.users for bet in user.bets if bet.completed) / sum(len(user.bets) for user in self.users) if sum(len(user.bets) for user in self.users) > 0 else 0,
            "house_take_percentage": self.house_take * 100
        }
        return stats

    def get_daily_stats(self):
        return self.daily_stats