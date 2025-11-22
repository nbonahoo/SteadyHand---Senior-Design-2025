using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using LiveChartsCore.SkiaSharpView.Maui;
using Microsoft.Maui.Storage;
using SkiaSharp;
using System.Diagnostics;
using System.Text;

namespace SeniorDesign
{
    public partial class GraphDetailPage : ContentPage
    {
        private string _title;
        private string _unitLabel;
        private double[] _values;
        private string[] _timestamps;

        public GraphDetailPage(string title, double[] values, string[] timestamps)
        {
            InitializeComponent();

            _title = title;
            _values = values;
            _timestamps = timestamps;

            GraphTitle.Text = title;
            NavigationPage.SetHasBackButton(this, true);

            // FIXED: set unit label
            if (title.ToLower().Contains("temperature"))
                _unitLabel = "Temperature (°C)";
            else
                _unitLabel = "Acceleration (m/s²)";

            LoadDetailChart();
        }

        private void LoadDetailChart()
        {
            DetailChart.Series = new ISeries[]
            {
                new LineSeries<double>
                {
                    Values = _values,
                    GeometrySize = 0,
                    Stroke = new SolidColorPaint(SKColor.Parse("#1565C0"))
                    {
                        StrokeThickness = 3
                    },
                    Fill = null,
                    LineSmoothness = 0
                }
            };

            DetailChart.XAxes = new[]
            {
                new Axis
                {
                    Labels = _timestamps,
                    TextSize = 14,
                    Name = "Time"
                }
            };

            DetailChart.YAxes = new[]
            {
                new Axis
                {
                    Name = _unitLabel,
                    TextSize = 14
                }
            };
        }
        private async void OnExportClicked(object sender, EventArgs e)
        {
            try
            {
                var stopwatch = Stopwatch.StartNew();
                ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.Gray;
                ExportStatusLabel.Text = "Exporting data...";

                if (_values == null || _values.Length == 0)
                {
                    ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.OrangeRed;
                    ExportStatusLabel.Text = "No data to export.";
                    await DisplayAlert("No Data", "There is no data to export.", "OK");
                    return;
                }

                var csv = new StringBuilder();
                csv.AppendLine($"Time,{_unitLabel}");

                for (int i = 0; i < _values.Length; i++)
                {
                    string time = _timestamps[i].Replace(",", " ");
                    string value = _values[i].ToString();
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

                stopwatch.Stop();
                ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.Green;
                ExportStatusLabel.Text = $"Export complete in {stopwatch.Elapsed.TotalSeconds:F2}s";
            }
            catch (Exception ex)
            {
                ExportStatusLabel.TextColor = Microsoft.Maui.Graphics.Colors.Red;
                ExportStatusLabel.Text = $"Export failed: {ex.Message}";
                await DisplayAlert("Export Failed", $"Error exporting CSV: {ex.Message}", "OK");
            }
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

            // Scale chart axis text
            foreach (var axis in DetailChart.XAxes) axis.TextSize = (float)(12 * scale);
            foreach (var axis in DetailChart.YAxes) axis.TextSize = (float)(12 * scale);
        }


    }
}
