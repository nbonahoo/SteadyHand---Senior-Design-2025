using System;
using System.Globalization;
using Microsoft.Maui.Controls;

namespace SeniorDesign
{
    public class Multiply : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            double baseSize = System.Convert.ToDouble(value);
            double scale = System.Convert.ToDouble(parameter);
            return baseSize * scale;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            return value;
        }
    }
}
