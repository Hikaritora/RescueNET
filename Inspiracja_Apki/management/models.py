from django.db import models
from django.contrib.auth.models import AbstractUser

class Uzytkownik(AbstractUser):
    ROLE_CHOICES = [
        ('dyspozytor', 'Dyspozytor'),
        ('ratownik', 'Ratownik'),
        ('admin', 'Administrator'),
    ]
    rola = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Incydent(models.Model):
    PRIORITY_CHOICES = [
        ('niski', 'Niski'),
        ('średni', 'Średni'),
        ('wysoki', 'Wysoki'),
        ('krytyczny', 'Krytyczny'),
    ]
    TYPE_CHOICES = [
        ('Road Incident', 'Road Incident'),
        ('Medical Emergency', 'Medical Emergency'),
        ('Public Order Disturbance', 'Public Order Disturbance'),
        ('Domestic Violence', 'Domestic Violence'),
        ('Fire', 'Fire'),
        ('Technical & Weather Hazard', 'Technical & Weather Hazard'),
        ('Intoxicated or Dangerous Person', 'Intoxicated or Dangerous Person'),
        ('Theft & Suspicious Activity', 'Theft & Suspicious Activity'),
        ('Animal Assistance', 'Animal Assistance'),
        ('Missing Person', 'Missing Person'),
        ('Other', 'Other'),
    ]

    typ = models.CharField(max_length=50, choices=TYPE_CHOICES)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    priorytet = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, default='zgłoszony')
    zglaszajacy = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE)
    data_zgloszenia = models.DateTimeField(auto_now_add=True)
    notatki = models.TextField(blank=True, default='')


class Zasob(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_zasobu')
    nazwa = models.CharField(max_length=100)
    typ = models.CharField(max_length=50)
    specjalizacja = models.CharField(max_length=100, blank=True)
    dostepnosc = models.BooleanField(default=True)
    status = models.CharField(max_length=100, default='Available')
    lat = models.FloatField(default=51.1079)
    lng = models.FloatField(default=17.0385)

    class Meta:
        db_table = 'zasob'

    def __str__(self):
        return self.nazwa
