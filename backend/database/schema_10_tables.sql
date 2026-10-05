-- =============================================================================
-- HOSTELOS - 10-TABLE RELATIONAL DATABASE SCHEMA DEFINITION (PostgreSQL DDL)
-- =============================================================================
-- Course: 23CSE202 - Database Management Systems (S3 B.Tech CSE)
-- Department of Computer Science & Engineering, Amrita School of Computing
-- Group: C9
-- Team Members:
--   AM.SC.U4CSE25209 - BYN.Siddharth Sai
--   AM.SC.U4CSE25258 - Vurukuti Gowtham Adithya
--   AM.SC.U4CSE25263 - K.Rama Sri Surya
--   AM.SC.U4CSE25264 - K.Sai Santhosh
--
-- NORMALIZATION ANALYSIS:
--   UNF  -> 1NF: Atomic attributes; multi-valued absence dates separated into ATTENDANCE.
--   1NF  -> 2NF: No partial functional dependencies; separated student and room info into ALLOCATION.
--   2NF  -> 3NF: No transitive functional dependencies; ROOM_TYPE extracted from ROOM.
--   3NF  -> BCNF: Every functional determinant is a candidate key.
-- =============================================================================

-- 1. DROP EXISTING RELATIONS (Cascading clean reset)
DROP VIEW IF EXISTS v_daily_roll_call CASCADE;
DROP VIEW IF EXISTS v_complaints_master CASCADE;
DROP VIEW IF EXISTS v_room_occupancy CASCADE;

DROP TRIGGER IF EXISTS trg_check_bed_capacity ON allocations CASCADE;
DROP FUNCTION IF EXISTS fn_check_bed_capacity() CASCADE;

DROP TRIGGER IF EXISTS trg_check_leave_dates ON leave_passes CASCADE;
DROP FUNCTION IF EXISTS fn_check_leave_dates() CASCADE;

DROP TRIGGER IF EXISTS trg_auto_gate_pass_token ON leave_passes CASCADE;
DROP FUNCTION IF EXISTS fn_auto_gate_pass_token() CASCADE;

DROP TRIGGER IF EXISTS trg_auto_resolve_complaint ON complaints CASCADE;
DROP FUNCTION IF EXISTS fn_auto_resolve_complaint() CASCADE;

DROP TABLE IF EXISTS leave_passes CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS authorities CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS allocations CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS room_types CASCADE;
DROP TABLE IF EXISTS students CASCADE;

-- -----------------------------------------------------------------------------
-- TABLE 1: STUDENT (StudentID [PK], Name, Major, EmergencyContact, Email, PasswordHash)
-- -----------------------------------------------------------------------------
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    roll_number VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    major VARCHAR(255) NOT NULL DEFAULT 'Computer Science & Engineering',
    emergency_contact VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE 2: ROOM_TYPE (TypeID [PK], TypeName, Capacity)
-- -----------------------------------------------------------------------------
CREATE TABLE room_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity IN (1, 2, 3, 4))
);

-- -----------------------------------------------------------------------------
-- TABLE 3: ROOM (RoomID [PK], Block, RoomNumber, TypeID [FK])
-- -----------------------------------------------------------------------------
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    block VARCHAR(50) NOT NULL,
    room_number VARCHAR(50) NOT NULL,
    type_id INTEGER NOT NULL REFERENCES room_types(id) ON DELETE RESTRICT,
    has_ac BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_block_room_number UNIQUE (block, room_number)
);

-- -----------------------------------------------------------------------------
-- TABLE 4: ALLOCATION (AllocationID [PK], StudentID [FK], RoomID [FK], AllocationDate, DepositPaid)
-- -----------------------------------------------------------------------------
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    allocation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    deposit_paid NUMERIC(10, 2) NOT NULL DEFAULT 5000.00 CHECK (deposit_paid >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE 5: ADMIN (AdminID [PK], Name, Email, PasswordHash)
-- -----------------------------------------------------------------------------
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE 6: STAFF (StaffID [PK], Name, RoleType, Phone)
-- -----------------------------------------------------------------------------
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role_type VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL
);

