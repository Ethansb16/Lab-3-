import mysql.connector
import curses
import roomsAndRates
import reservations
import resCancel
import resInfo
import revenue
import os
from functools import partial 


mydb = mysql.connector.connect(
host="mysql.labthreesixfive.com",
user="esbernha",
password="365-fall24-028346142",
database="esbernha"
)

def main_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    menu_options = [
        ("View Rooms and Rates", partial(roomsAndRates.view_rooms_and_rates, mydb)),
        ("View Reservations", partial(reservations.view_reservations, mydb)),
        ("Cancel a Reservation", partial(resCancel.cancel_reservation, mydb)),
        ("Receive Reservation Information", partial(resInfo.reservation_info, mydb)),
        ("View Revenue", partial(revenue.view_revenue, mydb)),
    ]

    current_selection = 0
    start_idx = 0  # Tracks the starting index for visible menu options

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Header
        stdscr.addstr(0, 0, "Welcome to the Hotel Database Hub\n\n", curses.A_BOLD)

        # Visible options (limit by terminal height - 3 for header/padding)
        visible_options = menu_options[start_idx:start_idx + height - 3]
        for idx, (option, _) in enumerate(visible_options):
            truncated_option = option[:max(0, width - 4)]  # Ensure it fits in width
            if idx + start_idx == current_selection:
                stdscr.addstr(idx + 2, 0, f"> {truncated_option}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 2, 0, f"  {truncated_option}\n")

        key = stdscr.getch()

        # Navigation
        if key == curses.KEY_UP:
            if current_selection > 0:
                current_selection -= 1
            if current_selection < start_idx:
                start_idx -= 1
        elif key == curses.KEY_DOWN:
            if current_selection < len(menu_options) - 1:
                current_selection += 1
            if current_selection >= start_idx + height - 3:
                start_idx += 1
        elif key in [10, 13]:  # Enter key
            stdscr.clear()
            try:
                menu_options[current_selection][1]()  # Execute the selected function
            except Exception as e:
                stdscr.addstr(0, 0, f"Error: {e}\n", curses.A_BOLD)
            stdscr.addstr("\nPress any key to return to the menu.")
            stdscr.getch()
        elif key == 27:  # Escape key
            break

        stdscr.refresh()




def main(): 
    curses.wrapper(main_menu)
    mydb.close()



if __name__ == "__main__":
    main()
