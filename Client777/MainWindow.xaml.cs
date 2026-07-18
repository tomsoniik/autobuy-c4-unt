using System;
using System.Windows;
using System.Windows.Input;
using System.Windows.Controls;

namespace Client777
{
    public partial class MainWindow : Window
    {
        private RecoilController _recoil;
        private AutoCrafter _crafter;

        public MainWindow()
        {
            InitializeComponent();
            _recoil = new RecoilController();
            _crafter = new AutoCrafter();
            
            // Sync UI to default values
            if (SliderPull != null) _recoil.PullHip = SliderPull.Value;
            if (SliderScope != null) _recoil.PullScope = SliderScope.Value;
            if (SliderPullX != null) _recoil.PullHipX = SliderPullX.Value;
            if (SliderScopeX != null) _recoil.PullScopeX = SliderScopeX.Value;
            if (SliderMultiplier != null) _recoil.Multiplier = SliderMultiplier.Value;
            if (ChkActive != null) _recoil.IsActive = ChkActive.IsChecked ?? false;
            if (ChkAimOnly != null) _recoil.AimOnly = ChkAimOnly.IsChecked ?? true;
            
            if (ChkCrafterActive != null) _crafter.IsActive = ChkCrafterActive.IsChecked ?? false;
            if (TxtBuyCommand != null) _crafter.BuyCommand = TxtBuyCommand.Text;
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            _recoil.Stop();
            _crafter.Stop();
            Application.Current.Shutdown();
        }

        private void Tab_Checked(object sender, RoutedEventArgs e)
        {
            if (ViewAutoCrafter == null || ViewRecoil == null || ViewSystem == null) return;

            ViewAutoCrafter.Visibility = Visibility.Hidden;
            ViewRecoil.Visibility = Visibility.Hidden;
            ViewSystem.Visibility = Visibility.Hidden;

            if (TabAutoCrafter.IsChecked == true) ViewAutoCrafter.Visibility = Visibility.Visible;
            if (TabRecoil.IsChecked == true) ViewRecoil.Visibility = Visibility.Visible;
            if (TabSystem.IsChecked == true) ViewSystem.Visibility = Visibility.Visible;
        }

        private void ChkActive_CheckedChanged(object sender, RoutedEventArgs e)
        {
            if (_recoil != null)
                _recoil.IsActive = ChkActive.IsChecked ?? false;
        }

        private void ChkAimOnly_CheckedChanged(object sender, RoutedEventArgs e)
        {
            if (_recoil != null)
                _recoil.AimOnly = ChkAimOnly.IsChecked ?? true;
        }

        private void SliderPull_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (_recoil == null) return;
            
            Slider senderSlider = sender as Slider;
            if (senderSlider == SliderPull && LblPull != null)
            {
                LblPull.Text = $"Vertical Hip Fire Pull (Y): {e.NewValue:F2}";
                _recoil.PullHip = e.NewValue;
            }
            else if (senderSlider == SliderScope && LblScope != null)
            {
                LblScope.Text = $"Vertical Scope Pull (Y): {e.NewValue:F2}";
                _recoil.PullScope = e.NewValue;
            }
            else if (senderSlider == SliderPullX && LblPullX != null)
            {
                LblPullX.Text = $"Horizontal Hip Fire Pull (X): {e.NewValue:F2}";
                _recoil.PullHipX = e.NewValue;
            }
            else if (senderSlider == SliderScopeX && LblScopeX != null)
            {
                LblScopeX.Text = $"Horizontal Scope Pull (X): {e.NewValue:F2}";
                _recoil.PullScopeX = e.NewValue;
            }
            else if (senderSlider == SliderMultiplier && LblMultiplier != null)
            {
                LblMultiplier.Text = $"Global Multiplier: {e.NewValue:F1}x";
                _recoil.Multiplier = e.NewValue;
            }
        }

        // --- Auto-Crafter UI Events ---
        private void ChkCrafterActive_CheckedChanged(object sender, RoutedEventArgs e)
        {
            if (_crafter != null && ChkCrafterActive != null)
            {
                _crafter.IsActive = ChkCrafterActive.IsChecked ?? false;
            }
        }

        private void TxtBuyCommand_TextChanged(object sender, System.Windows.Controls.TextChangedEventArgs e)
        {
            if (_crafter != null && TxtBuyCommand != null)
            {
                _crafter.BuyCommand = TxtBuyCommand.Text;
            }
        }
    }
}