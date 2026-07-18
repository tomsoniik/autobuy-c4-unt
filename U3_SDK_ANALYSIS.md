# Analiza Kodu Źródłowego Unturned (U3-SDK) a Optymalizacja AutoCrafting

Ten dokument podsumowuje, jakie korzyści przynosi analiza kodu źródłowego (udostępnionego oficjalnie na GitHubie) dla optymalizacji naszego bota do craftingu (`autocraft.py`) i dlaczego jest to obecnie najbezpieczniejsza i najbardziej stabilna ścieżka.

## 1. Perfekcyjny Chat Timing (Ominięcie kicków i opóźnień)
W pliku `ChatManager.cs` (linie ~397-410) widzimy wyraźne limity nakładane przez serwer:

```csharp
[SteamCall(ESteamCallValidation.SERVERSIDE, ratelimitHz = 15, legacyName = nameof(askChat))]
public static void ReceiveChatRequest(in ServerInvocationContext context, byte flags, string text)
{
    // ...
    if (Time.realtimeSinceStartup - player.lastChat < chatrate)
    {
        return;
    }
    player.lastChat = Time.realtimeSinceStartup;
    // ...
}
```
* **Co to oznacza?** Gra posiada globalną zmienną `chatrate` (domyślnie `0.25f` - linia 74) ograniczającą częstotliwość wiadomości. Ponadto SteamCall ma `ratelimitHz = 15` (15 wiadomości na sekundę).
* **Zastosowanie dla Bota:** Wiemy teraz z całą pewnością, że wpisywanie komend na czacie szybciej niż raz na 0.25 sekundy jest bezcelowe (serwer odrzuci komendę ignorując pakiet). W bocie ustalamy `time.sleep(0.26)` jako nasz absolutnie bezpieczny i maksymalnie szybki cooldown przy wpisywaniu komend. Pozwala to porzucić zgadywanie i zoptymalizować czas wykonywania skryptu.

## 2. Rozszyfrowanie UI (Kalkulacja dokładnych koordynatów)
W kodzie interfejsu (np. `PlayerDashboardCraftingUI.cs`) znajduje się precyzyjna logika wyświetlania list receptur:
* Zamiast szukać przycisków wizyjnie na pulpicie za pomocą mętnych koordynatów absolutnych (które ulegają zepsuciu po zmianie rozdzielczości lub parametru "UI Scale"), możemy przeanalizować pętle układające rzędy i kolumny siatki craftingu.
* Pozwala to zaimplementować funkcję, która np. prosi usera tylko o jego "UI Scale" (z opcji gry) oraz rozdzielczość ekranu, po czym w skrypcie Python **matematycznie wylicza, w którym pikselu na danym ekranie będzie konkretny slot**.  Czyni to makro uniwersalnym bez używania bibliotek AI odczytujących obraz.

## 3. Ukryte furtki (Bindy, ominięcia)
* Kod źródłowy (jak `PlayerDashboardCraftingUI.cs`) odsłania metody używane przez sam interfejs (`sendChat`, systemy tagów itd). 
* Z analizy wynika, że ominięcie interfejsu (pisanie od razu do serwera) wymaga pełnego parsowania Steam API - a to stwarza ogromne ryzyko zbanowania (metoda `ClientStaticMethod.Get...`). 
* Dowodzimy więc słuszności obranej metody symulowania fizycznej klawiatury. Kod pokazuje nam jednak, że do serwera wysyłany jest goły ciąg znaków, co upewnia nas, że samo wpisywanie "na ślepo" jest traktowane tak samo jak użycie myszki. Zoptymalizujemy wklejanie (PyAutoGUI potrafi wysłać całe zdanie błyskawicznie, pomijając wizualne stukanie po klawiszu).

## 4. Baza do Mapy Pamięci (Gdybyś zechciał rozszerzyć w stronę "Memory Reading")
* `ChatManager.cs` upewnił nas o istnieniu silnie obwarowanych klas `SteamPlayer` i `PlayerID`. 
* Struktury te są w pamięci Windowsa ułożone regularnie. Gdybyśmy chcieli wzbogacić bota o sprawdzanie portfela, posiadanie repozytorium kodu sprawia, że znalezienie tych zmiennych to wpisanie jednego offsetu klas do skryptu, co otwiera wrota na inteligentne boty weryfikujące, ile C4 już mają, *zanim* wezmą się za następne kupowanie, zmniejszając zużycie surowców.
