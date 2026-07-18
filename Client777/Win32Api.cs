using System;
using System.Runtime.InteropServices;

namespace Client777
{
    public static class Win32Api
    {
        [DllImport("user32.dll")]
        public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo);

        [DllImport("user32.dll")]
        public static extern short GetAsyncKeyState(int vKey);

        [DllImport("user32.dll", SetLastError = true)]
        public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        [DllImport("user32.dll")]
        public static extern bool SetCursorPos(int X, int Y);

        [DllImport("user32.dll")]
        public static extern bool GetCursorPos(out POINT lpPoint);

        [DllImport("user32.dll")]
        public static extern int GetSystemMetrics(int nIndex);

        [StructLayout(LayoutKind.Sequential)]
        public struct POINT
        {
            public int X;
            public int Y;
        }

        public const uint MOUSEEVENTF_MOVE = 0x0001;
        public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
        public const uint MOUSEEVENTF_LEFTUP = 0x0004;
        public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
        public const uint MOUSEEVENTF_RIGHTUP = 0x0010;

        public const int VK_LBUTTON = 0x01;
        public const int VK_RBUTTON = 0x02;
        public const int VK_F8 = 0x77;
        public const int VK_CONTROL = 0x11;
        public const int VK_RETURN = 0x0D;

        // Input struct for SendInput
        [StructLayout(LayoutKind.Sequential)]
        public struct INPUT
        {
            public uint type;
            public InputUnion u;
            public static int Size => Marshal.SizeOf(typeof(INPUT));
        }

        [StructLayout(LayoutKind.Explicit)]
        public struct InputUnion
        {
            [FieldOffset(0)] public MOUSEINPUT mi;
            [FieldOffset(0)] public KEYBDINPUT ki;
            [FieldOffset(0)] public HARDWAREINPUT hi;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct MOUSEINPUT
        {
            public int dx;
            public int dy;
            public uint mouseData;
            public uint dwFlags;
            public uint time;
            public UIntPtr dwExtraInfo;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct KEYBDINPUT
        {
            public ushort wVk;
            public ushort wScan;
            public uint dwFlags;
            public uint time;
            public UIntPtr dwExtraInfo;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct HARDWAREINPUT
        {
            public uint uMsg;
            public ushort wParamL;
            public ushort wParamH;
        }

        public const uint INPUT_MOUSE = 0;
        public const uint INPUT_KEYBOARD = 1;
        public const uint INPUT_HARDWARE = 2;
        public const uint KEYEVENTF_KEYUP = 0x0002;
        public const uint KEYEVENTF_UNICODE = 0x0004;

        public static void PressKey(ushort key)
        {
            INPUT[] inputs = new INPUT[2];

            inputs[0] = new INPUT { type = INPUT_KEYBOARD };
            inputs[0].u.ki.wVk = key;

            inputs[1] = new INPUT { type = INPUT_KEYBOARD };
            inputs[1].u.ki.wVk = key;
            inputs[1].u.ki.dwFlags = KEYEVENTF_KEYUP;

            SendInput((uint)inputs.Length, inputs, INPUT.Size);
        }

        public static void KeyDown(ushort key)
        {
            INPUT[] inputs = new INPUT[1];
            inputs[0] = new INPUT { type = INPUT_KEYBOARD };
            inputs[0].u.ki.wVk = key;
            SendInput(1, inputs, INPUT.Size);
        }

        public static void KeyUp(ushort key)
        {
            INPUT[] inputs = new INPUT[1];
            inputs[0] = new INPUT { type = INPUT_KEYBOARD };
            inputs[0].u.ki.wVk = key;
            inputs[0].u.ki.dwFlags = KEYEVENTF_KEYUP;
            SendInput(1, inputs, INPUT.Size);
        }

        public static void SendString(string text)
        {
            foreach (char c in text)
            {
                INPUT[] inputs = new INPUT[2];
                inputs[0] = new INPUT { type = INPUT_KEYBOARD };
                inputs[0].u.ki.wScan = c;
                inputs[0].u.ki.dwFlags = KEYEVENTF_UNICODE;
                
                inputs[1] = new INPUT { type = INPUT_KEYBOARD };
                inputs[1].u.ki.wScan = c;
                inputs[1].u.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP;
                
                SendInput((uint)inputs.Length, inputs, INPUT.Size);
            }
        }
    }
}
