# init_db.py

import sqlite3

def init_db():
    con = sqlite3.connect('instance/parking.db')
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            email TEXT UNIQUE NOT NULL,
            passwd TEXT NOT NULL,
            no_spots_booked INTEGER DEFAULT 0
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_number TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ParkingLots (
            lot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            pin_code TEXT,
            price_per_hour REAL NOT NULL,
            max_spots INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            free_spots INTEGER NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ParkingSpots (
            spot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'
                CHECK(status IN ('Available','Occupied','OutOfService')),
            FOREIGN KEY(lot_id) REFERENCES ParkingLots(lot_id) ON DELETE CASCADE
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            status TEXT NOT NULL DEFAULT 'Booked'
                CHECK(status IN ('Booked','Completed','Cancelled')),
            duration_hours FLOAT DEFAULT NULL,
            total_amount FLOAT DEFAULT NULL,
            FOREIGN KEY(spot_id) REFERENCES ParkingSpots(spot_id) ON DELETE CASCADE,
            FOREIGN KEY(vehicle_id) REFERENCES Vehicles(vehicle_id) ON DELETE CASCADE
        );
    ''')

    print("Database initialized successfully.")
    con.commit()
    con.close()

if __name__ == '__main__':
    init_db()
