using System;
using System.Threading;

namespace Client777
{
    public class AutoCrafter
    {
        private Thread _crafterThread;
        private bool _isRunning;
        
        public bool IsActive { get; set; } = false;
        public string BuyCommand { get; set; } = "/b 1054 5";
        
        public AutoCrafter()
        {
            _isRunning = true;
            _crafterThread = new Thread(CrafterLoop);
            _crafterThread.IsBackground = true;
            _crafterThread.Start();
        }

        private void CrafterLoop()
        {
            bool wasF8Pressed = false;
            
            while (_isRunning)
            {
                try
                {
                    if (IsActive)
                    {
                        short f8State = Win32Api.GetAsyncKeyState(Win32Api.VK_F8);
                        bool isF8Pressed = (f8State & 0x8000) != 0;

                        if (isF8Pressed && !wasF8Pressed)
                        {
                            wasF8Pressed = true;
                            ExecuteBuySequence();
                        }
                        else if (!isF8Pressed)
                        {
                            wasF8Pressed = false;
                        }
                    }
                    
                    Thread.Sleep(20);
                }
                catch (Exception)
                {
                    Thread.Sleep(50);
                }
            }
        }
        
        private void ExecuteBuySequence()
        {
            // Otwiera czat symulując klawisz Enter
            Win32Api.PressKey(Win32Api.VK_RETURN);
            Thread.Sleep(80); // Czas na pokazanie się okna czatu w grze
            
            // Wpisuje komendę przez pętlę symulacji Unicode (odporne na lagi i zabezpieczenia schowka)
            Win32Api.SendString(BuyCommand);
            Thread.Sleep(40);
            
            // Wysyła komendę Enterem
            Win32Api.PressKey(Win32Api.VK_RETURN);
            
            // Dodano opóźnienie aby zapobiec kickom z serwera za "spam" w konsoli/czacie
            Thread.Sleep(250); 
            
            // Po udanym zakupie, wykonaj crafting C4
            ExecuteCraftingSequence();
        }

        private void ClickCenterOffset(int offsetX, int offsetY)
        {
            int screenW = Win32Api.GetSystemMetrics(0); // SM_CXSCREEN
            int screenH = Win32Api.GetSystemMetrics(1); // SM_CYSCREEN
            
            int targetX = (screenW / 2) + offsetX;
            int targetY = (screenH / 2) + offsetY;
            
            Win32Api.SetCursorPos(targetX, targetY);
            Thread.Sleep(50);
            
            Win32Api.mouse_event(Win32Api.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
            Thread.Sleep(50);
            Win32Api.mouse_event(Win32Api.MOUSEEVENTF_LEFTUP, 0, 0, 0, UIntPtr.Zero);
            Thread.Sleep(50);
        }

        private void ExecuteCraftingSequence()
        {
            // Otwórz menu craftingu
            Win32Api.PressKey(0x59); // Klawisz 'Y'
            Thread.Sleep(800); // Gra musi wczytać obiekty UI

            // ETAP 0: Salvage Makeshift Grenade na Raw Explosives
            ClickCenterOffset(-859, -446);
            Win32Api.KeyDown(Win32Api.VK_CONTROL);
            Win32Api.PressKey(0x41); // A
            Win32Api.KeyUp(Win32Api.VK_CONTROL);
            Thread.Sleep(100);
            
            Win32Api.SendString("makeshift");
            Win32Api.PressKey(Win32Api.VK_RETURN);
            Thread.Sleep(300);

            Win32Api.KeyDown(Win32Api.VK_CONTROL);
            ClickCenterOffset(188, -355);
            Win32Api.KeyUp(Win32Api.VK_CONTROL);
            Thread.Sleep(500);

            // ETAP 1: Crafting Sticky Grenade
            // 1. Klik w pole wyszukiwania (offset np. -859, -446 dla 1080p przy skali 1.0)
            ClickCenterOffset(-859, -446);
            
            // Wyczyść pole wyszukiwania (Ctrl+A)
            Win32Api.KeyDown(Win32Api.VK_CONTROL);
            Win32Api.PressKey(0x41); // A
            Win32Api.KeyUp(Win32Api.VK_CONTROL);
            Thread.Sleep(100);
            
            Win32Api.SendString("sticky");
            Win32Api.PressKey(Win32Api.VK_RETURN);
            Thread.Sleep(300);

            // 2. Wciśnij Ctrl i Kliknij w pierwszą recepturę (Craft All)
            Win32Api.KeyDown(Win32Api.VK_CONTROL);
            ClickCenterOffset(188, -355);
            Win32Api.KeyUp(Win32Api.VK_CONTROL);
            Thread.Sleep(500);

            // ETAP 2: Crafting Demolition Charge
            ClickCenterOffset(-859, -446);
            Win32Api.KeyDown(Win32Api.VK_CONTROL);
            Win32Api.PressKey(0x41);
            Win32Api.KeyUp(Win32Api.VK_CONTROL);
            Thread.Sleep(100);
            
            Win32Api.SendString("demolition");
            Win32Api.PressKey(Win32Api.VK_RETURN);
            Thread.Sleep(300);

            Win32Api.KeyDown(Win32Api.VK_CONTROL);
            ClickCenterOffset(188, -355);
            Win32Api.KeyUp(Win32Api.VK_CONTROL);
            Thread.Sleep(500);

            // Zamknij UI
            Win32Api.PressKey(0x1B); // ESC
            Thread.Sleep(200);
        }

        public void Stop()
        {
            _isRunning = false;
        }
    }
}
