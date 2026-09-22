import os
from google import genai
from datetime import datetime

# 1. API şifresini al ve istemciyi başlat
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Hata logunda Google'ın bizden açıkça kullanmamızı istediği güncel sürüm
aktif_model = "gemini-3.6-flash"

# 3. Günün tarihini al ve promptu oluştur
bugun = datetime.now().strftime("%d %B")
prompt = f"Bugün {bugun}. Tarihte bugün Türkiye ve dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

# 4. İçeriği üret
try:
    response = client.models.generate_content(
        model=aktif_model,
        contents=prompt
    )
    yeni_icerik = response.text
except Exception as e:
    print(f"İçerik üretilirken model hatası oluştu: {e}")
    exit(1)

# 5. HTML dosyasını güncelle
dosya_adi = "TAMU.html" 

try:
    with open(dosya_adi, "r", encoding="utf-8") as f:
        html = f.read()
        
    yer_tutucu = "<!-- GUNUN_OZETI -->" 
    
    if yer_tutucu in html:
        html = html.replace(yer_tutucu, yeni_icerik)
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"TAMU başarıyla güncellendi! (Kullanılan Model: {aktif_model})")
    else:
        print("Uyarı: HTML içinde değiştirilecek yer tutucu (<!-- GUNUN_OZETI -->) bulunamadı.")
            
except FileNotFoundError:
    print(f"Hata: {dosya_adi} bulunamadı.")
