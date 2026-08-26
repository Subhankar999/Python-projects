import os
import sqlite3
import webbrowser
from threading import Timer
from flask import Flask, jsonify, request


# DATABASE & BACKEND LOGIC

student_db = sqlite3.connect("student.db", check_same_thread=False)
cursor = student_db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS student_data(
    REGISTRATION_NO INT PRIMARY KEY,
    NAME VARCHAR(80) NOT NULL,
    ROLL INT UNIQUE NOT NULL,
    DATE_OF_BIRTH DATE,
    GENDER TEXT CHECK (GENDER IN ('Male', 'Female', 'Others')),
    DEPARTMENT VARCHAR(50),
    YEAR INT NOT NULL,
    SEM INT NOT NULL,
    CONTACT_NO BIGINT NOT NULL,
    GURDIAN_NO BIGINT,
    ADDRESS VARCHAR(200)
)
""")
student_db.commit()

class Student:
    def adding(self, data):
        query = """
        INSERT INTO student_data(
            REGISTRATION_NO, NAME, ROLL, DATE_OF_BIRTH, GENDER,
            DEPARTMENT, YEAR, SEM, CONTACT_NO, GURDIAN_NO, ADDRESS
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, data)
        student_db.commit()

    def deleting(self, reg_id):
        query = "DELETE FROM student_data WHERE REGISTRATION_NO = ?"
        cursor.execute(query, (reg_id,))
        student_db.commit()

    def searching(self, roll):
        query = "SELECT * FROM student_data WHERE ROLL = ?"
        cursor.execute(query, (roll,))
        return cursor.fetchall()

    def updating(self, roll, column, value):
        allowed_columns = {
            "NAME", "ROLL", "DATE_OF_BIRTH", "GENDER", "DEPARTMENT",
            "YEAR", "SEM", "CONTACT_NO", "GURDIAN_NO", "ADDRESS"
        }
        if column not in allowed_columns:
            raise ValueError("Invalid column.")
        query = f"UPDATE student_data SET {column} = ? WHERE ROLL = ?"
        cursor.execute(query, (value, roll))
        student_db.commit()

    def showall(self):
        cursor.execute("SELECT * FROM student_data")
        return cursor.fetchall()

student = Student()


# FLASK API BRIDGE

app = Flask(__name__)

FIELDS = [
    "REGISTRATION_NO", "NAME", "ROLL", "DATE_OF_BIRTH", "GENDER",
    "DEPARTMENT", "YEAR", "SEM", "CONTACT_NO", "GURDIAN_NO", "ADDRESS"
]

def row_to_dict(row):
    return dict(zip(FIELDS, row))

@app.get("/")
def serve_index():
    return HTML_CONTENT

@app.get("/api/students")
def show_students():
    rows = student.showall()
    return jsonify({"students": [row_to_dict(row) for row in rows]})

@app.get("/api/students/search")
def search_student():
    roll = request.args.get("roll", type=int)
    if roll is None:
        return jsonify({"message": "Roll number is required."}), 400

    rows = student.searching(roll)
    if not rows:
        return jsonify({"students": [], "message": "Student data not found!"})

    return jsonify({"students": [row_to_dict(row) for row in rows]})

@app.post("/api/students")
def add_student():
    data = request.get_json(silent=True) or {}
    missing = [field for field in FIELDS if field not in data]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    values = [data[field] for field in FIELDS]
    try:
        student.adding(values)
        return jsonify({"message": "Student added successfully."}), 201
    except sqlite3.IntegrityError as exc:
        return jsonify({"message": str(exc)}), 409
    except Exception as exc:
        return jsonify({"message": str(exc)}), 500

@app.put("/api/students/update")
def update_student():
    data = request.get_json(silent=True) or {}
    if "roll" not in data or "column" not in data or "value" not in data:
        return jsonify({"message": "roll, column and value are required."}), 400

    roll, column, value = data["roll"], data["column"], data["value"]
    try:
        student.updating(roll, column, value)
        return jsonify({"message": "Student updated successfully."})
    except sqlite3.IntegrityError as exc:
        return jsonify({"message": str(exc)}), 409
    except Exception as exc:
        return jsonify({"message": str(exc)}), 500

@app.delete("/api/students/<int:registration_no>")
def delete_student(registration_no):
    try:
        student.deleting(registration_no)
        return jsonify({"message": "Student deleted successfully."})
    except Exception as exc:
        return jsonify({"message": str(exc)}), 500


