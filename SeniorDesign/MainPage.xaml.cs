using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Maui;
using LiveChartsCore.SkiaSharpView.Painting;
using Microsoft.Maui;
using SkiaSharp;

namespace SeniorDesign;

public partial class MainPage : ContentPage
{
    private readonly DatabaseService _db;

    private const int SimplificationFactor = 10;

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
            var sensorData = await _db.GetDataAsync();

            if (sensorData == null || sensorData.Count == 0)
            {
                await DisplayAlert("No Data",
                    "No sensor data available. Please ensure the server is running and data has been uploaded.",
                    "OK");
                return;
            }

            sensorData = sensorData.OrderBy(d => d.Timestamp).ToList();
            var simplified = SimplifyData(sensorData, SimplificationFactor);

            LoadShakinessChart(simplified);
            LoadTemperatureChart(simplified);
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", $"Failed to load data: {ex.Message}", "OK");
        }
    }

    private List<SensorData> SimplifyData(List<SensorData> data, int step)
    {
        if (data.Count <= 100)
            return data;

        var result = new List<SensorData>();
        for (int i = 0; i < data.Count; i += step)
            result.Add(data[i]);

        return result;
    }

    // -------------------------------------------------------
    // 🔵 SHAKINESS GRAPH (LiveCharts2)
    // -------------------------------------------------------
    private void LoadShakinessChart(List<SensorData> data)
    {
        var magnitudes = data.Select(d =>
            Math.Sqrt(
                d.AccelX * d.AccelX +
                d.AccelY * d.AccelY +
                d.AccelZ * d.AccelZ
            )
        ).ToArray();

        var labels = data.Select(d => FormatTimestamp(d.Timestamp)).ToArray();

        ShakinessChart.Series = new ISeries[]
        {
            new LineSeries<double>
            {
                Values = magnitudes,
                GeometrySize = 0,
                Stroke = new SolidColorPaint(SKColor.Parse("#1565C0")) { StrokeThickness = 3 },
                Fill = null,
                LineSmoothness = 0.0
            }
        };

        ShakinessChart.XAxes = new[]
        {
            new Axis
            {
                Labels = labels,
                LabelsRotation = 0,
                TextSize = 12,
                Name = "Time",
                MinStep = 1
            }
        };

        ShakinessChart.YAxes = new[]
        {
            new Axis
            {
                Name = "Acceleration (m/s²)",
                TextSize = 12
            }
        };
        ApplyTextScaling();
    }

    // -------------------------------------------------------
    // 🔴 TEMPERATURE GRAPH (LiveCharts2)
    // -------------------------------------------------------
    private void LoadTemperatureChart(List<SensorData> data)
    {
        var temps = data.Select(d => (double)d.Temperature).ToArray();
        var labels = data.Select(d => FormatTimestamp(d.Timestamp)).ToArray();

        TemperatureChart.Series = new ISeries[]
        {
            new LineSeries<double>
            {
                Values = temps,
                GeometrySize = 0,
                Stroke = new SolidColorPaint(SKColor.Parse("#1565C0")) { StrokeThickness = 3 },
                Fill = null,
                LineSmoothness = 0.0
            }
        };

        TemperatureChart.XAxes = new[]
        {
            new Axis
            {
                Labels = labels,
                LabelsRotation = 0,
                TextSize = 12,
                Name = "Time",
                MinStep = 1
            }
        };

        TemperatureChart.YAxes = new[]
        {
            new Axis
            {
                Name = "Temperature (°C)",
                TextSize = 12
            }
        };
        ApplyTextScaling();
    }

    // -------------------------------------------------------
    // TIMESTAMP FORMATTER
    // -------------------------------------------------------
    private static string FormatTimestamp(string timestamp)
    {
        if (long.TryParse(timestamp, out long unix))
        {
            try
            {
                if (unix > 1_000_000_000_000)
                    return DateTimeOffset.FromUnixTimeMilliseconds(unix)
                        .ToLocalTime()
                        .ToString("MM/dd/yyyy");
                else if (unix > 1_000_000_000)
                    return DateTimeOffset.FromUnixTimeSeconds(unix)
                        .ToLocalTime()
                        .ToString("MM/dd/yyyy");
            }
            catch { }
        }

        if (DateTime.TryParse(timestamp, out DateTime parsed))
            return parsed.ToLocalTime().ToString("MM/dd");

        return timestamp;
    }

    private async void OnShakinessTapped(object sender, EventArgs e)
    {
        var fullData = await _db.GetDataAsync();
        fullData = fullData.OrderBy(d => d.Timestamp).ToList();
        var magnitudes = fullData.Select(d =>
            Math.Sqrt(d.AccelX * d.AccelX + d.AccelY * d.AccelY + d.AccelZ * d.AccelZ)
        ).ToArray();

        var labels = fullData.Select(d => FormatTimestamp(d.Timestamp)).ToArray();

        await Navigation.PushAsync(new GraphDetailPage(
            "Hand Shakiness Over Time",
            magnitudes,
            labels
        ));


    }

    private async void OnTemperatureTapped(object sender, EventArgs e)
    {
        var fullData = await _db.GetDataAsync();
        fullData = fullData.OrderBy(d => d.Timestamp).ToList();
        var temps = fullData.Select(d => (double)d.Temperature).ToArray();
        var labels = fullData.Select(d => FormatTimestamp(d.Timestamp)).ToArray();

        await Navigation.PushAsync(new GraphDetailPage(
            "Hand Temperature Over Time",
            temps,
            labels
        ));

    }

    private async void OnDataUpdated(List<SensorData> data)
    {
        await MainThread.InvokeOnMainThreadAsync(() =>
        {
            data = SimplifyData(data.OrderBy(d => d.Timestamp).ToList(), SimplificationFactor);
            LoadShakinessChart(data);
            LoadTemperatureChart(data);
        });
    }
    private void OnIncreaseFont(object sender, EventArgs e)
    {
        (App.Current as App).FontScale += 0.1;
        ApplyTextScaling();
    }

    private void OnDecreaseFont(object sender, EventArgs e)
    {
        (App.Current as App).FontScale -= 0.1;
        ApplyTextScaling();
    }
    private void ApplyTextScaling()
    {
        double scale = (App.Current as App).FontScale;

        // SCALE CHART AXES
        foreach (var axis in ShakinessChart.XAxes) axis.TextSize = (float)(12 * scale);
        foreach (var axis in ShakinessChart.YAxes) axis.TextSize = (float)(12 * scale);
        foreach (var axis in TemperatureChart.XAxes) axis.TextSize = (float)(12 * scale);
        foreach (var axis in TemperatureChart.YAxes) axis.TextSize = (float)(12 * scale);
    }


}
