"""가이드 일러스트(64x64). build_guide.py / build_pages.py 공용.

브랜드 블루 그라디언트 + 하이라이트 + 바닥 그림자로 입체감을 낸 자체 제작 SVG.
실제 서비스 로고나 실제 신분증 디자인은 흉내 내지 않는다(신분증은 개인정보·문구가 없는 추상 일러스트).
같은 id의 그라디언트 정의는 모든 SVG에서 동일하므로 한 페이지에 여러 번 들어가도 안전하다.
"""
B1, B2, B3, L1, L2, W, D = '#1959d8', '#3d82f5', '#7db4ff', '#cfe0fb', '#eaf2ff', '#ffffff', '#13306e'
GOLD1, GOLD2 = '#ffd978', '#f2a900'


def _g(i, c1, c2, vertical=False):
    x2, y2 = ('0', '1') if vertical else ('1', '1')
    return ('<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="%s"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
            % (i, x2, y2, c1, c2))


DEFS = {
    'gb': _g('gb', B3, B1),            # 파랑 면
    'gbd': _g('gbd', B2, D),           # 진한 파랑
    'gl': _g('gl', W, L1, True),       # 밝은 면
    'gg': _g('gg', GOLD1, GOLD2),      # 금색(동전·칩)
}


def _svg(body, uses):
    defs = ''.join(DEFS[u] for u in uses)
    return '<defs>%s</defs>' % defs + body


SH = '<ellipse cx="32" cy="58" rx="17" ry="3.2" fill="#13306e" opacity=".13"/>'

