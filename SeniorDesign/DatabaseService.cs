using SQLite;

namespace SeniorDesign
{
    // Data model for your sensor readings
    public class SensorData
    {
        [PrimaryKey, AutoIncrement]
        public int Id { get; set; }

        public DateTime Timestamp { get; set; }
        public float Accelerometer { get; set; }
        public float Temperature { get; set; }
    }

    // Database service wrapper
    public class DatabaseService
    {
        private readonly SQLiteAsyncConnection _database;

        public DatabaseService(string dbPath)
        {
            _database = new SQLiteAsyncConnection(dbPath);
            _database.CreateTableAsync<SensorData>().Wait();
        }

        public Task<List<SensorData>> GetDataAsync()
        {
            return _database.Table<SensorData>().ToListAsync();
        }

        public Task<int> SaveDataAsync(SensorData data)
        {
            return _database.InsertAsync(data);
        }
    }
}
