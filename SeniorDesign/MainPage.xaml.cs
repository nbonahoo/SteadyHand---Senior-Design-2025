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

    // 🔧 Change this number to control how many points are shown
    private const int SimplificationFactor = 10; // e.g., keep 1 in every 10 points

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

    // ✅ Fetch and load data into charts
    private async Task LoadChartsAsync()
    {
        try
        {
            var sensorData = await _db.GetDataAsync();

            if (sensorData == null || sensorData.Count == 0)
            {
                await DisplayAlert("No Data",
                    "No sensor data available. Please ensure the server is running and data has been uploaded.",
                    "OK");
                return;
            }

            // Sort oldest → newest
            sensorData = sensorData.OrderBy(d => d.Timestamp).ToList();

            // Simplify before plotting
            var simplified = SimplifyData(sensorData, SimplificationFactor);

            Graph1.Chart = CreateLineChart(GenerateShakinessData(simplified));
            Graph2.Chart = CreateLineChart(GenerateTemperatureData(simplified));
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", $"Failed to load data: {ex.Message}", "OK");
        }
    }

    // ✅ Reduce dataset by taking every Nth point
    private List<SensorData> SimplifyData(List<SensorData> data, int step)
    {
        if (data.Count <= 100) // don’t simplify small datasets
            return data;

        var result = new List<SensorData>();
        for (int i = 0; i < data.Count; i += step)
        {
            result.Add(data[i]);
        }
        return result;
    }

    // ✅ Chart creation helper
    private LineChart CreateLineChart(ChartEntry[] entries) => new()
    {
        Entries = entries,
        LineMode = LineMode.Straight,
        LineSize = 3,
        PointMode = PointMode.Circle,
        PointSize = 5,
        LabelTextSize = 16,
        BackgroundColor = SKColor.Parse("#FAFAFA"),
        LabelColor = SKColor.Parse("#212121"),
        LabelOrientation = Orientation.Horizontal,
        ValueLabelOrientation = Orientation.Horizontal
    };

    // ✅ Hand shakiness chart (acceleration magnitude)
    private ChartEntry[] GenerateShakinessData(List<SensorData> data)
    {
        if (data.Count == 0) return Array.Empty<ChartEntry>();

        data = data.OrderBy(d => d.Timestamp).ToList();
        int labelStep = Math.Max(1, data.Count / 6);

        return data.Select((d, i) =>
        {
            float magnitude = (float)Math.Sqrt(
                Math.Pow(d.AccelX, 2) +
                Math.Pow(d.AccelY, 2) +
                Math.Pow(d.AccelZ, 2)
            );

            string formattedTime = FormatTimestamp(d.Timestamp);

            return new ChartEntry(magnitude)
            {
                Label = (i % labelStep == 0) ? formattedTime : "",
                Color = SKColor.Parse("#1565C0"),
                TextColor = SKColor.Parse("#212121")
            };
        }).ToArray();
    }

    // ✅ Temperature chart
    private ChartEntry[] GenerateTemperatureData(List<SensorData> data)
    {
        if (data.Count == 0) return Array.Empty<ChartEntry>();

        data = data.OrderBy(d => d.Timestamp).ToList();
        int labelStep = Math.Max(1, data.Count / 6);

        return data.Select((d, i) =>
        {
            string formattedTime = FormatTimestamp(d.Timestamp);

            return new ChartEntry(d.Temperature)
            {
                Label = (i % labelStep == 0) ? formattedTime : "",
                ValueLabel = "",
                Color = SKColor.Parse("#1E88E5"),
                TextColor = SKColor.Parse("#212121")
            };
        }).ToArray();
    }

    // ✅ Timestamp formatter (handles Unix and ISO)
    private static string FormatTimestamp(string timestamp)
    {
        // Try Unix time first
        if (long.TryParse(timestamp, out long unix))
        {
            try
            {
                if (unix > 1_000_000_000_000)
                    return DateTimeOffset.FromUnixTimeMilliseconds(unix).ToLocalTime().ToString("HH:mm");
                else if (unix > 1_000_000_000)
                    return DateTimeOffset.FromUnixTimeSeconds(unix).ToLocalTime().ToString("HH:mm");
            }
            catch { }
        }

        // ISO or SQL formats
        if (DateTime.TryParse(timestamp, out DateTime parsed))
            return parsed.ToLocalTime().ToString("HH:mm");

        return timestamp;
    }

    // ✅ Tap events open detail views (no change)
    // ✅ Taps open detail pages with FULL DATA (not simplified)
    private async void OnShakinessTapped(object sender, EventArgs e)
    {
        var fullData = await _db.GetDataAsync(); // full-resolution dataset
        fullData = fullData.OrderBy(d => d.Timestamp).ToList();

        await Navigation.PushAsync(new GraphDetailPage(
            "Hand Shakiness Over Time",
            GenerateShakinessData(fullData) // full dataset, no simplification
        ));
    }

    private async void OnTemperatureTapped(object sender, EventArgs e)
    {
        var fullData = await _db.GetDataAsync(); // full-resolution dataset
        fullData = fullData.OrderBy(d => d.Timestamp).ToList();

        await Navigation.PushAsync(new GraphDetailPage(
            "Hand Temperature Over Time",
            GenerateTemperatureData(fullData) // full dataset, no simplification
        ));
    }


    // ✅ Auto-refresh on update
    private async void OnDataUpdated(List<SensorData> data)
    {
        await MainThread.InvokeOnMainThreadAsync(() =>
        {
            data = SimplifyData(data.OrderBy(d => d.Timestamp).ToList(), SimplificationFactor);
            Graph1.Chart = CreateLineChart(GenerateShakinessData(data));
            Graph2.Chart = CreateLineChart(GenerateTemperatureData(data));
        });
    }
}
