"""Land aus Adresse oder Telefonvorwahl ableiten.

Gemeinsam genutzt von `pipedrive_kontakte.py` (Aufbereitung eines Exports) und
`kontakte_umbau.py` (Umbau der Lasche). Lag urspruenglich nur im ersten Skript;
beim Umbau am 14.09.2026 herausgezogen, damit beide dieselbe Ableitung benutzen
und eine Ergaenzung der Laenderliste nicht an einer Stelle haengenbleibt.

Die Ableitung ist bewusst vorsichtig: Sie nimmt den ausgeschriebenen Landesnamen
aus der Adresse, sonst die internationale Vorwahl, sonst nichts. Ein leeres Feld
heisst "aus den Daten nicht sicher bestimmbar" — nicht "kein Land".
"""

import re

LAENDER = {
    'deutschland': 'Deutschland', 'germany': 'Deutschland',
    'österreich': 'Österreich', 'austria': 'Österreich',
    'schweiz': 'Schweiz', 'switzerland': 'Schweiz',
    'vereinigtes königreich': 'Vereinigtes Königreich', 'united kingdom': 'Vereinigtes Königreich',
    'uk': 'Vereinigtes Königreich', 'england': 'Vereinigtes Königreich', 'scotland': 'Vereinigtes Königreich',
    'usa': 'USA', 'us': 'USA', 'united states': 'USA', 'vereinigte staaten': 'USA',
    'kanada': 'Kanada', 'canada': 'Kanada',
    'niederlande': 'Niederlande', 'netherlands': 'Niederlande', 'nederland': 'Niederlande',
    'belgien': 'Belgien', 'belgium': 'Belgien', 'frankreich': 'Frankreich', 'france': 'Frankreich',
    'italien': 'Italien', 'italy': 'Italien', 'italia': 'Italien',
    'spanien': 'Spanien', 'spain': 'Spanien', 'españa': 'Spanien',
    'portugal': 'Portugal', 'polen': 'Polen', 'poland': 'Polen', 'polska': 'Polen',
    'türkei': 'Türkei', 'turkey': 'Türkei', 'türkiye': 'Türkei',
    'griechenland': 'Griechenland', 'greece': 'Griechenland', 'ελλάδα': 'Griechenland',
    'israel': 'Israel', 'china': 'China', 'hongkong': 'Hongkong', 'hong kong': 'Hongkong',
    'indien': 'Indien', 'india': 'Indien', 'dänemark': 'Dänemark', 'denmark': 'Dänemark',
    'schweden': 'Schweden', 'sweden': 'Schweden', 'norwegen': 'Norwegen', 'norway': 'Norwegen',
    'finnland': 'Finnland', 'tschechien': 'Tschechien', 'czechia': 'Tschechien',
    'ungarn': 'Ungarn', 'hungary': 'Ungarn', 'rumänien': 'Rumänien', 'romania': 'Rumänien',
    'bulgarien': 'Bulgarien', 'bulgaria': 'Bulgarien', 'irland': 'Irland', 'ireland': 'Irland',
    'luxemburg': 'Luxemburg', 'slowakei': 'Slowakei', 'slowenien': 'Slowenien',
    'kroatien': 'Kroatien', 'serbien': 'Serbien', 'ukraine': 'Ukraine',
    'vae': 'VAE', 'vereinigte arabische emirate': 'VAE', 'japan': 'Japan',
    'südkorea': 'Südkorea', 'australien': 'Australien', 'brasilien': 'Brasilien',
    'mexiko': 'Mexiko', 'bangladesch': 'Bangladesch', 'bangladesh': 'Bangladesch',
    'pakistan': 'Pakistan', 'vietnam': 'Vietnam', 'taiwan': 'Taiwan', 'zypern': 'Zypern',
}

VORWAHLEN = [
    ('+49', 'Deutschland'), ('0049', 'Deutschland'),
    ('+43', 'Österreich'), ('+41', 'Schweiz'), ('+44', 'Vereinigtes Königreich'),
    ('+31', 'Niederlande'), ('+32', 'Belgien'), ('+33', 'Frankreich'), ('+34', 'Spanien'),
    ('+39', 'Italien'), ('+30', 'Griechenland'), ('+351', 'Portugal'), ('+48', 'Polen'),
    ('+90', 'Türkei'), ('+972', 'Israel'), ('+86', 'China'), ('+852', 'Hongkong'),
    ('+91', 'Indien'), ('+45', 'Dänemark'), ('+46', 'Schweden'), ('+47', 'Norwegen'),
    ('+358', 'Finnland'), ('+420', 'Tschechien'), ('+36', 'Ungarn'), ('+40', 'Rumänien'),
    ('+359', 'Bulgarien'), ('+353', 'Irland'), ('+352', 'Luxemburg'), ('+380', 'Ukraine'),
    ('+971', 'VAE'), ('+81', 'Japan'), ('+82', 'Südkorea'), ('+61', 'Australien'),
    ('+55', 'Brasilien'), ('+52', 'Mexiko'), ('+880', 'Bangladesch'), ('+92', 'Pakistan'),
    ('+84', 'Vietnam'), ('+886', 'Taiwan'), ('+357', 'Zypern'),
]

def clean(v):
    if v is None:
        return ''
    return re.sub(r'\s+', ' ', str(v).replace('\n', ' ').replace('\r', ' ')).strip()

def land_aus_adresse(adresse):
    """Land nur, wenn es in der Adresse ausgeschrieben steht."""
    if not adresse:
        return ''
    rest = adresse.lower().strip().rstrip('.')
    for segment in reversed(re.split(r'[,\n]', rest)):
        segment = segment.strip()
        if segment in LAENDER:
            return LAENDER[segment]
    for name, land in sorted(LAENDER.items(), key=lambda x: -len(x[0])):
        if rest.endswith(' ' + name) or rest == name:
            return land
    return ''

def land_aus_telefon(*nummern):
    """Ersatzsignal: internationale Vorwahl."""
    for nr in nummern:
        kompakt = re.sub(r'[\s\-()/.]', '', nr or '')
        for prefix, land in sorted(VORWAHLEN, key=lambda x: -len(x[0])):
            if kompakt.startswith(prefix):
                return land
    return ''
