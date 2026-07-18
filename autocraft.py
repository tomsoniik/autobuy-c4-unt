import pydirectinput
import time
import threading
import keyboard
import pyautogui
import pyperclip
import customtkinter as ctk
import sys
import os
import ctypes
import gc


# Do OCR
import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract

def get_resource_path(filename):
    try:
        # PyInstaller tworzy ukryty tymczasowy folder dla zasobów i zapisuje go tutaj:
        base_path = sys._MEIPASS
    except Exception:
        # Dla zwykłego uruchamiania z konsoli .py
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

pydirectinput.FAILSAFE = True

# Wewnętrzna pamięć Bota (Zliczanie operacji na ślepo, bez ingerencji w grę)
pamiec_bota = {
    "grenade": 0,
    "wire": 0,
    "glue": 0,
    "c4": 0
}

def press_key(key):
    pydirectinput.keyDown(key)
    time.sleep(0.05)
    pydirectinput.keyUp(key)

def kup_materialy(kup_grenade, kup_wire, kup_glue, cb_update=None):
    global pamiec_bota
    print(">>> Kupowanie zaznaczonych materiałów...")
    komendy = []
    
    # Dodajemy do listy komend i od razu zliczamy we własnej pamięci bota
    if kup_grenade:
        komendy.append('/b 1242 10')
        pamiec_bota["grenade"] += 10
    if kup_wire:
        komendy.append('/b 65 10')
        pamiec_bota["wire"] += 10
    if kup_glue:
        komendy.append('/b glue 10')
        pamiec_bota["glue"] += 10
        
    for komenda in komendy:
        pyperclip.copy(komenda)
        
        press_key('enter')
        time.sleep(0.15) # Czekamy aż gra na pewno otworzy pole czatu
        
        # Szybkie wklejanie komendy z Windowsa (0 ms)
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('v')
        pydirectinput.keyUp('ctrl')
        time.sleep(0.05)
        
        press_key('enter')
        
        # Zmniejszyliśmy bufor po wprowadzeniu wklejania
        time.sleep(0.3)
        
    if komendy:
        print(">>> Materiały kupione!")
        if cb_update:
            cb_update()
            
    time.sleep(0.2)

is_running = False

def uruchom_cykl(kup_grenade, kup_wire, kup_glue, label_status, do_craft, ui_scale, tryb_afk, tryb_vault, vault_name, root, cb_update=None, from_button=False):
    global is_running
    if is_running:
        is_running = False # F8 zadziała jako przycisk STOP
        root.after(0, lambda: label_status.configure(text="Status: Zatrzymywanie... Poczekaj na koniec cyklu.", text_color="red"))
        return
    
    is_running = True
    
    def cykl():
        global is_running
        
        if from_button:
            root.after(0, lambda: label_status.configure(text="Status: Za 5s zaczynamy... Zrób Alt+Tab!", text_color="#F59E0B"))
            for i in range(5, 0, -1):
                if not is_running: return
                time.sleep(1)
        
        while is_running:
            root.after(0, lambda: label_status.configure(text="Status: Kupowanie materiałów...", text_color="#3B82F6"))
            
            kup_materialy(kup_grenade, kup_wire, kup_glue, cb_update)
            if not is_running: break
            
            root.after(0, lambda: label_status.configure(text="Status: Wzrok Bota (Zczytywanie błędów)...", text_color="#F59E0B"))
            if czytaj_ostrzezenia():
                root.after(0, lambda: label_status.configure(text="Status: Zatrzymano! Brak kasy lub miejsca w plecaku.", text_color="red"))
                print(">>> ZATRZYMANO BOTA (OCR WYKRYŁ BŁĄD ZASOBÓW/MIEJSCA) <<<")
                is_running = False
                break
            
            # Jeśli aktywne craftowanie
            if do_craft:
                root.after(0, lambda: label_status.configure(text="Status: Bot craftuje C4...", text_color="#8B5CF6"))
                wykonaj_crafting(ui_scale, cb_update)
                
            if tryb_vault and vault_name:
                root.after(0, lambda: label_status.configure(text=f"Status: Zrzucam do /vault {vault_name}...", text_color="#10B981"))
                odloz_do_vaulta(vault_name)
                
            print(">>> SUKCES! Cykl wykonany.")
            
            if not tryb_afk:
                gc.collect() # Czyszczenie RAM
                break # Wykonaj tylko raz
                
            root.after(0, lambda: label_status.configure(text="Status: AFK (F8 by ZATRZYMAĆ). Kolejny cykl...", text_color="#10B981"))
            
            # Wymuszenie odśmiecania pamięci (Garbage Collector) przed kolejnym cyklem by uniknąć wycieków
            gc.collect()
            time.sleep(1) # Bufor bezpieczeństwa przed kolejnym spamem
            
        root.after(0, lambda: label_status.configure(text="Status: Gotowy. Wciśnij F8 w grze.", text_color="#10B981"))
        is_running = False
        
    threading.Thread(target=cykl, daemon=True).start()

