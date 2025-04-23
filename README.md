<p align="center">
  <img src="https://github.com/user-attachments/assets/25d0cfd8-ccf0-441b-9a4c-2f4aef45b861" alt="Fire Detection Circuit Diagram" height="320"/>
</p>

<h1 align="center">Fire Detection System using NodeMCU (ESP8266) & Multiple Sensors</h1>

<p align="center">Real-time fire, smoke, gas, temperature & humidity monitoring with instant alerts via WebSocket & FastAPI.</p>

## 📝 Table of Contents

1. [Project Overview](#-project-overview)  
2. [Sensors & Components Used](#-sensors--components-used)  
3. [Fire-Alert Logic](#-fire-alert-logic)  
4. [Real-Time Communication via WebSocket](#-real-time-communication-via-websocket)  
5. [System Architecture](#-system-architecture)  
6. [Hardware Setup Guide](#-hardware-setup-guide)  
7. [Backend (FastAPI) Overview](#-backend-fastapi-overview)  
8. [ESP8266 Firmware Code](#-esp8266-firmware-code)  
9. [Frontend Dashboard](#-frontend-dashboard)  
10. [Repository Structure](#-repository-structure)  
11. [License](#-license)  
12. [Contact](#-contact)  

---

## 1. 🔥 Project Overview

A modular **Fire Detection System** built on the ESP8266 (NodeMCU) that continuously monitors:

- **Temperature & Humidity** via DHT11  
- **Smoke/Gas** via MQ2  
- **Direct Flame** via Flame Sensor  

Sensor data is streamed in real-time over WebSocket to a FastAPI backend, which:

- Applies inline threshold logic in firmware and server  
- Triggers an alert page when fire conditions are met  
- Serves a live dashboard for monitoring  

---

## 2. 🌡️ Sensors & Components Used

| Component            | Quantity | Description                                    |
|----------------------|:--------:|------------------------------------------------|
| **NodeMCU ESP8266**  |    1     | MCU + WiFi module                              |
| **DHT11**            |    1     | Temperature & humidity sensor                  |
| **MQ2 Gas Sensor**   |    1     | Smoke/gas analog detection (LPG, smoke, CH₄…)  |
| **Flame Sensor**     |    1     | IR‐based flame detection                       |
| **Jumper Wires**     |    –     | For breadboard connections                     |
| **Breadboard**       |    1     | Prototyping platform                           |
| **USB Cable / 5 V**  |    1     | Power supply                                   |

---

## 3. 🧠 Fire-Alert Logic

The fire-alert logic is implemented directly in both the ESP8266 firmware and interpreted by the FastAPI backend.The thresholds are defined inline:

### In ESP8266 (NodeMCUCode.ino)
```cpp
bool temp_high    = temperature > 45.0;
bool smoke_high   = smoke_level > 400;
bool flame_detected = digitalRead(FLAME_SENSOR_PIN) == LOW;
bool fire_detected  = flame_detected || (smoke_high && temp_high);
```

### In FastAPI (main.py)
```python
# sensor reading arrives with "fire_detected" boolean
reading = SensorReading(**data)
if reading.fire_detected:
    # serve fire_alert.html
```

Whenever `fire_detected` is true, the backend’s `/fire-alert` endpoint returns the alert template.

---

## 4. 📡 Real-Time Communication via WebSocket

- **Endpoint**: `ws://<SERVER_IP>:8000/ws`  
- **Payload** (JSON):
  ```json
  {
    "temperature": 52.3,
    "humidity": 43.1,
    "smoke_level": 350,
    "flame_detected": 1,
    "fire_detected": 1,
    "latitude": 19.2436,
    "longitude": 72.8558,
    "timestamp": "2025-04-23 14:12:07"
  }
  ```
- **FastAPI** validates via Pydantic, stores last 100 readings, broadcasts to dashboard clients.

---

## 5. 🏗️ System Architecture

<p align="center">
  <img src="https://github.com/user-attachments/assets/e9c48bdd-d80f-437c-bd2a-dbca3756224a" alt="Fire Detection Circuit Diagram"/>
</p>

---

## 6. ⚙️ Hardware Setup Guide

### 🔌 DHT11 Sensor Connections
| Pin Name | Connects To    |
|----------|----------------|
| VCC      | NodeMCU 3.3V   |
| GND      | NodeMCU GND    |
| DATA     | NodeMCU D4     |

### 🔌 MQ2 Gas Sensor Connections
| Pin Name | Connects To    |
|----------|----------------|
| VCC      | NodeMCU 5V     |
| GND      | NodeMCU GND    |
| A0       | NodeMCU A0     |

### 🔌 Flame Sensor Connections
| Pin Name | Connects To    |
|----------|----------------|
| VCC      | NodeMCU 3.3V   |
| GND      | NodeMCU GND    |
| D0       | NodeMCU D0     |

### 🔌 NodeMCU Power Supply
| Description   | Connection         |
|---------------|--------------------|
| Power Source  | USB (to PC or 5V)  |

---

## 7. 🧪 Backend (FastAPI) Overview

```bash
# Clone & activate
git clone https://github.com/VishalRMahajan/Fire-Detection-Using-Sensor.git
cd Fire-Detection-Using-Sensor
python -m venv venv
.\venv\Scripts\activate

# Install
pip install -r requirements.txt
```

**Run server**  
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- **GET /** → Dashboard (`dashboard.html`)  
- **GET /fire-alert** → Alert component (`fire_alert.html`)  
- **GET /sensor-history** → JSON list of last 100 readings  
- **GET /current-status** → Most recent reading  

---

## 8. 📟 ESP8266 Firmware Code

This section highlights the key configuration inside `NodeMCUCode/NodeMCUCode.ino` that powers the ESP8266-based fire detection system.

> 📦 **Required Libraries (install in Arduino IDE):**
> - `ESP8266WiFi.h`
> - `WebSocketsClient.h`
> - `DHT.h`
> - `ArduinoJson.h`

```cpp
// Wi-Fi credentials
const char* ssid = "<Your-WiFi-SSID>";
const char* password = "<Your-WiFi-Password>";

// WebSocket server details
const char* websocket_host = "<FastAPI-IP-Address>"; // Replace with IP of the FastAPI backend server
const uint16_t websocket_port = 8000;
const char* websocket_path = "/ws";

// Location
const float latitude = <lon>;
const float longitude = <lat>;

// Fire Detection Logic
bool temp_high = temperature > 45.0;
bool smoke_high = smoke_level > 400;
bool flame_detected = digitalRead(FLAME_SENSOR_PIN) == LOW;
bool fire_detected = flame_detected || (smoke_high && temp_high);
```

> 💡 Ensure the backend (FastAPI server) and NodeMCU are connected to the same Wi-Fi network.


---

## 9. 🖥️ Frontend Dashboard

- `templates/dashboard.html`: live-updating values via JS WebSocket client  
- `templates/fire_alert.html`: full-screen alert component  
- Styles in `static/styles.css`

---

## 10. 📁 Repository Structure

```
.
├── NodeMCUCode
│   └── NodeMCUCode.ino
├── static
│   └── styles.css
├── templates
│   ├── dashboard.html
│   └── fire_alert.html
├── .gitignore
├── main.py
└── requirements.txt
```

---

## 11. 📜 License

Released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 12. 📫 Contact

Developed by **Vishal Rajesh Mahajan**  
✉️ vism06@gmail.com  
🌎 [vishalrmahajan.in](https://vishalrmahajan.in)
