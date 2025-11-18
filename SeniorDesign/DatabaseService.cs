using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;

// 👇 Explicitly alias Timer to avoid ambiguity with System.Threading.Timer
using Timer = System.Timers.Timer;

namespace SeniorDesign
{
    public class DatabaseService
    {
        private readonly HttpClient _http = new();

        // 👇 Replace with your server’s IP
        private const string ServerUrl = "https://steadyhand-server.onrender.com/data";

        private List<SensorData> _cachedData = new();
        private readonly Timer _refreshTimer;

        // 🔔 Event when new data arrives
        public event Action<List<SensorData>>? DataUpdated;

        public DatabaseService()
        {
            _refreshTimer = new Timer(5000);
            _refreshTimer.Elapsed += async (s, e) => await CheckForUpdatesAsync();
            _refreshTimer.AutoReset = true;
            _refreshTimer.Enabled = true;
        }

        // Manual fetch
        public async Task<List<SensorData>> GetDataAsync(int limit = 1000)
        {
            return await FetchFromServer(limit);
        }

        // Poll for updates
        private async Task CheckForUpdatesAsync()
        {
            try
            {
                var newData = await FetchFromServer();

                if (newData.Count != _cachedData.Count)
                {
                    _cachedData = newData;
                    DataUpdated?.Invoke(newData);
                }
            }
            catch
            {
                // Ignore connection failures
            }
        }

        // 🧠 Core fetching method
        private async Task<List<SensorData>> FetchFromServer(int limit = 1000)
        {
            var response = await _http.GetAsync($"{ServerUrl}?limit={limit}");
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();

            using var doc = JsonDocument.Parse(json);

            var list = new List<SensorData>();

            // FIX: This now reads objects, not arrays
            foreach (var row in doc.RootElement.GetProperty("data").EnumerateArray())
            {
                list.Add(new SensorData
                {
                    Id = row.GetProperty("Id").GetInt32(),
                    Timestamp = row.GetProperty("Timestamp").GetString()!,
                    AccelX = (float)row.GetProperty("AccelX").GetDouble(),
                    AccelY = (float)row.GetProperty("AccelY").GetDouble(),
                    AccelZ = (float)row.GetProperty("AccelZ").GetDouble(),
                    Temperature = (float)row.GetProperty("Temperature").GetDouble()
                });
            }

            return list;
        }
    }

    // Data model
    public class SensorData
    {
        public int Id { get; set; }
        public string Timestamp { get; set; }
        public float AccelX { get; set; }
        public float AccelY { get; set; }
        public float AccelZ { get; set; }
        public float Temperature { get; set; }
    }
}
