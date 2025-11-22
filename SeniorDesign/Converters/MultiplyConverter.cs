using System.Globalization;

namespace SeniorDesign.Converters
{
    public class MultiplyConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is double scale && parameter != null)
            {
                double baseSize = System.Convert.ToDouble(parameter);
                return scale * baseSize;
            }
            return 0;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}
