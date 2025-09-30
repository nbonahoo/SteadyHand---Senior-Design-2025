using Microsoft.Extensions.Logging;
using Microcharts.Maui;
using System.IO; // for Path
using Microsoft.Maui.Storage; // for FileSystem

namespace SeniorDesign
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .UseMicrocharts(); // chart support

#if DEBUG
            builder.Logging.AddDebug();
#endif

            // ✅ Register SQLite DatabaseService
            builder.Services.AddSingleton<DatabaseService>(s =>
            {
                string dbPath = Path.Combine(FileSystem.AppDataDirectory, "steadyhand.db3");
                return new DatabaseService(dbPath);
            });

            return builder.Build();
        }
    }
}
