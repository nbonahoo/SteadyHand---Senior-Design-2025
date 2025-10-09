using System.Text;
using Microsoft.Maui.Storage;
using Microcharts;
using Microcharts.Maui;
using SkiaSharp;

namespace SeniorDesign
{
    public partial class GraphDetailPage : ContentPage
    {
        private Chart _chart;
        private string _title;

        public GraphDetailPage(string title, Chart chart)
        {
            InitializeComponent();

            _title = title;
            _chart = chart;

            GraphTitle.Text = title;
            DetailedGraph.Chart = chart;

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
