#Najpierw w terminalu wpisac:
#python manage.py shell
#albo po prostu go odpalić XD
#!!!!!!!!!!!!!!!!


import random
from django.contrib.auth import get_user_model
from management.models import Incydent, Zasob

User = get_user_model()
autor = User.objects.first()

LAT_MIN, LAT_MAX = 51.0400, 51.1800
LNG_MIN, LNG_MAX = 16.8800, 17.1400

print("Generowanie 50 zasobów...")
typy_zasobow = ['Karetka', 'Wóz strażacki', 'Radiowóz']
for i in range(50):
    Zasob.objects.create(nazwa=f"Jednostka WRO-{i+1}", typ=random.choice(typy_zasobow), lat=round(random.uniform(LAT_MIN, LAT_MAX), 6), lng=round(random.uniform(LNG_MIN, LNG_MAX), 6), dostepnosc=True)

print("Generowanie 500 incydentów...")
typy_incydentow = ['Road Incident', 'Medical Emergency', 'Public Order Disturbance', 'Domestic Violence', 'Fire', 'Technical & Weather Hazard', 'Intoxicated or Dangerous Person', 'Theft & Suspicious Activity', 'Animal Assistance', 'Missing Person', 'Other']
statusy = ['zgłoszony', 'w toku', 'zakończony']
priorytety = ['niski', 'średni', 'wysoki', 'krytyczny']
for i in range(500):
    Incydent.objects.create(typ=random.choice(typy_incydentow), status=random.choice(statusy), priorytet=random.choice(priorytety), lat=round(random.uniform(LAT_MIN, LAT_MAX), 6), lng=round(random.uniform(LNG_MIN, LNG_MAX), 6), zglaszajacy=autor)

print("GOTOWE! Pomyślnie dodano zasoby i incydenty do bazy.")
