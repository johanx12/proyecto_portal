PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL,
 email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 role TEXT NOT NULL DEFAULT 'cliente' CHECK(role IN ('cliente','admin'))
);
CREATE TABLE IF NOT EXISTS tickets (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES users(id),
 subject TEXT NOT NULL,
 category TEXT NOT NULL CHECK(category IN ('Consulta','Reclamo','Soporte','Sugerencia')),
 description TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'Pendiente' CHECK(status IN ('Pendiente','En proceso','Resuelta')),
 created_at TEXT NOT NULL,
 resolved_at TEXT
);
CREATE TABLE IF NOT EXISTS responses (
 id INTEGER PRIMARY KEY,
 ticket_id INTEGER NOT NULL REFERENCES tickets(id),
 user_id INTEGER NOT NULL REFERENCES users(id),
 body TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('Pendiente','En proceso','Resuelta')),
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tickets_month ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_responses_ticket ON responses(ticket_id);