# EMBEDDED FRONTEND (HTML, CSS, JS)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Student Management Portal</title>
  <style>
    *{box-sizing:border-box}body{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;background:#f5f7fb;color:#172033}.sidebar{position:fixed;left:0;top:0;bottom:0;width:250px;background:#111827;color:#dbe3ef;padding:24px 16px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:12px;padding:8px 10px 28px}.brand-icon,.hero-mark{width:44px;height:44px;border-radius:12px;background:#2563eb;display:grid;place-items:center;color:white;font-weight:800}.brand strong,.brand span{display:block}.brand strong{font-size:16px}.brand span{font-size:11px;color:#94a3b8;margin-top:3px}.nav-item{width:100%;border:0;background:transparent;color:#aebbd0;padding:13px 14px;margin:3px 0;border-radius:10px;text-align:left;font-size:14px;cursor:pointer}.nav-item span{margin-left:10px}.nav-item:hover,.nav-item.active{background:#1f2937;color:#fff}.sidebar-footer{margin-top:auto;font-size:12px;color:#94a3b8;padding:14px}.status-dot{display:inline-block;width:8px;height:8px;background:#22c55e;border-radius:50%;margin-right:7px}.main{margin-left:250px;padding:32px 42px;min-height:100vh}.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}.eyebrow{font-size:11px;letter-spacing:.14em;font-weight:700;color:#64748b;margin:0 0 6px}.topbar h1{font-size:28px;margin:0}.hero{background:#111827;color:white;border-radius:18px;padding:34px;display:flex;justify-content:space-between;align-items:center;overflow:hidden}.hero h2{font-size:28px;margin:5px 0 10px}.hero p:not(.eyebrow){max-width:700px;color:#cbd5e1;line-height:1.6}.hero-mark{width:100px;height:100px;font-size:30px;border-radius:26px;background:#1d4ed8}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:20px 0}.stat-card,.panel{background:#fff;border:1px solid #e5eaf1;border-radius:16px;box-shadow:0 5px 20px rgba(15,23,42,.04)}.stat-card{padding:20px}.stat-card span{font-size:12px;color:#64748b}.stat-card strong{display:block;font-size:28px;margin-top:8px}.panel{padding:24px;margin-top:20px}.panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}.panel-head h3{margin:0;font-size:18px}.panel-head p{margin:5px 0 0;color:#64748b;font-size:13px}.quick-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.quick{border:1px solid #e2e8f0;background:#f8fafc;border-radius:12px;padding:18px;text-align:left;cursor:pointer}.quick:hover{border-color:#93c5fd;background:#eff6ff}.quick b{display:block;color:#2563eb;font-size:12px;margin-bottom:10px}.quick span{font-weight:700}.primary-btn,.secondary-btn,.danger-btn{border:0;border-radius:9px;padding:11px 16px;font-weight:700;cursor:pointer}.primary-btn{background:#2563eb;color:#fff}.primary-btn:hover{background:#1d4ed8}.secondary-btn{background:#eaf0f7;color:#1e293b}.danger-btn{background:#dc2626;color:white}.section{display:none}.section.active{display:block}.form-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.form-grid label,.inline-form label{font-size:12px;font-weight:700;color:#475569}.form-grid input,.form-grid select,.inline-form input{display:block;width:100%;margin-top:7px;padding:12px 13px;border:1px solid #d8e0ea;border-radius:9px;background:#fff;font-size:14px;outline:none}.form-grid input:focus,.form-grid select:focus,.inline-form input:focus{border-color:#60a5fa;box-shadow:0 0 0 3px #dbeafe}.full{grid-column:1/-1}.form-actions{display:flex;justify-content:flex-end;margin-top:4px}.inline-form{display:flex;align-items:end;gap:14px}.inline-form label{flex:1}.narrow{max-width:700px}.hidden{display:none!important}.danger-panel{border-color:#fecaca}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px;min-width:1100px}th,td{padding:12px 10px;border-bottom:1px solid #edf1f5;text-align:left;white-space:nowrap}th{background:#f8fafc;color:#475569;font-size:11px;text-transform:uppercase}tr:hover td{background:#fbfdff}code{background:#f1f5f9;padding:2px 5px;border-radius:4px}.result-card{border:1px solid #dbeafe;background:#f8fbff;border-radius:12px;padding:18px}.toast{position:fixed;right:24px;bottom:24px;background:#111827;color:#fff;padding:13px 17px;border-radius:9px;opacity:0;transform:translateY(10px);pointer-events:none;transition:.2s;z-index:10}.toast.show{opacity:1;transform:none}@media(max-width:1000px){.sidebar{width:210px}.main{margin-left:210px;padding:25px}.stats{grid-template-columns:repeat(2,1fr)}.quick-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:700px){.sidebar{position:static;width:100%;height:auto}.sidebar nav{display:flex;overflow:auto}.sidebar-footer{display:none}.main{margin:0;padding:18px}.topbar{gap:12px}.hero-mark{display:none}.form-grid{grid-template-columns:1fr}.full{grid-column:auto}.inline-form{flex-direction:column;align-items:stretch}.stats{grid-template-columns:1fr}.quick-grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <div id="toast" class="toast"></div>

  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">SM</div>
      <div><strong>Student Portal</strong><span>Management System</span></div>
    </div>
    <nav>
      <button class="nav-item active" data-section="dashboard">⌂ <span>Dashboard</span></button>
      <button class="nav-item" data-section="students">♙ <span>All Students</span></button>
      <button class="nav-item" data-section="add">＋ <span>Add Student</span></button>
      <button class="nav-item" data-section="search">⌕ <span>Search</span></button>
      <button class="nav-item" data-section="update">✎ <span>Update</span></button>
      <button class="nav-item" data-section="delete">⌫ <span>Delete</span></button>
    </nav>
    <!-- <div class="sidebar-footer">
      <span class="status-dot"></span>
      Backend integration ready
    </div> -->
  </aside>

  <main class="main">
    <header class="topbar">
      <div>
        <p class="eyebrow">STUDENT MANAGEMENT SYSTEM</p>
        <h1 id="pageTitle">Dashboard</h1>
      </div>
      <button class="primary-btn" data-section="add">＋ Add Student</button>
    </header>

    <section id="dashboard" class="section active">
      <div class="hero">
        <div>
          <!-- <p class="eyebrow">OVERVIEW</p> -->
          <h2> STUDENT MANAGEMENT PORTAL</h2>
         <!-- <p>Use the graphical interface for student operations: Add, Search, Update, Delete, and Show.</p> -->
        </div>
        <div class="hero-mark">SM</div>
      </div>
      <div class="stats">
        <div class="stat-card"><span>Total Students</span><strong id="statTotal">—</strong></div>
        <div class="stat-card"><span>Departments</span><strong id="statDepartments">—</strong></div>
        <div class="stat-card"><span>Male</span><strong id="statMale">—</strong></div>
        <div class="stat-card"><span>Female</span><strong id="statFemale">—</strong></div>
      </div>
      <div class="panel">
        <div class="panel-head"><div><h3>Quick Actions</h3><p>Choose an operation from the menu below.</p></div></div>
        <div class="quick-grid">
          <button class="quick" data-section="add"><b>1</b><span>Add Student</span></button>
          <button class="quick" data-section="search"><b>2</b><span>Search by Roll</span></button>
          <button class="quick" data-section="update"><b>3</b><span>Update Student</span></button>
          <button class="quick" data-section="delete"><b>4</b><span>Delete Student</span></button>
          <button class="quick" data-section="students"><b>5</b><span>Show All</span></button>
        </div>
      </div>
    </section>

    <section id="students" class="section">
      <div class="panel">
        <div class="panel-head">
          <div><h3>All Students</h3><p>Records returned from backend database.</p></div>
          <button id="refreshBtn" class="secondary-btn">↻ Refresh</button>
        </div>
        <div class="table-wrap"><table id="studentsTable"><thead></thead><tbody></tbody></table></div>
      </div>
    </section>

    <section id="add" class="section">
      <div class="panel">
        <div class="panel-head"><div><h3>Add Student</h3><p>Enter details to add a new record.</p></div></div>
        <form id="addForm" class="form-grid"></form>
        <div class="form-actions"><button type="submit" form="addForm" class="primary-btn">Add Student</button></div>
      </div>
    </section>

    <section id="search" class="section">
      <div class="panel narrow">
        <div class="panel-head"><div><h3>Search Student</h3><p>Search by <strong>ROLL</strong> number.</p></div></div>
        <form id="searchForm" class="inline-form">
          <label>Roll Number<input id="searchRoll" type="number" required></label>
          <button class="primary-btn">Search</button>
        </form>
      </div>
      <div id="searchResult" class="panel hidden"></div>
    </section>

    <section id="update" class="section">
      <div class="panel">
        <div class="panel-head"><div><h3>Update Student</h3><p>Select field and roll number to update.</p></div></div>
        <form id="updateForm" class="form-grid">
          <label>Current Roll Number<input id="updateRoll" type="number" required></label>
          <label>Field
            <select id="updateField" required>
              <option value="NAME">1. Name</option>
              <option value="ROLL">2. Roll</option>
              <option value="DATE_OF_BIRTH">3. DOB</option>
              <option value="GENDER">4. Gender</option>
              <option value="DEPARTMENT">5. Department</option>
              <option value="YEAR">6. Year</option>
              <option value="SEM">7. Semester</option>
              <option value="CONTACT_NO">8. Contact</option>
              <option value="GURDIAN_NO">9. Guardian Contact</option>
              <option value="ADDRESS">10. Address</option>
            </select>
          </label>
          <label class="full">New Data<input id="updateValue" required></label>
          <div class="full form-actions"><button class="primary-btn">Update Student</button></div>
        </form>
      </div>
    </section>

    <section id="delete" class="section">
      <div class="panel narrow danger-panel">
        <div class="panel-head"><div><h3>Delete Student</h3><p>Delete by <strong>REGISTRATION_NO</strong>.</p></div></div>
        <form id="deleteForm" class="inline-form">
          <label>Registration Number<input id="deleteReg" type="number" required></label>
          <button class="danger-btn">Delete Student</button>
        </form>
      </div>
    </section>
  </main>

  <script>
    const API_BASE = window.location.origin;

    async function request(path, options = {}) {
      const response = await fetch(`${API_BASE}${path}`, {
        headers: {"Content-Type": "application/json", ...(options.headers || {})},
        ...options
      });
      let data = {};
      try { data = await response.json(); } catch (_) {}
      if (!response.ok) throw new Error(data.message || data.error || `HTTP ${response.status}`);
      return data;
    }

    const StudentAPI = {
      showAll() { return request("/api/students"); },
      search(roll) { return request(`/api/students/search?roll=${encodeURIComponent(roll)}`); },
      add(student) { return request("/api/students", { method: "POST", body: JSON.stringify(student) }); },
      update(roll, column, value) { return request("/api/students/update", { method: "PUT", body: JSON.stringify({roll, column, value}) }); },
      remove(registrationNo) { return request(`/api/students/${encodeURIComponent(registrationNo)}`, { method: "DELETE" }); }
    };

    const FIELDS = [
      ["REGISTRATION_NO","Registration Number","number",true],
      ["NAME","Name","text",true],
      ["ROLL","Roll Number","number",true],
      ["DATE_OF_BIRTH","Date of Birth","date",false],
      ["GENDER","Gender","select",false],
      ["DEPARTMENT","Department","text",false],
      ["YEAR","Year","number",true],
      ["SEM","Semester","number",true],
      ["CONTACT_NO","Contact Number","number",true],
      ["GURDIAN_NO","Guardian Contact","number",false],
      ["ADDRESS","Address","text",false]
    ];

    document.addEventListener("DOMContentLoaded", () => {
      buildAddForm();
      bindNavigation();
      document.getElementById("addForm").addEventListener("submit", addStudent);
      document.getElementById("searchForm").addEventListener("submit", searchStudent);
      document.getElementById("updateForm").addEventListener("submit", updateStudent);
      document.getElementById("deleteForm").addEventListener("submit", deleteStudent);
      document.getElementById("refreshBtn").addEventListener("click", loadStudents);
      loadStudents().catch(() => {});
    });

    function buildAddForm() {
      const form = document.getElementById("addForm");
      form.innerHTML = FIELDS.map(([key,label,type,required]) => {
        if (key === "GENDER") return `<label>${label}<select name="${key}" ${required?"required":""}>
          <option value="">Select gender</option><option>Male</option><option>Female</option><option>Others</option>
        </select></label>`;
        return `<label>${label}<input name="${key}" type="${type}" ${required?"required":""}></label>`;
      }).join("");
      form.insertAdjacentHTML("beforeend", `<div class="full"><label>Address<input name="ADDRESS" type="text" required></label></div>`);
      const labels = form.querySelectorAll("label");
      let seen = false;
      labels.forEach(label => {
        if (label.textContent.trim().startsWith("Address")) {
          if (seen) label.remove(); else seen = true;
        }
      });
    }

    function bindNavigation() {
      document.querySelectorAll("[data-section]").forEach(btn => {
        btn.addEventListener("click", () => showSection(btn.dataset.section));
      });
    }

    function showSection(id) {
      document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
      document.getElementById(id).classList.add("active");
      document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.section === id));
      const titles = {dashboard:"Dashboard",students:"All Students",add:"Add Student",search:"Search Student",update:"Update Student",delete:"Delete Student"};
      document.getElementById("pageTitle").textContent = titles[id] || "Student Portal";
      if (id === "students") loadStudents();
    }

    async function loadStudents() {
      try {
        const data = await StudentAPI.showAll();
        const students = normalizeStudents(data);
        renderTable(students);
        updateStats(students);
      } catch (err) {
        renderTable([]);
        updateStats([]);
        toast("Backend connection error: " + err.message, true);
      }
    }

    function normalizeStudents(data) {
      if (Array.isArray(data)) return data;
      return data.students || data.data || data.records || [];
    }

    function renderTable(students) {
      const head = document.querySelector("#studentsTable thead");
      const body = document.querySelector("#studentsTable tbody");
      head.innerHTML = `<tr>${FIELDS.map(f => `<th>${f[1]}</th>`).join("")}</tr>`;
      body.innerHTML = students.length ? students.map(s =>
        `<tr>${FIELDS.map(([key]) => `<td>${escapeHtml(s[key] ?? s[key.toLowerCase()] ?? "")}</td>`).join("")}</tr>`
      ).join("") : `<tr><td colspan="11" style="text-align:center;padding:30px;color:#64748b">No records returned.</td></tr>`;
    }

    function updateStats(students) {
      document.getElementById("statTotal").textContent = students.length;
      document.getElementById("statDepartments").textContent = new Set(students.map(s => s.DEPARTMENT).filter(Boolean)).size;
      document.getElementById("statMale").textContent = students.filter(s => String(s.GENDER).toLowerCase() === "male").length;
      document.getElementById("statFemale").textContent = students.filter(s => String(s.GENDER).toLowerCase() === "female").length;
    }

    async function addStudent(e) {
      e.preventDefault();
      const form = new FormData(e.target);
      const student = {};
      for (const [k,v] of form.entries()) student[k] = v;
      ["REGISTRATION_NO","ROLL","YEAR","SEM","CONTACT_NO","GURDIAN_NO"].forEach(k => {
        if (student[k] !== "") student[k] = Number(student[k]);
      });
      student.NAME = String(student.NAME || "").toUpperCase();
      student.DEPARTMENT = String(student.DEPARTMENT || "").toUpperCase();
      student.ADDRESS = String(student.ADDRESS || "").toUpperCase();
      try {
        await StudentAPI.add(student);
        toast("Student added successfully.");
        e.target.reset();
        showSection("students");
      } catch (err) { toast(err.message, true); }
    }

    async function searchStudent(e) {
      e.preventDefault();
      const roll = document.getElementById("searchRoll").value;
      try {
        const data = await StudentAPI.search(roll);
        const students = normalizeStudents(data);
        const box = document.getElementById("searchResult");
        box.classList.remove("hidden");
        box.innerHTML = students.length
          ? `<div class="panel-head"><div><h3>Search Result</h3><p>Roll: ${escapeHtml(roll)}</p></div></div>${studentCard(students[0])}`
          : `<div class="result-card">Student data not found!</div>`;
      } catch (err) { toast(err.message, true); }
    }

    function studentCard(s) {
      return `<div class="result-card"><div class="form-grid">${FIELDS.map(([key,label]) =>
        `<div><small>${label}</small><strong style="display:block;margin-top:4px">${escapeHtml(s[key] ?? "")}</strong></div>`
      ).join("")}</div></div>`;
    }

    async function updateStudent(e) {
      e.preventDefault();
      const roll = Number(document.getElementById("updateRoll").value);
      const column = document.getElementById("updateField").value;
      let value = document.getElementById("updateValue").value;
      if (["ROLL","YEAR","SEM","CONTACT_NO","GURDIAN_NO"].includes(column)) value = Number(value);
      if (["NAME","DEPARTMENT","ADDRESS"].includes(column)) value = value.toUpperCase();
      if (column === "GENDER") value = value[0] ? value[0].toUpperCase() + value.slice(1).toLowerCase() : value;
      try {
        await StudentAPI.update(roll, column, value);
        toast("Student updated successfully.");
        document.getElementById("updateForm").reset();
        loadStudents();
      } catch (err) { toast(err.message, true); }
    }

    async function deleteStudent(e) {
      e.preventDefault();
      const reg = Number(document.getElementById("deleteReg").value);
      if (!confirm(`Delete student with registration number ${reg}?`)) return;
      try {
        await StudentAPI.remove(reg);
        toast("Student deleted successfully.");
        e.target.reset();
        loadStudents();
      } catch (err) { toast(err.message, true); }
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
    }

    function toast(message, error=false) {
      const el = document.getElementById("toast");
      el.textContent = message;
      el.style.background = error ? "#dc2626" : "#111827";
      el.classList.add("show");
      setTimeout(() => el.classList.remove("show"), 3200);
    }
  </script>
</body>
</html>
"""


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)