def kalkuluj_pozycje(offset_x, offset_y, ui_scale):
    """
    Na podstawie UnturnedCanvasScaler.cs wiemy, że gra używa ConstantPixelSize
    pomnożonego przez userInterfaceScale. Obliczamy pozycję od środka ekranu.
    """
    screen_w, screen_h = pyautogui.size()
    center_x = screen_w / 2
    center_y = screen_h / 2
    
    x = center_x + (offset_x * ui_scale)
    y = center_y + (offset_y * ui_scale)
    return int(x), int(y)

# Globalne koordynaty, które użytkownik może sobie wpisać (Jeśli kalibracja matematyczna zawodzi przez układ HUD)
CORDS = {
    "search": (-859, -446),    # Offset Paska Wyszukiwania
    "blueprint": (188, -355),  # Offset Pierwszej Receptury C4
    "craft_btn": (250, 200)    # <--- ZOSTAWIONE DOMYŚLNE (Nie podałeś go!)
}

def odloz_do_vaulta(vault_name):
    global is_running
    # Otwiera vault przez czat używając szybkiego schowka
    pyperclip.copy(f"/vault {vault_name}")
    
    press_key('j')
    time.sleep(0.1)
    
    pydirectinput.keyDown('ctrl')
    pydirectinput.press('v')
    pydirectinput.keyUp('ctrl')
    time.sleep(0.05)
    
    press_key('enter')
    time.sleep(1.0) # Czekamy ułamek sekundy (ping), aż otworzy się GUI skrzyni
    
    screen_w, screen_h = pyautogui.size()
    c4_img_path = get_resource_path("c4.png")
    
    # Przeładowana logika: Inteligentny Skaner C4
    if os.path.exists(c4_img_path):
        print(f">>> Używam obrazka {c4_img_path} do precyzyjnego przenoszenia...")
        pydirectinput.keyDown('ctrl')
        time.sleep(0.05)
        
        try:
            # Skanujemy tylko lewą połowę ekranu (tutaj jest EQ)
            region = (0, 0, int(screen_w * 0.5), screen_h)
            
            # Wyszukaj wszystkie wystąpienia c4.png i od razu zrzuć do listy (aby OpenCV nie wisiało w RAM podczas pętli)
            matches = list(pyautogui.locateAllOnScreen(c4_img_path, confidence=0.75, region=region))
            
            for pos in matches:
                if not is_running: break # Zatrzymanie natychmiastowe z klawisza F8
                
                # Kliknij w środek c4
                cx = pos.left + int(pos.width / 2)
                cy = pos.top + int(pos.height / 2)
                
                pydirectinput.moveTo(cx, cy)
                pydirectinput.rightClick()
                time.sleep(0.05)
                
            del matches
            gc.collect()
        except Exception as e:
            print(f">>> Nie znalazłem niczego pasującego do c4.png (lub błąd: {e})")
            
        pydirectinput.keyUp('ctrl')
    else:
        print(">>> Brak pliku c4.png. Używam turbo-skanera siatki na LEWEJ stronie (EQ)...")
        
        start_x = int(screen_w * 0.05)
        end_x = int(screen_w * 0.45)
        start_y = int(screen_h * 0.15)
        end_y = int(screen_h * 0.9)
        
        pydirectinput.keyDown('ctrl')
        time.sleep(0.05)
        
        # C4 to duży item (2x2). Skok co 80 pikseli trafia w niego w 100%, a wykonuje 4x mniej kliknięć
        for y in range(start_y, end_y, 80):
            if not is_running: break
            for x in range(start_x, end_x, 80):
                if not is_running: break
                pydirectinput.moveTo(x, y)
                pydirectinput.rightClick()
                time.sleep(0.01)
                
        pydirectinput.keyUp('ctrl')
    
    time.sleep(0.2)
    # Zamknij GUI vaulta
    if is_running:
        press_key('esc')
    time.sleep(0.5)

