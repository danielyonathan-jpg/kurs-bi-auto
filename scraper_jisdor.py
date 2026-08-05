import cloudscraper
from bs4 import BeautifulSoup
import requests
import re

# ⚠️ TEMPELKAN URL WEB APP GOOGLE APPS SCRIPT ANDA DI SINI
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzU2RW2Or2gi_qTWca5hfwZyLHXLpD5vUkWNrERudTyrdz3NZrCOQSQgip9JFIv-8LF/exec"

def parse_indo_date(date_str):
    date_str = date_str.lower().strip()
    bulan_indo = {
        "januari": "01", "februari": "02", "maret": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
        "september": "09", "oktober": "10", "november": "11", "desember": "12"
    }
    
    for b_indo, b_num in bulan_indo.items():
        if b_indo in date_str:
            date_str = date_str.replace(b_indo, b_num)
            break
            
    parts = date_str.split()
    if len(parts) >= 3:
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return date_str

def main():
    print("Membuka Web BI (JISDOR) via Cloudscraper...")
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    url_jisdor = "https://www.bi.go.id/id/statistik/informasi-kurs/jisdor/Default.aspx"
    response = scraper.get(url_jisdor)
    
    if response.status_code != 200:
        print(f"Gagal mengakses Web BI JISDOR. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    data_extracted = []
    
    rows = soup.find_all('tr')
    
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        
        if len(cols) >= 2:
            tgl_str = cols[0]
            kurs_str = cols[1]
            
            if re.search(r'\d+', tgl_str):
                tgl_format = parse_indo_date(tgl_str)
                kurs_bersih = re.sub(r'[^\d,]', '', kurs_str).replace(',', '.')
                
                try:
                    kurs_angka = float(kurs_bersih)
                    data_extracted.append({
                        "tanggalBI": tgl_format,
                        "kurs": kurs_angka
                    })
                except ValueError:
                    continue

    print(f"Berhasil menarik {len(data_extracted)} data Kurs JISDOR!")
    
    if len(data_extracted) > 0:
        print("Mengirimkan data ke Google Sheets...")
        res = requests.post(WEBHOOK_URL, json={"type": "jisdor", "data": data_extracted})
        print("Respon Google Sheets:", res.text)

if __name__ == "__main__":
    main()
