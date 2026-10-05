-- =============================================================================
-- HOSTELOS - RELATIONAL DATABASE SCHEMA DEFINITION (DDL)
-- =============================================================================
-- Course: 23CSE202 - Database Management Systems
-- Project: Hostel Room Allocation and Complaint Management System
-- Group: C9
--
-- NORMALIZATION:
--   The schema is designed in Third Normal Form (3NF):
--   1NF: All attribute values are atomic; primary keys defined for each table.
--   2NF: No partial functional dependencies (all non-key attributes fully depend
--        on the entire primary key).
--   3NF: No transitive functional dependencies (non-key attributes do not depend
--        on other non-key attributes; room details are normalized into `rooms`).
--
-- INTEGRITY CONSTRAINTS:
--   - Entity Integrity: Primary Keys (id)
--   - Referential Integrity: Foreign Keys with ON DELETE CASCADE / SET NULL
--   - Domain Integrity: CHECK constraints and ENUM-style domain values
--   - Unique Key Constraints: email, roll_number, room_number, ticket_number, pass_code
-- =============================================================================

-- Clean existing tables if resetting
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;

-- -----------------------------------------------------------------------------
-- 1. TABLE: rooms (Accommodation Entities)
-- -----------------------------------------------------------------------------
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(50) NOT NULL UNIQUE,
    block VARCHAR(50) NOT NULL,
    room_type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 2 CHECK (capacity IN (1, 2, 3, 4)),
    has_ac BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. TABLE: users (Students, Wardens, Institute Heads)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('STUDENT', 'WARDEN', 'INSTITUTE_HEAD')),
    roll_number VARCHAR(50) UNIQUE,
    phone VARCHAR(50),
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. TABLE: complaints (Maintenance Tickets)
-- -----------------------------------------------------------------------------
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'Plumbing',
        'Electrical & Lighting',
        'Internet Connectivity',
        'Carpentry / Furniture',
        'Housekeeping',
        'Other'
    )),
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    urgency VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (urgency IN ('High', 'Medium', 'Low')),
    status VARCHAR(50) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Escalated', 'Resolved')),
    assigned_staff VARCHAR(255),
    resolution_notes TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- -----------------------------------------------------------------------------
-- 4. TABLE: leave_requests (Out-station Gate Passes)
-- -----------------------------------------------------------------------------
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    pass_code VARCHAR(50) NOT NULL UNIQUE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    leave_type VARCHAR(50) NOT NULL CHECK (leave_type IN ('Weekend outing', 'Emergency leave', 'Vacation')),
    departure_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP NOT NULL,
    destination VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    emergency_contact VARCHAR(50) NOT NULL,
    parent_consent BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN (
        'Pending',
        'Approved',
        'Validated',
        'Rejected',
        'Checked Out',
        'Returned'
    )),
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 5. TABLE: attendance (Daily Night Roll-Call Roster)
-- -----------------------------------------------------------------------------
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Present' CHECK (status IN ('Present', 'Absent', 'Late / Permitted')),
    notes VARCHAR(255),
    marked_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_date_attendance UNIQUE (student_id, date)
);

-- =============================================================================
-- PERFORMANCE INDEXES (B-Tree)
-- =============================================================================
CREATE INDEX idx_users_email ON users(LOWER(email));
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_room_id ON users(room_id);

CREATE INDEX idx_rooms_block ON rooms(block);
CREATE INDEX idx_rooms_room_number ON rooms(room_number);

CREATE INDEX idx_complaints_ticket_number ON complaints(ticket_number);
CREATE INDEX idx_complaints_student_id ON complaints(student_id);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_category ON complaints(category);

CREATE INDEX idx_leave_requests_pass_code ON leave_requests(pass_code);
CREATE INDEX idx_leave_requests_student_id ON leave_requests(student_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);

CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);

-- =============================================================================
-- RELATIONAL DATABASE VIEWS (FOR REPORTING & AUDITING)
-- =============================================================================

-- View 1: Room Occupancy Statistics per Room
CREATE OR REPLACE VIEW v_room_occupancy AS
SELECT
    r.id AS room_id,
    r.room_number,
    r.block,
    r.room_type,
    r.capacity,
    COUNT(u.id) AS occupied_beds,
    (r.capacity - COUNT(u.id)) AS vacant_beds,
    CASE
        WHEN COUNT(u.id) >= r.capacity THEN 'Full'
        WHEN COUNT(u.id) > 0 THEN 'Partially Occupied'
        ELSE 'Vacant'
    END AS occupancy_status
FROM rooms r
LEFT JOIN users u ON u.room_id = r.id AND u.role = 'STUDENT'
GROUP BY r.id, r.room_number, r.block, r.room_type, r.capacity;

-- View 2: Complaints Master Roster
CREATE OR REPLACE VIEW v_complaints_master AS
SELECT
    c.id AS complaint_id,
    c.ticket_number,
    c.title,
    c.category,
    c.urgency,
    c.status,
    u.name AS student_name,
    u.roll_number,
    r.room_number,
    r.block,
    c.assigned_staff,
    c.created_at
FROM complaints c
JOIN users u ON c.student_id = u.id
LEFT JOIN rooms r ON c.room_id = r.id;

-- View 3: Daily Roll Call Attendance Report
CREATE OR REPLACE VIEW v_daily_roll_call AS
SELECT
    a.id AS attendance_id,
    a.date,
    r.block,
    r.room_number,
    u.roll_number,
    u.name AS student_name,
    a.status AS attendance_status,
    a.notes,
    w.name AS marked_by_warden
FROM attendance a
JOIN users u ON a.student_id = u.id
JOIN rooms r ON a.room_id = r.id
LEFT JOIN users w ON a.marked_by = w.id;
