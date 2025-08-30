import tkinter as tk
from tkinter import messagebox
import serial
import time
import pickle
import pandas as pd
import requests
import base64

# === CONFIGURATION ===
COM_PORT = 'COM6'  # Replace with your ESP32 COM port
BAUD_RATE = 115200

# Twilio credentials
account_sid = "your acc sid"
auth_token = "your auth token"
twilio_number = "your twilio number"
destination_number = "your number"

# Internal flags
sms_sent = False

# === Load AI Model ===
try:
    model = pickle.load(open("flood_model.pkl", "rb"))
    ai_model = True
except:
    ai_model = False
    print("⚠️ AI model not found. Dashboard will run without predictions.")

# === Connect to ESP32 Serial ===
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
    time.sleep(2)
except:
    messagebox.showerror("Error", f"Could not open port {COM_PORT}")
    exit()

# === Tkinter GUI Setup ===
root = tk.Tk()
root.title("🌊 Real-Time Flood Detection Dashboard")
root.geometry("420x320")

lbl_humidity = tk.Label(root, text="Humidity: -- %", font=("Arial", 12))
lbl_humidity.pack(pady=5)

lbl_distance = tk.Label(root, text="Distance: -- cm", font=("Arial", 12))
lbl_distance.pack(pady=5)

lbl_water = tk.Label(root, text="Water Level: --", font=("Arial", 12))
lbl_water.pack(pady=5)

lbl_status = tk.Label(root, text="Status: Waiting for data...", fg="blue", font=("Arial", 14, "bold"))
lbl_status.pack(pady=15)

# === Function to Send SMS Alert ===
def send_sms_alert(msg):
    global sms_sent
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        data = {
            "To": destination_number,
            "From": twilio_number,
            "Body": msg
        }
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
        }
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 201:
            print("📩 SMS Alert Sent Successfully!")
            sms_sent = True
        else:
            print("❌ SMS Failed:", response.text)
    except Exception as e:
        print("❌ Error sending SMS:", e)

# === Function to Fetch and Display Serial Data ===
def fetch_data():
    global sms_sent
    try:
        line = ser.readline().decode().strip()
        print("Serial:", line)

        if line.startswith("Humidity:"):
            parts = line.split(',')
            humidity = float(parts[0].split(':')[1])
            distance = float(parts[1].split(':')[1])
            water = float(parts[2].split(':')[1])

            # Update GUI
            lbl_humidity.config(text=f"Humidity: {humidity:.2f} %")
            lbl_distance.config(text=f"Distance: {distance:.2f} cm")
            lbl_water.config(text=f"Water Level: {water}")

            flood = False
            if ai_model:
                df = pd.DataFrame([[humidity, distance, water]], columns=['humidity', 'distance', 'water'])
                prediction = model.predict(df)[0]
                flood = prediction == 1

            # 🚨 Flood Risk Logic
            if flood or distance < 20.00:
                lbl_status.config(text="🚨 FLOOD RISK DETECTED!", fg="red")
                if not sms_sent:
                    alert_msg = f"🚨 Flood Alert!\nReason: {'AI Prediction' if flood else 'AI Flood Prediction'}\nHumidity: {humidity}%\nDistance: {distance:.2f} cm\nWater Level: {water}"
                    send_sms_alert(alert_msg)
            else:
                lbl_status.config(text="✅ Safe Conditions", fg="green")
                sms_sent = False  # Reset flag when safe

    except Exception as e:
        print("❌ Error reading data:", e)

    root.after(3000, fetch_data)  # Check every 3 seconds

# Start reading sensor data
fetch_data()

# Launch the GUI window
root.mainloop()
