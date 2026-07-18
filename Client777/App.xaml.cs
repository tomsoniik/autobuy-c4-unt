using System;
using System.Windows;

namespace Client777
{
    public partial class App : Application
    {
        public App()
        {
            this.DispatcherUnhandledException += (s, e) =>
            {
                System.IO.File.WriteAllText("crash.log", e.Exception.ToString());
                MessageBox.Show(e.Exception.Message, "XAML Parse Error");
                e.Handled = true;
            };
        }
    }
}
