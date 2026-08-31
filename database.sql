CREATE DATABASE personal_finance;

USE personal_finance;

CREATE TABLE finance (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    transaction_type VARCHAR(20),
    amount DECIMAL(10,2),
    category VARCHAR(50),
    description VARCHAR(50),
    payment_method VARCHAR(30)
);