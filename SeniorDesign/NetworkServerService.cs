using System.Net;
using System.Net.Sockets;
using System.Text;

namespace SeniorDesign
{
    public class NetworkServerService
    {
        private TcpListener? _listener;
        private bool _isRunning = false;

        // Optional event if you want to display live data in the app
        public event Action<string>? DataReceived;

        public async Task StartServerAsync(int port = 5000)
        {
            if (_isRunning)
                return;

            _isRunning = true;
            _listener = new TcpListener(IPAddress.Any, port);
            _listener.Start();

            Console.WriteLine($"[Server] Listening on port {port}...");

            while (_isRunning)
            {
                var client = await _listener.AcceptTcpClientAsync();
                Console.WriteLine("[Server] Client connected!");
                _ = HandleClientAsync(client);
            }
        }

        public void StopServer()
        {
            _isRunning = false;
            _listener?.Stop();
            Console.WriteLine("[Server] Stopped");
        }

        private async Task HandleClientAsync(TcpClient client)
        {
            var buffer = new byte[1024];
            using var stream = client.GetStream();

            while (_isRunning && client.Connected)
            {
                int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                if (bytesRead == 0)
                    break; // client disconnected

                string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                Console.WriteLine($"[Server] Received: {message}");

                // Optional: notify UI layer
                DataReceived?.Invoke(message);
            }

            client.Close();
            Console.WriteLine("[Server] Client disconnected.");
        }
    }
}
