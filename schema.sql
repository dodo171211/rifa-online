-- Rifa online: numeros de 1 a 700
-- SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS compradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL,
    email TEXT,
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS numeros_rifa (
    numero INTEGER PRIMARY KEY CHECK (numero >= 1 AND numero <= 700),
    status TEXT NOT NULL DEFAULT 'disponivel'
        CHECK (status IN ('disponivel', 'reservado')),
    comprador_id INTEGER REFERENCES compradores(id) ON DELETE SET NULL,
    reservado_em TEXT
);

CREATE INDEX IF NOT EXISTS idx_numeros_status ON numeros_rifa (status);
CREATE INDEX IF NOT EXISTS idx_numeros_comprador ON numeros_rifa (comprador_id);

CREATE VIEW IF NOT EXISTS vw_compras AS
SELECT
    c.id,
    c.nome,
    c.telefone,
    c.email,
    c.criado_em,
    GROUP_CONCAT(n.numero, ', ') AS numeros,
    COUNT(n.numero) AS quantidade_numeros
FROM compradores c
JOIN numeros_rifa n ON n.comprador_id = c.id AND n.status = 'reservado'
GROUP BY c.id, c.nome, c.telefone, c.email, c.criado_em
ORDER BY c.criado_em DESC;
