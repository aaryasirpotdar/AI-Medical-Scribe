import sqlite3

DB_NAME = "database/patients.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_name TEXT,
    age INTEGER,
    gender TEXT,
    phone TEXT,

    symptoms TEXT,
    duration TEXT,
    bp TEXT,
    history TEXT,
    medicines TEXT,
    tests TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_patient(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
INSERT INTO patients (
    patient_name,
    age,
    gender,
    phone,
    symptoms,
    duration,
    bp,
    history,
    medicines,
    tests
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    data["Patient Name"],
    data["Age"],
    data["Gender"],
    data["Phone"],
    data["Symptoms"],
    data["Duration"],
    data["BP"],
    data["Medical History"],
    data["Medicines"],
    data["Tests"]
))

    conn.commit()
    conn.close()
    
def get_latest_patient():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT symptoms,
           duration,
           bp,
           history,
           medicines,
           tests
        FROM patients
        ORDER BY id DESC
        LIMIT 1
        """)

    row = cursor.fetchone()

    conn.close()

    if row:
        return {
    "Symptoms": row[0],
    "Duration": row[1],
    "BP": row[2],
    "Medical History": row[3],
    "Medicines": row[4],
    "Tests": row[5]
}

    return None

def get_all_patients():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM patients
    ORDER BY id DESC
""")
    rows = cursor.fetchall()

    conn.close()

    return rows

def search_patients(name):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_name LIKE ?
        ORDER BY id DESC
    """, ('%' + name + '%',))

    rows = cursor.fetchall()

    conn.close()

    return rows


