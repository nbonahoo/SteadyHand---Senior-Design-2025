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

        // 🔔 Event raised when new data is detected
        public event Action<List<SensorData>>? DataUpdated;

        public DatabaseService()
        {
            // Poll every 5 seconds (5000 ms)
            _refreshTimer = new Timer(5000);
            _refreshTimer.Elapsed += async (s, e) => await CheckForUpdatesAsync();
            _refreshTimer.AutoReset = true;
            _refreshTimer.Enabled = true; // start timer
        }

        // ✅ Manual fetch (used by initial LoadChartsAsync)
        public async Task<List<SensorData>> GetDataAsync(int limit = 1000)
        {
            return await FetchFromServer(limit);
        }

        // 🔁 Periodic check for new data
        private async Task CheckForUpdatesAsync()
        {
            try
            {
                var newData = await FetchFromServer();

                // Compare by count first; optionally check last timestamp for smarter update
                if (newData.Count != _cachedData.Count)
                {
                    _cachedData = newData;
                    DataUpdated?.Invoke(newData);
                }
            }
            catch
            {
                // Silent fail — server may be temporarily unreachable
            }
        }

        // 🧠 Core fetch logic (GET /data)
        private async Task<List<SensorData>> FetchFromServer(int limit = 1000)
        {
            var response = await _http.GetAsync($"{ServerUrl}?limit={limit}");
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(json);

            var list = new List<SensorData>();

            foreach (var row in doc.RootElement.GetProperty("data").EnumerateArray())
            {
                list.Add(new SensorData
                {
                    Id = row[0].GetInt32(),
                    Timestamp = row[1].GetString()!,
                    AccelX = (float)row[2].GetDouble(),
                    AccelY = (float)row[3].GetDouble(),
                    AccelZ = (float)row[4].GetDouble(),
                    Temperature = (float)row[5].GetDouble()
                });
            }

            return list;
        }
    }

    // ✅ Data model class
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
