import mysql.connector
from mysql.connector import Error
import time


class MiniParkingSystem:
    def __init__(self, max_retries=3, retry_delay=2):
        self.connection_params = {
            'host': 'nozomi.proxy.rlwy.net',
            'port': 40881,
            'user': 'root',
            'password': 'MmURHRpxRMQkrEqmeqKLJIVbWxPHUrjU',
            'database': 'railway'
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.conn = None
        self._connect_with_retry()

    def _connect_with_retry(self):
        """Attempt connection with retries"""
        for attempt in range(self.max_retries):
            try:
                self.conn = mysql.connector.connect(**self.connection_params)
                print("MySQL connection established successfully")
                return
            except Error as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise ConnectionError(f"Failed to connect after {self.max_retries} attempts")

    def _execute_query(self, query, params=None, fetch=False):
        """Generic query executor with retry logic"""
        cursor = None
        try:
            if not self.conn or not self.conn.is_connected():
                self._connect_with_retry()

            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                self.conn.commit()
                return result
            else:
                self.conn.commit()
                return cursor.lastrowid if cursor.lastrowid else True

        except Error as e:
            self.conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if cursor: cursor.close()

    def add_city(self, name):
        # Check if city already exists
        result = self._execute_query(
            "SELECT city_id FROM cities WHERE name = %s",
            (name,),
            fetch=True
        )
        if result:
            print(f"City '{name}' already exists with ID: {result[0]['city_id']}")
            return result[0]['city_id']  # Return existing city_id

        # Insert if not found
        return self._execute_query(
            "INSERT INTO cities (name) VALUES (%s)",
            (name,)
        )

    def add_lot(self, city_id, name, capacity):
        result = self._execute_query(
            "SELECT lot_id FROM parking_lots WHERE city_id = %s AND name = %s",
            (city_id, name),
            fetch=True
        )
        if result:
            print(f"Lot '{name}' already exists in city ID {city_id} with ID: {result[0]['lot_id']}")
            return result[0]['lot_id']

        return self._execute_query(
            "INSERT INTO parking_lots (city_id, name, capacity) VALUES (%s, %s, %s)",
            (city_id, name, capacity)
        )

    def add_slots(self, lot_id, count):
        """Add multiple slots to a parking lot"""
        try:
            for i in range(1, count + 1):
                self._execute_query(
                    "INSERT INTO slots (lot_id, slot_number) VALUES (%s, %s)",
                    (lot_id, f"SL-{i:03d}")
                )
            return True
        except Error as e:
            print(f"Error adding slots: {e}")
            raise

    def add_slots(self, lot_id, count):
        try:
            existing_slots = self._execute_query(
                "SELECT slot_number FROM slots WHERE lot_id = %s",
                (lot_id,),
                fetch=True
            )
            existing_slot_numbers = {s['slot_number'] for s in existing_slots}

            for i in range(1, count + 1):
                slot_number = f"SL-{i:03d}"
                if slot_number in existing_slot_numbers:
                    print(f"Slot {slot_number} already exists. Skipping.")
                    continue

                self._execute_query(
                    "INSERT INTO slots (lot_id, slot_number) VALUES (%s, %s)",
                    (lot_id, slot_number)
                )
            return True
        except Error as e:
            print(f"Error adding slots: {e}")
            raise

    def get_available_slots(self, lot_id):
        return self._execute_query(
            "SELECT * FROM slots WHERE lot_id = %s AND is_occupied = FALSE",
            (lot_id,),
            fetch=True
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn and self.conn.is_connected():
            self.conn.close()


# Test with context manager
if __name__ == "__main__":
    try:
        with MiniParkingSystem() as system:
            # Create sample data
            city_id = system.add_city("Kamsar")
            print(f"Created city ID: {city_id}")

            lot_id = system.add_lot(city_id, "Marché Kausa", 50)
            print(f"Created lot ID: {lot_id}")

            system.add_slots(lot_id, 5)

            # Test slot operations
            slots = system.get_available_slots(lot_id)
            print(f"Available slots: {len(slots)}")

            if slots:
                system.occupy_slot(slots[0]['slot_id'])
                print(f"Occupied slot {slots[0]['slot_number']}")

            updated_slots = system.get_available_slots(lot_id)
            print(f"Now available: {len(updated_slots)}")

    except Exception as e:
        print(f"Application error: {e}")