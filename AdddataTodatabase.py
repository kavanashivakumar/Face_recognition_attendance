import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://imageattandance-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ref = db.reference('Students')

data = {
    "001": {
        "name": "Kavana S",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 6,
        "standing": "G",
        "year": 3,
        "last_attendance_time": "2024-12-11 09:54:34"
    },
    "002": {
        "name": "Kranti",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 6,
        "standing": "G",
        "year": 3,
        "last_attendance_time": "2024-12-11 09:54:34"
    },
    "003": {
        "name": "Keerthana",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 6,
        "standing": "G",
        "year": 3,
        "last_attendance_time": "2024-12-11 09:54:34"
    },
    "004": {
        "name": "Priyanka",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 6,
        "standing": "G",
        "year": 3,
        "last_attendance_time": "2024-12-11 09:54:34"
    }
}

for key, value in data.items():
    ref.child(key).set(value)