def wykonaj_crafting(ui_scale, cb_update=None):
    global pamiec_bota
    press_key('y')
    time.sleep(0.8) # Czekamy ułamek dłużej na wczytanie modeli UI
    
    search_bar_pos = kalkuluj_pozycje(CORDS["search"][0], CORDS["search"][1], ui_scale)
    blueprint_pos = kalkuluj_pozycje(CORDS["blueprint"][0], CORDS["blueprint"][1], ui_scale)

    # --- ETAP 0: Salvage Makeshift Grenade na Raw Explosives ---
    pyautogui.moveTo(search_bar_pos[0], search_bar_pos[1], 0.1)
    pyautogui.click()
    
    press_key('ctrl')
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.write("makeshift", interval=0.01)
    press_key('enter')
    time.sleep(0.3)
    
    pyautogui.moveTo(blueprint_pos[0], blueprint_pos[1], 0.1)
    pydirectinput.keyDown('ctrl')
    time.sleep(0.05)
    pyautogui.click()
    time.sleep(0.05)
    pydirectinput.keyUp('ctrl')
    time.sleep(0.5)

    # --- ETAP 1: Crafting Sticky Grenade ---
    pyautogui.moveTo(search_bar_pos[0], search_bar_pos[1], 0.1)
    pyautogui.click()
    
    press_key('ctrl')
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.write("sticky", interval=0.01)
    press_key('enter')
    time.sleep(0.3)
    
    pyautogui.moveTo(blueprint_pos[0], blueprint_pos[1], 0.1)
    pydirectinput.keyDown('ctrl')
    time.sleep(0.05)
    pyautogui.click()
    time.sleep(0.05)
    pydirectinput.keyUp('ctrl')
    time.sleep(0.5)
    
    # --- ETAP 2: Crafting Demolition Charge ---
    pyautogui.moveTo(search_bar_pos[0], search_bar_pos[1], 0.1)
    pyautogui.click()
    
    press_key('ctrl')
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.write("demolition", interval=0.01)
    press_key('enter')
    time.sleep(0.3)
    
    pyautogui.moveTo(blueprint_pos[0], blueprint_pos[1], 0.1)
    pydirectinput.keyDown('ctrl')
    time.sleep(0.05)
    pyautogui.click()
    time.sleep(0.05)
    pydirectinput.keyUp('ctrl')
    time.sleep(0.5)
    
    press_key('esc')
    time.sleep(0.2)
    
    # Odliczamy uśrednione zasoby z pamięci bota (Przykład: na 1x C4 idzie 2 granaty, 2 druty, 2 kleje)
    # Zależy od wyciągniętych przez bota zasobów Raw Explosives (Craft all zbierze wszystko, ale do testów liczymy statycznie)
    pamiec_bota["grenade"] = max(0, pamiec_bota["grenade"] - 2)
    pamiec_bota["wire"] = max(0, pamiec_bota["wire"] - 2)
    pamiec_bota["glue"] = max(0, pamiec_bota["glue"] - 2)
    pamiec_bota["c4"] += 1
    if cb_update:
        cb_update()

def test_ocr():
    # Pobiera prawy górny róg ekranu (Gdzie często jest HUD gotówki na serwerach)
    try:
        screen_w, screen_h = pyautogui.size()
        region = (screen_w - 300, 20, 280, 100) 
            
        img = ImageGrab.grab(bbox=(region[0], region[1], region[0]+region[2], region[1]+region[3]))
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Prosty preprocessing do polepszenia OCR
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Zastąp swoim pathem do Tesseracta jeśli masz inny
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(thresh, config='--psm 7').strip()
        print(f"Wynik OCR (Prawy górny róg): {text}")
        return text
    except Exception as e:
        print(f"Błąd OCR (Upewnij się, że pobrałeś instalator Tesseract-OCR dla Windows): {e}")
    gc.collect()

