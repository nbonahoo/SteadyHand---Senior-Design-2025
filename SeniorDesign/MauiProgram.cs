using LiveChartsCore.SkiaSharpView.Maui;
using Microcharts.Maui;
using Microsoft.Extensions.Logging;

namespace SeniorDesign
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();

            builder
                .UseMauiApp<App>()
                .UseLiveCharts()
                .UseLiveCharts()
                .UseMicrocharts(); // Enables Microcharts.MAUI support
                
#if DEBUG
            builder.Logging.AddDebug();
#endif

            // ✅ Register HTTP-based DatabaseService (connects to FastAPI server)
            builder.Services.AddSingleton<DatabaseService>();

            return builder.Build();
        }
    }
}