-- -----------------------------------------------------------------------------
-- TABLE 7: AUTHORITY (AuthorityID [PK], Name, Designation, Email, PasswordHash)
-- -----------------------------------------------------------------------------
CREATE TABLE authorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(100) NOT NULL DEFAULT 'Chief Warden',
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE 8: COMPLAINT (ComplaintID [PK], StudentID [FK], StaffID [FK], Category, Title, Status, Urgency)
-- -----------------------------------------------------------------------------
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'Plumbing',
        'Electrical & Lighting',
        'Internet Connectivity',
        'Carpentry / Furniture',
        'Housekeeping',
        'Other'
    )),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    urgency VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (urgency IN ('High', 'Medium', 'Low')),
    status VARCHAR(50) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Escalated', 'Resolved')),
    resolution_notes TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- -----------------------------------------------------------------------------
-- TABLE 9: ATTENDANCE (AttendanceID [PK], StudentID [FK], AdminID [FK], Date, Status)
-- -----------------------------------------------------------------------------
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    admin_id INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Present' CHECK (status IN ('Present', 'Absent', 'Late / Permitted')),
    notes VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_date_attendance UNIQUE (student_id, date)
);

-- -----------------------------------------------------------------------------
-- TABLE 10: LEAVE_PASS (PassID [PK], StudentID [FK], AuthorityID [FK], LeaveType, DepartExpected, ExpectedReturn, ActualReturn, Status, RejectionReason, GatePassToken)
-- -----------------------------------------------------------------------------
CREATE TABLE leave_passes (
    id SERIAL PRIMARY KEY,
    pass_code VARCHAR(50) NOT NULL UNIQUE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    authority_id INTEGER REFERENCES authorities(id) ON DELETE SET NULL,
    leave_type VARCHAR(50) NOT NULL CHECK (leave_type IN ('Weekend outing', 'Emergency leave', 'Vacation')),
    depart_expected TIMESTAMP NOT NULL,
    expected_return TIMESTAMP NOT NULL,
    actual_return TIMESTAMP,
    destination VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    emergency_contact VARCHAR(50) NOT NULL,
    parent_consent BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Validated', 'Rejected', 'Checked Out', 'Returned')),
    rejection_reason TEXT,
    gate_pass_token VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_leave_dates CHECK (expected_return >= depart_expected)
);

-- =============================================================================
-- PERFORMANCE B-TREE INDEXES
-- =============================================================================
CREATE INDEX idx_students_email ON students(LOWER(email));
CREATE INDEX idx_students_roll ON students(roll_number);

CREATE INDEX idx_rooms_block ON rooms(block);
CREATE INDEX idx_rooms_number ON rooms(room_number);

CREATE INDEX idx_alloc_student ON allocations(student_id);
CREATE INDEX idx_alloc_room ON allocations(room_id);
CREATE INDEX idx_alloc_active ON allocations(is_active);

CREATE INDEX idx_complaints_ticket ON complaints(ticket_number);
CREATE INDEX idx_complaints_student ON complaints(student_id);
CREATE INDEX idx_complaints_status ON complaints(status);

CREATE INDEX idx_att_date ON attendance(date);
CREATE INDEX idx_att_student ON attendance(student_id);

CREATE INDEX idx_leave_code ON leave_passes(pass_code);
CREATE INDEX idx_leave_status ON leave_passes(status);

-- =============================================================================
-- DATABASE CONSTRAINTS & TRIGGERS (DBMS EVALUATION HIGHLIGHT)
-- =============================================================================

-- TRIGGER 1: Enforce Room Bed Capacity Limit
-- Prevents overbooking a room beyond its associated room_type.capacity
CREATE OR REPLACE FUNCTION fn_check_bed_capacity()
RETURNS TRIGGER AS $$
DECLARE
    max_cap INTEGER;
    current_occ INTEGER;
BEGIN
    SELECT rt.capacity INTO max_cap
    FROM rooms r
    JOIN room_types rt ON r.type_id = rt.id
    WHERE r.id = NEW.room_id;

    SELECT COUNT(*) INTO current_occ
    FROM allocations
    WHERE room_id = NEW.room_id AND is_active = TRUE AND id != COALESCE(NEW.id, 0);

    IF (current_occ + 1) > max_cap THEN
        RAISE EXCEPTION 'Constraint Violation: Room % is at full capacity (%/% occupied).', NEW.room_id, current_occ, max_cap;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_bed_capacity
