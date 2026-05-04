CREATE TABLE User_Account (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('dispatcher', 'rescuer', 'admin')), 
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE Incident (
    incident_id SERIAL PRIMARY KEY,
    incident_type VARCHAR(50) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES User_Account(user_id)
);

CREATE TABLE Operation (
    operation_id SERIAL PRIMARY KEY,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP CHECK (start_date <= CURRENT_TIMESTAMP), 
    status VARCHAR(20) NOT NULL CHECK (status IN ('planned', 'active', 'completed')), 
    incident_id INTEGER REFERENCES Incident(incident_id) NOT NULL 
);

CREATE TABLE Resource (
    resource_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,  
    specialization VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    latitude DECIMAL(9,6) NOT NULL, 
    longitude DECIMAL(9,6) NOT NULL 
);

CREATE TABLE Operation_Resource (
    operation_id INTEGER REFERENCES Operation(operation_id),
    resource_id INTEGER REFERENCES Resource(resource_id),
    PRIMARY KEY (operation_id, resource_id) 
);
