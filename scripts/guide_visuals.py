"""Shared generated artwork. Real product/capture assets stay separate."""
ART = '/img/guide-art/guide-%s-blue.webp'
CATEGORY_ART = {'all':'checklist','check':'checklist','sim':'sim-cards',
                'self':'self-activation','esim':'esim','move':'number-transfer',
                'plan':'recharge','fix':'identity'}
GUIDE_ART = {'/선불폰-개통/':'preparation','/선불폰-개통방법/':'preparation',
             '/편의점-선불유심/':'sim-cards',
             '/앤텔레콤-웹개통/':'clock','/v4-1/topic/weekend-activation/':'clock',
             '/v4-1/topic/network-activation/':'preparation',
             '/알뜰폰-셀프개통-안됨/':'identity','/선불폰-셀프개통/':'identity'}
FILTERS = {'check':[('신청 조건','신청조건'),('개통 시간','개통시간'),('통신망','K망')],
           'sim':[('KT 바로유심','KT'),('LG 원칩','LG'),('다이소','다이소')],
           'self':[('KT 개통','KT'),('본인인증','본인인증'),('회원번호','회원번호')],
           'esim':[('지원 기종','아이폰'),('신청 방법','신규가입')],
           'move':[('번호이동','번호이동'),('미납·정지','미납')],
           'plan':[('요금제','요금제'),('요금 충전','충전')],
           'fix':[('본인인증','본인인증'),('유심 오류','유심')]}


def illustration(key):
    return ART % CATEGORY_ART[key]


def guide_illustration(guide):
    return ART % GUIDE_ART.get(guide['href'], CATEGORY_ART[guide['cat']])


def art_img(src, size=512, cls='', eager=False):
    return '<img%s src="%s" width="%d" height="%d" alt="" loading="%s" decoding="async">' % (
        ' class="%s"' % cls if cls else '', src, size, size, 'eager' if eager else 'lazy')
