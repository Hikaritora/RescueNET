
INSERT INTO Uzytkownik (imie, nazwisko, rola, login, haslo) VALUES 
('Mike', 'Administrator', 'admin', 'admin', 'admin123'),
('John', 'Dispatcher', 'dyspozytor', 'dispatcher', 'dispatch123'),
('Sarah', 'Rescuer', 'ratownik', 'rescuer', 'rescue123');


INSERT INTO Zasob (nazwa, typ, specjalizacja, status, dostepnosc) VALUES 
('Dr. Emily Chen', 'Medical', 'Emergency Medicine', 'W akcji', FALSE),
('Ambulance A-12', 'Equipment', NULL, 'W akcji', FALSE),
('Fire Unit Alpha', 'Unit', 'Fire Response', 'Dostępny', TRUE);


INSERT INTO Incydent (typ, lokalizacja, priorytet, status, id_uzytkownika) VALUES 
('Medical', '123 Main St, Downtown', 'krytyczny', 'w toku', 2);


INSERT INTO Operacja (status, id_incydentu) VALUES 
('aktywna', 1);


INSERT INTO Jednostka (id_operacji, id_zasobu) VALUES 
(1, 1), 
(1, 2); 
