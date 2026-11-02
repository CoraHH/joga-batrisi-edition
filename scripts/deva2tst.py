# deva2tst.py  –  Devanāgarī → IAST nach TST-Konvention
# Corinna May Lhoir mit Claude, 28.10.2026
#
# Zweck: Die eigene Devanāgarī-Transkription (z. B. A_AKGM145480_deva.txt)
# einmalig in die Umschrift zu bringen, die der TST-Editor erwartet.
# Das Skript ist ein Hilfswerkzeug und gehört NICHT in die XML-Datei;
# in die XML-Datei kommt nur sein Ergebnis (der IAST-Text).
#
# Aufruf (im Terminal, im Ordner Transkriptionen):
#     python deva2tst.py EINGABE.txt AUSGABE.txt
#   z. B.
#     python deva2tst.py "..\Korpora\Joga Batrisi\N_NaniKhakhar_deva.txt" N_NaniKhakhar_tst-iast.txt
# Die Eingabedatei bleibt unverändert; die Ausgabedatei wird neu geschrieben (UTF-8).
#
# Regeln:
#   1. Konsonant + Vokalzeichen  → Konsonant + Vokal        (कि → ki)
#   2. Konsonant ohne Vokalzeichen → Konsonant + a           (क → ka)
#   3. Konsonant + Virāma (्)    → Konsonant allein         (क् → k)
#   4. Vollform-Vokal (अ आ इ …)  → Vokal                    (इ → i)
#      AUSNAHME (TST-Konvention): steht die Vollform इ oder उ
#      direkt nach einem Vokal (Vokalhiat), wird ï bzw. ü geschrieben,
#      damit der Editor beim Rückweg wieder ein selbständiges इ/उ
#      erzeugt und nicht den Diphthong ै/ौ:
#          लाभइ → lābhaï   (aber: लाभै → lābhai)
#          कह्यउ → kahyaü  (aber: कह्यौ → kahyau)
#   5. ं → ṃ, ँ → m̐, ः → ḥ, ऽ → ' , । → | , ॥ → || , Ziffern → 0–9
#
# Bekannte Grenzen:
#   – Für selbständiges ई/ऊ nach Vokal gibt es in TST kein Zeichen.
#   – Der TST-Editor setzt nach ï/ü + Anusvāra fälschlich ein Avagraha
#     (harakhiïṃ → हरखिइऽं). Das ist ein Fehler in der Editor-Bibliothek,
#     nicht in dieser Umschrift (Stand 28.10.2026, Charles gemeldet?).

import sys

# Tabellen: Devanāgarī-Zeichen → Umschrift
VOLLVOKALE = {'अ':'a','आ':'ā','इ':'i','ई':'ī','उ':'u','ऊ':'ū','ऋ':'ṛ',
              'ए':'e','ऐ':'ai','ओ':'o','औ':'au'}
VOKALZEICHEN = {'ा':'ā','ि':'i','ी':'ī','ु':'u','ू':'ū','ृ':'ṛ',
                'े':'e','ै':'ai','ो':'o','ौ':'au'}
KONSONANTEN = {'क':'k','ख':'kh','ग':'g','घ':'gh','ङ':'ṅ',
               'च':'c','छ':'ch','ज':'j','झ':'jh','ञ':'ñ',
               'ट':'ṭ','ठ':'ṭh','ड':'ḍ','ढ':'ḍh','ण':'ṇ',
               'त':'t','थ':'th','द':'d','ध':'dh','न':'n',
               'प':'p','फ':'ph','ब':'b','भ':'bh','म':'m',
               'य':'y','र':'r','ल':'l','व':'v',
               'श':'ś','ष':'ṣ','स':'s','ह':'h','ळ':'ḷ'}
ZIFFERN = {'०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9'}
HIAT = {'इ':'ï','उ':'ü'}          # Regel 4, Ausnahme
VOKALE_LAT = 'aāiīuūṛeo'          # womit ein Vokal in der Umschrift endet

def konvertiere(text):
    out = []
    i = 0
    while i < len(text):
        z = text[i]
        folge = text[i+1] if i+1 < len(text) else ''
        if z in KONSONANTEN:                       # Regeln 1–3
            out.append(KONSONANTEN[z])
            if folge == '्':
                i += 2; continue                   # Virāma: kein Vokal
            if folge in VOKALZEICHEN:
                out.append(VOKALZEICHEN[folge]); i += 2; continue
            out.append('a'); i += 1; continue      # inhärentes a
        if z in VOLLVOKALE:                        # Regel 4
            vorher = out[-1][-1] if out and out[-1] else ''
            if z in HIAT and vorher in VOKALE_LAT:
                out.append(HIAT[z])                # Vokalhiat → ï / ü
            else:
                out.append(VOLLVOKALE[z])
            i += 1; continue
        # Regel 5 und Rest
        if z == 'ं':   out.append('ṃ')
        elif z == 'ँ': out.append('m̐')
        elif z == 'ः': out.append('ḥ')
        elif z == 'ऽ': out.append("'")
        elif z == '।': out.append('|')
        elif z == '॥': out.append('||')
        elif z in ZIFFERN: out.append(ZIFFERN[z])
        elif z == '्': pass                        # verwaistes Virāma
        elif z in VOKALZEICHEN: out.append(VOKALZEICHEN[z])   # verwaistes Vokalzeichen
        else: out.append(z)                        # Leerzeichen, Latein, Satzzeichen
        i += 1
    return ''.join(out)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Aufruf: python deva2tst.py EINGABE.txt AUSGABE.txt'); sys.exit(1)
    eingabe, ausgabe = sys.argv[1], sys.argv[2]
    with open(eingabe, encoding='utf-8') as ein, open(ausgabe, 'w', encoding='utf-8') as aus:
        for zeile in ein:
            zeile = zeile.rstrip('\n')
            if '\t' in zeile:                      # Format "JB5a<TAB>Text"
                kennung, text = zeile.split('\t', 1)
                aus.write(kennung + '\t' + konvertiere(text) + '\n')
            else:
                aus.write(konvertiere(zeile) + '\n')
    print('fertig:', ausgabe)
