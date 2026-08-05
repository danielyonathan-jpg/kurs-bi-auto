import cloudscraper
from bs4 import BeautifulSoup
import requests
import json

# ⚠️ TEMPELKAN URL WEB APP GOOGLE APPS SCRIPT ANDA DI SINI
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzU2RW2Or2gi_qTWca5hfwZyLHXLpD5vUkWNrERudTyrdz3NZrCOQSQgip9JFIv-8LF/exec"

def parse_num(val_str):
    """Mengubah format angka Indonesia (15.800,00) menjadi float (15800.00)"""
    val_str = val_str.strip().replace('.', '').replace(',', '.')
    return float(val_str)

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

    # Parsing struktur DOM HTML menggunakan BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    list_mata_uang = [
        "USD", "SGD", "EUR", "JPY", "AUD", "HKD", "MYR", "GBP", 
        "CAD", "CHF", "CNY", "DKK", "NZD", "SAR", "SEK", "THB"
    ]
    
    data_extracted = []
    
    # Cari seluruh baris tabel (tr)
    rows = soup.find_all('tr')
    
    for row in rows:
        # Ambil teks murni dari setiap kolom (td) dalam baris tersebut
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        
        # Baris tabel kurs BI memiliki minimal 4 kolom (Mata Uang, Nilai, Jual, Beli)
        if len(cols) >= 4:
            code = cols[0].upper()
            
            if code in list_mata_uang:
                try:
                    nilai = parse_num(cols[1])
                    jual = parse_num(cols[2])
                    beli = parse_num(cols[3])
                    avg = (jual + beli) / 2.0
                    
                    data_extracted.append({
                        "mataUang": code,
                        "nilai": nilai,
                        "jual": jual,
                        "beli": beli,
                        "average": avg
                    })
                except Exception as e:
                    print(f"Gagal memproses {code}: {e}")

    print(f"Berhasil menarik {len(data_extracted)} data kurs eksak dari BI!")
    
    if len(data_extracted) > 0:
        print("Mengirimkan data ke Google Sheets...")
        res = requests.post(WEBHOOK_URL, json={"data": data_extracted})
        print("Respon Google Sheets:", res.text)

if __name__ == "__main__":
    main()
