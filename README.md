
#  SteadyHand — Senior Design 2025

**Team 16 – Purdue University ECE Senior Design**
**Members:** Anna Babus, Noah Bonahoom, Emma Tarrence, Jason Reust, Jordan Weiler
**Advisors:** Professor Qi Minghao, GTA: Manu Ramesh
**Date:** Fall 2025

---

##  Overview

**SteadyHand** is a **self-stabilizing assistive utensil** designed to help individuals with hand tremors eat with greater independence and confidence. Using an **ESP32 microcontroller**, **sensors**, and **servo-controlled stabilization**, the utensil compensates for small, involuntary tremors in real time.

The system also collects **accelerometer, gyroscope, and temperature data**, which are sent via **WiFi** to a **database and web application** for visualization and long-term analysis. This data can provide users and caregivers with valuable insights into tremor intensity and health patterns over time.

---

##  Repository Structure

SteadyHand---Senior-Design-2025/
│
│   .gitattributes
│   .gitignore
│   README.md
│   SeniorDesign.sln
│   steadyHand.db
│
├───Database/                     # Database logic and storage
│       database.py
│
├───Embedded/                     # ESP32 firmware and scripts
│       gptPID.py
│       main.py
│       switchpress.py
│       README.md
│
└───SeniorDesign/                 # .NET MAUI application
    │   App.xaml
    │   App.xaml.cs
    │   AppShell.xaml
    │   AppShell.xaml.cs
    │   DatabaseService.cs
    │   GlobalXmlns.cs
    │   GraphDetailPage.xaml
    │   GraphDetailPage.xaml.cs
    │   MainPage.xaml
    │   MainPage.xaml.cs
    │   MauiProgram.cs
    │   SeniorDesign.csproj
    │
    ├───Platforms/                # Platform-specific code
    │   ├───Android/
    │   │   │   AndroidManifest.xml
    │   │   │   MainActivity.cs
    │   │   │   MainApplication.cs
    │   │   │
    │   │   └───Resources/
    │   │           values/colors.xml
    │   │
    │   ├───iOS/
    │   │   │   AppDelegate.cs
    │   │   │   Info.plist
    │   │   │   Program.cs
    │   │   │
    │   │   └───Resources/
    │   │           PrivacyInfo.xcprivacy
    │   │
    │   ├───MacCatalyst/
    │   │       AppDelegate.cs
    │   │       Entitlements.plist
    │   │       Info.plist
    │   │       Program.cs
    │   │
    │   ├───Tizen/
    │   │       Main.cs
    │   │       tizen-manifest.xml
    │   │
    │   └───Windows/
    │           app.manifest
    │           App.xaml
    │           App.xaml.cs
    │           Package.appxmanifest
    │
    ├───Properties/
    │       launchSettings.json
    │
    └───Resources/                # App assets and UI resources
        ├───AppIcon/
        │       appicon.svg
        │       appiconfg.svg
        │
        ├───Fonts/
        │       OpenSans-Regular.ttf
        │       OpenSans-Semibold.ttf
        │
        ├───Images/
        │       dotnet_bot.png
        │
        ├───Raw/
        │       AboutAssets.txt
        │
        ├───Splash/
        │       splash.svg
        │
        └───Styles/
                Colors.xaml
                Styles.xaml

##  System Architecture

```
[Accelerometer/Gyroscope] ─► [ESP32 Microcontroller] ─► [WiFi Transmission]
                                                               │
                                                               ▼
                                                        [SQLite Database]
                                                               │
                                                               ▼
                                                        [Web App Dashboard]
```

1. The **ESP32** reads sensor data, applies a **Kalman filter** and **PID control**, and stabilizes the utensil via servos.
2. Processed tremor and temperature data are sent as **JSON packets** to the **SQLite database**.
3. The **.NET MAUI web app** visualizes this data with graphs, CSV export, and historical summaries.

---

##  Core Algorithms

###  Kalman Filter

Used on the ESP32 to smooth noisy accelerometer and gyroscope readings, providing accurate estimates of utensil tilt and motion.

###  PID Controller

Computes servo angle corrections in real time to counteract tremors, keeping the utensil head stable.

