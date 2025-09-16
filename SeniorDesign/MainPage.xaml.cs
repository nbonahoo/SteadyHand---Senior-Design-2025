namespace SeniorDesign
{
    public partial class MainPage : ContentPage
    {
        int count = 0;

        public MainPage()
        {
            InitializeComponent();
        }
        private async void OnBluetoothPairClicked(object sender, EventArgs e)
        {
            // Placeholder for Bluetooth pairing logic
            await DisplayAlert("Bluetooth", "Pairing process started...", "OK");
        }
    }
}
