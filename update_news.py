import os
import time
import urllib.request
import xml.etree.ElementTree as ET
from google import genai
from datetime import datetime
import glob

def guncel_haberleri_al():
    # Haber sitelerinin bot engellerine takılmamak için en stabil kaynaklardan BBC Türkçe'yi kullanıyoruz
    rss_url = "https://feeds.bbci.co.uk/turkce/rss.xml"
    haber_html = ""
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        # XML düğümlerini kesin bulmak için iter() kullanıyoruz
        items = list(root.iter('item'))[:5]
        if not items:
            return "<div style='padding:10px; color:#7A2E12;'>Haberler çekildi fakat okunamadı.</div>"
            
        for item in items:
            baslik = item.find('title').text if item.find('title') is not None else "Başlık Yok"
            link = item.find('link').text if item.find('link') is not None else "#"
            
            haber_html += f"""
            <div style="display:flex;gap:12px;padding:11px 0;border-bottom:1px solid #DED8B8">
              <span style="font-size:14px;font-variant-numeric:tabular-nums;color:#5C5F50;min-width:42px">YENİ</span>
              <div style="min-width:0">
                <div style="font-size:12.5px;letter-spacing:.05em;color:#6E5437;margin-bottom:3px">GÜNDEM</div>
                <a href="{link}" target="_blank" style="font-size:17px;line-height:1.35;font-weight:500;color:#262820;text-decoration:none;border-bottom:1px solid #C0C78C">{baslik}</a>
              </div>
            </div>"""
        return haber_html
    except Exception as e:
        print(f"RSS Çekme Hatası: {e}")
        return f"<div style='padding:10px; color:#7A2E12;'>Canlı haber akışı hatası: {e}</div>"

def html_degistir(html_metni, baslangic, bitis, yeni_icerik):
    # Kırılgan kodlar yerine, kesin çalışan böl-birleştir mantığı
    if baslangic in html_metni and bitis in html_metni:
        ilk_kisim = html_metni.split(baslangic)[0] + baslangic + "\n"
        ikinci_kisim = "\n" + bitis + html_metni.split(bitis)[1]
        return ilk_kisim + yeni_icerik + ikinci_kisim
    return html_metni

# --- 1. GEMINI TARİHTE BUGÜN MOTORU ---
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
aktif_model = "gemini-3.6-flash"

# Sistemin çalıştığı konumun yerel saatini dinamik olarak alır
bugun = datetime.now().astimezone().strftime("%d %B")

# Sadece "dünyada" diyerek küresel olaylara odaklanıyoruz
prompt = f"Bugün {bugun}. Tarihte bugün dünyada yaşanmış en önemli 3 olayı tarafsız ve gazetecilik diliyle özetle. Sadece HTML formatında <ul><li>...</li></ul> listesi olarak ver. Görsel kullanamadığımız için betimleyici ol."

tarihte_bugun_icerik = "<ul><li><em>Şu an yapay zeka sunucularındaki yoğunluk nedeniyle veri çekilememektedir.</em></li></ul>"
for deneme in range(3):
    try:
        response = client.models.generate_content(model=aktif_model, contents=prompt)
        tarihte_bugun_icerik = response.text
        print(f"Tarihte Bugün ({bugun}) başarıyla üretildi.")
        break  
    except Exception as e:
        print(f"Deneme {deneme + 1} başarısız: {e}")
        if deneme < 2: time.sleep(15)
        
# --- 2. CANLI RSS HABERLERİ ---
yeni_haberler = guncel_haberleri_al()
print("Güncel haberler çekildi.")

# --- 3. TÜM HTML DOSYALARINI GÜNCELLEME ---
# İsmi ne olursa olsun içindeki etiketleri bulup güncelleyecek
html_dosyalari = glob.glob("*.html")
guncellenen_dosya_sayisi = 0

for dosya in html_dosyalari:
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            html = f.read()
            
        yeni_html = html_degistir(html, "<!-- GUNUN_OZETI -->", "<!-- /GUNUN_OZETI -->", tarihte_bugun_icerik)
        yeni_html = html_degistir(yeni_html, "<!-- SON_HABERLER -->", "<!-- /SON_HABERLER -->", yeni_haberler)
            
        if html != yeni_html:
            with open(dosya, "w", encoding="utf-8") as f:
                f.write(yeni_html)
            print(f"{dosya} başarıyla güncellendi.")
            guncellenen_dosya_sayisi += 1
    except Exception as e:
        print(f"Hata ({dosya}): {e}")

if guncellenen_dosya_sayisi == 0:
    print("Uyarı: Değiştirilecek yer tutucu etiketi hiçbir HTML dosyasında bulunamadı veya içerik aynı.")
