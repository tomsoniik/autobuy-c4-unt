using System;
using System.Diagnostics;
using System.Threading;

namespace Client777
{
    public class RecoilController
    {
        private Thread _recoilThread;
        private bool _isRunning;
        
        public bool IsActive { get; set; }
        public bool AimOnly { get; set; } = true;
        public double PullHip { get; set; } = 15.0;
        public double PullScope { get; set; } = 20.0;
        
        // Dodatkowa kompensacja pozioma (X)
        public double PullHipX { get; set; } = 0.0;
        public double PullScopeX { get; set; } = 0.0;
        
        public double Multiplier { get; set; } = 1.0;
        
        // Certyfikowany stan OpenCV (zmieniany przez zewn. detekcję)
        public bool IsScopeDetected { get; set; }

        public RecoilController()
        {
            _isRunning = true;
            _recoilThread = new Thread(RecoilLoop);
            _recoilThread.IsBackground = true;
            _recoilThread.Start();
        }

        private void RecoilLoop()
        {
            double accumY = 0.0;
            double accumX = 0.0;
            bool wasShooting = false;
            
            Stopwatch sw = new Stopwatch();
            sw.Start();
            double lastTime = sw.Elapsed.TotalSeconds;
            
            while (_isRunning)
            {
                try
                {
                    double currentTime = sw.Elapsed.TotalSeconds;
                    double dt = currentTime - lastTime;
                    lastTime = currentTime;

                    if (IsActive)
                    {
                        short lmbState = Win32Api.GetAsyncKeyState(Win32Api.VK_LBUTTON);
                        short rmbState = Win32Api.GetAsyncKeyState(Win32Api.VK_RBUTTON);
                        
                        bool isLmbPressed = (lmbState & 0x8000) != 0;
                        bool isRmbPressed = (rmbState & 0x8000) != 0;

                        if (isLmbPressed)
                        {
                            if (!wasShooting)
                            {
                                wasShooting = true;
                                accumY = 0.0; // Reset akumulatora przy nowej serii
                            }

                            if (!AimOnly || isRmbPressed)
                            {
                                double basePullY = IsScopeDetected ? PullScope : PullHip;
                                double basePullX = IsScopeDetected ? PullScopeX : PullHipX;
                                
                                double currentPullY = basePullY * Multiplier;
                                
                                // Symetryczne działanie lewo/prawo (Oscylacja Sinusoidalna X)
                                // Mnożymy przez Math.Sin, by co ułamek sekundy zmieniało kierunek na przeciwny.
                                double currentPullX = basePullX * Multiplier * Math.Sin(currentTime * 25.0);
                                
                                // Oparty na ułamkach (Float) akumulator dla gładkiego ciągnięcia
                                double pullPerSecondY = currentPullY * 50.0; 
                                double pullPerSecondX = currentPullX * 50.0; 
                                
                                accumY += pullPerSecondY * dt;
                                accumX += pullPerSecondX * dt;
                                
                                int pullIntY = (int)Math.Floor(accumY);
                                int pullIntX = (int)Math.Floor(accumX);
                                
                                if (pullIntY > 0 || pullIntX != 0)
                                {
                                    Win32Api.mouse_event(Win32Api.MOUSEEVENTF_MOVE, pullIntX, pullIntY, 0, UIntPtr.Zero);
                                    accumY -= pullIntY;
                                    accumX -= pullIntX;
                                }
                            }
                        }
                        else
                        {
                            wasShooting = false;
                        }
                    }
                    
                    // Wysyłamy zdarzenia w większych paczkach (co 10-15ms, czyli ok. 80-100Hz).
                    // Jeżeli pętla chodzi na 1ms, wysyłamy setki poleceń +1 piksel na sekundę.
                    // Windows Raw Input oraz silnik Unity potrafią gubić tak małe wartości przez co broń "leci do góry".
                    // 12ms to idealny interwał dla makr sprzętowych - mysz "zbiera" ułamek i przesuwa od razu o np. 4-5 pikseli, co gra z pewnością rejestruje.
                    Thread.Sleep(12); 
                }
                catch (Exception)
                {
                    Thread.Sleep(50);
                }
            }
        }
        
        public void Stop()
        {
            _isRunning = false;
        }
    }
}
