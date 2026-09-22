import os
from google import genai
from datetime import datetime

# 1. API şifresini al ve yeni nesil istemciyi başlat
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# --- KALICI ÇÖZÜM: DİNAMİK MODEL SEÇİCİ ---
# Sabit bir model adı yazmak yerine, sistemdeki en güncel aktif "flash" modelini otomatik bulur.
aktif_model = "gemini-2.5-flash" # Sistem bulamazsa çökmeyi önleyecek son nesil yedek

try:
    for model_info in client.models.list():
        isim = model_info.name.replace("models/", "")
        # Adında flash geçen ve metin üretebilen aktif bir model bul
        if "flash" in isim.lower() and "generateContent" in model_info.supported_generation_methods:
            aktif_model = isim
            break # Güncel modeli buldu ve kilitledi
except Exception:
    pass
# ------------------------------------------

# 2. Günün tarihini al ve promptu oluştur
bugun = datetime.now().strftime("%d %B")
prompt = f"Bugün {bugun}. Tarihte bugün Türkiye ve dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

# 3. İçeriği Gemini'den üret
try:
    response = client.models.generate_content(
        model=aktif_model,
        contents=prompt
    )
    yeni_icerik = response.text
except Exception as e:
    print(f"İçerik üretilirken model hatası oluştu: {e}")
    exit(1)

# 4. HTML dosyasını aç ve yeni içerikle güncelle
dosya_adi = "TAMU.html" 

try:
    with open(dosya_adi, "r", encoding="utf-8") as f:
        html = f.read()
        
    yer_tutucu = "<!-- GUNUN_OZETI -->" 
    
    if yer_tutucu in html:
        html = html.replace(yer_tutucu, yeni_icerik)
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"TAMU başarıyla güncellendi! (Otomatik Seçilen Model: {aktif_model})")
    else:
        print("Uyarı: HTML içinde değiştirilecek yer tutucu (<!-- GUNUN_OZETI -->) bulunamadı.")
        
except FileNotFoundError:
    print(f"Hata: {dosya_adi} bulunamadı.")
