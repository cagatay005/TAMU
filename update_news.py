import os
import time
import re
import urllib.request
import xml.etree.ElementTree as ET
from google import genai
from datetime import datetime

# --- 1. GERÇEK GÜNCEL HABERLERİ ÇEKME (CANLI RSS MOTORU) ---
def guncel_haberleri_al():
    rss_url = "https://www.ntv.com.tr/gundem.rss" # Güvenilir ve hızlı ulusal haber akışı
    haber_html = ""
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        # En güncel 5 haberi al ve Claude'un tasarımına uygun HTML'e çevir
        for item in root.findall('./channel/item')[:5]:
            baslik = item.find('title').text
            link = item.find('link').text
            
            haber_html += f"""
            <div style="display:flex;gap:12px;padding:11px 0;border-bottom:1px solid #DED8B8">
              <span style="font-size:14px;font-variant-numeric:tabular-nums;color:#5C5F50;min-width:42px">YENİ</span>
              <div style="min-width:0">
                <div style="font-size:12.5px;letter-spacing:.05em;color:#6E5437;margin-bottom:3px">GÜNDEM</div>
                <a href="{link}" target="_blank" style="font-size:17px;line-height:1.35;font-weight:500;color:#262820;text-decoration:none;border-bottom:1px solid #C0C78C">{baslik}</a>
              </div>
            </div>
            """
        return haber_html
    except Exception as e:
        print(f"RSS Çekme Hatası: {e}")
        return "<!-- Güncel haberler şu an çekilemiyor -->"

# --- 2. TARİHTE BUGÜN (GEMINI YAPAY ZEKA MOTORU) ---
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
aktif_model = "gemini-3.6-flash"

bugun = datetime.now().strftime("%d %B")
prompt = f"Bugün {bugun}. Tarihte bugün Türkiye ve dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

max_deneme = 3
tarihte_bugun_icerik = None

for deneme in range(max_deneme):
    try:
        response = client.models.generate_content(
            model=aktif_model,
            contents=prompt
        )
        tarihte_bugun_icerik = response.text
        print("Tarihte Bugün başarıyla üretildi.")
        break  
    except Exception as e:
        print(f"Deneme {deneme + 1} başarısız: {e}")
        if deneme < max_deneme - 1:
            time.sleep(900) 
        else:
            tarihte_bugun_icerik = "<ul><li><em>Şu an yapay zeka sunucularındaki yoğunluk nedeniyle veri çekilememektedir.</em></li></ul>"

# --- 3. HTML DOSYASINI GÜNCELLEME VE KAYDETME ---
dosya_adi = "TAMU.html" 

try:
    with open(dosya_adi, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Tarihte Bugün bloğunu korumalı şekilde değiştir
    html = re.sub(
        r'(<!-- GUNUN_OZETI -->)(.*?)(<!-- /GUNUN_OZETI -->)', 
        rf'\g<1>\n{tarihte_bugun_icerik}\n\g<3>', 
        html, 
        flags=re.DOTALL
    )
    
    # Canlı Haberler bloğunu korumalı şekilde değiştir
    yeni_son_haberler = guncel_haberleri_al()
    html = re.sub(
        r'(<!-- SON_HABERLER -->)(.*?)(<!-- /SON_HABERLER -->)', 
        rf'\g<1>\n{yeni_son_haberler}\n\g<3>', 
        html, 
        flags=re.DOTALL
    )
        
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(html)
    print("TAMU başarıyla güncellendi! (Yapay Zeka + Canlı RSS)")
            
except FileNotFoundError:
    print(f"Hata: {dosya_adi} bulunamadı.")
