using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;
using Timer = System.Timers.Timer;

namespace SeniorDesign
{
    public class DatabaseService
    {
        private readonly HttpClient _http = new();

        private const string ServerUrl = "https://steadyhand-server.onrender.com/data";

        private List<SensorData> _cachedData = new();
        private readonly Timer _refreshTimer;

        // Track highest Id we've seen so far
        private int _lastMaxId = 0;

        public event Action<List<SensorData>>? DataUpdated;

        public DatabaseService()
        {
            _refreshTimer = new Timer(5000); // 5 seconds
            _refreshTimer.Elapsed += async (s, e) => await CheckForUpdatesAsync();
            _refreshTimer.AutoReset = true;
            _refreshTimer.Enabled = true;
        }

        // Manual fetch
        public async Task<List<SensorData>> GetDataAsync(int limit = 1000)
        {
            var data = await FetchFromServer(limit);

            // Keep cache in sync when you fetch manually too
            _cachedData = data;
            if (data.Count > 0)
                _lastMaxId = data.Max(d => d.Id);

            return data;
        }

        // Poll for updates
        private async Task CheckForUpdatesAsync()
        {
            try
            {
                var newData = await FetchFromServer();

                if (newData.Count == 0)
                    return;

                // Look at the newest Id
                var maxId = newData.Max(d => d.Id);

                // Only fire event if there's actually newer data
                if (maxId != _lastMaxId)
                {
                    _lastMaxId = maxId;
                    _cachedData = newData;
                    DataUpdated?.Invoke(newData);
                }
            }
            catch
            {
                // swallow network errors for now
            }
        }

        // Core fetching method
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
