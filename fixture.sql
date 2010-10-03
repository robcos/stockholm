TRUNCATE TABLE indicator;
INSERT INTO indicator VALUES 
('AAPL','2001-01-01','100.1','110.1', '120.1'),
('AAPL','2001-01-02','200.2','210.2', '220.2'),
('AAPL','2001-01-03','300.3','310.3', '320.3'),
('LUPE','2001-01-01','400.4','410.4', '320.4')
;

TRUNCATE TABLE quote;
INSERT INTO quote VALUES 
('AAPL','2001-01-01','100.1','110.1', '120.1', '130.1', '140.1'),
('AAPL','2001-01-02','200.2','210.2', '220.2', '230.2', '240.2'),
('AAPL','2001-01-03','300.3','310.3', '320.3', '330.3', '340.3'),
('LUPE','2001-01-01','400.4','410.4', '320.4', '430.4', '440.4')
;

TRUNCATE TABLE position;
INSERT INTO position VALUES 
('MILL', 'SEK', 1, '2010-09-09', '2010-09-29', 719.50, 647.0, 99, 99, 30, 647, 1),
('LUPE', 'SEK', 1, '2010-09-28', null, 55,     null,  99, null, 2400, 53, 1),
('AAPL', 'USD', 1, '2010-07-05', null, 259.98, null, 109, null,   15, 234, 1)
;
