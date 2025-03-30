# Globalworth-Api

## Opis projektu

Aplikacja ** Globalworth-Api ** to narzędzie służące do monitorowania zużycia zasobów (energii elektrycznej i wody) w budynkach biurowych, w kontekście liczby obecnych pracowników. Dane wykorzystywane w aplikacji umożliwiają analizę efektywności zużycia zasobów na osobę, porównanie ich z poprzednimi okresami oraz anonimowe zestawienie z innymi firmami znajdującymi się w tym samym budynku.

## Funkcjonalności

- Pobieranie danych o zużyciu energii i wody.
- Zbieranie informacji o liczbie osób obecnych w budynku na podstawie bramek wejściowych i wyjściowych.
- Obliczanie średniego zużycia zasobów na osobę.
- Porównanie aktualnych wyników z wcześniejszymi danymi.
- Anonimowe porównania między firmami znajdującymi się w tym samym budynku.

## Architektura systemu

- **API Backend** – udostępnia dane zużycia zasobów i obecności pracowników.
- **Baza danych** – przechowuje dane historyczne wraz z timestampami wejść i wyjść.
- **Moduł analityczny** – oblicza zużycie na osobę oraz generuje raporty porównawcze.

## Zbieranie danych

Dane o liczbie osób są gromadzone na podstawie rejestrowanych **wejść i wyjść przez bramki**. Każde zdarzenie zawiera:
- unikalny identyfikator (anonimowy),
- timestamp wejścia/wyjścia.

Na podstawie tych danych system może precyzyjnie określić liczbę obecnych osób w dowolnym przedziale czasowym.



