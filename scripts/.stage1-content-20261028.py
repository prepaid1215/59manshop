#!/usr/bin/env python3
from pathlib import Path
import sys, json, re
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from build_hub import context, categories
guides=json.loads((ROOT/'data/guides.json').read_text(encoding='utf-8'))['guides']
paths=sorted({g['href'].split('#')[0] for g in guides})
modified=set()
def save(path,old,new):
    if old!=new:
        (ROOT/path).write_text(new,encoding='utf-8',newline='')
        modified.add(path)
def replace_exact(path,old,new,count=1):
    p=ROOT/path
    s=p.read_text(encoding='utf-8')
    found=s.count(old)
    if found!=count: raise ValueError(f'{path} expected {count} instances, found {found}: {old[:60]}')
    save(path,s,s.replace(old,new))
def after_nav(path,old,new):
    p=ROOT/path;s=p.read_text(encoding='utf-8')
    if old not in s: raise ValueError(f'nav not found {path}')
    save(path,s,s.replace(old,new,1))
for url in paths:
    path=url.lstrip('/')+'index.html'
    p=ROOT/path
    original=p.read_text(encoding='utf-8')
    s,n=re.subn(r'<aside class="guide-context"[\s\S]*?</aside>',lambda m:context(url),original,count=1)
    if n!=1: raise ValueError('context missing '+url)
    s,n=re.subn(r'<nav class="gc-tiles detail-categories"[\s\S]*?</nav>',lambda m:categories(url),s,count=1)
    if n!=1: raise ValueError('categories missing '+url)
    if '26개 가이드' not in s: raise ValueError('guide count '+url)
    save(path,original,s)
# A4: eSIM preparation & device fields
p='v4-1/topic/esim-new/index.html'
replace_exact(p,'단말이 eSIM을 지원하는지, EID를 확인할 수 있는지 먼저 확인하세요.','L망 선불 eSIM은 지원 단말의 신규가입에서 이용합니다. 발급비는 2,750원이며, 신청 전에 모델명·단말기 일련번호·EID·IMEI1·IMEI2를 확인해 두세요. 실제 입력 항목과 단말 지원 여부는 신청 화면이 최종 기준입니다.')
replace_exact(p,'eSIM 지원 여부와 EID는 전화 화면에서 *#06#을 눌러 확인하세요.','전화 화면에서 *#06#을 눌러 EID와 IMEI를 확인하거나 휴대폰 설정의 기기 정보에서 살펴보세요. EID가 보이더라도 가입 지원 여부는 신청 화면에서 확인해야 합니다.')
replace_exact(p,'전화 화면에서 *#06#을 눌러 EID와 단말 정보를 확인하세요.','전화 화면에서 *#06#을 눌러 EID·IMEI1·IMEI2를 확인하세요. 모델명과 일련번호도 휴대폰 설정의 기기 정보에서 확인합니다.')
# A5: platform member number distinction incl FAQ LD data
p='태블릿-소유자-회원번호/index.html'
replace_exact(p,'<td>화면에 칸이 나오면 2893496</td>','<td>입력 불필요(플랫폼에는 회원번호 입력란 없음)</td>')
replace_exact(p,'휴대폰으로 신청해도 이 칸이 나오면 담당 판매점 번호를 넣습니다.','앤텔레콤 멤버십 앱에서 신청할 때만 담당 판매점 번호를 넣습니다. 59만모바일 웹 플랫폼 개통에는 회원번호 입력이 필요하지 않습니다.',count=2)
# A6: titles match comparison intent, keep canonical/URLs
p='v4-1/topic/network-activation/index.html'
replace_exact(p,'앤텔레콤 K망 유심 준비와 개통 순서','앤텔레콤 K망·L망 선택 기준',count=3)
replace_exact(p,'앤텔레콤 K망 개통은 망을 선택한 뒤 호환 유심을 준비해 개통을 신청하는 순서로 진행합니다. K망에서는 KT 바로유심을 사용합니다.','미납정지 단말, eSIM·5G, 투넘버·핫스팟·로밍 조건에 따라 앤텔레콤 K망과 L망을 선택하는 기준을 비교합니다.',count=3)
replace_exact(p,'<h1>앤텔레콤 K망 개통 방법 안내</h1>','<h1>앤텔레콤 K망·L망 선택 기준</h1>')
replace_exact(p,'<p>K망 유심 준비와 개통 신청 순서</p>','<p>내 휴대폰과 이용 목적에 맞는 통신망 고르기</p>')
# A7: skip only if offered by platform
p='알뜰폰-셀프개통-안됨/index.html'
replace_exact(p,'네. 현재 신청 화면에는 <b>안면인증 안정화 기간이라 안면인증에 실패해도 개통이 가능하다</b>고 안내돼 있습니다(2026년 10월 기준).','일부 신청 화면에서는 <b>안면인증 SKIP 대상자</b> 안내가 표시될 때 다음 단계로 진행할 수 있습니다(2026년 10월 기준). 모든 인증 실패에 적용되는 것은 아닙니다.')
replace_exact(p,'안면인증이 계속 실패하면 다음 단계로 넘어가 간편인증으로 본인확인을 마치면 됩니다.','화면에 실제로 건너뛰기 또는 SKIP 대상자 안내가 표시되는 경우에만 다음 단계로 이동하세요. 이런 안내가 없으면 임의로 단계를 생략할 수 없으며, 인증 오류를 확인하거나 상담을 이용해야 합니다.')
# A8: L 464 supplementary call allowance
p='l망-464-요금제/index.html'
replace_exact(p,'<tr><td>기본 데이터</td><td>20GB</td></tr>','<tr><td>기본 데이터</td><td>20GB</td></tr><tr><td>일반 음성·문자</td><td>기본 제공</td></tr><tr><td>영상·부가통화</td><td>50분</td></tr>')
# A3: avoid misrepresenting callback 114 as guaranteed caller ID
p='선불폰-충전-방법/index.html'
replace_exact(p,'<div class="warn-box"><b>해피콜은 꼭 받으세요</b><p>앤텔레콤 본사 확인 전화를 받지 않으면 이용이 정지될 수 있어요. L망은 개통 당일에 유심을 꽂는 것을 권장합니다.</p></div>','<div class="warn-box"><b>해피콜은 꼭 받으세요</b><p>앤텔레콤 본사 확인 전화를 받지 않으면 이용이 정지될 수 있어요. L망은 개통 당일에 유심을 꽂는 것을 권장합니다.</p><p>해피콜 연락은 1899-7700 등 본사 안내 번호를 확인하세요. 직접 고객센터에 문의할 때는 앤텔레콤 회선에서 114(무료), 다른 통신사 전화에서는 1899-7700(유료)을 이용합니다. 수신되는 발신번호와 고객센터에 거는 번호는 구분하세요.</p></div>')
# no accidental changes
assert len(paths)==26,(len(paths),paths)
assert len(modified)==26,(len(modified),sorted(modified))
print(json.dumps({'stage':'1','guidePages':len(paths),'modifiedFiles':len(modified),'files':sorted(modified)},ensure_ascii=False))
