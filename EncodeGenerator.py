import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://imageattandance-default-rtdb.asia-southeast1.firebasedatabase.app/",  # Replace with your database URL
        'storageBucket': "imageattandance.firebasestorage.app"  # Replace with your storage bucket name
    })

    # Importing student images
    folderPath = 'Images'
    pathList = os.listdir(folderPath)
    print(pathList)

    imgList = []
    studentIds = []
    for path in pathList:
        full_path = os.path.join(folderPath, path)
        img = cv2.imread(full_path)
        if img is None:
            print(f"Could not read image: {path}")
            continue

        imgList.append(img)
        studentIds.append(os.path.splitext(path)[0])

        try:  # Handle potential upload errors
            bucket = storage.bucket()
            blob = bucket.blob(f"Images/{path}")  # Upload to the 'Images' folder
            blob.upload_from_filename(full_path)
        except Exception as upload_error:
            print(f"Error uploading {path}: {upload_error}")

    print(studentIds)

    def findEncodings(imagesList):
        encodeList = []
        for img in imagesList:
            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    encode = encodings[0]
                    encodeList.append(encode)
                else:
                    print("No face detected in one of the images.")
            except Exception as encoding_error:
                print(f"Error encoding image: {encoding_error}")
        return encodeList

    print("Encoding Started ...")
    encodeListKnown = findEncodings(imgList)

    if encodeListKnown:
        encodeListKnownWithIds = [encodeListKnown, studentIds]
        print("Encoding Complete")

        file = open("EncodeFile.p", 'wb')
        pickle.dump(encodeListKnownWithIds, file)
        file.close()
        print("File Saved")
    else:
        print("No face encodings were generated. Check your images.")

except Exception as main_error:
    print(f"A main error occurred: {main_error}")
