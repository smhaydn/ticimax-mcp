# ticimax-mcp

Ticimax e-ticaret platformunu Claude ile yönetmek için MCP sunucusu.

Sipariş listeleme, stok güncelleme, ürün yönetimi, üye sorgulama ve daha fazlası — hepsini Claude'a söyleyerek yapabilirsin.

---

## Kurulum

### Yetki Kodunu Al

Ticimax paneline gir → **Ayarlar → Entegrasyon → Web Servisleri** → yetki kodunu kopyala.

---

### Yöntem 1 — Claude Code Arayüzünden (En Kolay)

1. VS Code'da **Claude Code** yan panelini aç
2. Alttaki **ayarlar simgesine** tıkla → **MCP Servers** → **Add MCP Server**
3. Şu bilgileri gir:

| Alan | Değer |
|------|-------|
| Command | `uv` |
| Arguments | `tool, run, ticimax-mcp` |
| TICIMAX_ALAN_ADI | `magazan.com` |
| TICIMAX_YETKI_KODU | `ticimax-yetki-kodun` |

4. Kaydet ve Claude Code'u yeniden başlat.

---

### Yöntem 2 — Elle Dosyaya Ekle

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

---

## Gereksinimler

- [Claude Code](https://claude.ai/code) (VS Code eklentisi)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) paket yöneticisi
- Ticimax mağaza yetki kodu
