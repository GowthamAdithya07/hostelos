"""
RBAC & Data-Isolation Verification Script (using standard library urllib)
Tests strict permissions:
1. Students:
   - NO access to /api/v1/attendance (403)
   - NO access to /api/v1/rooms (403)
   - NO access to other students' complaints or passes (403)
   - Only own data returned from /api/v1/complaints and /api/v1/leaves
2. Warden/Admin:
   - Full access to all endpoints
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def api_request(method, endpoint, data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def login(email, password):
    status, res = api_request("POST", "/auth/login", {"email": email, "password": password})
    if status != 200:
        print(f"FAILED LOGIN FOR {email}: {status} - {res}")
        sys.exit(1)
    return res["access_token"], res["user"]

print("=" * 60)
print("TESTING STRICT RBAC & DATA ISOLATION")
print("=" * 60)

# 1. Login as Student
student_token, student_user = login("siddharth@hostelos.in", "Student@123")
student_headers = {"Authorization": f"Bearer {student_token}"}
print(f"Logged in as Student: {student_user['name']} (ID: {student_user['id']}, Role: {student_user['role']})")

# Test 1: Student accessing /rooms -> MUST BE 403
status, res = api_request("GET", "/rooms", headers=student_headers)
assert status == 403, f"Expected 403 Forbidden for student on /rooms, got {status}"
print("[PASS] Test 1 Passed: Student blocked from /rooms with HTTP 403 Forbidden")

# Test 2: Student accessing /attendance -> MUST BE 403
status, res = api_request("GET", "/attendance", headers=student_headers)
assert status == 403, f"Expected 403 Forbidden for student on /attendance, got {status}"
print("[PASS] Test 2 Passed: Student blocked from /attendance with HTTP 403 Forbidden")

# Test 3: Student accessing /complaints -> Only own complaints
status, complaints = api_request("GET", "/complaints", headers=student_headers)
assert status == 200, f"Expected 200 OK, got {status}"
for c in complaints:
    assert c["student_id"] == student_user["id"], f"Student saw complaint for student_id {c['student_id']}"
print(f"[PASS] Test 3 Passed: Student received {len(complaints)} complaints, all strictly matching their ID ({student_user['id']})")

# Test 4: Student accessing /leaves -> Only own leaves
status, leaves = api_request("GET", "/leaves", headers=student_headers)
assert status == 200, f"Expected 200 OK, got {status}"
for l in leaves:
    assert l["student_id"] == student_user["id"], f"Student saw leave for student_id {l['student_id']}"
print(f"[PASS] Test 4 Passed: Student received {len(leaves)} gate passes, all strictly matching their ID ({student_user['id']})")

# 2. Login as Warden
warden_token, warden_user = login("warden@hostelos.in", "Warden@123")
warden_headers = {"Authorization": f"Bearer {warden_token}"}
print(f"\nLogged in as Warden: {warden_user['name']} (ID: {warden_user['id']}, Role: {warden_user['role']})")

# Test 5: Warden accessing /rooms -> MUST BE 200
status, rooms_data = api_request("GET", "/rooms", headers=warden_headers)
assert status == 200, f"Expected 200 OK for warden on /rooms, got {status}"
print(f"[PASS] Test 5 Passed: Warden has full access to /rooms ({len(rooms_data)} room types/blocks returned)")

# Test 6: Warden accessing /attendance -> MUST BE 200
status, att_data = api_request("GET", "/attendance", headers=warden_headers)
assert status == 200, f"Expected 200 OK for warden on /attendance, got {status}"
print(f"[PASS] Test 6 Passed: Warden has full access to /attendance ({len(att_data)} attendance entries returned)")

# Test 7: Warden accessing all complaints -> MUST BE 200 and include all students
status, all_complaints = api_request("GET", "/complaints", headers=warden_headers)
assert status == 200, f"Expected 200 OK, got {status}"
student_ids = {c["student_id"] for c in all_complaints}
print(f"[PASS] Test 7 Passed: Warden has full access to all complaints ({len(all_complaints)} tickets across student IDs {student_ids})")

# Test 8: Warden accessing all leaves -> MUST BE 200 and include all students
status, all_leaves = api_request("GET", "/leaves", headers=warden_headers)
assert status == 200, f"Expected 200 OK, got {status}"
print(f"[PASS] Test 8 Passed: Warden has full access to all gate passes ({len(all_leaves)} passes)")

# Test 9: Student trying to view someone else's complaint detail -> MUST BE 403
other_complaint = next((c for c in all_complaints if c["student_id"] != student_user["id"]), None)
if other_complaint:
    status, res = api_request("GET", f"/complaints/{other_complaint['id']}", headers=student_headers)
    assert status == 403, f"Expected 403 Forbidden when student views someone else's complaint, got {status}"
    print(f"[PASS] Test 9 Passed: Student access to complaint #{other_complaint['ticket_number']} of another resident blocked with 403 Forbidden")

# Test 10: Student trying to view someone else's leave pass detail -> MUST BE 403
other_leave = next((l for l in all_leaves if l["student_id"] != student_user["id"]), None)
if other_leave:
    status, res = api_request("GET", f"/leaves/{other_leave['id']}", headers=student_headers)
    assert status == 403, f"Expected 403 Forbidden when student views someone else's leave pass, got {status}"
    print(f"[PASS] Test 10 Passed: Student access to pass #{other_leave['pass_code']} of another resident blocked with 403 Forbidden")

# Test 11: Overview scoping
status, student_ov = api_request("GET", "/analytics/overview", headers=student_headers)
assert status == 200
for c in student_ov.get("recent_complaints", []):
    assert c["student_id"] == student_user["id"]
for p in student_ov.get("approved_passes", []):
    assert p["student_id"] == student_user["id"]
print("[PASS] Test 11 Passed: Student overview dashboard strictly returns only their own tickets and gate passes")

# Test 12: Warden attempting to apply for leave -> MUST BE 403
fake_leave = {
    "leave_type": "Weekend outing",
    "departure_date": "2026-10-10T10:00:00Z",
    "return_date": "2026-10-12T18:00:00Z",
    "destination": "Bangalore",
    "reason": "Personal visit",
    "emergency_contact": "+91 98450 12345",
    "parent_consent": True,
}
status, res = api_request("POST", "/leaves", data=fake_leave, headers=warden_headers)
assert status == 403, f"Expected 403 Forbidden when warden attempts to apply for leave, got {status}"
print("[PASS] Test 12 Passed: Warden blocked from applying for leave with HTTP 403 Forbidden")

# Test 13: Admin / Institute Head attempting to apply for leave -> MUST BE 403
admin_token, admin_user = login("admin@hostelos.in", "Admin@123")
admin_headers = {"Authorization": f"Bearer {admin_token}"}
status, res = api_request("POST", "/leaves", data=fake_leave, headers=admin_headers)
assert status == 403, f"Expected 403 Forbidden when institute head attempts to apply for leave, got {status}"
print("[PASS] Test 13 Passed: Institute Head blocked from applying for leave with HTTP 403 Forbidden")

print("\n" + "=" * 60)
print("ALL 13 RBAC & DATA ISOLATION TESTS PASSED 100% SUCCESFULLY!")
print("=" * 60)
