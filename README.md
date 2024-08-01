## Running:

GUI doesn't work in VSCode for some reason so you need to CD into the source folder and run `main.py` via a stand-alone terminal. You will likely need to install the nescessary packages in your terminal via, `python3 -m pip install tkinter ttkbootstrap matplotlib setuptools`, might need to run `brew install tcl-tk`

## Problems/Fixes:

Some problems, no reset button, added users are overwritten when a simulation is run, betting outside of the simulation needs work, scrolling is weird and some graph data is cutoff, will work on adding more insight into the calculations.
There is also probably some iffy shit in the odd calculations and its integration with the sim, I havent looked at any of the data yet.

## Odds Calculation: 

$`\text{Odds} = \max \left( 1 + 0.5 \times \left( \frac{\text{due\_date} - \text{date}}{\text{due\_date} - \text{open\_date}} \right), \frac{\text{total\_bet} \times (1 - \text{house\_take})}{\text{total\_bet}} \right)`$

where:
- `date` is the current date.
- `open_date` is the date the assignment was opened.
- `due_date` is the date the assignment is due.
- `total_bet` is the total amount bet on the assignment.
- `house_take` is the percentage of the total pool taken by the house (default is 5%).

## Simulation:

The simulation progresses day by day, adjusting the completion rates of assignments and bets based on a normal distribution. At the end of the simulation period, the total pool, house take, and prize pool are calculated, and winnings are distributed to users based on the completion of their bets.
