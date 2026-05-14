# Ticimax MCP Kurulum Rehberi

## 1. Gerekli paketleri kur

```bash
cd "C:\Users\ASUS\Desktop\Projeler\ticimax mcp"
pip install -r requirements.txt
```

## 2. Yetki kodunu ayarla

`.env.example` dosyasını kopyala ve `.env` yap:

```bash
copy .env.example .env
```

`.env` dosyasını aç ve yetki kodunu gir:
```
TICIMAX_ALAN_ADI=lolaofshine.com
TICIMAX_YETKI_KODU=BURAYA_TICIMAX_YETKI_KODUNU_YAZ
```

## 3. Claude Code'a bağla

`C:\Users\ASUS\.claude\settings.json` dosyasına şunu ekle:

```json
{
  "mcpServers": {
    "ticimax": {
      "command": "python",
      "args": ["C:\\Users\\ASUS\\Desktop\\Projeler\\ticimax mcp\\server.py"],
      "env": {
        "TICIMAX_ALAN_ADI": "lolaofshine.com",
        "TICIMAX_YETKI_KODU": "BURAYA_YETKI_KODU"
      }
    }
  }
}
```

## 4. Test et

Claude Code'da şunu yaz:
> "Ticimax bağlantısını test et"

## Mevcut Araçlar

| Araç | Ne Yapar |
|------|----------|
| `baglanti_test` | Servislerin çalışıp çalışmadığını kontrol eder |
| `siparis_listele` | Son N günün siparişlerini listeler |
| `siparis_detay` | Sipariş detayı + ürünler + ödeme bilgisi |
| `siparis_durumu_guncelle` | Sipariş durumu değiştirir |
| `kargo_takip_no_ekle` | Siparişe takip no ekler |
| `kargo_secenekleri_listele` | Kullanılabilir kargo firmalarını gösterir |
| `stok_guncelle` | Tek ürün stok güncelleme |
| `toplu_stok_guncelle` | Çoklu ürün stok güncelleme |
| `urun_listele` | Ürünleri sayfalı listeler |
| `urun_ara` | İsme göre ürün arama |
| `varyasyon_listele` | Ürünün beden/renk varyasyonları |
| `urun_fiyat_guncelle` | Tek ürün fiyat güncelleme |
| `indirimli_fiyat_uygula` | Toplu yüzdelik indirim uygulama |
| `kategori_listele` | Tüm kategorileri listeler |
| `marka_listele` | Tüm markaları listeler |
| `uye_listele` | Üyeleri listeler, mail/tel ile arama |
| `uye_adres_listele` | Üyenin kayıtlı adresleri |
| `kargo_firma_listele` | Tanımlı kargo firmaları |
| `iade_talepleri_listele` | İade taleplerini listeler |
| `il_listele` | Türkiye illeri |
