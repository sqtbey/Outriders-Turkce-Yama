# Outriders %100 Türkçe Yama (PC / Steam)

![Yama Durumu](https://img.shields.io/badge/Durum-%25100_Tamamland%C4%B1-success?style=for-the-badge)
![Oyun Sürümü](https://img.shields.io/badge/Oyun-Outriders_Steam-blue?style=for-the-badge)
![Mimari](https://img.shields.io/badge/Motor-Unreal_Engine_4.25-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-PC_Windows-lightgrey?style=for-the-badge)

Outriders için hazırlanmış; hikaye, görevler, arayüz, beceriler, yan içerikler ve dünya notları dahil olmak üzere tüm oyunu eksiksiz Türkçeleştiren, çökme riski barındırmayan modern yerelleştirme yamasıdır.

---

## 📥 Hızlı İndir
- **[Outriders_Turkce_Yama_v1.0.0.zip](https://github.com/sqtbey/Outriders-Turkce-Yama/raw/main/Outriders_Turkce_Yama_v1.0.0.zip)** *(1.3 MB - Tek tıkla kuruluma hazır paket)*

---

## 📊 Çeviri İstatistikleri ve Kapsam

| Metrik | Değer | Açıklama |
| :--- | :---: | :--- |
| **Toplam Metin Girdisi** | **38.171** | Oyunun tüm lokalizasyon girdileri |
| **Benzersiz Çeviri Satırı** | **16.862** | Tekilleştirilmiş tüm diyalog ve arayüz dizeleri |
| **İsim Uzayı (Namespace)** | **76** | UI, Subtitles, Quests, Lore, Skills vb. |
| **Çeviri Oranı** | **%100** | Arayüz, altyazılar, menüler ve günlükler |
| **Karakter / Eşya İsimleri** | **Orijinal** | Rehber uyumluluğu için aslına sadık tutuldu |
| **Yazı Tipi Güvenliği** | **ASCII Normalizasyonu** | Kareleşme / kutu hatası sıfır |

---

## 🧠 Teknik Mimari ve Çökme Önleme Çözümü (Tersine Mühendislik)

Outriders, standart Unreal Engine 4 oyunlarından farklı olarak People Can Fly tarafından modifiye edilmiş özel bir paket yükleme motoru kullanır:

```
                            [ OUTRIDERS BAŞLATMA ]
                                      │
                                      ▼
                        Pak Dosyaları Taranıyor
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
   Klasik .pak Dosyaları                       Outriders pakchunk00
 (Repak / UnrealPak ile üretilen)             (Frozen Index Memory Image)
              │                                               │
              ▼                                               ▼
  C++ Bellek Dökümü Değil!                     2-Baytlık Dil Etiketi Değişimi
  Düz Dizin İndeksi Bulundu                   (Localization/Game/en -> xx)
              │                                               │
              ▼                                               ▼
   EXCEPTION_ACCESS_VIOLATION                   Pak İçi İngilizce Dosya Atlanır
  (Adres: 0xffffffff ÇÖKME!)                                  │
                                                              ▼
                                               Diskteki Açık Dosyaya Geçilir
                                            (Madness/Content/Localization/Game/en)
                                                              │
                                                              ▼
                                                   %100 TÜRKÇE VE STABİL
```

### 1. Neden Klasik `~mods/*.pak` Dosyaları Çöküyordu?
Unreal Engine topluluğunda standart olarak kullanılan `UnrealPak` veya `repak` araçları, paket içine düz dizin tabloları (flat string table) yazar. Fakat Outriders UE4.25 derlemesi, başlatma hızını artırmak amacıyla **Frozen Index Memory Image** (`FPakFile_Version_FrozenIndex = 9`) teknolojisini kullanır. 
Oyun motoru başlatılırken dizin tablosunu ayrıştırmaz; doğrudan bellek adreslerine C++ `TArray<FPakEntry>` ve `TMap` yapısı olarak dönüştürür. Düz indeksli bir `.pak` dosyası algılandığında motor bellek sınırını aşarak `0xffffffff` adresini okumaya çalışır ve açılışta `EXCEPTION_ACCESS_VIOLATION` vererek çöker.

### 2. Çözümümüz: 2-Baytlık Güvenli Yönlendirme (Surgical Redirection)
Oyunun donmuş bellek indeksine dokunup bozmak yerine, Unreal Engine'in dosya arama önceliğinden faydalanılmıştır:
1. `pakchunk00_s00-WindowsNoEditor_0_P.pak` içindeki tek bir dizin etiketinde yer alan `Localization/Game/en/` ifadesi `Localization/Game/xx/` olarak değiştirilir (sadece 2 bayt, sıfır offset kayması).
2. Oyun motoru `en` dilini aradığında paket içinde bulamaz ve standart motor mimarisi gereği diskteki açık dosyalara (loose files) başvurur.
3. Motor, diskteki `Madness\Content\Localization\Game\en\Game.locres` dosyamızı doğrudan okur.
4. Böylece paket yapısı bozulmaz, oyun sıfır riskle ve tam performansla Türkçe çalışır.

---

## 🛠️ Kurulum Rehberi

### Yöntem 1: Tek Tıkla Otomatik Kurulum (Önerilen)
1. **[Outriders_Turkce_Yama_v1.0.0.zip](https://github.com/sqtbey/Outriders-Turkce-Yama/raw/main/Outriders_Turkce_Yama_v1.0.0.zip)** dosyasını indirin.
2. Zip içerisindeki tüm dosyaları oyunun ana klasörüne çıkartın:
   *(Örnek Steam Yolu: `C:\Program Files (x86)\Steam\steamapps\common\OUTRIDERS\`)*
3. Oyundan tamamen çıkmış olduğunuzdan emin olun.
4. Oyun klasöründeki **`Install_Yama.bat`** dosyasına çift tıklayın.
5. Ekranda **"TÜRKÇE YAMA BAŞARIYLA KURULDU VE AKTİF EDİLDİ!"** yazısını görünce oyunu Steam üzerinden başlatın.

### Yöntem 2: Manuel Kurulum (İleri Düzey Kullanıcılar)
1. `patch_files\Game.locres` dosyasını `Madness\Content\Localization\Game\en\Game.locres` konumuna kopyalayın.
2. PowerShell'i açıp oyun ana dizininde şu komutu çalıştırarak pak yönlendirmesini aktif edin:
   ```powershell
   $path = 'Madness\Content\Paks\pakchunk00_s00-WindowsNoEditor_0_P.pak'
   $fs = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite)
   $fs.Seek(2626660779, [System.IO.SeekOrigin]::Begin)
   $fs.Write([byte[]]@(0x78, 0x78), 0, 2)
   $fs.Close()
   ```

---

## 🔄 Kaldırma Rehberi (Orijinale Dönüş)

Yamayı dilediğiniz an tek hamlede kaldırabilirsiniz:
- Oyun ana klasöründeki **`Uninstall_Yama.bat`** dosyasını çalıştırın.
- Bu işlem pak dosyasındaki 2 baytlık yönlendirmeyi tekrar `en` (orijinal) haline getirir ve diskteki ek Türkçe dosyayı temizler. Oyununuz saniyeler içinde fabrika ayarlarına döner.

---

## ❓ Sıkça Sorulan Sorular (SSS)

**S: Bu yama ban riski taşır mı?**  
*C: Hayır.* Yama yalnızca yerelleştirme metin kaynağını (`Game.locres`) günceller. Oyun mekaniklerine, EXE kodlarına, belleğe veya hile koruma mekanizmalarına kesinlikle müdahale etmez.

**S: Karakter ve silah/ekipman isimleri neden İngilizce bırakıldı?**  
*C:* Outriders zengin bir build, looter-shooter ve modifikasyon ekosistemine sahiptir. Silah isimleri (*Absolute Zero*, *Deathshield* vb.), modlar ve Enoch evreni terimleri (*Altered*, *ECA*, *Anomaly*) uluslararası topluluk rehberleri ve wiki kaynaklarıyla tam uyumlu kalması için bilinçli olarak orijinal hallerinde tutulmuştur.

**S: Türkçe karakterlerde (ç, ğ, ı, ö, ş, ü) font bozulması var mı?**  
*C:* Oyun motorunun orijinal yazı tipi glif sınırları nedeniyle oyunda kutucuk `[?]` hataları oluşmaması için diyakritik işaretler metin bütünlüğünü ve akıcılığını bozmayacak şekilde ASCII standartlarına uyarlanmıştır.

**S: Oyun güncellenirse ne olur?**  
*C:* Steam üzerinden oyun dosyaları güncellenirse `pakchunk00` orijinal haline dönecektir. Tekrar `Install_Yama.bat` dosyasını çalıştırmanız yamayı yeniden aktif etmek için yeterlidir.

---

## 📐 Proje Mimarisi ve Geliştirici Araçları

Projenin tam mühendislik döngüsü ve veri akışı:

- **`tools/extract_locres.py`**: Orijinal AES-256 şifreli bloklardan ham LocRes çıkarma aracı.
- **`tools/finish_translation.py`**: Biçimlendirme etiketlerini (`{0}`, `<p>`, `[Key]`) koruyan akıllı çeviri boru hattı.
- **`tools/build_turkish_locres.py`**: Unreal Engine `ELocResVersion.Optimized_CRC32` uyumlu bit-exact ikili serileştirici.
- **İnteraktif Mimari Görselleştirme**: `docs/architecture/outriders_localization_pipeline.html` dosyasını tarayıcınızda açarak Archify ile üretilmiş showcase mimari şemasını detaylı olarak inceleyebilirsiniz.

---

## 📄 Lisans ve Katkı
Bu yama topluluk kullanımı için ücretsiz olarak paylaşılmıştır. Çeviriyi geliştirmek veya katkıda bulunmak için Pull Request gönderebilirsiniz.
