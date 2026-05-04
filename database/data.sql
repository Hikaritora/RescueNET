INSERT INTO User_Account (first_name, last_name, role, login, password_hash) VALUES 
('Mike', 'Administrator', 'admin', 'admin', 'admin123'),            
('John', 'Dispatcher', 'dispatcher', 'dispatcher', 'dispatch123'),   
('Sarah', 'Rescuer', 'rescuer', 'rescuer', 'rescue123');            


INSERT INTO Resource (name, resource_type, specialization, status, is_available, latitude, longitude) VALUES 
('Dr. Emily Chen', 'Medical', 'Emergency Medicine', 'Available', TRUE, 51.02, 17.02), 
('Fire Unit Alpha', 'Unit', 'Fire Response', 'Available', TRUE, 52.07, 18.2),        
('Ambulance A-12', 'Equipment', 'Life Support', 'Available', TRUE, 50.02, 18.1),    
('Fire Truck F-5', 'Equipment', 'Water Pump', 'Available', TRUE, 50.5, 17.7);       

INSERT INTO Incident (incident_type, latitude, longitude, priority, status, user_id) VALUES 
('Medical', 51.107883, 17.038538, 'critical', 'in progress', 2), 
('Fire', 51.112000, 17.055000, 'high', 'reported', 2);    

INSERT INTO Operation (start_date, status, incident_id) VALUES 
(CURRENT_TIMESTAMP, 'active', 1), 
(CURRENT_TIMESTAMP, 'planned', 2); 


INSERT INTO Operation_Resource (operation_id, resource_id) VALUES 
(1, 1),
(1, 3),
(2, 2), 
(2, 4);
