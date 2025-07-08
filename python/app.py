# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from parking_core import MiniParkingSystem
# import json
# import mysql.connector
#
# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend integration
#
# # Initialize the parking system
# try:
#     parking_system = MiniParkingSystem()
#     print("Parking system initialized successfully")
# except Exception as e:
#     print(f"Failed to initialize parking system: {e}")
#     parking_system = None
# print("Parking system initialized")
#
# @app.route('/')
# def home():
#     return jsonify({
#         "message": "Parking Management System API",
#         "version": "1.0",
#         "endpoints": {
#             "cities": "/api/cities",
#             "lots": "/api/lots",
#             "slots": "/api/slots",
#             "occupy": "/api/slots/<slot_id>/occupy",
#             "free": "/api/slots/<slot_id>/free"
#         }
#     })
#
# # Cities endpoints
# @app.route('/api/cities', methods=['GET'])
# def get_cities():
#     try:
#         cursor = parking_system.conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM cities")
#         cities = cursor.fetchall()
#         return jsonify({"cities": cities})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/api/cities', methods=['POST'])
# def add_city():
#     try:
#         if not parking_system:
#             return jsonify({"error": "Database connection not available"}), 500
#
#         data = request.get_json()
#         name = data.get('name')
#         if not name:
#             return jsonify({"error": "City name is required"}), 400
#
#         city_id = parking_system.add_city(name)
#         return jsonify({"message": "City added successfully", "city_id": city_id}), 201
#     except Exception as e:
#         print(f"Error adding city: {e}")
#         return jsonify({"error": "MySQL Connection not available"}), 500
#
# # Parking lots endpoints
# @app.route('/api/lots', methods=['GET'])
# def get_lots():
#     try:
#         cursor = parking_system.conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT pl.*, c.name as city_name
#             FROM parking_lots pl
#             JOIN cities c ON pl.city_id = c.city_id
#         """)
#         lots = cursor.fetchall()
#         return jsonify({"lots": lots})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/api/lots', methods=['POST'])
# def add_lot():
#     try:
#         data = request.get_json()
#         city_id = data.get('city_id')
#         name = data.get('name')
#         capacity = data.get('capacity')
#
#         if not all([city_id, name, capacity]):
#             return jsonify({"error": "city_id, name, and capacity are required"}), 400
#
#         lot_id = parking_system.add_lot(city_id, name, capacity)
#         return jsonify({"message": "Parking lot added successfully", "lot_id": lot_id}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # Slots endpoints
# @app.route('/api/slots', methods=['GET'])
# def get_slots():
#     try:
#         lot_id = request.args.get('lot_id')
#         cursor = parking_system.conn.cursor(dictionary=True)
#
#         if lot_id:
#             cursor.execute("""
#                 SELECT s.*, pl.name as lot_name
#                 FROM slots s
#                 JOIN parking_lots pl ON s.lot_id = pl.lot_id
#                 WHERE s.lot_id = %s
#             """, (lot_id,))
#         else:
#             cursor.execute("""
#                 SELECT s.*, pl.name as lot_name
#                 FROM slots s
#                 JOIN parking_lots pl ON s.lot_id = pl.lot_id
#             """)
#
#         slots = cursor.fetchall()
#         return jsonify({"slots": slots})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/api/slots/<int:slot_id>/occupy', methods=['PUT'])
# def occupy_slot(slot_id):
#     try:
#         parking_system.occupy_slot(slot_id)
#         return jsonify({"message": f"Slot {slot_id} occupied successfully"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/api/slots/<int:slot_id>/free', methods=['PUT'])
# def free_slot(slot_id):
#     try:
#         cursor = parking_system.conn.cursor()
#         cursor.execute("""
#             UPDATE slots SET is_occupied = FALSE
#             WHERE slot_id = %s
#         """, (slot_id,))
#         parking_system.conn.commit()
#         return jsonify({"message": f"Slot {slot_id} freed successfully"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/api/slots/available', methods=['GET'])
# def get_available_slots():
#     try:
#         lot_id = request.args.get('lot_id')
#         if lot_id:
#             slots = parking_system.get_available_slots(int(lot_id))
#         else:
#             cursor = parking_system.conn.cursor(dictionary=True)
#             cursor.execute("SELECT * FROM slots WHERE is_occupied = FALSE")
#             slots = cursor.fetchall()
#
#         return jsonify({"available_slots": slots})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5002)





















from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
from parking_core import MiniParkingSystem

# Définir le bon dossier des templates (frontend)
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, template_folder=template_dir)

# Page d'accueil → redirige vers utilisateur
@app.route('/')
def landing_page():
    return redirect(url_for('user_page'))

# Page admin
@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/add-city', methods=['POST'])
def add_city():
    city_name = request.form['city_name']
    with MiniParkingSystem() as system:
        city_id = system.add_city(city_name)
    return redirect(url_for('admin_page'))

# Page utilisateur
@app.route('/user')
def user_page():
    with MiniParkingSystem() as system:
        cities = system._execute_query("SELECT * FROM cities", fetch=True)
    return render_template('user.html', cities=cities)

# Récupérer les parkings d'une ville (format JSON pour JavaScript)
@app.route('/get-parking/<int:city_id>')
def get_parking(city_id):
    with MiniParkingSystem() as system:
        lots = system._execute_query("SELECT * FROM parking_lots WHERE city_id = %s", (city_id,), fetch=True)
    return jsonify(lots)

# Voir les slots disponibles dans un parking
@app.route('/get-slots/<int:lot_id>')
def get_slots(lot_id):
    with MiniParkingSystem() as system:
        slots = system.get_available_slots(lot_id)
    return render_template('reserve.html', slots=slots)

if __name__ == '__main__':
    app.run(debug=True)