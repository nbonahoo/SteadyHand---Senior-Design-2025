using System.ComponentModel;
using Microsoft.Maui.Dispatching;

namespace SeniorDesign.Services
{
    public class TextSizeService : INotifyPropertyChanged
    {
        private double _scale = 1.0;

        public double Scale
        {
            get => _scale;
            set
            {
                if (_scale != value)
                {
                    _scale = value;

                    MainThread.BeginInvokeOnMainThread(() =>
                    {
                        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Scale)));
                    });
                }
            }
        }

        public void Increase() => Scale = Math.Min(2.0, Scale + 0.1);
        public void Decrease() => Scale = Math.Max(0.5, Scale - 0.1);

        public event PropertyChangedEventHandler? PropertyChanged;
    }
}
