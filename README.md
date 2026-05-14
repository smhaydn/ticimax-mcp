# ticimax-mcp

Ticimax e-ticaret platformunu Claude ile yönetmek için MCP sunucusu.

Her Ticimax mağazası kendi alan adı ve yetki koduyla bağlanır — tek sunucu, sınırsız mağaza.

---

## Kurulum

### Adım 1 — Railway'e Deploy Et

Aşağıdaki butona tıkla, Railway hesabınla giriş yap ve deploy et. Kimlik bilgisi girmen gerekmez, her kullanıcı kendi bilgilerini URL ile verir.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template?template=https://github.com/smhaydn/ticimax-mcp)

Deploy tamamlandığında Railway sana bir URL verir:
```
https://ticimax-mcp-xxxx.railway.app
```

---

### Adım 2 — Yetki Kodunu Al

Ticimax paneline gir → **Ayarlar → Entegrasyon → Web Servisleri** → yetki kodunu kopyala.

---

### Adım 3 — Claude Desktop'a Ekle

1. Claude Desktop'ı aç → sol menüden **Connectors** → **Add connector** → **Add custom connector**
2. Şu bilgileri gir:

| Alan | Değer |
|------|-------|
| Name | `Ticimax` |
| Remote MCP server URL | `https://ticimax-mcp-xxxx.railway.app/mcp?alan=ALAN_ADIN&yetki=YETKİ_KODUN` |

**Örnek URL:**
```
https://ticimax-mcp-xxxx.railway.app/mcp?alan=magazan.com&yetki=ABC123XYZ
```

3. **Add** butonuna bas → hazır.

---

### Bağlantıyı Test Et

Claude'a şunu söyle:

> "Ticimax bağlantısını test et"

"Bağlantı başarılı" mesajları geliyorsa her şey çalışıyor.

---

## Claude Code (VS Code) ile Kullanım

VS Code'da Claude Code kullanıyorsan `~/.claude/mcp.json` dosyasına ekle:

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