BEFORE INSERT OR UPDATE ON allocations
FOR EACH ROW
WHEN (NEW.is_active = TRUE)
EXECUTE FUNCTION fn_check_bed_capacity();


-- TRIGGER 2: Enforce Leave Date Consistency
CREATE OR REPLACE FUNCTION fn_check_leave_dates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expected_return < NEW.depart_expected THEN
        RAISE EXCEPTION 'Constraint Violation: Expected return date (%) cannot be before departure date (%).',
            NEW.expected_return, NEW.depart_expected;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_leave_dates
BEFORE INSERT OR UPDATE ON leave_passes
FOR EACH ROW
EXECUTE FUNCTION fn_check_leave_dates();


-- TRIGGER 3: Auto-Generate Gate Pass Token On Approval
CREATE OR REPLACE FUNCTION fn_auto_gate_pass_token()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Approved' AND (OLD.status IS DISTINCT FROM 'Approved' OR NEW.gate_pass_token IS NULL) THEN
        NEW.gate_pass_token := 'TOKEN-' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_gate_pass_token
BEFORE UPDATE ON leave_passes
FOR EACH ROW
EXECUTE FUNCTION fn_auto_gate_pass_token();


-- TRIGGER 4: Auto-Timestamp Resolved Complaints
CREATE OR REPLACE FUNCTION fn_auto_resolve_complaint()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Resolved' AND OLD.status != 'Resolved' THEN
        NEW.resolved_at := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_resolve_complaint
BEFORE UPDATE ON complaints
FOR EACH ROW
EXECUTE FUNCTION fn_auto_resolve_complaint();

-- =============================================================================
-- RELATIONAL DATABASE REPORTING VIEWS
-- =============================================================================

-- VIEW 1: Live Room Occupancy View
CREATE OR REPLACE VIEW v_room_occupancy AS
SELECT
    r.id AS room_id,
    r.block,
    r.room_number,
    rt.type_name,
    rt.capacity,
    COUNT(a.id) FILTER (WHERE a.is_active = TRUE) AS occupied_beds,
    (rt.capacity - COUNT(a.id) FILTER (WHERE a.is_active = TRUE)) AS vacant_beds,
    ROUND(CAST(COUNT(a.id) FILTER (WHERE a.is_active = TRUE) * 100.0 / NULLIF(rt.capacity, 0) AS NUMERIC), 1) AS occupancy_pct
FROM rooms r
JOIN room_types rt ON r.type_id = rt.id
LEFT JOIN allocations a ON a.room_id = r.id AND a.is_active = TRUE
GROUP BY r.id, r.block, r.room_number, rt.type_name, rt.capacity;

-- VIEW 2: Complaints Master Roster View
CREATE OR REPLACE VIEW v_complaints_master AS
SELECT
    c.id AS complaint_id,
    c.ticket_number,
    c.category,
    c.title,
    c.urgency,
    c.status,
    s.name AS student_name,
    s.roll_number,
    r.room_number,
    r.block,
    st.name AS assigned_staff_name,
    st.role_type AS staff_role,
    c.created_at,
    c.resolved_at
FROM complaints c
JOIN students s ON c.student_id = s.id
LEFT JOIN staff st ON c.staff_id = st.id
LEFT JOIN allocations a ON a.student_id = s.id AND a.is_active = TRUE
LEFT JOIN rooms r ON a.room_id = r.id;

-- VIEW 3: Daily Roll Call Attendance Report View
CREATE OR REPLACE VIEW v_daily_roll_call AS
SELECT
    att.id AS attendance_id,
    att.date,
    s.roll_number,
    s.name AS student_name,
    r.block,
    r.room_number,
    att.status AS roll_call_status,
    att.notes,
    adm.name AS marked_by_admin
FROM attendance att
JOIN students s ON att.student_id = s.id
LEFT JOIN admins adm ON att.admin_id = adm.id
LEFT JOIN allocations a ON a.student_id = s.id AND a.is_active = TRUE
LEFT JOIN rooms r ON a.room_id = r.id;
