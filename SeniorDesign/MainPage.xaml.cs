using Microcharts;
using Microcharts.Maui;
using SkiaSharp;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace SeniorDesign;

public partial class MainPage : ContentPage
{
    private readonly DatabaseService _db;

    public MainPage(DatabaseService db)
    {
        InitializeComponent();
        _db = db;
        _db.DataUpdated += OnDataUpdated;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await LoadChartsAsync();
    }

    private async Task LoadChartsAsync()
    {
        try
        {
            // ✅ Fetch latest data from FastAPI server
            var sensorData = await _db.GetDataAsync();

            if (sensorData == null || sensorData.Count == 0)
            {
                await DisplayAlert("No Data", "No sensor data available. Please ensure the server is running and data has been uploaded.", "OK");
                return;
            }

            // ✅ Chart 1: Hand Shakiness (using accelerometer magnitude)
            Graph1.Chart = new LineChart
            {
                Entries = GenerateShakinessData(sensorData),
                LineMode = LineMode.Straight,
                LineSize = 4,
                PointMode = PointMode.Circle,
                PointSize = 5,
                LabelTextSize = 18,
                BackgroundColor = SKColor.Parse("#FAFAFA"), // Light accessible background
                LabelColor = SKColor.Parse("#212121"),       // Dark text
                LabelOrientation = Orientation.Horizontal,
                ValueLabelOrientation = Orientation.Horizontal
            };

            // ✅ Chart 2: Temperature
            Graph2.Chart = new LineChart
            {
                Entries = GenerateTemperatureData(sensorData),
                LineMode = LineMode.Straight,
                LineSize = 4,
                PointMode = PointMode.Circle,
                PointSize = 5,
                LabelTextSize = 18,
                BackgroundColor = SKColor.Parse("#FAFAFA"),
                LabelColor = SKColor.Parse("#212121"),
                LabelOrientation = Orientation.Horizontal,
                ValueLabelOrientation = Orientation.Horizontal
            };
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", $"Failed to load data: {ex.Message}", "OK");
        }
    }

    // ✅ Tap Handlers
    private async void OnShakinessTapped(object sender, EventArgs e)
    {
        var sensorData = await _db.GetDataAsync();
        await Navigation.PushAsync(new GraphDetailPage(
            "Hand Shakiness Over Time",
            GenerateShakinessData(sensorData)
        ));
    }

    private async void OnTemperatureTapped(object sender, EventArgs e)
    {
        var sensorData = await _db.GetDataAsync();
        await Navigation.PushAsync(new GraphDetailPage(
            "Hand Temperature Over Time",
            GenerateTemperatureData(sensorData)
        ));
    }

    // ✅ Chart Data Generation
    private ChartEntry[] GenerateShakinessData(List<SensorData> data)
    {
        // Compute magnitude if accel components exist
        return data.Select(d =>
        {
            float magnitude = (float)Math.Sqrt(
                Math.Pow(d.AccelX, 2) +
                Math.Pow(d.AccelY, 2) +
                Math.Pow(d.AccelZ, 2)
            );

            return new ChartEntry(magnitude)
            {
                Label = d.Timestamp,
                ValueLabel = magnitude.ToString("0.00"),
                Color = SKColor.Parse("#1565C0"), // Primary Blue
                TextColor = SKColor.Parse("#212121")
            };
        }).ToArray();
    }

    private ChartEntry[] GenerateTemperatureData(List<SensorData> data)
    {
        return data.Select(d => new ChartEntry(d.Temperature)
        {
            Label = d.Timestamp,
            ValueLabel = d.Temperature.ToString("0.0"),
            Color = SKColor.Parse("#1E88E5"), // Secondary Blue
            TextColor = SKColor.Parse("#212121")
        }).ToArray();
    }
    private async void OnDataUpdated(List<SensorData> data)
    {
        await MainThread.InvokeOnMainThreadAsync(() =>
        {
            Graph1.Chart = new LineChart
            {
                Entries = GenerateShakinessData(data),
                LineMode = LineMode.Straight,
                LineSize = 4,
                PointMode = PointMode.Circle,
                PointSize = 5,
                LabelTextSize = 18,
                BackgroundColor = SKColor.Parse("#FAFAFA"),
                LabelColor = SKColor.Parse("#212121"),
                LabelOrientation = Orientation.Horizontal,
                ValueLabelOrientation = Orientation.Horizontal
            };

            Graph2.Chart = new LineChart
            {
                Entries = GenerateTemperatureData(data),
                LineMode = LineMode.Straight,
                LineSize = 4,
                PointMode = PointMode.Circle,
                PointSize = 5,
                LabelTextSize = 18,
                BackgroundColor = SKColor.Parse("#FAFAFA"),
                LabelColor = SKColor.Parse("#212121"),
                LabelOrientation = Orientation.Horizontal,
                ValueLabelOrientation = Orientation.Horizontal
            };
        });
    }

}