def czytaj_ostrzezenia():
    """ 
    Skanuje lewy-dolny róg ekranu w poszukiwaniu błędów serwera. Zoptymalizowano pamięć.
    """
    try:
        screen_w, screen_h = pyautogui.size()
        region = (20, screen_h - 400, 500, 350) 
            
        img = ImageGrab.grab(bbox=(region[0], region[1], region[0]+region[2], region[1]+region[3]))
        img_np = np.array(img)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        img.close()
        del img
        
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        del img_np
        del img_cv
        
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        del gray
        
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(thresh).lower()
        del thresh
        
        bad_words = ["not enough", "money", "funds", "balance", "cannot carry", "no space", "full", "inventory"]
        for word in bad_words:
            if word in text:
                print(f"[OCR] Znaleziono OSTRZEŻENIE z serwera: '{word}'")
                gc.collect()
                return True
                
        gc.collect()
        return False
    except:
        # Ignorujemy błędy (np. brak tesseracta w systemie) - bot poleci w ciemno dalej
        gc.collect()
        return False

def stworz_ui():
    # Nowoczesny Design System (CustomTkinter)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("777client ")
    root.geometry("500x750")
    root.resizable(False, False)
    
    # Hero Title
    title = ctk.CTkLabel(root, text="777 APP by t0mson", font=ctk.CTkFont(family="Inter", size=22, weight="bold"))
    title.pack(pady=(20, 2))
    
    subtitle = ctk.CTkLabel(root, text="", font=ctk.CTkFont(family="Inter", size=12), text_color="gray")
    subtitle.pack(pady=(0, 10))
    
    # Główne zakładki
    tabview = ctk.CTkTabview(root, width=460)
    tabview.pack(pady=5, padx=20, fill="both", expand=True)
    
    tab_crafter = tabview.add("Auto-Crafter C4")
    tab_nowa = tabview.add("Recoil Control")
    tab_ustawienia = tabview.add("Settings")
    
    # Bento Grid-style Frame 1: Materiały
    frame1 = ctk.CTkFrame(tab_crafter, corner_radius=12, fg_color="#1E1E1E")
    frame1.pack(pady=5, padx=10, fill="x")
    
    var_grenade = ctk.BooleanVar(value=True)
    var_wire = ctk.BooleanVar(value=True)
    var_glue = ctk.BooleanVar(value=True)
    
    # Modern Switches
    switch1 = ctk.CTkSwitch(frame1, text="Makeshift Grenade (/b 1242 10)", variable=var_grenade, font=ctk.CTkFont(size=12, weight="bold"))
    switch1.pack(pady=(15, 5), padx=20, anchor="w")
    switch2 = ctk.CTkSwitch(frame1, text="Wire (/b 65 10)", variable=var_wire, font=ctk.CTkFont(size=12, weight="bold"))
    switch2.pack(pady=5, padx=20, anchor="w")
    switch3 = ctk.CTkSwitch(frame1, text="Glue (/b glue 10)", variable=var_glue, font=ctk.CTkFont(size=12, weight="bold"))
    switch3.pack(pady=(5, 15), padx=20, anchor="w")

    # Bento Grid-style Frame 2: Crafting UI
    frame2 = ctk.CTkFrame(tab_crafter, corner_radius=12, fg_color="#1E1E1E")
    frame2.pack(pady=5, padx=10, fill="x")
    
    var_craft = ctk.BooleanVar(value=False)
    switch_craft = ctk.CTkSwitch(frame2, text="Automatyczny Crafting (Wymaga otwartej gry!)", variable=var_craft, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#8B5CF6")
    switch_craft.pack(pady=(15, 5), padx=20, anchor="w")
    
    var_afk = ctk.BooleanVar(value=False)
    switch_afk = ctk.CTkSwitch(frame2, text="Tryb AFK (Nieskończona Pętla, F8 by wyłączyć)", variable=var_afk, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#F59E0B")
    switch_afk.pack(pady=5, padx=20, anchor="w")
    
    vault_frame = ctk.CTkFrame(frame2, fg_color="transparent")
    vault_frame.pack(fill="x", padx=20, pady=(5, 5))
    
    var_vault = ctk.BooleanVar(value=False)
    switch_vault = ctk.CTkSwitch(vault_frame, text="Auto-Zrzut (/vault)", variable=var_vault, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#10B981")
    switch_vault.pack(side="left")
    
    var_vault_name = ctk.StringVar(value="c4")
    vault_entry = ctk.CTkEntry(vault_frame, textvariable=var_vault_name, placeholder_text="Nazwa vaulta", width=80)
    vault_entry.pack(side="right")
    
    scale_frame = ctk.CTkFrame(frame2, fg_color="transparent")
    scale_frame.pack(fill="x", padx=20, pady=(5, 15))
    ctk.CTkLabel(scale_frame, text="Unturned UI Scale (z ustawień gry):", font=ctk.CTkFont(size=11)).pack(side="left")
    
    var_scale = ctk.DoubleVar(value=1.0)
    scale_entry = ctk.CTkEntry(scale_frame, width=50, textvariable=var_scale)
    scale_entry.pack(side="right")
    
    # Bento Grid-style Frame 3: Pamięć i OCR (Teraz w zakładce Ustawienia)
    frame3 = ctk.CTkFrame(tab_ustawienia, corner_radius=12, fg_color="#1E1E1E")
    frame3.pack(pady=10, padx=10, fill="x")
    
    ctk.CTkLabel(frame3, text="Świadomość Bota (Pamięć Wewnętrzna)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#10B981").pack(pady=(10, 5))
    
    lbl_mem_grenade = ctk.CTkLabel(frame3, text="Grenades: 0", font=ctk.CTkFont(size=11))
    lbl_mem_grenade.pack()
    lbl_mem_wire = ctk.CTkLabel(frame3, text="Wire: 0", font=ctk.CTkFont(size=11))
    lbl_mem_wire.pack()
    lbl_mem_glue = ctk.CTkLabel(frame3, text="Glue: 0", font=ctk.CTkFont(size=11))
    lbl_mem_glue.pack()
    lbl_mem_c4 = ctk.CTkLabel(frame3, text="Wyprodukowane C4: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8B5CF6")
    lbl_mem_c4.pack(pady=(5, 10))
    
    lbl_mouse_pos = ctk.CTkLabel(frame3, text="Pozycja myszki (do kalibracji): X: 0, Y: 0", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray")
    lbl_mouse_pos.pack(pady=(5, 5))
    
    def odswiez_ui_pamieci():
        lbl_mem_grenade.configure(text=f"Grenades: {pamiec_bota['grenade']}")
        lbl_mem_wire.configure(text=f"Wire: {pamiec_bota['wire']}")
        lbl_mem_glue.configure(text=f"Glue: {pamiec_bota['glue']}")
        lbl_mem_c4.configure(text=f"Wyprodukowane C4: {pamiec_bota['c4']}")
        
    def btn_test_ocr():
        wynik = test_ocr()
        label_status.configure(text=f"Odczytano (OCR): {wynik}", text_color="#F59E0B")
        
    btn_ocr = ctk.CTkButton(frame3, text="Testuj odczyt ekranu (OCR HUD-a)", fg_color="#F59E0B", hover_color="#D97706", command=btn_test_ocr)
    btn_ocr.pack(pady=(0, 10))
    
    label_status = ctk.CTkLabel(tab_crafter, text="Gotowy. Wciśnij F8 w grze lub Start.", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
    label_status.pack(pady=(10, 5))
    
    ctk.CTkLabel(tab_nowa, text="Recoil Control (Kompensacja Odrzutu)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#EF4444").pack(pady=(15, 5))
    
    var_recoil = ctk.BooleanVar(value=False)
    switch_recoil = ctk.CTkSwitch(tab_nowa, text="Aktywuj Macro", variable=var_recoil, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#EF4444")
    switch_recoil.pack(pady=(10, 10))
    
    lbl_current_mode = ctk.CTkLabel(tab_nowa, text="Aktualny tryb: Z biodra / 3 Osoba (Auto)", text_color="#3B82F6", font=ctk.CTkFont(weight="bold", size=14))
    lbl_current_mode.pack(pady=(0, 10))
    
    var_autodetect = ctk.BooleanVar(value=False)
    switch_autodetect = ctk.CTkSwitch(tab_nowa, text="Auto-Detekcja Broni (Skanowanie Ikonki)", variable=var_autodetect, font=ctk.CTkFont(size=12, weight="bold"), progress_color="#10B981")
    switch_autodetect.pack(pady=(0, 5))
    
    lbl_detected_weapon = ctk.CTkLabel(tab_nowa, text="Wykryta broń: Brak (Ręczne ustawienia)", text_color="#10B981", font=ctk.CTkFont(weight="bold", size=12))
    lbl_detected_weapon.pack(pady=(0, 10))
    
    var_aim_only = ctk.BooleanVar(value=True)
    switch_aim = ctk.CTkSwitch(tab_nowa, text="Działa tylko podczas Celowania (PPM)", variable=var_aim_only, font=ctk.CTkFont(size=12))
    switch_aim.pack(pady=(0, 20))
    
    lbl_pull = ctk.CTkLabel(tab_nowa, text="Siła ściągania PION (Z biodra / 3 osoba): 15.00")
    lbl_pull.pack()
    slider_pull = ctk.CTkSlider(tab_nowa, from_=0.1, to=50.0, number_of_steps=4990, command=lambda v: lbl_pull.configure(text=f"Siła ściągania PION (Z biodra / 3 osoba): {v:.2f}"))
    slider_pull.set(15.0)
    slider_pull.pack(pady=(0, 10))
    
    lbl_pull_scope = ctk.CTkLabel(tab_nowa, text="Siła ściągania PION (Wielki Celownik Scope): 20.00")
    lbl_pull_scope.pack()
    slider_pull_scope = ctk.CTkSlider(tab_nowa, from_=0.1, to=100.0, number_of_steps=9990, command=lambda v: lbl_pull_scope.configure(text=f"Siła ściągania PION (Wielki Celownik Scope): {v:.2f}"))
    slider_pull_scope.set(20.0)
    slider_pull_scope.pack(pady=(0, 20))
    
    # Usunięte nadmiarowe suwaki i skomplikowane ustawienia matematyczne dla czystego interfejsu (Plug & Play)
    lbl_global_mult = ctk.CTkLabel(tab_nowa, text="Korekta siły dla Auto-Detekcji (Zmień tylko jeśli bot ściąga za mocno/słabo): 1.0x", font=ctk.CTkFont(size=11), text_color="gray")
    lbl_global_mult.pack(pady=(15, 0))
    slider_global_mult = ctk.CTkSlider(tab_nowa, from_=0.1, to=5.0, number_of_steps=49, command=lambda v: lbl_global_mult.configure(text=f"Korekta siły dla Auto-Detekcji: {v:.1f}x"))
    slider_global_mult.set(1.0)
    slider_global_mult.pack(pady=(0, 10))
    
    jitter_state = [1]
    is_scope_mode = [False]
    
    recoil_state = {
        "interval": 0.001,
        "pull_hip": 1.0,
        "pull_scope": 3.0,
        "pull_x": 0.0,
        "is_active": False,
        "aim_only": True,
        "auto_x": False,
        "autodetect": False,
        "current_weapon": None,
        "multiplier_hip": 1.0,
        "multiplier_scope": 1.0
    }
    
    # Baza profili broni (możesz tu dodawać kolejne bronie)
    WEAPON_PROFILES = {
        "maplestrike": {"hip": 15, "scope": 14.0},
        "zubeknakov": {"hip": 3.2, "scope": 6.5},
        "heartbreaker": {"hip": 2.0, "scope": 4.0},
        "nightraider": {"hip": 2.8, "scope": 5.5},
        "eaglefire": {"hip": 1.5, "scope": 3.0},
        "peacemaker": {"hip": 1.2, "scope": 2.5}
    }
    
    def weapon_detect_loop():
        while True:
            try:
                # Autodetekcja broni
                if recoil_state.get("autodetect", False):
                    screen_w, screen_h = pyautogui.size()
                    region = (0, int(screen_h * 0.5), screen_w, int(screen_h * 0.5))
                    
                    detected_weapon = None
                    maple_path = get_resource_path("maplestrike.png")
                    
                    if os.path.exists(maple_path):
                        if pyautogui.locateOnScreen(maple_path, confidence=0.75, region=region) is not None:
                            detected_weapon = "maplestrike"
                            
                    if detected_weapon:
                        profile = WEAPON_PROFILES[detected_weapon]
                        recoil_state["pull_hip"] = profile["hip"]
                        recoil_state["pull_scope"] = profile["scope"]
                        recoil_state["current_weapon"] = detected_weapon
                        
                # Czyszczenie pamięci z obrazów
                gc.collect()
                
                time.sleep(0.5) # Skanuje 2 razy na sekundę
            except Exception as e:
                time.sleep(1.0)

    threading.Thread(target=weapon_detect_loop, daemon=True).start()
    
    def scope_detect_loop():
        scope_path = get_resource_path("scope.png")
        if not os.path.exists(scope_path):
            return
            
        scope_img = cv2.imread(scope_path, cv2.IMREAD_GRAYSCALE)
        screen_w, screen_h = pyautogui.size()
        bbox = (int(screen_w * 0.4), int(screen_h * 0.4), int(screen_w * 0.6), int(screen_h * 0.6))
        
        while True:
            try:
                # Tylko skanuj jesli gracz trzyma PPM
                ppm_pressed = ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000
                if ppm_pressed:
                    img = ImageGrab.grab(bbox=bbox)
                    img_np = np.array(img)
                    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                    
                    res = cv2.matchTemplate(img_gray, scope_img, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(res)
                    
                    if max_val > 0.6:
                        is_scope_mode[0] = True
                    else:
                        is_scope_mode[0] = False
                    
                    time.sleep(0.01) # 100 klatek na sekunde - błyskawiczna detekcja!
                else:
                    is_scope_mode[0] = False
                    time.sleep(0.05) # gdy puszczasz PPM, zwalnia żeby oszczędzać CPU
            except Exception as e:
                time.sleep(0.5)

    threading.Thread(target=scope_detect_loop, daemon=True).start()
    
    def recoil_loop():
        is_shooting = False
        accum_y = 0.0
        accum_x = 0.0
        print("Recoil loop started!")
        
        last_time = time.perf_counter()
        
        while True:
            try:
                current_time = time.perf_counter()
                dt = current_time - last_time
                last_time = current_time
                
                if recoil_state["is_active"]:
                    # 0x01 = LPM, 0x02 = PPM
                    lpm_pressed = ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000
                    ppm_pressed = ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000
                    
                    if lpm_pressed:
                        if not is_shooting:
                            is_shooting = True
                            accum_y = 0.0
                            accum_x = 0.0
                            
                        # Sprawdzamy, czy gracz celuje (jeśli wymuszone w ustawieniach)
                        if not recoil_state["aim_only"] or ppm_pressed:
                            # Jesli PPM wcisniete ORAZ obraz celownika jest na ekranie
                            if is_scope_mode[0]:
                                mult = recoil_state.get("multiplier_scope", 1.0)
                                base_pull_y = recoil_state["pull_scope"] * mult
                            else:
                                mult = recoil_state.get("multiplier_hip", 1.0)
                                base_pull_y = recoil_state["pull_hip"] * mult
                            
                            # TRADYCYJNA METODA (DZIAŁA NAJLEPIEJ W UNTURNED):
                            # Wstrzykujemy większą ilość pikseli na raz co określony czas (20ms), 
                            # ponieważ silnik gry (Unity) potrafi ignorować mikro-ruchy rzędu 1 piksela co 1ms.
                            pull_y = int(base_pull_y)
                            pull_x = 0
                            
                            if pull_x != 0 or pull_y != 0:
                                ctypes.windll.user32.mouse_event(0x0001, int(pull_x), int(pull_y), 0, 0)
                                
                            # Wymuszone opóźnienie 20ms (standard dla gier FPS) aby gra zarejestrowała ruch myszy
                            time.sleep(recoil_state.get("interval", 0.02))
                            continue
                    else:
                        if is_shooting:
                            is_shooting = False
                            
                time.sleep(0.005)
            except Exception as e:
                print(f"Recoil Thread Error: {e}")
                time.sleep(0.01)
                
    # Odpalamy jako osobny, potężny sprzętowy wątek, całkowicie niezależny od zacinania się GUI bota
    recoil_thread = threading.Thread(target=recoil_loop, daemon=True)
    recoil_thread.start()
    
    # Bezpieczna aktualizacja w głównym wątku Tkinter
    def update_mouse_loop():
        try:
            # Jeśli autodetect nie jest aktywne, odczytujemy z suwaków
            recoil_state["autodetect"] = bool(var_autodetect.get())
            
            if recoil_state["autodetect"]:
                # Jeśli autodetekcja jest włączona, zaktualizuj suwaki i teksty
                if recoil_state["current_weapon"]:
                    slider_pull.set(recoil_state["pull_hip"])
                    slider_pull_scope.set(recoil_state["pull_scope"])
                    lbl_detected_weapon.configure(text=f"Wykryta broń: {recoil_state['current_weapon'].upper()}", text_color="#3B82F6")
                    
                    lbl_pull.configure(text=f"Siła ściągania PION (Z biodra / 3 osoba): {recoil_state['pull_hip']:.2f}")
                    lbl_pull_scope.configure(text=f"Siła ściągania PION (Wielki Celownik Scope): {recoil_state['pull_scope']:.2f}")
                else:
                    lbl_detected_weapon.configure(text="Wykryta broń: Szukam na HUD...")
                
                
            # Błyskawiczna detekcja PPM (Prawy Przycisk Myszy) dla UI
            ppm_is_down = ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000
            
            if recoil_state.get("autodetect", False):
                if is_scope_mode[0]:
                    lbl_current_mode.configure(text="Aktualny tryb: CELOWNIK SCOPE (Wykryto)", text_color="#EF4444")
                elif ppm_is_down:
                    lbl_current_mode.configure(text="Aktualny tryb: Celowanie Iron Sights / 3 Osoba", text_color="#F59E0B")
                else:
                    lbl_current_mode.configure(text="Aktualny tryb: Z biodra / 3 Osoba", text_color="#3B82F6")
            else:
                recoil_state["pull_hip"] = float(slider_pull.get())
                recoil_state["pull_scope"] = float(slider_pull_scope.get())
                lbl_detected_weapon.configure(text="Wykryta broń: Brak (Ręczne ustawienia)", text_color="#10B981")
                
                if is_scope_mode[0]:
                    lbl_current_mode.configure(text="Aktualny tryb: CELOWNIK SCOPE (Wykryto)", text_color="#EF4444")
                elif ppm_is_down:
                    lbl_current_mode.configure(text="Aktualny tryb: Celowanie Iron Sights / 3 Osoba", text_color="#F59E0B")
                else:
                    lbl_current_mode.configure(text="Aktualny tryb: Z biodra / 3 Osoba", text_color="#3B82F6")
            
            recoil_state["interval"] = 0.02
            recoil_state["pull_x"] = 0.0
            recoil_state["is_active"] = bool(var_recoil.get())
            recoil_state["aim_only"] = bool(var_aim_only.get())
            recoil_state["auto_x"] = False
            
            # Prosty, czysty mnożnik używany głównie do kompensacji Auto-Detekcji jeśli domyślne 15.0 to za mało dla danego gracza
            global_mult = float(slider_global_mult.get())
            recoil_state["multiplier_hip"] = global_mult
            recoil_state["multiplier_scope"] = global_mult
        except Exception as e:
            print(f"GUI Thread Error 1: {e}")
            
        mx, my = pyautogui.position()
        sw, sh = pyautogui.size()
        cx, cy = sw / 2, sh / 2
        offset_x = mx - cx
        offset_y = my - cy
        lbl_mouse_pos.configure(text=f"Mysz: X:{mx} Y:{my} | Offset: {int(offset_x)}, {int(offset_y)}")
        root.after(100, update_mouse_loop)
            
    # Odpalenie pętli od razu
    update_mouse_loop()
    
    def on_start_click():
        try: scale_val = float(var_scale.get())
        except ValueError: scale_val = 1.0
        uruchom_cykl(var_grenade.get(), var_wire.get(), var_glue.get(), label_status, var_craft.get(), scale_val, var_afk.get(), var_vault.get(), var_vault_name.get(), root, cb_update=odswiez_ui_pamieci, from_button=True)
        
    def on_hotkey():
        try: scale_val = float(var_scale.get())
        except ValueError: scale_val = 1.0
        uruchom_cykl(var_grenade.get(), var_wire.get(), var_glue.get(), label_status, var_craft.get(), scale_val, var_afk.get(), var_vault.get(), var_vault_name.get(), root, cb_update=odswiez_ui_pamieci, from_button=False)
        
    keyboard.add_hotkey('f8', on_hotkey)
    
    # Call to Action Button
    btn_start = ctk.CTkButton(
        tab_crafter, 
        text="🚀 START C4 (5s OPÓŹNIENIA)", 
        font=ctk.CTkFont(size=14, weight="bold"), 
        height=45, 
        corner_radius=8,
        command=on_start_click
    )
    btn_start.pack(pady=(5, 5), padx=20, fill="x")
    
    # F8 Hint
    f8_hint = ctk.CTkLabel(tab_crafter, text="Naciskaj F8 bez wychodzenia z gry!", font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B82F6")
    f8_hint.pack()
    
    root.mainloop()

if __name__ == "__main__":
    stworz_ui()
