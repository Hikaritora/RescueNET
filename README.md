# RescueNET
## TODO
~~1. przycisk assign i details usunac w resources z danego zasobu~~

~~2. zamiast details na zasobie dodac koordynaty pod current status~~

~~3. usunac avg response z reports and archive~~

~~4. poprawic pozycje pie charta w reports and archive (za nisko jest i wychodzi poza pole)~~

~~5. dodac lokalizacje incydentu w archiwum~~

~~6. zmienic w dashboardzie "total reports" na "total incidents"~~

~~7. zmienic w UI w incidents w priority na angielski (e.g. krytyczny -> critical)~~

~~8. upewnic sie czy w danym incydencie widac kto zreportowal go?~~

~~9. dodac mozliwosc tworzenia zasobow jako admin w GUI zamiast tylko przez django administration~~

~~10. w dodawaniu incydentu typ moze nie wpisywac recznie tylko dropdown list i jakies częste bo wtedy statystyki sie beda zgadzac i nie bedzie np 2 roznych typow "incydent drogowy" i "Incydent drogowy"~~

~~11. dodac daty zgloszenia do incydentow~~

~~12. dodac do incydentu pole na notatki od osoby tworzącej zgloszenie~~

~~13. dodac do incydentu podczas tworzenia mapę na ktorej sie postawi pinezke zamiast wpisywania manualnego koordynatow incydentu~~

~~14. w sekcji new incident przetlumaczyc na angielski rzeczy i rozwinac lat i lng na pelne slowa~~

~~15. W incydencie status in progress nie dziala? to znaczy istnieje pewnie w bazie danych ale nie przypisuje sie nigdy, a chyba powinien jak przypiszemy jakies jednostki~~

16. wygenerowac duza baze danych 


Kolejnosc do zmian:

~~Etap 1 - 1-8, 14 - HTML + forms.py~~

~~Etap 2 — 11, 12 — migracje: data zgłoszenia + notatki~~ 

~~Etap 3 — 10 - dropdown typów incydentu~~

~~Etap 4 — 15 — views.py: status "in progress" przy przypisaniu zasobu~~

~~Etap 5 — 9 — nowy widok/formularz/szablon: tworzenie zasobu przez GUI~~

~~Etap 6 — 13 — mapa przy tworzeniu incydentu~~

Etap 7 — 16 — generowanie dużej bazy danych

Etap 8 (opcjonalnie) poprawic pliki .sql (dodac date zgloszenia i notatki do incydentu)


