namespace SeniorDesign
{
    public partial class App : Application
    {
        private readonly NetworkServerService _server = new();
        public App()
        {
            InitializeComponent();
            Task.Run(() => _server.StartServerAsync(5000));
        }

        protected override Window CreateWindow(IActivationState? activationState)
        {
            return new Window(new AppShell());
        }
    }
}