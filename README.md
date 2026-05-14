# ticimax-mcp

Ticimax e-ticaret platformunu Claude ile yönetmek için MCP sunucusu.

Sipariş listeleme, stok güncelleme, ürün yönetimi, üye sorgulama ve daha fazlası — hepsini Claude'a söyleyerek yapabilirsin.

---

## Kurulum Yöntemleri

### Yöntem 1 — Railway ile Uzak Sunucu (En Kolay, Önerilen)

Bu yöntemde sunucu internette çalışır. Claude Desktop'tan tek tıkla bağlanılır, bilgisayara hiçbir şey kurulmaz.

#### Adım 1 — Railway'e Deploy Et

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template?template=https://github.com/smhaydn/ticimax-mcp)

Butona tıkla → Railway hesabınla giriş yap → Aşağıdaki bilgileri gir:

| Değişken | Değer |
|----------|-------|
| `TICIMAX_ALAN_ADI` | `magazan.com` |
| `TICIMAX_YETKI_KODU` | Ticimax panelinden aldığın yetki kodu |

Deploy tamamlandığında Railway sana bir URL verir:
`https://ticimax-mcp-xxxx.railway.app`

#### Adım 2 — Claude Desktop'a Ekle

1. Claude Desktop'ı aç → sol menüden **Connectors** → **Add connector**
2. **Add custom connector** ekranında:

| Alan | Değer |
|------|-------|
| Name | `Ticimax` |
| Remote MCP server URL | `https://ticimax-mcp-xxxx.railway.app/mcp` |

3. **Add** butonuna bas → hazır.

#### Yetki Kodunu Nereden Alırsın?

Ticimax paneli → **Ayarlar → Entegrasyon → Web Servisleri** → yetki kodunu kopyala.

---

### Yöntem 2 — Claude Code (VS Code) ile Yerel Kurulum

VS Code'da Claude Code kullanıyorsan bu yöntemi tercih edebilirsin.

#### Adım 1 — uv'yi Kur (yoksa)

```bash
pip install uv
```

#### Adım 2 — Claude Code'a Ekle

`~/.claude/mcp.json` dosyasına şu bloğu ekle:

```json
{
  "mcpServers": {
    "ticimax": {
      "command": "uv",
      "args": ["tool", "run", "ticimax-mcp"],
      "env": {
        "TICIMAX_ALAN_ADI": "magazan.com",
        "TICIMAX_YETKI_KODU": "ticimax-yetki-kodun"
      }
    }
  }
}
```

Kaydet ve Claude Code'u yeniden başlat.

---

### Bağlantıyı Test Et

Claude'a şunu söyle:

> "Ticimax bağlantısını test et"

Her servis için "Bağlantı başarılı" mesajı geliyorsa hazırsın.

---

## Araçlar

| Araç | Ne Yapar |
|------|----------|
| `baglanti_test` | Servislerin çalışıp çalışmadığını kontrol eder |
| `siparis_listele` | Son N günün siparişlerini listeler |
| `siparis_detay` | Sipariş detayı + ürünler + ödeme bilgisi |
| `siparis_durumu_guncelle` | Sipariş durumunu değiştirir |
| `kargo_takip_no_ekle` | Siparişe kargo takip numarası ekler |
| `kargo_secenekleri_listele` | Kullanılabilir kargo firmalarını gösterir |
| `stok_guncelle` | Tek ürün stok güncelleme |
| `toplu_stok_guncelle` | Çoklu ürün stok güncelleme |
| `urun_listele` | Ürünleri listeler |
| `urun_ara` | İsme göre ürün arama |
| `varyasyon_listele` | Ürünün beden/renk varyasyonları |
| `urun_fiyat_guncelle` | Ürün fiyatı güncelleme |
| `indirimli_fiyat_uygula` | Toplu yüzdelik indirim uygulama |
| `kategori_listele` | Tüm kategorileri listeler |
| `marka_listele` | Tüm markaları listeler |
| `uye_listele` | Üyeleri listeler, mail/tel ile arama |
| `uye_adres_listele` | Üyenin kayıtlı adresleri |
| `kargo_firma_listele` | Tanımlı kargo firmaları |
| `iade_talepleri_listele` | İade taleplerini listeler |
| `il_listele` | Türkiye illeri |

---

## Örnek Kullanım

Claude'a şunları söyleyebilirsin:

- "Son 7 günün siparişlerini listele"
- "Sipariş #1234'ü kargoya verildi olarak işaretle"
- "XYZ ürününün stokunu 50 yap"
- "Tüm ürünlere %20 indirim uygula"
- "İade taleplerini listele"
- "Bugün kaç sipariş geldi?"
