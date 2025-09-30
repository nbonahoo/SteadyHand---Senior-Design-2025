using Microcharts;
using SkiaSharp;

namespace SeniorDesign;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();

        var shakinessChart = new LineChart
        {
            Entries = GenerateShakinessData(),
            LineSize = 4,
            PointSize = 6,
            LabelTextSize = 20,
            BackgroundColor = SKColors.White,
            LabelOrientation = Orientation.Horizontal,
            ValueLabelOrientation = Orientation.Horizontal
        };

        var tempChart = new LineChart
        {
            Entries = GenerateTemperatureData(),
            LineSize = 4,
            PointSize = 6,
            LabelTextSize = 20,
            BackgroundColor = SKColors.White,
            LabelOrientation = Orientation.Horizontal,
            ValueLabelOrientation = Orientation.Horizontal
        };

        Graph1.Chart = shakinessChart;
        Graph2.Chart = tempChart;

        // Add tap gesture recognizers
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

    // Generate shakiness data: small random fluctuations
    private ChartEntry[] GenerateShakinessData()
    {
        var random = new Random();
        var entries = new ChartEntry[20];
        for (int i = 0; i < 20; i++)
        {
            float value = 0.5f + (float)(random.NextDouble() - 0.5); // fluctuate around 0.5
            entries[i] = new ChartEntry(value)
            {
                Label = (i + 1).ToString(),         // numeric x-axis (time)
                ValueLabel = value.ToString("0.00"),
                Color = SKColors.Red,               // bright red line
                TextColor = SKColors.Black          // readable numeric labels
            };
        }
        return entries;
    }

    // Generate hand temperature data: ~36–37.5°C
    private ChartEntry[] GenerateTemperatureData()
    {
        var random = new Random();
        var entries = new ChartEntry[20];
        for (int i = 0; i < 20; i++)
        {
            float value = 36f + (float)(random.NextDouble() * 1.5f);
            entries[i] = new ChartEntry(value)
            {
                Label = (i + 1).ToString(),        // numeric x-axis (time)
                ValueLabel = value.ToString("0.0"),
                Color = SKColors.Red,               // bright red line
                TextColor = SKColors.Black
            };
        }
        return entries;
    }
}