ILL = {
    'clipboard': _svg(SH +
        '<rect x="14" y="9" width="36" height="47" rx="8" fill="url(#gb)"/>'
        '<rect x="19" y="15" width="26" height="36" rx="4.5" fill="url(#gl)"/>'
        '<rect x="24" y="5" width="16" height="11" rx="4" fill="url(#gbd)"/>'
        '<circle cx="25" cy="26" r="3.6" fill="url(#gb)"/><path d="M23.4 26l1.3 1.4 2.4-2.8" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="25" cy="38" r="3.6" fill="url(#gb)"/><path d="M23.4 38l1.3 1.4 2.4-2.8" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M32 26h9M32 38h9M32 44h6" stroke="#9db8e8" stroke-width="2.6" stroke-linecap="round"/>', ['gb', 'gl', 'gbd']),
    'clock': _svg(SH +
        '<circle cx="32" cy="31" r="23" fill="url(#gb)"/><circle cx="32" cy="31" r="17" fill="url(#gl)"/>'
        '<path d="M32 17v3M32 42v3M18 31h3M43 31h3" stroke="#9db8e8" stroke-width="2.4" stroke-linecap="round"/>'
        '<path d="M32 21v11l7 4" fill="none" stroke="#1959d8" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="32" cy="31" r="2.4" fill="#13306e"/>', ['gb', 'gl']),
    'calendar': _svg(SH +
        '<rect x="10" y="13" width="44" height="42" rx="9" fill="url(#gl)" stroke="#cfe0fb" stroke-width="1.5"/>'
        '<path d="M10 22a9 9 0 0 1 9-9h26a9 9 0 0 1 9 9v5H10z" fill="url(#gb)"/>'
        '<path d="M21 8v10M43 8v10" stroke="#13306e" stroke-width="4" stroke-linecap="round"/>'
        '<g fill="#9db8e8"><circle cx="21" cy="37" r="2.6"/><circle cx="32" cy="37" r="2.6"/><circle cx="43" cy="37" r="2.6"/><circle cx="21" cy="47" r="2.6"/><circle cx="43" cy="47" r="2.6"/></g>'
        '<circle cx="32" cy="47" r="5" fill="url(#gb)"/><path d="M29.6 47l1.8 1.9 3.2-3.6" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>', ['gb', 'gl']),
    'signal': _svg(SH +
        '<rect x="9" y="38" width="11" height="17" rx="4" fill="url(#gl)" stroke="#cfe0fb" stroke-width="1.4"/>'
        '<rect x="24" y="27" width="11" height="28" rx="4" fill="url(#gb)" opacity=".85"/>'
        '<rect x="39" y="14" width="11" height="41" rx="4" fill="url(#gbd)"/>'
        '<path d="M54 18a13 13 0 0 1 0 14M58 13a20 20 0 0 1 0 24" fill="none" stroke="#7db4ff" stroke-width="3" stroke-linecap="round"/>', ['gb', 'gl', 'gbd']),
    'sim': _svg(SH +
        '<path d="M19 6h20l11 11v37a5 5 0 0 1-5 5H19a5 5 0 0 1-5-5V11a5 5 0 0 1 5-5z" fill="url(#gb)"/>'
        '<path d="M19 6h20l11 11H19z" fill="#fff" opacity=".18"/>'
        '<rect x="22" y="27" width="22" height="20" rx="4.5" fill="url(#gg)"/>'
        '<path d="M22 37h22M33 27v20M27.5 27v6.5h-5.5M38.5 27v6.5H44M27.5 47v-6.5h-5.5M38.5 47v-6.5H44" fill="none" stroke="#c98a00" stroke-width="1.4" stroke-linecap="round" opacity=".7"/>', ['gb', 'gg']),
    'phone': _svg(SH +
        '<rect x="17" y="5" width="30" height="53" rx="8" fill="url(#gbd)"/>'
        '<rect x="20.5" y="11" width="23" height="41" rx="4" fill="url(#gl)"/>'
        '<rect x="27" y="7.5" width="10" height="2.4" rx="1.2" fill="#7db4ff"/>'
        '<circle cx="32" cy="29" r="10" fill="url(#gb)"/><path d="M27 29.5l3.7 3.8 6.6-7.6" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M25 44h14" stroke="#9db8e8" stroke-width="2.6" stroke-linecap="round"/>', ['gbd', 'gl', 'gb']),
    'esim': _svg(SH +
        '<rect x="9" y="17" width="44" height="32" rx="9" fill="url(#gb)"/>'
        '<rect x="9" y="17" width="44" height="12" rx="9" fill="#fff" opacity=".16"/>'
        '<text x="31" y="38.5" text-anchor="middle" font-size="14.5" font-weight="900" fill="#ffffff" font-family="sans-serif">eSIM</text>'
        '<path d="M47 11a10 10 0 0 1 10 10M47 5.5a15.5 15.5 0 0 1 15.5 15.5" fill="none" stroke="#7db4ff" stroke-width="3.2" stroke-linecap="round"/>', ['gb']),
    'swap': _svg(SH +
        '<circle cx="32" cy="30" r="24" fill="url(#gl)" stroke="#cfe0fb" stroke-width="1.5"/>'
        '<path d="M15 24h28l-7-7" fill="none" stroke="#3d82f5" stroke-width="4.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M49 37H21l7 7" fill="none" stroke="#1959d8" stroke-width="4.8" stroke-linecap="round" stroke-linejoin="round"/>', ['gl']),
    'coins': _svg(SH +
        '<ellipse cx="32" cy="46" rx="19" ry="7.5" fill="#d98e00"/><ellipse cx="32" cy="43" rx="19" ry="7.5" fill="url(#gg)"/>'
        '<ellipse cx="32" cy="34" rx="19" ry="7.5" fill="#d98e00"/><ellipse cx="32" cy="31" rx="19" ry="7.5" fill="url(#gg)"/>'
        '<ellipse cx="32" cy="22" rx="19" ry="7.5" fill="#d98e00"/><ellipse cx="32" cy="19" rx="19" ry="7.5" fill="url(#gg)"/>'
        '<ellipse cx="32" cy="19" rx="12" ry="4.4" fill="none" stroke="#c98a00" stroke-width="1.6" opacity=".7"/>'
        '<text x="32" y="22" text-anchor="middle" font-size="9" font-weight="900" fill="#b97a00" font-family="sans-serif">₩</text>', ['gg']),
    'shield': _svg(SH +
        '<path d="M32 5l20 7v16c0 14-8.5 22.5-20 27C20.500 50.500 12 42 12 28V12z" fill="url(#gb)"/>'
        '<path d="M32 5l20 7v6H12v-6z" fill="#fff" opacity=".16"/>'
        '<path d="M22.500 29l7 7 12-13.500" fill="none" stroke="#fff" stroke-width="4.8" stroke-linecap="round" stroke-linejoin="round"/>', ['gb']),
    'bolt': _svg(SH +
        '<circle cx="32" cy="30" r="24" fill="url(#gb)"/><circle cx="32" cy="30" r="24" fill="none" stroke="#fff" stroke-width="2" opacity=".25"/>'
        '<path d="M36.500 9L19 34h12.500l-4 19L46 26H33.500z" fill="url(#gg)" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/>', ['gb', 'gg']),
    'bars': _svg(SH +
        '<rect x="8" y="34" width="11" height="21" rx="4" fill="url(#gl)" stroke="#cfe0fb" stroke-width="1.4"/>'
        '<rect x="22" y="24" width="11" height="31" rx="4" fill="url(#gb)" opacity=".85"/>'
        '<rect x="36" y="14" width="11" height="41" rx="4" fill="url(#gbd)"/>'
        '<path d="M10 20l13-9 10 6 20-12" fill="none" stroke="#f2a900" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M46 5h7v7" fill="none" stroke="#f2a900" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>', ['gb', 'gl', 'gbd']),
    'wrench': _svg(SH +
        '<g transform="rotate(45 32 31)"><rect x="27.500" y="22" width="9" height="36" rx="4.500" fill="url(#gb)"/>'
        '<path d="M20 4h7v11a5 5 0 0 0 10 0V4h7v13a12 12 0 0 1-24 0z" fill="url(#gbd)"/></g>'
        '<circle cx="14" cy="14" r="3" fill="#7db4ff"/><circle cx="52" cy="48" r="2.4" fill="#cfe0fb"/>', ['gb', 'gbd']),
    'alert': _svg(SH +
        '<path d="M32 6c1.800 0 3.200.9 4.100 2.500l19 33c1.800 3.100-.5 7-4.100 7H13c-3.600 0-5.900-3.900-4.100-7l19-33C28.800 6.900 30.200 6 32 6z" fill="url(#gb)"/>'
        '<path d="M32 21v13" stroke="#fff" stroke-width="4.800" stroke-linecap="round"/><circle cx="32" cy="42.500" r="3" fill="#fff"/>', ['gb']),
    'id': _svg(SH +
        '<rect x="7" y="14" width="50" height="35" rx="7" fill="url(#gb)"/>'
        '<rect x="7" y="14" width="50" height="11" rx="7" fill="#fff" opacity=".15"/>'
        '<circle cx="22" cy="31" r="6" fill="#eaf2ff"/><path d="M12 45c1.500-8 18.500-8 20 0z" fill="#eaf2ff"/>'
        '<path d="M38 29h14M38 36h10M38 43h6" stroke="#eaf2ff" stroke-width="3" stroke-linecap="round"/>', ['gb']),
    'idcard': _svg(SH +
        '<rect x="6" y="13" width="52" height="37" rx="6.500" fill="url(#gl)" stroke="#bcd3fb" stroke-width="1.6"/>'
        '<rect x="6" y="13" width="52" height="9" rx="6.500" fill="url(#gb)"/>'
        '<circle cx="21" cy="33" r="5.500" fill="#9db8e8"/><path d="M11.500 46c1.500-7.500 18-7.500 19 0z" fill="#9db8e8"/>'
        '<path d="M37 31h15M37 37h11M37 43h7" stroke="#9db8e8" stroke-width="3" stroke-linecap="round"/>', ['gl', 'gb']),
    'license': _svg(SH +
        '<rect x="6" y="13" width="52" height="37" rx="6.500" fill="url(#gl)" stroke="#bcd3fb" stroke-width="1.6"/>'
        '<rect x="6" y="40" width="52" height="10" rx="6.500" fill="url(#gbd)"/>'
        '<rect x="12" y="19" width="16" height="17" rx="3.500" fill="#9db8e8"/><circle cx="20" cy="25" r="3.200" fill="#eaf2ff"/><path d="M14.500 35c1-5 10-5 11 0z" fill="#eaf2ff"/>'
        '<path d="M34 22h18M34 29h14M34 35h9" stroke="#9db8e8" stroke-width="3" stroke-linecap="round"/><rect x="46" y="42.500" width="7" height="5" rx="1.500" fill="url(#gg)"/>', ['gl', 'gbd', 'gg']),
    'mobileid': _svg(SH +
        '<rect x="15" y="4" width="34" height="55" rx="8.500" fill="url(#gbd)"/>'
        '<rect x="19" y="10" width="26" height="43" rx="4" fill="url(#gl)"/>'
        '<rect x="22" y="17" width="20" height="14" rx="3" fill="url(#gb)"/><circle cx="28" cy="22.500" r="2.200" fill="#eaf2ff"/><path d="M24.500 29c.8-4 6.500-4 7.300 0z" fill="#eaf2ff"/><path d="M34 21.500h6M34 25.500h4" stroke="#eaf2ff" stroke-width="1.800" stroke-linecap="round"/>'
        '<rect x="22" y="36" width="20" height="3.600" rx="1.800" fill="#9db8e8"/><rect x="22" y="43" width="13" height="3.600" rx="1.800" fill="#cfe0fb"/>', ['gbd', 'gl', 'gb']),
    'nfc': _svg(SH +
        '<rect x="7" y="19" width="36" height="26" rx="7" fill="url(#gb)"/>'
        '<rect x="12" y="25" width="11" height="9" rx="2.200" fill="url(#gg)"/>'
        '<path d="M47 22a14 14 0 0 1 0 20M53 16a22 22 0 0 1 0 32" fill="none" stroke="#7db4ff" stroke-width="3.400" stroke-linecap="round"/>', ['gb', 'gg']),
    'grid': _svg(SH +
        '<rect x="9" y="8" width="21" height="21" rx="6" fill="url(#gb)"/><rect x="34" y="8" width="21" height="21" rx="6" fill="url(#gbd)"/>'
        '<rect x="9" y="33" width="21" height="21" rx="6" fill="url(#gbd)"/><rect x="34" y="33" width="21" height="21" rx="6" fill="url(#gb)"/>', ['gb', 'gbd']),
    'face': _svg(SH +
        '<path d="M10 22v-7a5 5 0 0 1 5-5h7M42 10h7a5 5 0 0 1 5 5v7M54 42v7a5 5 0 0 1-5 5h-7M22 54h-7a5 5 0 0 1-5-5v-7" fill="none" stroke="url(#gb)" stroke-width="4.200" stroke-linecap="round"/>'
        '<circle cx="32" cy="32" r="14" fill="url(#gl)" stroke="#cfe0fb" stroke-width="1.500"/><circle cx="27" cy="30" r="2" fill="#13306e"/><circle cx="37" cy="30" r="2" fill="#13306e"/><path d="M27 37c3 3 7 3 10 0" fill="none" stroke="#13306e" stroke-width="2.200" stroke-linecap="round"/>', ['gb', 'gl']),
}

CAT_ILL = {'check': 'clipboard', 'sim': 'sim', 'self': 'phone', 'esim': 'esim', 'move': 'swap', 'plan': 'coins', 'fix': 'wrench', 'all': 'grid'}


def ill_svg(name, size=64):
    return ('<svg viewBox="0 0 64 64" width="%d" height="%d" role="img" aria-hidden="true">%s</svg>' % (size, size, ILL[name]))
