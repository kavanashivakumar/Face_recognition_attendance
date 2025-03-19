import os
import pickle
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

# Firebase setup
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://imageattandance-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "imageattandance.firebasestorage.app"
})

bucket = storage.bucket()

# Webcam initialization
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Load resources
imgBackground = cv2.imread('Resources/background.png')
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load encoding file
print("Loading encodings...")
with open('Encodefile.p', 'rb') as file:
    encodeListknownWithId = pickle.load(file)
encodeListknown, studentIds = encodeListknownWithId
print("Encodings loaded.")

# Variables
modeType = 0
counter = 0
id = -1
studentInfo = {}
imgStudent = None

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to read frame from webcam.")
        break

    # Resize and convert the image for face recognition
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListknown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListknown, encodeFace)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            id = studentIds[matchIndex]
            print(f"Detected: {id}")
            y1, x2, y2, x1 = [v * 4 for v in faceLoc]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, id.upper(), (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if counter == 0:
                counter = 1
                modeType = 1

    if counter != 0:
        if counter == 1:
            try:
                # Fetch student info
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Fetch student image from Firebase Storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                # Update attendance
                lastAttendanceTime = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - lastAttendanceTime).total_seconds()
                print(f"Time since last attendance: {secondsElapsed} seconds")

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
            except Exception as e:
                print(f"Error retrieving data or image: {e}")
                counter = 0
                modeType = 0

        if modeType != 3:
            if 10 < counter < 20:
                modeType = 2

            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if counter <= 10:
                # Display student details
                fields = [
                    ("Total Attendance", studentInfo['total_attendance'], (861, 125)),
                    ("Major", studentInfo['major'], (1006, 550)),
                    ("ID", id, (1006, 493)),
                    ("Standing", studentInfo['standing'], (910, 625)),
                    ("Year", studentInfo['year'], (1025, 625)),
                    ("Starting Year", studentInfo['starting_year'], (1125, 625))
                ]
                for label, value, pos in fields:
                    cv2.putText(imgBackground, str(value), pos, cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

                (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w) // 2
                cv2.putText(imgBackground, studentInfo['name'], (808 + offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

            counter += 1

            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = {}
                imgStudent = None

    # Overlay webcam image
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # Show the output
    cv2.imshow("Face Attendance", imgBackground)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
