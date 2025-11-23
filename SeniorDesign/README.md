# SteadyHand MAUI App

Cross-platform .NET MAUI application for the SteadyHand Senior Design Project.  
Displays real-time sensor data from the SteadyHand Server, shows graphs, supports accessibility text scaling, and allows detailed data inspection.

This app is intended for **Senior Design use** and runs primarily on **Windows**.

---

## Overview

The SteadyHand MAUI application is the user-facing interface for the SteadyHand system.  
It pulls accelerometer data from the backend server, renders graphs, supports larger text for accessibility, and allows the user to view detailed IMU data for a given session.

### Current features include:

- Fetches data from the SteadyHand FastAPI backend  
- Periodic background polling for updates (5-second interval)  
- Displays acceleration graphs (Microcharts + SkiaSharp)  
- Opens a detail view for each axis  
- Text scaling for accessibility (manual user-controlled scaling)  
- Custom converters for UI bindings  
- (Optional) Local TCP listener (NetworkServerService) for debugging IMU output over WiFi  
- MVVM-like structure with clear service separation  

---
# Repository Structure

SeniorDesign/  
│  
├── App.xaml                     (Global app resources)  
├── AppShell.xaml                (Navigation structure)  
│  
├── MainPage.xaml                (Landing page, graph overview)  
├── GraphDetailPage.xaml         (Detailed graph page)  
│  
├── DatabaseService.cs           (HTTP client for backend /data endpoint)  
├── NetworkServerService.cs      (Optional local TCP debug server)  
├── TextSizeService.cs           (Accessibility text scaling)  
├── GlobalXmlns.cs               (XAML namespace mappings)  
│  
├── Multiply.cs                  (Value converter for UI scaling)  
│  
├── MauiProgram.cs               (App startup + dependency registration)  
├── Platforms/                   (Platform-specific configs)  
├── Resources/                   (Images, styles, fonts)  
└── ...  

---

# How the App Works

---

## 1. Data Fetching (DatabaseService)

The app communicates with:

https://steadyhand-server.onrender.com/data

Every **5 seconds**, the `DatabaseService`:

- Sends an HTTP GET to `/data?limit=1000`  
- Parses JSON into `SensorData` objects  
- Checks if the dataset changed  
- Fires `DataUpdated` event so the UI auto-refreshes  

The service uses a single HttpClient and a System.Timers.Timer to avoid threading conflicts.

Data model fields:

- Id  
- Timestamp  
- AccelX  
- AccelY  
- AccelZ  
- Temperature  

---

## 2. Graph Rendering

The app uses **Microcharts + SkiaSharp** to draw axis charts for:

- Acceleration X  
- Acceleration Y  
- Acceleration Z  

The MainPage shows simplified graphs.  
The GraphDetailPage shows a full-size graph with labels, improved scaling, and more precise timestamps.

---

## 3. Navigation

Navigation uses **AppShell.xaml**, enabling:

- MainPage → GraphDetailPage  
- Parameter passing via query strings (axis name, data array, timestamps)

---

## 4. Local Debugging Server (Optional)

`NetworkServerService` is a TCP listener that:

- Listens on port 5000  
- Accepts raw string messages from your ESP32 or debug clients  
- Emits received messages via the `DataReceived` event  

Used only for engineering testing and not required for normal operation.

---

## 5. Accessibility (TextSizeService)

`TextSizeService` adjusts global font sizes based on user-selected scaling:

- Supports slider or button-based scaling  
- All UI elements that bind to text sizes update in real-time  
- Helps meet WCAG readability requirements in Senior Design  

---

# Running the App Locally

These steps assume Windows development via Visual Studio 2022.

---

## 1. Install Requirements

- .NET 9 SDK  
- Visual Studio 2022 with MAUI workload  
- Windows 10 or 11  

---

## 2. Clone Repo

git clone https://github.com/nbonahoo/SteadyHand---Senior-Design-2025  
cd SeniorDesign

---

## 3. Restore & Build

Open the solution in Visual Studio and build normally,  
or use CLI:

dotnet restore  
dotnet build

---

## 4. Run the App

dotnet run -f net9.0-windows10.0.19041.0

---

## 5. Required Backend

The MAUI app expects the FastAPI server located at:

https://steadyhand-server.onrender.com

You may change the API URL in:

DatabaseService.cs  
(ServerUrl constant)

---


# Team & Contact

Developer: Emma Tarrence  
Institution: Purdue University — ECE Senior Design  
Role: MAUI app development  

This MAUI application is part of the SteadyHand Senior Design project for Fall 2024–Spring 2025.
