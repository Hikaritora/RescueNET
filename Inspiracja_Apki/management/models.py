
from django.db import models
from django.contrib.auth.models import AbstractUser

# Rozszerzamy standardowego użytkownika o Twoje role [cite: 461]
class Uzytkownik(AbstractUser):
    ROLE_CHOICES = [
        ('dyspozytor', 'Dyspozytor'),
        ('ratownik', 'Ratownik'),
        ('admin', 'Administrator'),
    ]
    rola = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Incydent(models.Model):
    PRIORITY_CHOICES = [('niski', 'Niski'), ('średni', 'Średni'), ('wysoki', 'Wysoki'), ('krytyczny', 'Krytyczny')]
    
    typ = models.CharField(max_length=50) # [cite: 444]
    lat = models.DecimalField(max_digits=9, decimal_places=6) # Nasza decyzja o koordynatach
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    priorytet = models.CharField(max_length=10, choices=PRIORITY_CHOICES) # [cite: 444]
    status = models.CharField(max_length=20, default='zgłoszony') # [cite: 444]
    zglaszajacy = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE) # [cite: 507]
    

class Zasob(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_zasobu')
    nazwa = models.CharField(max_length=100)
    typ = models.CharField(max_length=50) # [cite: 456]
    specjalizacja = models.CharField(max_length=100, blank=True)
    dostepnosc = models.BooleanField(default=True) # [cite: 456]
    status = models.CharField(max_length=100, default='Available')
    lat = models.FloatField(default=51.1079) # Domyślnie Wrocław
    lng = models.FloatField(default=17.0385)
    
    class Meta:
        db_table = 'zasob'

    def __str__(self):
        return self.nazwa