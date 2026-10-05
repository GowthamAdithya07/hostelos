-- =============================================================================
-- HOSTELOS - RELATIONAL DATABASE DDL SCHEMA (10 TABLES)
-- Course: 23CSE202 (Database Management Systems, Group C9)
-- Engine: PostgreSQL 14+ / SQLite Compatible
-- Normalization: Boyce-Codd Normal Form (BCNF / 3NF)
-- =============================================================================

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS leave_passes CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS allocations CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS room_types CASCADE;
DROP TABLE IF EXISTS authorities CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS students CASCADE;

-- =============================================================================
-- 1. SUBSYSTEM: AUTHENTICATION & USER PERSONAS
-- =============================================================================

-- Table 1: students
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    major VARCHAR(255) NOT NULL DEFAULT 'Computer Science & Engineering',
    emergency_contact VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_students_roll ON students(roll_number);
CREATE INDEX idx_students_email ON students(email);

-- Table 2: authorities (Chief Warden & Deputy Wardens)
CREATE TABLE authorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(100) NOT NULL DEFAULT 'Chief Warden',
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_authorities_email ON authorities(email);

-- Table 3: admins (Institute Head & College Administration)
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_admins_email ON admins(email);

-- =============================================================================
-- 2. SUBSYSTEM: ACCOMMODATION & ROOM ALLOCATION
-- =============================================================================

-- Table 4: room_types (Decomposed from rooms to satisfy 3NF/BCNF)
CREATE TABLE room_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

-- Table 5: rooms (Hostel residential quarters across Blocks A, B, C)
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    block VARCHAR(50) NOT NULL,
    room_number VARCHAR(50) NOT NULL,
    type_id INTEGER NOT NULL REFERENCES room_types(id) ON DELETE RESTRICT,
    has_ac BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_block_room UNIQUE (block, room_number)
);
CREATE INDEX idx_rooms_block ON rooms(block);
CREATE INDEX idx_rooms_number ON rooms(room_number);

-- Table 6: allocations (Junction entity for student-room residency)
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    allocation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    deposit_paid NUMERIC(10,2) NOT NULL DEFAULT 5000.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_allocations_active ON allocations(is_active);
CREATE INDEX idx_allocations_student ON allocations(student_id);
CREATE INDEX idx_allocations_room ON allocations(room_id);

-- =============================================================================
-- 3. SUBSYSTEM: MAINTENANCE & COMPLAINT DISPATCH
-- =============================================================================

-- Table 7: staff (Maintenance technicians)
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role_type VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL
);

-- Table 8: complaints (Grievances filed by students & resolved by wardens)
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    urgency VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (urgency IN ('High', 'Medium', 'Low')),
    status VARCHAR(50) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Escalated', 'Resolved')),
    assigned_staff VARCHAR(255),
    resolution_notes TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_complaints_ticket ON complaints(ticket_number);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_student ON complaints(student_id);
CREATE INDEX idx_complaints_category ON complaints(category);

-- =============================================================================
-- 4. SUBSYSTEM: WELFARE, ATTENDANCE & GATE PASSES
-- =============================================================================

-- Table 9: attendance (Daily night roll-call register)
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    admin_id INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Present' CHECK (status IN ('Present', 'Absent', 'Late / Permitted')),
    notes VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_student_date UNIQUE (student_id, date)
);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_student ON attendance(student_id);

-- Table 10: leave_passes (Official out-station permits)
CREATE TABLE leave_passes (
    id SERIAL PRIMARY KEY,
    pass_code VARCHAR(50) UNIQUE NOT NULL,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    authority_id INTEGER REFERENCES authorities(id) ON DELETE SET NULL,
    leave_type VARCHAR(50) NOT NULL CHECK (leave_type IN ('Weekend outing', 'Emergency leave', 'Vacation')),
    departure_date TIMESTAMP WITH TIME ZONE NOT NULL,
    return_date TIMESTAMP WITH TIME ZONE NOT NULL,
    destination VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    emergency_contact VARCHAR(50) NOT NULL,
    parent_consent BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Validated', 'Rejected', 'Checked Out', 'Returned')),
    gate_pass_token VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_leave_dates CHECK (return_date >= departure_date)
);
CREATE INDEX idx_leave_code ON leave_passes(pass_code);
CREATE INDEX idx_leave_status ON leave_passes(status);
CREATE INDEX idx_leave_student ON leave_passes(student_id);
