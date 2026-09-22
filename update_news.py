import os
import time
from google import genai
from datetime import datetime

# 1. API şifresini al ve istemciyi başlat
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

aktif_model = "gemini-3.6-flash"

# 2. Günün tarihini al ve promptu oluştur
bugun = datetime.now().strftime("%d %B")
prompt = f"Bugün {bugun}. Tarihte bugün Türkiye ve dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

# 3. İçeriği üret (Zarif Çöküş - Graceful Degradation Mantığı)
max_deneme = 3
yeni_icerik = None

for deneme in range(max_deneme):
    try:
        response = client.models.generate_content(
            model=aktif_model,
            contents=prompt
        )
        yeni_icerik = response.text
        print("İçerik başarıyla üretildi.")
        break  # Başarılı olursa döngüden çık
    except Exception as e:
        print(f"Deneme {deneme + 1} başarısız: {e}")
        if deneme < max_deneme - 1:
            print("Sunucu yoğun, 15 saniye beklenip tekrar denenecek...")
            time.sleep(15)
        else:
            print("Maksimum deneme sayısına ulaşıldı. Google sunucuları tamamen kapalı.")
            # Sistemin çökmesini engellemek için yedek (fallback) bir metin atıyoruz
            yeni_icerik = "<ul><li><em>Şu an yapay zeka sunucularındaki yoğunluk nedeniyle güncel özet çekilememektedir. Lütfen daha sonra tekrar kontrol edin.</em></li></ul>"

# 4. HTML dosyasını güncelle
dosya_adi = "TAMU.html" 

try:
    with open(dosya_adi, "r", encoding="utf-8") as f:
        html = f.read()
        
    yer_tutucu = "<!-- GUNUN_OZETI -->" 
    
    if yer_tutucu in html:
        html = html.replace(yer_tutucu, yeni_icerik)
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"TAMU başarıyla güncellendi! (Kullanılan İçerik Durumu: {'Yedek Metin' if 'yoğunluk nedeniyle' in yeni_icerik else aktif_model})")
    else:
        print("Uyarı: HTML içinde değiştirilecek yer tutucu (<!-- GUNUN_OZETI -->) bulunamadı.")
            
except FileNotFoundError:
    print(f"Hata: {dosya_adi} bulunamadı.")
