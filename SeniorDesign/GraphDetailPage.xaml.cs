using DocumentFormat.OpenXml.Spreadsheet;
using Microcharts;
using Microcharts.Maui;
using Microsoft.Maui.Storage;
using SkiaSharp;
using System.Text;

namespace SeniorDesign
{
    public partial class GraphDetailPage : ContentPage
    {
        private Chart _chart;
        private string _title;

        public GraphDetailPage(string title, IEnumerable<ChartEntry> entries)
        {
            InitializeComponent();
            GraphTitle.Text = title;
            _title = title;
            //_chart = chart;

            GraphTitle.Text = title;
            DetailedGraph.Chart = new LineChart
            {
                Entries = entries,
                LineMode = LineMode.Straight,
                LineSize = 4,
                PointMode = PointMode.Circle,
                PointSize = 6,
                LabelTextSize = 20,
                LabelOrientation = Orientation.Horizontal,
                ValueLabelOrientation = Orientation.Horizontal,
                BackgroundColor = SKColors.White,
                LabelColor = new SKColor(33, 33, 33)
            };

            // Show the back arrow automatically
            NavigationPage.SetHasBackButton(this, true);
        }

        private async void OnExportClicked(object sender, EventArgs e)
        {
            try
            {
                IEnumerable<Microcharts.ChartEntry>? entries = null;

                // Extract entries based on chart type
                switch (_chart)
                {
                    case LineChart lineChart:
                        entries = lineChart.Entries;
                        break;
                    case BarChart barChart:
                        entries = barChart.Entries;
                        break;
                    case PointChart pointChart:
                        entries = pointChart.Entries;
                        break;
                    case DonutChart donutChart:
                        entries = donutChart.Entries;
                        break;
                    case RadarChart radarChart:
                        entries = radarChart.Entries;
                        break;
                    case RadialGaugeChart gaugeChart:
                        entries = gaugeChart.Entries;
                        break;
                }

                if (entries == null || !entries.Any())
                {
                    await DisplayAlert("No Data", "There is no data to export.", "OK");
                    return;
                }

                var csv = new StringBuilder();
                csv.AppendLine("Label,Value,ValueLabel,Color");

                foreach (var entry in entries)
                {
                    string label = entry.Label?.Replace(",", " ") ?? "";
                    string valueLabel = entry.ValueLabel ?? "";
                    string value = entry.Value.ToString();

                    // Convert SKColor → #RRGGBB
                    string color = $"#{entry.Color.Red:X2}{entry.Color.Green:X2}{entry.Color.Blue:X2}";

                    csv.AppendLine($"{label},{value},{valueLabel},{color}");
                }

                string fileName = $"{_title.Replace(" ", "_")}_{DateTime.Now:yyyyMMdd_HHmmss}.csv";
                string filePath = Path.Combine(FileSystem.AppDataDirectory, fileName);

                File.WriteAllText(filePath, csv.ToString());

                await Share.Default.RequestAsync(new ShareFileRequest
                {
                    Title = "Exported Graph Data",
                    File = new ShareFile(filePath)
                });
            }
            catch (Exception ex)
            {
                await DisplayAlert("Export Failed", $"Error exporting CSV: {ex.Message}", "OK");
            }
        }
    }
}
