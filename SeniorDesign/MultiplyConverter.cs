using System;
using System.Globalization;

public class Multiply : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        double scale = (double)value;
        double baseSize = double.Parse(parameter.ToString());
        return baseSize * scale;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value;
    }
}
