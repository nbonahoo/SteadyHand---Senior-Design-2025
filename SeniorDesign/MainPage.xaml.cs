using Microcharts;
using Microcharts.Maui;
using SkiaSharp;

namespace SeniorDesign;

public partial class MainPage : ContentPage
{
    private readonly DatabaseService _db;

    public MainPage(DatabaseService db)
    {
        InitializeComponent();
        _db = db;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await LoadChartsAsync();
    }

    private async Task LoadChartsAsync()
    {
        // Load data from database
        var sensorData = await _db.GetDataAsync();

        // Seed test data if empty
        if (sensorData.Count == 0)
        {
            var random = new Random();
            for (int i = 0; i < 20; i++)
            {
                await _db.SaveDataAsync(new SensorData
                {
                    Timestamp = DateTime.Now.AddSeconds(i),
                    Accelerometer = 0.5f + (float)(random.NextDouble() - 0.5),
                    Temperature = 36f + (float)(random.NextDouble() * 1.5f)
                });
            }
            sensorData = await _db.GetDataAsync();
        }

        // Create charts
        Graph1.Chart = new LineChart
        {
            Entries = GenerateShakinessData(sensorData),
            LineMode = LineMode.Straight,
            LineSize = 4,
            PointMode = PointMode.Circle,
            PointSize = 6,
            LabelTextSize = 20,
            BackgroundColor = SKColors.White,
            LabelOrientation = Orientation.Horizontal,
            ValueLabelOrientation = Orientation.Horizontal,
            LabelColor = new SKColor(33, 33, 33)
        };

        Graph2.Chart = new LineChart
        {
            Entries = GenerateTemperatureData(sensorData),
            LineMode = LineMode.Straight,
            LineSize = 4,
            PointMode = PointMode.Circle,
            PointSize = 6,
            LabelTextSize = 20,
            BackgroundColor = SKColors.White,
            LabelColor = new SKColor(33, 33, 33),
            LabelOrientation = Orientation.Horizontal,
            ValueLabelOrientation = Orientation.Horizontal,
        };
    }

    // Tap handlers — simple and clean
    private async void OnShakinessTapped(object sender, EventArgs e)
    {
        var sensorData = await _db.GetDataAsync();
        await Navigation.PushAsync(new GraphDetailPage("Hand Shakiness Over Time", GenerateShakinessData(sensorData)));
    }

    private async void OnTemperatureTapped(object sender, EventArgs e)
    {
        var sensorData = await _db.GetDataAsync();
        await Navigation.PushAsync(new GraphDetailPage("Hand Temperature Over Time", GenerateTemperatureData(sensorData)));
    }

    // Chart entry generation
    private ChartEntry[] GenerateShakinessData(List<SensorData> data) =>
        data.Select(d => new ChartEntry(d.Accelerometer)
        {
            Label = d.Timestamp.ToString("HH:mm"),
            ValueLabel = d.Accelerometer.ToString("0.00"),
            Color = SKColors.Red,
            TextColor = SKColors.Black
        }).ToArray();

    private ChartEntry[] GenerateTemperatureData(List<SensorData> data) =>
        data.Select(d => new ChartEntry(d.Temperature)
        {
            Label = d.Timestamp.ToString("HH:mm"),
            ValueLabel = d.Temperature.ToString("0.0"),
            Color = SKColors.Red,
            TextColor = SKColors.Black
        }).ToArray();
}
