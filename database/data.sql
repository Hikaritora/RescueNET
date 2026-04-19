
INSERT INTO uzytkownik (imie, nazwisko, rola, login, haslo) VALUES 
('Mike', 'Administrator', 'admin', 'admin', 'admin123'),           
('John', 'Dispatcher', 'dyspozytor', 'dispatcher', 'dispatch123'),  
('Sarah', 'Rescuer', 'ratownik', 'rescuer', 'rescue123');           


INSERT INTO zasob (nazwa, typ, specjalizacja, status, dostepnosc) VALUES 
('Dr. Emily Chen', 'Medical', 'Emergency Medicine', 'Available', TRUE), 
('Fire Unit Alpha', 'Unit', 'Fire Response', 'Available', TRUE),        
('Ambulance A-12', 'Equipment', 'Life Support', 'Available', TRUE),    
('Fire Truck F-5', 'Equipment', 'Water Pump', 'Available', TRUE);       


INSERT INTO incydent (typ, lat, lng, priorytet, status, id_uzytkownika) VALUES 
('Medical', 51.107883, 17.038538, 'krytyczny', 'w toku', 2), 
('Fire', 51.112000, 17.055000, 'wysoki', 'zgłoszony', 2);    


INSERT INTO operacja (data_rozpoczecia, status, id_incydentu) VALUES 
(CURRENT_TIMESTAMP, 'aktywna', 1), 
(CURRENT_TIMESTAMP, 'planowana', 2); 


INSERT INTO jednostka (id_operacji, id_zasobu) VALUES 
(1, 1),
(1, 3),
(2, 2), 
(2, 4); 
