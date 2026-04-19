
CREATE TABLE Uzytkownik (
    id_uzytkownika SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    rola VARCHAR(20) NOT NULL CHECK (rola IN ('dyspozytor', 'ratownik', 'admin')), 
    login VARCHAR(50) UNIQUE NOT NULL,
    haslo VARCHAR(255) NOT NULL
);

CREATE TABLE Incydent (
    id_incydentu SERIAL PRIMARY KEY,
    typ VARCHAR(50) NOT NULL,
    lat DECIMAL(9,6) NOT NULL, -- Szerokość geograficzna
    lng DECIMAL(9,6) NOT NULL, -- Długość geograficzna
    priorytet VARCHAR(10) NOT NULL CHECK (priorytet IN ('niski', 'średni', 'wysoki', 'krytyczny')),
    status VARCHAR(20) NOT NULL,
    id_uzytkownika INTEGER REFERENCES Uzytkownik(id_uzytkownika)
);


CREATE TABLE Operacja (
    id_operacji SERIAL PRIMARY KEY,
    data_rozpoczecia TIMESTAMP DEFAULT CURRENT_TIMESTAMP CHECK (data_rozpoczecia <= CURRENT_TIMESTAMP), 
    status VARCHAR(20) NOT NULL CHECK (status IN ('planowana', 'aktywna', 'zakończona')), 
    id_incydentu INTEGER REFERENCES Incydent(id_incydentu) NOT NULL 
);


CREATE TABLE Zasob (
    id_zasobu SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    typ VARCHAR(50) NOT NULL, -- np. karetka, straż 
    specjalizacja VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    dostepnosc BOOLEAN NOT NULL DEFAULT TRUE 
);


CREATE TABLE Jednostka (
    id_operacji INTEGER REFERENCES Operacja(id_operacji),
    id_zasobu INTEGER REFERENCES Zasob(id_zasobu),
    PRIMARY KEY (id_operacji, id_zasobu) 
);
