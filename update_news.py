import os
from google import genai
from datetime import datetime

# 1. API şifresini al ve yeni nesil istemciyi (client) başlat
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Günün tarihini al ve promptu oluştur
bugun = datetime.now().strftime("%d %B")
prompt = f"Bugün {bugun}. Tarihte bugün Türkiye ve dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

# 3. İçeriği Gemini'den üret (Yeni SDK formatı)
response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents=prompt
)
yeni_icerik = response.text

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
        print("TAMU başarıyla güncellendi.")
    else:
        print("Uyarı: HTML içinde değiştirilecek yer tutucu bulunamadı.")
        
except FileNotFoundError:
    print(f"Hata: {dosya_adi} bulunamadı.")
