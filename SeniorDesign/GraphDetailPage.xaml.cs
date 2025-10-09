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

            _chart = DetailedGraph.Chart;
            // Show the back arrow automatically
            NavigationPage.SetHasBackButton(this, true);
        }

        private async void OnExportClicked(object sender, EventArgs e)
        {
            try
            {
                IEnumerable<Microcharts.ChartEntry>? entries = null;

                // Extract entries depending on chart type
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
                csv.AppendLine("Time,Value");

                foreach (var entry in entries)
                {
                    // Label = Time (X-axis)
                    string time = entry.Label?.Replace(",", " ") ?? "";

                    // Value = Y-axis
                    string value = entry.Value.ToString();

                    csv.AppendLine($"{time},{value}");
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