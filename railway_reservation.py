import json, os, random, datetime as dt
from dataclasses import dataclass, asdict
from typing import List

# JSON file names
USERS_FILE = "id.json"
TRAINS_FILE = "t.json"
RESERVATIONS_FILE = "p.json"
CANCELLATIONS_FILE = "cn.json"

ADMIN_PASSWORD = "admin"

# Day abbreviations like IRCTC
DAY_ABBR = ["M", "T", "W", "T", "F", "S", "S"]  # Monday..Sunday
FULL_DAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]


# -------------------- JSON Helpers --------------------

def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# -------------------- Data Models --------------------

@dataclass
class Passenger:
    name: str
    age: int

    def to_dict(self):
        return asdict(self)


@dataclass
class Detail:
    tno: int
    tname: str
    bp: str
    dest: str
    c1: int
    c1fare: int
    c2: int
    c2fare: int
    dep_time: str
    arr_time: str
    running_days: List[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class Reservation:
    pnr: int
    tno: int
    tname: str
    bp: str
    dest: str
    passengers: List[Passenger]
    clas: str
    nosr: int
    journey_date: str
    con: int
    amc: float

    def to_dict(self):
        return {
            "pnr": self.pnr,
            "tno": self.tno,
            "tname": self.tname,
            "bp": self.bp,
            "dest": self.dest,
            "passengers": [p.to_dict() for p in self.passengers],
            "clas": self.clas,
            "nosr": self.nosr,
            "journey_date": self.journey_date,
            "con": self.con,
            "amc": self.amc,
        }


@dataclass
class Cancellation:
    pnr: int
    tno: int
    tname: str
    bp: str
    dest: str
    passengers: List[Passenger]
    clas: str
    nosc: int
    cancel_date: str
    amr: float

    def to_dict(self):
        return {
            "pnr": self.pnr,
            "tno": self.tno,
            "tname": self.tname,
            "bp": self.bp,
            "dest": self.dest,
            "passengers": [p.to_dict() for p in self.passengers],
            "clas": self.clas,
            "nosc": self.nosc,
            "cancel_date": self.cancel_date,
            "amr": self.amr,
        }


# -------------------- Date Helpers --------------------

def parse_date_input(prompt="Date (dd-mm-yyyy): "):
    while True:
        s = input(prompt).strip()
        try:
            d, m, y = map(int, s.split("-"))
            return dt.date(y, m, d)
        except:
            print("Invalid format. Use dd-mm-yyyy.")


def parse_date_from_iso(s: str):
    y, m, d = map(int, s.split("-"))
    return dt.date(y, m, d)


def get_day_abbr(date_obj: dt.date) -> str:
    return DAY_ABBR[date_obj.weekday()]


def pretty_date(date_obj: dt.date):
    return date_obj.strftime("%a, %d %b")


# -------------------- IRCTC-Style Display --------------------

def print_train_irctc(t: dict, journey_date: dt.date):
    running = " ".join(t["running_days"])

    dep_time = t["dep_time"]
    arr_time = t["arr_time"]

    dep_h, dep_m = map(int, dep_time.split(":"))
    arr_h, arr_m = map(int, arr_time.split(":"))

    arr_date = journey_date
    if (arr_h, arr_m) < (dep_h, dep_m):
        arr_date = journey_date + dt.timedelta(days=1)

    print()
    print(f"{t['tname']} ({t['tno']})")
    print(f"Runs On: {running}")
    print(f"{dep_time} | {t['bp']} | {pretty_date(journey_date)}")
    print(f"{arr_time} | {t['dest']} | {pretty_date(arr_date)}")
    print(f"First Class : seats {t['c1']} | fare {t['c1fare']}")
    print(f"Second Class: seats {t['c2']} | fare {t['c2fare']}")
    print("-" * 60)


def display_trains_pattern():
    trains = load_json(TRAINS_FILE, [])
    if not trains:
        print("No trains available.")
        return
    print("\n--- TRAIN LIST (Pattern) ---")
    for t in trains:
        running = " ".join(t["running_days"])
        print(f"{t['tname']} ({t['tno']}) {t['bp']} -> {t['dest']}")
        print(f"Dep: {t['dep_time']} Arr: {t['arr_time']} Runs On: {running}")
        print("-" * 60)


# -------------------- Admin: User Management --------------------

def manage_users():
    while True:
        print("\n--- USER MANAGEMENT ---")
        print("1. Create user DB (overwrite)")
        print("2. Add user")
        print("3. Display users")
        print("4. Back")
        ch = input("Enter choice: ").strip()

        users = load_json(USERS_FILE, [])

        if ch == "1":
            users = []
            uid = input("User ID: ")
            pw = input("Password: ")
            users.append({"user_id": uid, "password": pw})
            save_json(USERS_FILE, users)
            print("User DB created.")

        elif ch == "2":
            uid = input("User ID: ")
            pw = input("Password: ")
            users.append({"user_id": uid, "password": pw})
            save_json(USERS_FILE, users)
            print("User added.")

        elif ch == "3":
            print("\nUsers:")
            for u in users:
                print(u["user_id"], "-", u["password"])

        elif ch == "4":
            return

        else:
            print("Invalid choice.")


# -------------------- Admin: Train Management --------------------

def create_or_add_train(overwrite=False):
    trains = [] if overwrite else load_json(TRAINS_FILE, [])
    while True:
        print("\n--- ADD TRAIN ---")

        try:
            tno = int(input("Train No: "))
            tname = input("Train Name: ")
            bp = input("Boarding Station: ")
            dest = input("Destination Station: ")
            c1 = int(input("1st Class Seats: "))
            c1fare = int(input("1st Class Fare: "))
            c2 = int(input("2nd Class Seats: "))
            c2fare = int(input("2nd Class Fare: "))
        except:
            print("Invalid input. Try again.")
            continue

        dep_time = input("Departure Time (HH:MM): ")
        arr_time = input("Arrival Time (HH:MM): ")

        print("Select Running Days:")
        running_days = []
        for i, d in enumerate(FULL_DAYS):
            ans = input(f"{d} (y/n): ").lower()
            if ans == "y":
                running_days.append(DAY_ABBR[i])

        trains.append(Detail(
            tno, tname, bp, dest,
            c1, c1fare, c2, c2fare,
            dep_time, arr_time, running_days
        ).to_dict())

        if input("Add more trains? (y/n): ").lower() != "y":
            break

    save_json(TRAINS_FILE, trains)
    print("Train(s) saved successfully.")


def update_train():
    trains = load_json(TRAINS_FILE, [])
    if not trains:
        print("No trains available.")
        return

    try:
        tno = int(input("Enter Train No to update: "))
    except:
        print("Invalid number.")
        return

    for t in trains:
        if t["tno"] == tno:
            print("Updating Train:", t["tname"])

            new_name = input(f"Name [{t['tname']}]: ").strip()
            if new_name: t["tname"] = new_name

            new_bp = input(f"Boarding [{t['bp']}]: ").strip()
            if new_bp: t["bp"] = new_bp

            new_dest = input(f"Destination [{t['dest']}]: ").strip()
            if new_dest: t["dest"] = new_dest

            v = input(f"1st Class Seats [{t['c1']}]: ").strip()
            if v: t["c1"] = int(v)

            v = input(f"1st Class Fare [{t['c1fare']}]: ").strip()
            if v: t["c1fare"] = int(v)

            v = input(f"2nd Class Seats [{t['c2']}]: ").strip()
            if v: t["c2"] = int(v)

            v = input(f"2nd Class Fare [{t['c2fare']}]: ").strip()
            if v: t["c2fare"] = int(v)

            v = input(f"Departure Time [{t['dep_time']}]: ").strip()
            if v: t["dep_time"] = v

            v = input(f"Arrival Time [{t['arr_time']}]: ").strip()
            if v: t["arr_time"] = v

            print("Update Running Days:")
            new_run = []
            for i, d in enumerate(FULL_DAYS):
                cur = DAY_ABBR[i] in t["running_days"]
                inp = input(f"{d} (y/n, blank keep {'y' if cur else 'n'}): ").lower()
                if inp == "":
                    if cur: new_run.append(DAY_ABBR[i])
                elif inp == "y":
                    new_run.append(DAY_ABBR[i])

            if new_run:
                t["running_days"] = new_run

            save_json(TRAINS_FILE, trains)
            print("Train updated.")
            return

    print("Train not found.")


def delete_train():
    trains = load_json(TRAINS_FILE, [])
    if not trains:
        print("No trains available.")
        return

    try:
        tno = int(input("Enter Train No to delete: "))
    except:
        print("Invalid number.")
        return

    new_list = [t for t in trains if t["tno"] != tno]
    if len(new_list) == len(trains):
        print("Train not found.")
    else:
        save_json(TRAINS_FILE, new_list)
        print("Train deleted.")


# -------------------- Search Trains --------------------

def search_trains():
    trains = load_json(TRAINS_FILE, [])
    if not trains:
        print("No trains available.")
        return None

    bp = input("From Station: ").strip().lower()
    dest = input("To Station: ").strip().lower()

    jdate = parse_date_input("Journey Date (dd-mm-yyyy): ")
    day = get_day_abbr(jdate)

    matches = [
        t for t in trains
        if t["bp"].lower() == bp
        and t["dest"].lower() == dest
        and day in t["running_days"]
    ]

    if not matches:
        print("No trains found for this route & day.")
        return None

    print(f"\nTrains on {pretty_date(jdate)} ({day})")
    for t in matches:
        print_train_irctc(t, jdate)

    return matches, jdate


# -------------------- Reservation --------------------

def do_reservation():
    result = search_trains()
    if not result:
        return

    matches, jdate = result

    try:
        chosen = int(input("Enter Train No to Reserve: "))
    except:
        print("Invalid.")
        return

    train = None
    for t in matches:
        if t["tno"] == chosen:
            train = t
            break

    if not train:
        print("Train not in list.")
        return

    try:
        nosr = int(input("Seats Required: "))
    except:
        print("Invalid.")
        return

    passengers = []
    for i in range(nosr):
        name = input(f"Passenger {i+1} Name: ")
        age = int(input("Age: "))
        passengers.append(Passenger(name, age))

    clas = input("Class (f/s): ").lower()
    if clas not in ("f", "s"):
        print("Invalid class.")
        return

    print("\nConcession:")
    print("1. Military\n2. Senior Citizen\n3. Child <5yrs\n4. None")
    try:
        con = int(input("Choice: "))
    except:
        con = 4

    # Fare logic
    if clas == "f":
        if train["c1"] < nosr:
            print("Not enough seats.")
            return
        fare = train["c1fare"]
        train["c1"] -= nosr
    else:
        if train["c2"] < nosr:
            print("Not enough seats.")
            return
        fare = train["c2fare"]
        train["c2"] -= nosr

    if con == 1:
        amc = nosr * (fare * 0.5)
    elif con == 2:
        amc = nosr * (fare * 0.4)
    elif con == 3:
        amc = 0
    else:
        amc = nosr * fare

    pnr = random.randint(100000, 999999)

    reservation_entry = Reservation(
        pnr, train["tno"], train["tname"], train["bp"], train["dest"],
        passengers, clas, nosr, jdate.isoformat(), con, amc
    ).to_dict()

    reservations = load_json(RESERVATIONS_FILE, [])
    reservations.append(reservation_entry)
    save_json(RESERVATIONS_FILE, reservations)

    # Update train seats
    all_trains = load_json(TRAINS_FILE, [])
    for t in all_trains:
        if t["tno"] == train["tno"]:
            t.update(train)
            break
    save_json(TRAINS_FILE, all_trains)

    print("\nReservation Successful!")
    show_pnr_status(pnr)


# -------------------- PNR Status --------------------

def show_pnr_status(pnr=None):
    reservations = load_json(RESERVATIONS_FILE, [])
    if not reservations:
        print("No reservations.")
        return

    if pnr is None:
        try:
            pnr = int(input("Enter PNR: "))
        except:
            print("Invalid.")
            return

    for r in reservations:
        if r["pnr"] == pnr:
            jdate = parse_date_from_iso(r["journey_date"])
            print("\n===== PNR STATUS =====")
            print(f"PNR: {r['pnr']}")
            print(f"Train: {r['tno']} {r['tname']}")
            print(f"Route: {r['bp']} -> {r['dest']}")
            print(f"Date: {pretty_date(jdate)}")
            print(f"Class: {r['clas']}")
            print("Passengers:")
            for p in r["passengers"]:
                print(f" - {p['name']} (Age {p['age']})")
            print(f"Amount Paid: {r['amc']}")

            trains = load_json(TRAINS_FILE, [])
            for t in trains:
                if t["tno"] == r["tno"]:
                    print_train_irctc(t, jdate)

            print("=" * 30)
            return

    print("PNR not found.")


# -------------------- Cancel Ticket --------------------

def cancel_ticket():
    reservations = load_json(RESERVATIONS_FILE, [])
    if not reservations:
        print("No reservations.")
        return

    try:
        pnr = int(input("Enter PNR: "))
    except:
        print("Invalid.")
        return

    res = None
    for r in reservations:
        if r["pnr"] == pnr:
            res = r
            break

    if not res:
        print("PNR not found.")
        return

    jdate = parse_date_from_iso(res["journey_date"])
    cancel_date = parse_date_input("Cancellation Date (dd-mm-yyyy): ")

    trains = load_json(TRAINS_FILE, [])
    train = None
    for t in trains:
        if t["tno"] == res["tno"]:
            train = t
            break

    if not train:
        print("Train not found.")
        return

    days_diff = (jdate - cancel_date).days
    tamt = res["amc"]

    if days_diff < 0:
        print("Journey already passed. No refund.")
        return
    elif days_diff == 0:
        amr = tamt * 0.4
    elif days_diff <= 30:
        amr = tamt * 0.5
    else:
        amr = tamt * 0.8

    if res["clas"] == "f":
        train["c1"] += res["nosr"]
    else:
        train["c2"] += res["nosr"]

    # Save cancellation
    passengers = [Passenger(**p) for p in res["passengers"]]
    cancel_entry = Cancellation(
        pnr, res["tno"], res["tname"], res["bp"],
        res["dest"], passengers, res["clas"], res["nosr"],
        cancel_date.isoformat(), amr
    ).to_dict()

    cancels = load_json(CANCELLATIONS_FILE, [])
    cancels.append(cancel_entry)

    save_json(CANCELLATIONS_FILE, cancels)

    # Remove reservation
    reservations = [r for r in reservations if r["pnr"] != pnr]
    save_json(RESERVATIONS_FILE, reservations)

    # Update train seats
    save_json(TRAINS_FILE, trains)

    print("Ticket cancelled. Refund:", amr)


# -------------------- Admin Reports --------------------

def admin_reports():
    reservations = load_json(RESERVATIONS_FILE, [])
    if not reservations:
        print("No reservations.")
        return

    total = sum(r["amc"] for r in reservations)
    print("\n--- ADMIN REPORTS ---")
    print("Total Reservations:", len(reservations))
    print("Total Revenue:", total)

    per_train = {}
    for r in reservations:
        key = f"{r['tno']} {r['tname']}"
        per_train.setdefault(key, 0)
        per_train[key] += r["amc"]

    print("\nRevenue Per Train:")
    for k, v in per_train.items():
        print(k, ":", v)


# -------------------- User Mode --------------------

def user_mode():
    uid = input("User ID: ")
    pw = input("Password: ")

    users = load_json(USERS_FILE, [])
    ok = any(u["user_id"] == uid and u["password"] == pw for u in users)

    if not ok:
        print("Invalid credentials.")
        return

    while True:
        print("\n--- USER MENU ---")
        print("1. Search & Reserve")
        print("2. Cancel Ticket")
        print("3. PNR Status")
        print("4. Enquiry")
        print("5. Back")
        ch = input("Choice: ")

        if ch == "1":
            do_reservation()
        elif ch == "2":
            cancel_ticket()
        elif ch == "3":
            show_pnr_status()
        elif ch == "4":
            display_trains_pattern()
        elif ch == "5":
            return
        else:
            print("Invalid.")


# -------------------- Admin Mode --------------------

def admin_mode():
    pw = input("Admin Password: ")
    if pw != ADMIN_PASSWORD:
        print("Wrong password.")
        return

    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Create Train DB")
        print("2. Add Train")
        print("3. Display Trains")
        print("4. Update Train")
        print("5. Delete Train")
        print("6. Manage Users")
        print("7. Reports")
        print("8. Back")
        ch = input("Choice: ")

        if ch == "1":
            create_or_add_train(True)
        elif ch == "2":
            create_or_add_train(False)
        elif ch == "3":
            display_trains_pattern()
        elif ch == "4":
            update_train()
        elif ch == "5":
            delete_train()
        elif ch == "6":
            manage_users()
        elif ch == "7":
            admin_reports()
        elif ch == "8":
            return
        else:
            print("Invalid choice.")


# -------------------- Main Menu --------------------

def main():
    print("=== RAILWAY RESERVATION SYSTEM (Python) ===")

    while True:
        print("\nMAIN MENU")
        print("1. Admin Mode")
        print("2. User Mode")
        print("3. PNR Status")
        print("4. Exit")

        ch = input("Choice: ")

        if ch == "1":
            admin_mode()
        elif ch == "2":
            user_mode()
        elif ch == "3":
            show_pnr_status()
        elif ch == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()

