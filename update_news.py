import os
import google.generativeai as genai
from datetime import datetime

# 1. GitHub Secrets kasasından API şifreni güvenlice al
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Gemini 1.5 modelini ayarla
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Günün tarihini al ve haber/tarih promptu oluştur
bugun = datetime.now().strftime("%d %B")
prompt = f"Bugün {bugun}. Tarihte bugün Türkiye ve dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

# 4. İçeriği Gemini'den üret
cevap = model.generate_content(prompt)
yeni_icerik = cevap.text

# 5. HTML dosyasını aç ve yeni içerikle güncelle
dosya_adi = "TAMU.html" # Claude'un verdiği dosya adı farklıysa burayı düzeltin (ör. index.html)

try:
    with open(dosya_adi, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Claude'un tasarımında ayrılan yeri bul ve Gemini'nin metniyle değiştir
    # Not: Gerçek entegrasyonda 'yer_tutucu' kısmına Claude'un koyduğu başlık veya yorum satırı yazılır
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