###  Database Averaging Algorithm

Condenses raw 50 Hz sensor data into averaged summaries after one week, allowing three months of efficient historical storage.

###  Data Flow Summary

1. ESP32 reads IMU and temperature data.
2. Kalman filter processes readings → PID computes motor output.
3. JSON packets (timestamp, filtered acceleration, temperature) sent to database.
4. Web app queries database → graphs acceleration and temperature over time.

---

##  Web Application

**Location:** `/SeniorDesign`
**Framework:** .NET MAUI
**Features:**

* Real-time tremor and temperature graphs
* Clickable data points and CSV export
* Accessibility support (WCAG 2.1 AA, scalable font sizes)
* New data detection to minimize redundant queries

---

##  Database Subsystem

**Location:** `/Database`
**Type:** SQLite
**Functions:**

* Stores timestamped sensor readings at 50 Hz
* Rolls over after one week
* Archives condensed data (minute averages)
* Exports datasets as CSV

---

##  Embedded System

**Location:** `/Embedded`
**Microcontroller:** ESP32 Feather V2
**Functions:**

* Reads MPU-6050 (accelerometer/gyroscope) and DS18B20 (temperature sensor)
* Runs Kalman filter and PID loop for motor stabilization
* Sends data to database over WiFi (IEEE 802.11)
* Controls three MG90D/MG92B servos for utensil motion

---

##  Design Subsystems (from Design Document 2)

| Subsystem             | Owner         | Description                                                     |
| --------------------- | ------------- | --------------------------------------------------------------- |
| **Power & Bluetooth** | Anna Babus    | Wireless Qi charging and power regulation (MCP73812, TPS61022). |
| **App & Database**    | Emma Tarrence | .NET MAUI front-end and SQLite backend for data visualization.  |
| **Motor & Sensors**   | Jason Reust   | Controls servo movement based on IMU input.                     |
| **Sensors & WiFi**    | Jordan Weiler | Manages sensor data acquisition and WiFi communication.         |
| **Embedded Software** | Noah Bonahoom | Implements Kalman + PID algorithms and core logic.              |

---

##  Getting Started

### Requirements

* Visual Studio with .NET MAUI workload
* STM32CubeIDE or PlatformIO (for firmware)
* SQLite installed or included
* ESP32 Feather V2 + sensors and servos

### Run Instructions

####  Embedded

1. Flash firmware from `/Embedded` to the ESP32.
2. Configure WiFi credentials in `config.h`.
3. Power device and confirm data packets are sent to the database.

####  Database

```bash
cd Database
python data_handler.py
```

####  Web App

```bash
cd SeniorDesign
dotnet build
dotnet run
```

Then open the web app locally or on your configured host (e.g., AWS Free Tier).

---

## Example Workflow

1. User powers on utensil → device self-centers.
2. Sensors capture tremor and temperature data.
3. ESP32 filters and transmits JSON packets to database.
4. Web app displays live graphs of shakiness and temperature.
5. Data archived weekly, exportable as CSV.

---

##  Standards Followed

* **IEEE 802.11** – WiFi communication
* **IEEE 2686** – Rechargeable battery safety
* **IEEE 11073 / 11073-10101** – Medical data formatting
* **WCAG 2.1 AA** – Accessibility for all users
* **RFC 4180** – CSV export compatibility

---

## Team Contacts

| Name          | Role                            | Email                                             |
| ------------- | ------------------------------- | ------------------------------------------------- |
| Anna Babus    | Team Lead / Power & Bluetooth   | [ababus@purdue.edu](mailto:ababus@purdue.edu)     |
| Jason Reust   | Motor & Sensor Implementation   | [reustj@purdue.edu](mailto:reustj@purdue.edu)     |
| Noah Bonahoom | Embedded Software / Facilitator | [nbonahoo@purdue.edu](mailto:nbonahoo@purdue.edu) |
| Emma Tarrence | App & Database / Communicator   | [etarrenc@purdue.edu](mailto:etarrenc@purdue.edu) |
| Jordan Weiler | WiFi Integration / Budgeter     | [weiler7@purdue.edu](mailto:weiler7@purdue.edu)   |


