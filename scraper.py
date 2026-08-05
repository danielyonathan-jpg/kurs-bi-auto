import cloudscraper
import re
import requests
import json

# ⚠️ TEMPELKAN URL WEB APP GOOGLE APPS SCRIPT ANDA DI SINI
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzU2RW2Or2gi_qTWca5hfwZyLHXLpD5vUkWNrERudTyrdz3NZrCOQSQgip9JFIv-8LF/exec"

def main():
    print("Membuka Web Bank Indonesia via Cloudscraper...")
    
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    url_bi = "https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx"
    response = scraper.get(url_bi)
    
    if response.status_code != 200:
        print(f"Gagal mengakses BI. Status code: {response.status_code}")
        return

    html = response.text
    
    list_mata_uang = [
        "USD", "SGD", "EUR", "JPY", "AUD", "HKD", "MYR", "GBP", 
        "CAD", "CHF", "CNY", "DKK", "NZD", "SAR", "SEK", "THB"
    ]
    
    data_extracted = []
    
    for curr in list_mata_uang:
        pattern = rf"{curr}[^\d]*?([\d.,]+)[^\d]*?([\d.,]+)[^\d]*?([\d.,]+)"
        match = re.search(pattern, html, re.IGNORECASE)
        
        if match:
            nilai_str = match.group(1).replace('.', '').replace(',', '.')
            jual_str = match.group(2).replace('.', '').replace(',', '.')
            beli_str = match.group(3).replace('.', '').replace(',', '.')
            
            try:
                nilai = float(nilai_str)
                jual = float(jual_str)
                beli = float(beli_str)
                avg = (jual + beli) / 2.0
                
                data_extracted.append({
                    "mataUang": curr,
                    "nilai": nilai,
                    "jual": jual,
                    "beli": beli,
                    "average": avg
                })
            except ValueError:
                continue

    print(f"Berhasil menarik {len(data_extracted)} data kurs eksak dari BI!")
    
    if len(data_extracted) > 0:
        print("Mengirimkan data ke Google Sheets...")
        res = requests.post(WEBHOOK_URL, json={"data": data_extracted})
        print("Respon Google Sheets:", res.text)

if __name__ == "__main__":
    main()
