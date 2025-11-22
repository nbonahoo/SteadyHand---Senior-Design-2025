namespace SeniorDesign
{
    public partial class App : Application
    {
        private readonly NetworkServerService _server = new();

        public App()
        {
            InitializeComponent();

            // Make sure our scaled font resources match the initial FontScale
            UpdateScaledFontResources();

            Task.Run(() => _server.StartServerAsync(5000));
        }

        public double FontScale
        {
            get => (double)Resources["FontScale"];
            set
            {
                double clamped = Math.Clamp(value, 0.5, 2.0);
                if (Math.Abs(clamped - (double)Resources["FontScale"]) < 0.0001)
                    return;

                Resources["FontScale"] = clamped;
                UpdateScaledFontResources();
            }
        }

        private void UpdateScaledFontResources()
        {
            double scale = (double)Resources["FontScale"];

            double baseSmall = (double)Resources["BaseFontSmall"];
            double baseNormal = (double)Resources["BaseFontNormal"];
            double baseTitle = (double)Resources["BaseFontTitle"];
            double baseHeader = (double)Resources["BaseFontHeader"];

            Resources["SmallFontSize"] = baseSmall * scale;
            Resources["BodyFontSize"] = baseNormal * scale;
            Resources["TitleFontSize"] = baseTitle * scale;
            Resources["HeaderFontSize"] = baseHeader * scale;
        }

        protected override Window CreateWindow(IActivationState? activationState)
        {
            return new Window(new AppShell());
        }
    }
}
