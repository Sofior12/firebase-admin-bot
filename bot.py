import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://YOUR-PROJECT-default-rtdb.firebaseio.com"
})

ref = db.reference("/devices")   # या "/" अगर पूरा डेटाबेस पढ़ना है
data = ref.get()

print(data)
