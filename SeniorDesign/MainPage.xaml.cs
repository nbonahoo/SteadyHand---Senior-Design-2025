using Microcharts;
using SkiaSharp;

namespace SeniorDesign;

public partial class MainPage : ContentPage
{
    private readonly DatabaseService _db;
    private bool _initialized = false; // 👈 Prevents duplicate setup

    public MainPage(DatabaseService db)
    {
        InitializeComponent();
        _db = db;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();

        // Only load data + attach gestures once
        if (_initialized) return;
        _initialized = true;

        // Load data from the database
        var sensorData = await _db.GetDataAsync();

        // If DB is empty, insert seed data for testing
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

        // Build charts from DB data
        var shakinessChart = new LineChart
        {
            Entries = GenerateShakinessData(sensorData),
            LineSize = 4,
            PointSize = 6,
            LabelTextSize = 20,
            BackgroundColor = SKColors.White,
            LabelOrientation = Orientation.Horizontal,
            ValueLabelOrientation = Orientation.Horizontal
        };

        var tempChart = new LineChart
        {
            Entries = GenerateTemperatureData(sensorData),
            LineSize = 4,
            PointSize = 6,
            LabelTextSize = 20,
            BackgroundColor = SKColors.White,
            LabelOrientation = Orientation.Horizontal,
            ValueLabelOrientation = Orientation.Horizontal
        };

        Graph1.Chart = shakinessChart;
        Graph2.Chart = tempChart;

        // Add gesture recognizers ONCE
        var tapShakiness = new TapGestureRecognizer();
        tapShakiness.Tapped += async (s, e) =>
        {
            await Navigation.PushAsync(new GraphDetailPage("Hand Shakiness Over Time", shakinessChart));
        };
        Graph1.GestureRecognizers.Add(tapShakiness);

        var tapTemp = new TapGestureRecognizer();
        tapTemp.Tapped += async (s, e) =>
        {
            await Navigation.PushAsync(new GraphDetailPage("Hand Temperature Over Time", tempChart));
        };
        Graph2.GestureRecognizers.Add(tapTemp);
    }

    private ChartEntry[] GenerateShakinessData(List<SensorData> sensorData)
    {
        return sensorData
            .Select(d => new ChartEntry(d.Accelerometer)
            {
                Label = d.Timestamp.ToString("HH:mm"),
                ValueLabel = d.Accelerometer.ToString("0.00"),
                Color = SKColors.Red,
                TextColor = SKColors.Black
            })
            .ToArray();
    }

    private ChartEntry[] GenerateTemperatureData(List<SensorData> sensorData)
    {
        return sensorData
            .Select(d => new ChartEntry(d.Temperature)
            {
                Label = d.Timestamp.ToString("HH:mm"),
                ValueLabel = d.Temperature.ToString("0.0"),
                Color = SKColors.Red,
                TextColor = SKColors.Black
            })
            .ToArray();
    }
}
