import curses
import time
import os
import pandas as pd

def cancel_reservation(mydb):
    curses.endwin() #close main menu window 
    os.system('clear')

    print("To cancel reservation")

    try: 
        user_res_code = input("Enter reservation code: ")

        # execute db search for reservations associated with the provided code
        cursor = mydb.cursor()
        cursor.execute("""
            SELECT FirstName, LastName, CheckIn, (Adults + Kids) as total_Occupants 
                FROM lab7_reservations 
                WHERE Code = %s
            """, [user_res_code])

        result = cursor.fetchall()

        if len(result) > 0: 

            column_names = [description[0] for description in cursor.description]

            # Convert the result into a Pandas DataFrame
            df = pd.DataFrame(result, columns=column_names)

            # Display the DataFrame
            print(df)

            if input("Confirm cancellation (y/n): ") == "y": 
                print("Cancelling...")
                
                cursor.execute("""
                DELETE FROM lab7_reservations 
                WHERE Code = %s
                """, [user_res_code])
                mydb.commit()
                
                input("Cancelling complete, press enter to return to the main menu")
                return

            else: 
                os.system('clear')
                print("Did not cancel, returning to menu...")
                time.sleep(2.5)
                return
        else: 
 

            os.system('clear')      
            print("No reservation associated with code: ", user_res_code)
            print("Returning to main menu...")
            time.sleep(2.5)
            return

        # df = pd.read_sql(query, mydb)
        # df
        # saying that you can't connect to mysql with pandas? Commented out way works
    
    except Exception as e:
        print(f"An error occurred: {e}")

    finally: 
        cursor.close()
