"""가이드 일러스트(64x64, 브랜드 블루 2톤). build_guide.py / build_pages.py 공용."""
# ---------- 일러스트(64x64, 브랜드 블루 2톤) ----------
B, S, L, W, D = '#1959d8', '#5aa0ff', '#cfe0fb', '#ffffff', '#13306e'
ILL = {
    'clipboard': '<rect x="15" y="11" width="34" height="44" rx="7" fill="%s"/><rect x="19" y="16" width="26" height="35" rx="4" fill="%s"/><rect x="24" y="7" width="16" height="9" rx="3" fill="%s"/><path d="M24 27l3 3 6-6M24 40l3 3 6-6" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M37 28h5M37 41h5" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (L, W, B, B, S),
    'clock': '<circle cx="32" cy="32" r="22" fill="%s"/><circle cx="32" cy="32" r="16" fill="%s"/><path d="M32 22v11l7 4" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>' % (B, W, B),
    'calendar': '<rect x="12" y="15" width="40" height="38" rx="7" fill="%s"/><path d="M12 25h40" stroke="%s" stroke-width="10"/><rect x="12" y="15" width="40" height="38" rx="7" fill="none" stroke="%s" stroke-width="3"/><path d="M22 10v10M42 10v10" stroke="%s" stroke-width="4" stroke-linecap="round"/><g fill="%s"><circle cx="23" cy="35" r="2.6"/><circle cx="32" cy="35" r="2.6"/><circle cx="41" cy="35" r="2.6"/><circle cx="23" cy="44" r="2.6"/><circle cx="32" cy="44" r="2.6"/></g>' % (W, B, B, D, S),
    'signal': '<rect x="12" y="38" width="9" height="14" rx="3" fill="%s"/><rect x="25" y="28" width="9" height="24" rx="3" fill="%s"/><rect x="38" y="16" width="9" height="36" rx="3" fill="%s"/><path d="M52 20a14 14 0 0 1 0 14" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (L, S, B, S),
    'sim': '<path d="M20 9h18l10 10v34a4 4 0 0 1-4 4H20a4 4 0 0 1-4-4V13a4 4 0 0 1 4-4z" fill="%s"/><rect x="23" y="28" width="18" height="18" rx="4" fill="%s"/><path d="M23 37h18M32 28v18" stroke="%s" stroke-width="2.4"/>' % (B, L, B),
    'phone': '<rect x="19" y="7" width="26" height="50" rx="7" fill="%s"/><rect x="23" y="13" width="18" height="36" rx="3" fill="%s"/><circle cx="32" cy="31" r="8" fill="%s"/><path d="M28 31l3 3 5-6" fill="none" stroke="%s" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>' % (B, W, S, W),
    'esim': '<rect x="11" y="17" width="42" height="30" rx="7" fill="%s"/><text x="32" y="37" text-anchor="middle" font-size="14" font-weight="800" fill="%s" font-family="sans-serif">eSIM</text><path d="M45 12a9 9 0 0 1 9 9M45 7a14 14 0 0 1 14 14" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (B, W, S),
    'swap': '<circle cx="32" cy="32" r="23" fill="%s"/><path d="M17 26h28l-7-7M47 38H19l7 7" fill="none" stroke="%s" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>' % (L, B),
    'coins': '<ellipse cx="32" cy="46" rx="18" ry="7" fill="%s"/><path d="M14 38v8c0 4 8 7 18 7s18-3 18-7v-8" fill="%s"/><ellipse cx="32" cy="38" rx="18" ry="7" fill="%s"/><ellipse cx="32" cy="26" rx="18" ry="7" fill="%s"/><path d="M14 26v12c0 4 8 7 18 7s18-3 18-7V26" fill="%s" opacity=".0"/><text x="32" y="30" text-anchor="middle" font-size="11" font-weight="800" fill="%s" font-family="sans-serif">₩</text>' % (S, B, L, W, B, B),
    'shield': '<path d="M32 7l18 6v15c0 13-8 21-18 25C22 49 14 41 14 28V13z" fill="%s"/><path d="M24 31l6 6 11-12" fill="none" stroke="%s" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>' % (B, W),
    'bolt': '<circle cx="32" cy="32" r="23" fill="%s"/><path d="M36 10L19 35h12l-3 19 17-26H33z" fill="%s"/>' % (L, B),
    'bars': '<rect x="11" y="34" width="9" height="18" rx="3" fill="%s"/><rect x="24" y="24" width="9" height="28" rx="3" fill="%s"/><rect x="37" y="14" width="9" height="38" rx="3" fill="%s"/><rect x="50" y="28" width="5" height="24" rx="2.5" fill="%s"/>' % (L, S, B, S),
    'wrench': '<g transform="rotate(45 32 32)"><rect x="28" y="22" width="8" height="34" rx="4" fill="%s"/><path d="M22 8h6v10a4 4 0 0 0 8 0V8h6v12a10 10 0 0 1-20 0z" fill="%s"/></g>' % (S, B),
    'alert': '<path d="M32 9l24 42H8z" fill="%s" stroke="%s" stroke-width="4" stroke-linejoin="round"/><path d="M32 24v12" stroke="%s" stroke-width="4.4" stroke-linecap="round"/><circle cx="32" cy="43" r="2.8" fill="%s"/>' % (S, S, W, W),
    'nfc': '<rect x="10" y="20" width="34" height="24" rx="6" fill="%s"/><rect x="15" y="26" width="10" height="8" rx="2" fill="%s"/><path d="M46 22a14 14 0 0 1 0 20M52 17a22 22 0 0 1 0 30" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % (B, L, S),
    'id': '<rect x="9" y="16" width="46" height="32" rx="6" fill="%s"/><circle cx="23" cy="30" r="6" fill="%s"/><path d="M14 42c1-6 17-6 18 0" fill="%s"/><path d="M37 27h13M37 34h9" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (B, L, L, L),
}


CAT_ILL = {'check': 'clipboard', 'sim': 'sim', 'self': 'phone', 'esim': 'esim', 'move': 'swap', 'plan': 'coins', 'fix': 'wrench', 'all': 'clipboard'}


def ill_svg(name, size=64):
    return ('<svg viewBox="0 0 64 64" width="%d" height="%d" role="img" aria-hidden="true">%s</svg>' % (size, size, ILL[name]))
