using Microcharts;

namespace SeniorDesign;

public partial class GraphDetailPage : ContentPage
{
    public GraphDetailPage(string title, Chart chart)
    {
        InitializeComponent();

        GraphTitle.Text = title;
        DetailedGraph.Chart = chart;

        // Show the back arrow automatically
        NavigationPage.SetHasBackButton(this, true);
    }

    private void OnExportClicked(object sender, EventArgs e)
    {
        // Placeholder
        DisplayAlert("Export", "Export to CSV clicked!", "OK");
    }
}
