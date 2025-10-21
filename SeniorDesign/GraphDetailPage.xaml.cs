using DocumentFormat.OpenXml.Spreadsheet;
using Microcharts;
using Microcharts.Maui;
using Microsoft.Maui.Storage;
using SkiaSharp;
using System.Text;
using System.Diagnostics;

namespace SeniorDesign
{
    public partial class GraphDetailPage : ContentPage
    {
        private Chart _chart;
        private string _title;
        private string _unitLabel; // <-- new: holds "Temperature (°C)" or "Acceleration (m/s²)"

        public GraphDetailPage(string title, IEnumerable<ChartEntry> entries)
        {
            InitializeComponent();

            _title = title;
            GraphTitle.Text = title;
            NavigationPage.SetHasBackButton(this, true);

            // ✅ Dynamically set Y-axis label and unit for export
            if (title.ToLower().Contains("temperature"))
            {
                YAxisLabel.Text = "Temperature (°C)";
                _unitLabel = "Temperature (°C)";
            }
            else if (title.ToLower().Contains("shakiness") || title.ToLower().Contains("acceleration"))
            {
                YAxisLabel.Text = "Acceleration (m/s²)";
                _unitLabel = "Acceleration (m/s²)";
            }
            else
            {
                YAxisLabel.Text = "Value";
                _unitLabel = "Value";
            }

            // ✅ Configure chart
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
        }

        private async void OnExportClicked(object sender, EventArgs e)
        {
            try
            {
                // ⏳ Start timing
                var stopwatch = Stopwatch.StartNew();
                ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.Gray;
                ExportStatusLabel.Text = "Exporting data...";

                IEnumerable<ChartEntry>? entries = null;

                // ✅ Extract entries depending on chart type
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
                    ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.OrangeRed;
                    ExportStatusLabel.Text = " No data to export.";
                    await DisplayAlert("No Data", "There is no data to export.", "OK");
                    return;
                }

                // ✅ Create CSV with correct header
                var csv = new StringBuilder();
                csv.AppendLine($"Time,{_unitLabel}");

                foreach (var entry in entries)
                {
                    string time = entry.Label?.Replace(",", " ") ?? "";
                    string value = entry.Value.ToString();
                    csv.AppendLine($"{time},{value}");
                }

                // ✅ Save to file
                string fileName = $"{_title.Replace(" ", "_")}_{DateTime.Now:yyyyMMdd_HHmmss}.csv";
                string filePath = Path.Combine(FileSystem.AppDataDirectory, fileName);
                File.WriteAllText(filePath, csv.ToString());

                // ✅ Share the file
                await Share.Default.RequestAsync(new ShareFileRequest
                {
                    Title = "Exported Graph Data",
                    File = new ShareFile(filePath)
                });

                // ✅ Done
                stopwatch.Stop();
                double seconds = stopwatch.Elapsed.TotalSeconds;
                ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.Green;
                ExportStatusLabel.Text = $"Export complete in {seconds:F2} seconds at {DateTime.Now:hh:mm:ss tt}";
            }
            catch (Exception ex)
            {
                ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.Red;
                ExportStatusLabel.Text = $"Export failed: {ex.Message}";
                await DisplayAlert("Export Failed", $"Error exporting CSV: {ex.Message}", "OK");
            }
        }
    }
}
