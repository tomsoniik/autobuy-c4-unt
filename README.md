# Unturned 777-BUY-bot

Nic tu ni ma

## 📥 Jak używać? (Dla graczy)

Jeśli chcesz tylko używać bota, pobierz skompilowaną aplikację z zakładki **Releases**:

1. Wejdź w [Releases](../../releases) na GitHubie.
2. Pobierz najnowszy plik `autocraft.exe`.
3. Uruchom jako **Administrator** (wymagane, by gra odbierała klawisze).
4. Zaznacz co chcesz kupować.
5. Wejdź do Unturned i wciśnij **F8**.

## 🛠️ Jak skompilować samodzielnie? (Dla deweloperów)

Jeśli chcesz przebudować aplikację lub dodać nowe komendy, oto co musisz zrobić.

**Wymagania:** Python 3.10+

1. Pobierz kod i zainstaluj wymagane biblioteki:

```bash
pip install pydirectinput keyboard pyautogui customtkinter
```

2. Uruchom skrypt bezpośrednio w terminalu (jako Administrator!):

```bash
python autocraft.py
```

### ⚙️ Tworzenie pliku .exe

Wpisz w konsoli:

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole autocraft.py
```

Plik gotowy do udostępnienia znajdziesz w nowym folderze `dist`.
