PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS Utilisateurs (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student','technician','admin')),
    department TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    score INTEGER NOT NULL DEFAULT 85 CHECK(score BETWEEN 0 AND 100),
    privilege TEXT NOT NULL DEFAULT 'trusted' CHECK(privilege IN ('restricted','standard','trusted')),
    privilege_override TEXT CHECK(privilege_override IN ('restricted','standard','trusted')),
    blocked_until TEXT,
    blacklisted INTEGER NOT NULL DEFAULT 0 CHECK(blacklisted IN (0,1)),
    audit_log TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS Equipements (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT NOT NULL CHECK(length(trim(category)) > 0),
    description TEXT NOT NULL DEFAULT '',
    total INTEGER NOT NULL CHECK(total >= 0),
    available INTEGER NOT NULL CHECK(available BETWEEN 0 AND total),
    maintenance INTEGER NOT NULL DEFAULT 0 CHECK(maintenance >= 0),
    lost INTEGER NOT NULL DEFAULT 0 CHECK(lost >= 0),
    premium INTEGER NOT NULL DEFAULT 0 CHECK(premium IN (0,1)),
    archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1)),
    CHECK(available + maintenance + lost <= total)
);
CREATE TABLE IF NOT EXISTS Emprunts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Utilisateurs(id) ON DELETE RESTRICT,
    equipment_id INTEGER NOT NULL REFERENCES Equipements(id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK(status IN ('pending','active','returned','rejected','cancelled')),
    requested_at TEXT NOT NULL,
    duration_days INTEGER NOT NULL CHECK(duration_days BETWEEN 1 AND 21),
    borrowed_at TEXT,
    due_date TEXT,
    returned_at TEXT,
    condition TEXT CHECK(condition IN ('good','damaged','lost')),
    approved_by INTEGER REFERENCES Utilisateurs(id),
    returned_by INTEGER REFERENCES Utilisateurs(id),
    decision_reason TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    score_before INTEGER CHECK(score_before BETWEEN 0 AND 100),
    score_after INTEGER CHECK(score_after BETWEEN 0 AND 100),
    score_delta INTEGER,
    late_days INTEGER NOT NULL DEFAULT 0 CHECK(late_days >= 0),
    CHECK(status NOT IN ('active','returned') OR (borrowed_at IS NOT NULL AND due_date IS NOT NULL)),
    CHECK(status != 'returned' OR (returned_at IS NOT NULL AND condition IS NOT NULL)),
    CHECK(due_date IS NULL OR due_date >= borrowed_at),
    CHECK(returned_at IS NULL OR returned_at >= borrowed_at)
);
CREATE INDEX IF NOT EXISTS idx_loans_user_status ON Emprunts(user_id,status);
CREATE INDEX IF NOT EXISTS idx_loans_equipment_status ON Emprunts(equipment_id,status);
CREATE INDEX IF NOT EXISTS idx_loans_due ON Emprunts(status,due_date);
