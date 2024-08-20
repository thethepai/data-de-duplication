CREATE TABLE articles_info (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    time DATETIME NOT NULL,
    source_name VARCHAR(255),
    source_url VARCHAR(255)
);