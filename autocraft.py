import pydirectinput
import time
import threading
import keyboard
import pyautogui
import customtkinter as ctk

pydirectinput.FAILSAFE = True

def press_key(key):
    pydirectinput.keyDown(key)
    time.sleep(0.05)
    pydirectinput.keyUp(key)

def kup_materialy(kup_grenade, kup_wire, kup_glue):
    print(">>> Kupowanie zaznaczonych materiałów...")
    komendy = []
    if kup_grenade:
        komendy.append('/b 1242 10')
    if kup_wire:
        komendy.append('/b 65 10')
    if kup_glue:
        komendy.append('/b glue 10')
        
    for komenda in komendy:
        press_key('enter')
        time.sleep(0.1)
        pyautogui.write(komenda, interval=0.01)
        press_key('enter')
        time.sleep(0.3)
        
    if komendy:
        print(">>> Materiały kupione!")
    time.sleep(0.5)

is_running = False

def uruchom_cykl(kup_grenade, kup_wire, kup_glue, label_status, from_button=False):
    global is_running
    if is_running:
        return
    
    is_running = True
    
    def cykl():
        global is_running
        
        if from_button:
            label_status.configure(text="Status: Za 5s zaczynamy... Zrób Alt+Tab!", text_color="#F59E0B")
            for i in range(5, 0, -1):
                time.sleep(1)
        
        label_status.configure(text="Status: Bot kupuje...", text_color="#3B82F6")
        
        kup_materialy(kup_grenade, kup_wire, kup_glue)
        
        print(">>> SUKCES! Cykl kupowania wykonany.")
        label_status.configure(text="Status: Gotowy. Wciśnij F8 w grze.", text_color="#10B981")
        is_running = False
        
    threading.Thread(target=cykl, daemon=True).start()

def stworz_ui():
    # Nowoczesny Design System (CustomTkinter)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Unturned Auto-Buyer 777")
    root.geometry("450x420")
    root.resizable(False, False)
    
    # Hero Title
    title = ctk.CTkLabel(root, text="Unturned Auto-Buyer", font=ctk.CTkFont(family="Inter", size=24, weight="bold"))
    title.pack(pady=(25, 2))
    
    subtitle = ctk.CTkLabel(root, text="Błyskawiczne kupowanie materiałów w tle", font=ctk.CTkFont(family="Inter", size=12), text_color="gray")
    subtitle.pack(pady=(0, 20))
    
    # Bento Grid-style Frame
    frame = ctk.CTkFrame(root, corner_radius=12, fg_color="#1E1E1E")
    frame.pack(pady=10, padx=30, fill="both", expand=True)
    
    var_grenade = ctk.BooleanVar(value=True)
    var_wire = ctk.BooleanVar(value=True)
    var_glue = ctk.BooleanVar(value=True)
    
    # Modern Switches
    switch1 = ctk.CTkSwitch(frame, text="Makeshift Grenade (/b 1242 10)", variable=var_grenade, font=ctk.CTkFont(size=13, weight="bold"))
    switch1.pack(pady=(20, 10), padx=25, anchor="w")
    
    switch2 = ctk.CTkSwitch(frame, text="Wire (/b 65 10)", variable=var_wire, font=ctk.CTkFont(size=13, weight="bold"))
    switch2.pack(pady=10, padx=25, anchor="w")
    
    switch3 = ctk.CTkSwitch(frame, text="Glue (/b glue 10)", variable=var_glue, font=ctk.CTkFont(size=13, weight="bold"))
    switch3.pack(pady=(10, 20), padx=25, anchor="w")
    
    label_status = ctk.CTkLabel(root, text="Gotowy. Wciśnij F8 w grze lub Start.", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
    
    def on_start_click():
        uruchom_cykl(var_grenade.get(), var_wire.get(), var_glue.get(), label_status, from_button=True)
        
    def on_hotkey():
        uruchom_cykl(var_grenade.get(), var_wire.get(), var_glue.get(), label_status, from_button=False)
        
    keyboard.add_hotkey('f8', on_hotkey)
    
    # Call to Action Button
    btn_start = ctk.CTkButton(
        root, 
        text="🚀 START (5s OPÓŹNIENIA)", 
        font=ctk.CTkFont(size=14, weight="bold"), 
        height=45, 
        corner_radius=8,
        command=on_start_click
    )
    btn_start.pack(pady=(15, 5), padx=50, fill="x")
    
    # F8 Hint
    f8_hint = ctk.CTkLabel(root, text="Naciskaj F8 bez wychodzenia z gry!", font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B82F6")
    f8_hint.pack()
    
    label_status.pack(side="bottom", pady=15)
    
    root.mainloop()

if __name__ == "__main__":
    stworz_ui()
