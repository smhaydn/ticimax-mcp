"""
Ticimax MCP Sunucusu
lolaofshine.com mağazasını Claude ile yönetmek için
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
from zeep import Client
from zeep.transports import Transport
import requests

load_dotenv()

# Bağlantı ayarları
ALAN_ADI = os.getenv("TICIMAX_ALAN_ADI", "lolaofshine.com")
YETKI_KODU = os.getenv("TICIMAX_YETKI_KODU", "")

# Servis adresleri
def servis_url(servis_adi: str) -> str:
    return f"https://{ALAN_ADI}/servis/{servis_adi}.svc?wsdl"

# Zeep istemcileri — ilk çağrıda oluşturulur (lazy loading)
_istemciler = {}

def istemci_al(servis_adi: str):
    """Belirtilen servis için SOAP istemcisi döndürür."""
    if servis_adi not in _istemciler:
        session = requests.Session()
        transport = Transport(session=session, timeout=60)
        _istemciler[servis_adi] = Client(servis_url(servis_adi), transport=transport)
    return _istemciler[servis_adi]

def siparis_client():
    return istemci_al("SiparisServis")

def urun_client():
    return istemci_al("UrunServis")

def uye_client():
    return istemci_al("UyeServis")

def custom_client():
    return istemci_al("CustomServis")

# FastMCP sunucusu
mcp = FastMCP("Ticimax - lolaofshine.com")


# ─────────────────────────────────────────────
#  SİPARİŞ ARAÇLARI
# ─────────────────────────────────────────────

@mcp.tool()
def siparis_listele(
    son_kac_gun: int = 10,
    siparis_durumu: int = -1,
    odeme_durumu: int = -1,
    siparis_no: str = "",
    kayit_sayisi: int = 100
) -> str:
    """
    Siparişleri listeler.

    siparis_durumu değerleri:
    -1=hepsi, 0=ön sipariş, 1=onay bekliyor, 2=onaylandı, 3=ödeme bekliyor,
    4=paketleniyor, 5=tedarik ediliyor, 6=kargoya verildi, 7=teslim edildi,
    8=iptal edildi, 9=iade edildi

    odeme_durumu değerleri:
    -1=hepsi, 0=onay bekliyor, 1=onaylandı, 2=hatalı, 3=iade edilmiş, 4=iptal edilmiş
    """
    try:
        c = siparis_client()

        filtre = c.get_type("ns0:WebSiparisFiltre")(
            EntegrasyonAktarildi=-1,
            IptalEdilmisUrunler=True,
            OdemeDurumu=odeme_durumu,
            OdemeTipi=-1,
            SiparisDurumu=siparis_durumu,
            SiparisID=-1,
            SiparisKodu="",
            SiparisNo=siparis_no,
            SiparisTarihiBas=datetime.now() - timedelta(days=son_kac_gun),
            SiparisTarihiSon=datetime.now(),
            TedarikciID=-1,
            UyeID=-1,
        )

        sayfalama = c.get_type("ns0:WebSiparisSayfalama")(
            BaslangicIndex=0,
            KayitSayisi=kayit_sayisi,
            SiralamaDegeri="id",
            SiralamaYonu="Desc"
        )

        liste = c.service.SelectSiparis(YETKI_KODU, filtre, sayfalama)

        if not liste:
            return "Belirtilen kriterlere uygun sipariş bulunamadı."

        sonuc = []
        for s in liste:
            sonuc.append({
                "SiparisID": s.ID,
                "SiparisNo": s.SiparisNo,
                "Tarih": str(s.SiparisTarihi),
                "Durum": s.SiparisDurumu,
                "Tutar": s.ToplamTutar,
                "UyeAdi": f"{s.UyeAdi} {s.UyeSoyadi}",
                "OdemeTipi": s.OdemeTipi,
                "KargoTakipNo": s.KargoTakipNo,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Siparişler alınamadı. Sebep: {str(e)}"


@mcp.tool()
def siparis_detay(siparis_id: int) -> str:
    """Belirli bir siparişin detaylarını ve içindeki ürünleri getirir."""
    try:
        c = siparis_client()

        # Siparişteki ürünleri çek
        urunler = c.service.SelectSiparisUrun(YETKI_KODU, siparis_id, False)
        urun_listesi = []
        for u in (urunler or []):
            urun_listesi.append({
                "UrunAdi": u.UrunAdi,
                "Adet": u.Adet,
                "Fiyat": u.Fiyat,
                "Barkod": u.Barkod,
            })

        # Ödeme bilgisini çek
        odemeler = c.service.SelectSiparisOdeme(YETKI_KODU, siparis_id, 0)
        odeme_listesi = []
        for o in (odemeler or []):
            odeme_listesi.append({
                "OdemeTipi": o.OdemeTipi,
                "Tutar": o.Tutar,
                "Tarih": str(o.Tarih),
                "Durum": o.OdemeDurumu,
            })

        sonuc = {
            "SiparisID": siparis_id,
            "Urunler": urun_listesi,
            "Odemeler": odeme_listesi,
        }

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Sipariş detayı alınamadı. Sebep: {str(e)}"


@mcp.tool()
def siparis_durumu_guncelle(
    siparis_id: int,
    yeni_durum: int,
    kargo_takip_no: str = "",
    mail_gonder: bool = False
) -> str:
    """
    Siparişin durumunu günceller.

    yeni_durum değerleri:
    0=ön sipariş, 1=onay bekliyor, 2=onaylandı, 3=ödeme bekliyor,
    4=paketleniyor, 5=tedarik ediliyor, 6=kargoya verildi, 7=teslim edildi,
    8=iptal edildi, 9=iade edildi
    """
    try:
        c = siparis_client()

        istek = c.get_type("ns0:SetSiparisDurumRequest")(
            SiparisID=siparis_id,
            Durum=yeni_durum,
            KargoTakipNo=kargo_takip_no,
            MailBilgilendir=mail_gonder
        )

        cevap = c.service.SetSiparisDurum(YETKI_KODU, istek)

        if cevap.IsError:
            return f"Hata: {cevap.ErrorMessage}"

        durum_isimleri = {
            0: "Ön Sipariş", 1: "Onay Bekliyor", 2: "Onaylandı",
            3: "Ödeme Bekliyor", 4: "Paketleniyor", 5: "Tedarik Ediliyor",
            6: "Kargoya Verildi", 7: "Teslim Edildi", 8: "İptal Edildi", 9: "İade Edildi"
        }
        return f"Sipariş #{siparis_id} durumu '{durum_isimleri.get(yeni_durum, yeni_durum)}' olarak güncellendi."

    except Exception as e:
        return f"Hata: Sipariş durumu güncellenemedi. Sebep: {str(e)}"


@mcp.tool()
def kargo_takip_no_ekle(siparis_id: int, takip_no: str) -> str:
    """Siparişe kargo takip numarası ekler."""
    try:
        c = siparis_client()
        sonuc = c.service.SaveKargoTakipNo(YETKI_KODU, siparis_id, "", takip_no)

        if sonuc == "OK":
            return f"Sipariş #{siparis_id} için kargo takip numarası eklendi: {takip_no}"
        return f"Beklenmedik yanıt: {sonuc}"

    except Exception as e:
        return f"Hata: Kargo takip numarası eklenemedi. Sebep: {str(e)}"


@mcp.tool()
def kargo_secenekleri_listele(sehir_id: int = 34) -> str:
    """Kullanılabilir kargo firmalarını ve fiyatlarını listeler. sehir_id: 34=İstanbul"""
    try:
        c = siparis_client()

        istek = c.get_type("ns0:GetKargoSecenekRequest")(
            ParaBirimi="TL",
            SehirId=sehir_id,
        )

        liste = c.service.GetKargoSecenek(YETKI_KODU, istek)

        if not liste:
            return "Kargo seçeneği bulunamadı."

        sonuc = []
        for k in liste:
            sonuc.append({
                "KargoID": k.ID,
                "KargoAdi": k.Adi,
                "Fiyat": k.Fiyat,
                "TahminiSure": k.TahminiSure,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Kargo seçenekleri alınamadı. Sebep: {str(e)}"


@mcp.tool()
def iade_talepleri_listele(durum_id: int = -1) -> str:
    """
    İade taleplerini listeler.
    durum_id: -1=hepsi, 1=bekliyor, 2=onaylandı, 3=reddedildi
    """
    try:
        c = custom_client()

        filtre = c.get_type("ns0:IadeTalepFiltre")(
            DurumID=durum_id,
            ParaIadeTipi=-1,
            SiparisID=-1,
            UyeID=-1,
            ID=-1,
        )
        istek = c.get_type("ns0:WebIadeTalepSelectRequest")(Filtre=filtre)

        cevap = c.service.SelectIadeTalebi(YETKI_KODU, istek)

        if cevap.IsError:
            return f"Hata: {cevap.ErrorMessage}"

        if not cevap.IadeTalepList:
            return "İade talebi bulunamadı."

        sonuc = []
        for t in cevap.IadeTalepList:
            sonuc.append({
                "TalepID": t.ID,
                "SiparisID": t.SiparisID,
                "UyeID": t.UyeID,
                "Durum": t.Durum,
                "ParaIadeTipi": t.ParaIadeTipi,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: İade talepleri alınamadı. Sebep: {str(e)}"


# ─────────────────────────────────────────────
#  ÜRÜN & STOK ARAÇLARI
# ─────────────────────────────────────────────

@mcp.tool()
def stok_guncelle(varyasyon_id: int, yeni_stok: int) -> str:
    """Bir ürün varyasyonunun stok adedini günceller."""
    try:
        c = urun_client()

        varyasyon = c.get_type("ns0:Varyasyon")(
            ID=varyasyon_id,
            StokAdedi=yeni_stok
        )

        c.service.StokAdediGuncelle(YETKI_KODU, [varyasyon])

        return f"Varyasyon #{varyasyon_id} stok adedi {yeni_stok} olarak güncellendi."

    except Exception as e:
        return f"Hata: Stok güncellenemedi. Sebep: {str(e)}"


@mcp.tool()
def toplu_stok_guncelle(varyasyon_stok_listesi: str) -> str:
    """
    Birden fazla ürünün stokunu tek seferde günceller.
    varyasyon_stok_listesi: JSON formatında liste, örnek:
    [{"varyasyon_id": 123, "stok": 50}, {"varyasyon_id": 456, "stok": 30}]
    """
    try:
        c = urun_client()
        liste_data = json.loads(varyasyon_stok_listesi)

        varyasyon_tipi = c.get_type("ns0:Varyasyon")
        varyasyonlar = []
        for item in liste_data:
            varyasyonlar.append(varyasyon_tipi(
                ID=item["varyasyon_id"],
                StokAdedi=item["stok"]
            ))

        c.service.StokAdediGuncelle(YETKI_KODU, varyasyonlar)

        return f"{len(varyasyonlar)} ürünün stoğu güncellendi."

    except json.JSONDecodeError:
        return "Hata: Liste formatı yanlış. Örnek: [{\"varyasyon_id\": 123, \"stok\": 50}]"
    except Exception as e:
        return f"Hata: Toplu stok güncellenemedi. Sebep: {str(e)}"


@mcp.tool()
def urun_listele(
    kategori_id: int = -1,
    marka_id: int = -1,
    aktif: int = 1,
    kayit_sayisi: int = 50,
    sayfa_no: int = 1
) -> str:
    """
    Ürünleri listeler.
    aktif: 1=aktif ürünler, 0=pasif ürünler, -1=hepsi
    """
    try:
        c = urun_client()

        filtre = c.get_type("ns0:UrunFiltre")(
            AktifDurum=aktif,
            KategoriID=kategori_id,
            MarkaID=marka_id,
        )

        sayfalama = c.get_type("ns0:UrunSayfalama")(
            KayitSayisi=kayit_sayisi,
            SiralamaDegeri="id",
            SiralamaYonu="Desc",
            SayfaNo=sayfa_no
        )

        liste = c.service.SelectUrun(YETKI_KODU, filtre, sayfalama)

        if not liste:
            return "Ürün bulunamadı."

        sonuc = []
        for u in liste:
            sonuc.append({
                "UrunID": u.ID,
                "UrunAdi": u.Adi,
                "Barkod": u.Barkod,
                "Fiyat": u.SatisFiyati,
                "Aktif": u.Aktif,
                "Stok": u.ToplamStok,
                "KategoriID": u.KategoriID,
                "MarkaID": u.MarkaID,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Ürünler alınamadı. Sebep: {str(e)}"


@mcp.tool()
def urun_ara(arama_metni: str, kayit_sayisi: int = 20) -> str:
    """İsme göre ürün arar."""
    try:
        c = urun_client()

        filtre = c.get_type("ns0:UrunFiltre")(
            Adi=arama_metni,
            AktifDurum=-1,
        )

        sayfalama = c.get_type("ns0:UrunSayfalama")(
            KayitSayisi=kayit_sayisi,
            SiralamaDegeri="id",
            SiralamaYonu="Desc",
            SayfaNo=1
        )

        liste = c.service.SelectUrun(YETKI_KODU, filtre, sayfalama)

        if not liste:
            return f"'{arama_metni}' aramasında ürün bulunamadı."

        sonuc = []
        for u in liste:
            sonuc.append({
                "UrunID": u.ID,
                "UrunAdi": u.Adi,
                "Barkod": u.Barkod,
                "Fiyat": u.SatisFiyati,
                "Stok": u.ToplamStok,
                "Aktif": u.Aktif,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Ürün araması yapılamadı. Sebep: {str(e)}"


@mcp.tool()
def varyasyon_listele(urun_kart_id: int) -> str:
    """Bir ürüne ait tüm varyasyonları (beden, renk vb.) listeler."""
    try:
        c = urun_client()

        filtre = c.get_type("ns0:VaryasyonFiltre")(
            UrunKartiID=urun_kart_id,
        )

        liste = c.service.SelectVaryasyon(YETKI_KODU, filtre)

        if not liste:
            return f"Ürün #{urun_kart_id} için varyasyon bulunamadı."

        sonuc = []
        for v in liste:
            sonuc.append({
                "VaryasyonID": v.ID,
                "Barkod": v.Barkod,
                "StokAdedi": v.StokAdedi,
                "Fiyat": v.SatisFiyati,
                "Ozellik1": v.Ozellik1,
                "Ozellik2": v.Ozellik2,
                "Aktif": v.Aktif,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Varyasyonlar alınamadı. Sebep: {str(e)}"


@mcp.tool()
def kategori_listele() -> str:
    """Tüm ürün kategorilerini listeler."""
    try:
        c = urun_client()
        liste = c.service.SelectKategori(YETKI_KODU)

        if not liste:
            return "Kategori bulunamadı."

        sonuc = []
        for k in liste:
            sonuc.append({
                "KategoriID": k.ID,
                "KategoriAdi": k.Adi,
                "UstKategoriID": k.PID,
                "Aktif": k.Aktif,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Kategoriler alınamadı. Sebep: {str(e)}"


@mcp.tool()
def marka_listele() -> str:
    """Tüm markaları listeler."""
    try:
        c = urun_client()
        liste = c.service.SelectMarka(YETKI_KODU)

        if not liste:
            return "Marka bulunamadı."

        sonuc = []
        for m in liste:
            sonuc.append({
                "MarkaID": m.ID,
                "MarkaAdi": m.Adi,
                "Aktif": m.Aktif,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Markalar alınamadı. Sebep: {str(e)}"


@mcp.tool()
def urun_fiyat_guncelle(
    varyasyon_id: int,
    satis_fiyati: float,
    liste_fiyati: Optional[float] = None
) -> str:
    """Bir ürün varyasyonunun fiyatını günceller."""
    try:
        c = urun_client()

        varyasyon = c.get_type("ns0:Varyasyon")(
            ID=varyasyon_id,
            SatisFiyati=satis_fiyati,
            ListeFiyati=liste_fiyati or satis_fiyati,
        )

        c.service.VaryasyonGuncelle(YETKI_KODU, [varyasyon])

        return f"Varyasyon #{varyasyon_id} fiyatı {satis_fiyati} TL olarak güncellendi."

    except Exception as e:
        return f"Hata: Fiyat güncellenemedi. Sebep: {str(e)}"


# ─────────────────────────────────────────────
#  ÜYE ARAÇLARI
# ─────────────────────────────────────────────

@mcp.tool()
def uye_listele(
    mail: str = "",
    telefon: str = "",
    aktif: int = -1,
    kayit_sayisi: int = 50,
    sayfa_no: int = 1
) -> str:
    """
    Üyeleri listeler. Mail veya telefon ile arama yapılabilir.
    aktif: -1=hepsi, 1=aktif, 0=pasif
    """
    try:
        c = uye_client()

        filtre = c.get_type("ns0:UyeFiltre")(
            Aktif=aktif,
            AlisverisYapti=-1,
            Cinsiyet=-1,
            MailIzin=-1,
            SmsIzin=-1,
            UyeID=-1,
            Mail=mail,
            Telefon=telefon,
        )

        sayfalama = c.get_type("ns0:UyeSayfalama")(
            KayitSayisi=kayit_sayisi,
            SiralamaDegeri="id",
            SiralamaYonu="Desc",
            SayfaNo=sayfa_no
        )

        liste = c.service.SelectUyeler(YETKI_KODU, filtre, sayfalama)

        if not liste:
            return "Üye bulunamadı."

        sonuc = []
        for u in liste:
            sonuc.append({
                "UyeID": u.ID,
                "Isim": u.Isim,
                "Soyisim": u.Soyisim,
                "Mail": u.Mail,
                "Telefon": u.Telefon,
                "UyelikTarihi": str(u.UyelikTarihi),
                "Aktif": u.Aktif,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Üyeler alınamadı. Sebep: {str(e)}"


@mcp.tool()
def uye_adres_listele(uye_id: int) -> str:
    """Belirli bir üyenin kayıtlı adreslerini listeler."""
    try:
        c = uye_client()
        liste = c.service.SelectUyeAdres(YETKI_KODU, 0, uye_id)

        if not liste:
            return f"Üye #{uye_id} için adres bulunamadı."

        sonuc = []
        for a in liste:
            sonuc.append({
                "AdresID": a.ID,
                "Tanim": a.Tanim,
                "Adres": a.Adres,
                "Ilce": a.Ilce,
                "Sehir": a.Sehir,
                "Ulke": a.Ulke,
                "AliciAdi": a.AliciAdi,
                "Telefon": a.AliciTelefon,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Üye adresleri alınamadı. Sebep: {str(e)}"


# ─────────────────────────────────────────────
#  KAMPANYA / İNDİRİM ARAÇLARI
# ─────────────────────────────────────────────

@mcp.tool()
def kampanya_listele() -> str:
    """
    Mevcut kampanyaları listeler.
    Not: Kampanya bilgisi Custom Servis üzerinden alınır.
    """
    try:
        c = custom_client()
        # Kampanya için entegrasyon veya özel servis çağrısı
        # Ticimax'ın kampanya servisi CustomServis altında
        return (
            "Kampanya yönetimi için Ticimax panel üzerinden ilerleyebilirsiniz. "
            "Kampanya fiyatlarını urun_fiyat_guncelle aracıyla ürün bazlı güncelleyebilir, "
            "toplu_stok_guncelle ile stok ayarlaması yapabilirsiniz."
        )
    except Exception as e:
        return f"Hata: {str(e)}"


@mcp.tool()
def indirimli_fiyat_uygula(
    varyasyon_id_listesi: str,
    indirim_yuzdesi: float
) -> str:
    """
    Birden fazla varyasyona yüzdelik indirim uygular.

    varyasyon_id_listesi: JSON formatında liste, örnek: [123, 456, 789]
    indirim_yuzdesi: örnek 20 (yüzde 20 indirim)
    """
    try:
        c = urun_client()
        id_listesi = json.loads(varyasyon_id_listesi)

        # Önce mevcut fiyatları çek
        filtre = c.get_type("ns0:VaryasyonFiltre")(
            IDList=id_listesi
        )
        mevcut_varyasyonlar = c.service.SelectVaryasyon(YETKI_KODU, filtre)

        if not mevcut_varyasyonlar:
            return "Belirtilen varyasyonlar bulunamadı."

        varyasyon_tipi = c.get_type("ns0:Varyasyon")
        guncellenecekler = []

        for v in mevcut_varyasyonlar:
            yeni_fiyat = round(v.SatisFiyati * (1 - indirim_yuzdesi / 100), 2)
            guncellenecekler.append(varyasyon_tipi(
                ID=v.ID,
                SatisFiyati=yeni_fiyat,
                ListeFiyati=v.SatisFiyati,  # Liste fiyatı orijinal kalır (üstü çizili fiyat)
            ))

        c.service.VaryasyonGuncelle(YETKI_KODU, guncellenecekler)

        return f"{len(guncellenecekler)} ürüne %{indirim_yuzdesi} indirim uygulandı."

    except json.JSONDecodeError:
        return "Hata: Liste formatı yanlış. Örnek: [123, 456, 789]"
    except Exception as e:
        return f"Hata: İndirim uygulanamadı. Sebep: {str(e)}"


# ─────────────────────────────────────────────
#  KARGO & LOJİSTİK ARAÇLARI
# ─────────────────────────────────────────────

@mcp.tool()
def kargo_firma_listele() -> str:
    """Tanımlı kargo firmalarını listeler."""
    try:
        c = custom_client()
        liste = c.service.SelectKargoFirmalari(YETKI_KODU)

        if not liste:
            return "Kargo firması bulunamadı."

        sonuc = []
        for k in liste:
            sonuc.append({
                "KargoID": k.ID,
                "KargoAdi": k.Adi,
                "Aktif": k.Aktif,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: Kargo firmaları alınamadı. Sebep: {str(e)}"


# ─────────────────────────────────────────────
#  GENEL BİLGİ ARAÇLARI
# ─────────────────────────────────────────────

@mcp.tool()
def baglanti_test() -> str:
    """Ticimax servislerine bağlantının çalışıp çalışmadığını test eder."""
    sonuclar = {}

    servisler = [
        ("SiparisServis", lambda: siparis_client()),
        ("UrunServis", lambda: urun_client()),
        ("UyeServis", lambda: uye_client()),
        ("CustomServis", lambda: custom_client()),
    ]

    for ad, client_fn in servisler:
        try:
            client_fn()
            sonuclar[ad] = "Bağlantı başarılı"
        except Exception as e:
            sonuclar[ad] = f"Bağlantı başarısız: {str(e)}"

    return json.dumps(sonuclar, ensure_ascii=False)


@mcp.tool()
def il_listele() -> str:
    """Türkiye'deki tüm illeri listeler."""
    try:
        c = custom_client()

        istek = c.get_type("ns0:SelectIlRequest")(
            FiltreIlID=-1,
            FiltreUlkeID=-1
        )

        liste = c.service.SelectIller(YETKI_KODU, istek)

        if not liste:
            return "İl bulunamadı."

        sonuc = []
        for il in liste:
            sonuc.append({
                "IlID": il.ID,
                "IlAdi": il.Adi,
            })

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return f"Hata: İller alınamadı. Sebep: {str(e)}"


def main():
    mcp.run()

if __name__ == "__main__":
    main()
