from django.db import models
from django.utils import timezone

# Veritabanı için modeller oluşturulur.
"""
    Son Kontrol: 05.07.2020 MS
"""

class Uyeler(models.Model):
    UyeAdi = models.CharField(name="Üye Adı", max_length=40)
    UyeKullaniciAdi = models.CharField(name="Üye Kullanıcı Adı", max_length=16)
    UyeEmail =  models.CharField(name="Üye Email", max_length=40)
    UyeUnvan =  models.CharField(name="Üye Ünvan", max_length=30)
    UyeSifre =  models.TextField(name="Üye Şifre", )
    UyeBiyografi = models.CharField(name="Üye Biyografi", max_length=200)
    UyeMeslegi = models.CharField(name="Üye Mesleği", max_length=20)
    UyePuani = models.IntegerField(name="Üye Puanı")
    UyeSayginligi = models.IntegerField(name="Üye Saygınlığı")
    UyeAvatarYolu =  models.TextField(name="Üye Avatarı", )
    UyeRol = models.IntegerField(name="Üye Rolü")
    UyeKayitTarihi = models.DateTimeField(name="Üye Kayıt Tarihi", default=timezone.now)

class ForumKonulari(models.Model):
    KonuBasligi = models.CharField(name="Konu Başlığı", max_length=140)
    KonuDetayi =  models.TextField(name="Konu Detayı")
    KonuSahibi=  models.CharField(name="Konu Sahibi", max_length=16)
    KonuTarihi =  models.DateTimeField(name="Konu Tarihi", default=timezone.now)
    KonuKategori =  models.CharField(name="Konu Kategorisi", max_length=20)
    KonuOnay = models.BooleanField(default=False)

class ForumIslemleri(models.Model):
    IslemKullanicisi = models.CharField(name="İşlemi Yapan", max_length=16)
    IslemTipi = models.IntegerField(name="İşlem Tipi")
    IslemTarihi = models.DateTimeField(name="Üye Kayıt Tarihi", default=timezone.now)