(function generator(){
 const fs=require('node:fs'), path=require('node:path');
 const args=process.argv.slice(2), publish=args.includes('--publish'), check=args.includes('--check');
 const ix=args.indexOf('--out'), out=path.resolve(ix>=0?args[ix+1]:path.join(__dirname,'build-preview'));
 if(ix>=0&&!args[ix+1])throw Error('Missing --out folder');
 if([path.resolve(__dirname),path.resolve(__dirname,'../../../../')].includes(out))throw Error('Unsafe output directory');
 const site='https://www.59man.shop/';
 const s=fs.readFileSync(path.join(__dirname,'manifest.tsv'),'utf8').replace(/\r?\n$/, '').split(/\r?\n/);
 const header=s.shift().split('\t');
 const data=s.map((line,i)=>{const parts=line.split('\t');if(parts.length!==header.length)throw Error('Column mismatch line '+(i+2));return Object.fromEntries(header.map((k,j)=>[k,parts[j]]))});
 if(data.length!==1000)throw Error('Manifest must have 1000 entries');
 const groups=['A','B','C','D'], names=new Set(), regions=[...new Set(data.map(r=>r.province))].sort();
 const esc=x=>String(x).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
 for(const r of data){
  if(!groups.includes(r.cohort)||!/^[가-힣]+$/.test(r.province)||!/^[가-힣]+동$/.test(r.dong))throw Error('Bad place '+r.slug);
  if(r.slug!==['bulk-lab',r.province,r.dong+'-선불폰'].join('/'))throw Error('Invalid slug '+r.slug);
  if(names.has(r.slug))throw Error('Duplicate slug '+r.slug);
  names.add(r.slug);
 }
 for(const g of groups)if(data.filter(r=>r.cohort===g).length!==250)throw Error('Bad group size '+g);
 if(publish){
  const notes=new Set();
  for(const r of data){
   if(r.editorial_status!=='approved'||r.local_note.length<120||!/^https:\/\//.test(r.local_source))throw Error('Unapproved/unsourced article '+r.slug);
   const normalized=r.local_note.replaceAll(r.dong,'{DONG}').replaceAll(r.province,'{PROVINCE}');
   if(notes.has(normalized))throw Error('Repeated article with only place changed '+r.slug);
   notes.add(normalized);
  }
 }
 const cohorts=new Map();
 for(const r of data){const key=r.province+'|'+r.cohort;if(!cohorts.has(key))cohorts.set(key,[]);cohorts.get(key).push(r)}
 const related=r=>{
  const list=cohorts.get(r.province+'|'+r.cohort)||[];
  const i=list.findIndex(q=>q.slug===r.slug);
  return (r.cohort==='C'||r.cohort==='D')?list.filter(q=>q.slug!==r.slug).slice(Math.max(0,i-2),Math.max(0,i-2)+4):[];
 };
 const document=r=>{
  const title=r.province+' '+r.dong+' 선불폰 온라인 개통 준비';
  const canon=site+r.slug+'/',robots=publish?'index,follow':'noindex,follow';
  const hub=(r.cohort==='B'||r.cohort==='D')?'<p><a href="/bulk-lab-hub/'+esc(r.province)+'/">'+esc(r.province)+' 지역 안내</a></p>':'';
  const sibling=related(r).map(x=>'<li><a href="/'+esc(x.slug)+'/">'+esc(x.dong)+' 선불폰</a></li>').join('');
  const note=publish?'<section><h2>검증된 지역별 안내</h2><p>'+esc(r.local_note)+'</p><p>정보 출처: <a rel="nofollow noopener" href="'+esc(r.local_source)+'">지역 자료</a></p></section>':'<section><h2>편집 전 실험용 문서</h2><p>지역별 고유 정보를 검증하기 전에는 검색엔진에 공개하지 않습니다.</p></section>';
  return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+' | 59만선불폰</title><meta name="description" content="'+esc(title)+'에서 유심·인증·요금제·신규번호 신청 조건을 확인하세요."><meta name="robots" content="'+robots+'"><link rel="canonical" href="'+esc(canon)+'"><link rel="stylesheet" href="/assets/v4-1-final.css"></head><body><header><a href="/">59만선불폰</a></header><main><h1>'+esc(title)+'</h1><p>'+esc(r.dong)+' 지역에서 새 번호를 온라인으로 신청할 때 필요한 일반적인 안내입니다. 이 지역에 방문 매장이나 판매 재고가 있다는 뜻은 아닙니다.</p><h2>신규가입과 번호이동</h2><p>미납·정지 번호의 번호이동은 제한될 수 있습니다. 새 번호 신규가입은 별도로 확인할 수 있지만 개통 완료를 보장하지 않습니다.</p><h2>인증과 유심</h2><p>신분증, 안면인증, 지원되는 간편인증과 망에 맞는 유심을 준비합니다. K망 KT 바로유심, L망 모두의 원칩 또는 지원되는 고고비 유심을 확인하세요. 신규가입 신청 가능 시간은 매일 08:00~21:50입니다.</p><h2>요금제</h2><p>K망 396은 월 39,600원·10.3GB 이후 최대 3Mbps, L망 5G 464는 월 46,400원·20GB 이후 최대 3Mbps입니다.</p>'+note+'<nav><a href="/선불폰-개통방법/">개통방법 상세</a> · <a href="/선불폰-셀프개통/">오류 해결</a>'+hub+'<ul>'+sibling+'</ul></nav><p><a href="https://preplan.site/?from='+encodeURIComponent('59man_'+r.province+'_'+r.dong)+'">59만모바일 비대면 개통 시작</a></p></main></body></html>';
 };
 const homeHub=()=>'<html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="'+(publish?'index,follow':'noindex,follow')+'"><title>선불폰 지역별 안내</title></head><body><h1>지역별 비대면 선불폰 안내</h1><ul>'+regions.map(p=>'<li><a href="/bulk-lab-hub/'+esc(p)+'/">'+esc(p)+'</a></li>').join('')+'</ul></body></html>';
 const regionHub=p=>'<html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="'+(publish?'index,follow':'noindex,follow')+'"><title>'+esc(p)+' 선불폰 안내</title></head><body><h1>'+esc(p)+' 선불폰 지역 안내</h1><a href="/bulk-lab-hub/">전체 지역</a><ul>'+data.filter(r=>r.province===p&&(r.cohort==='B'||r.cohort==='D')).map(r=>'<li><a href="/'+esc(r.slug)+'/">'+esc(r.dong)+'</a></li>').join('')+'</ul></body></html>';
 const xml=locs=>'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+locs.map(s=>'<url><loc>'+esc(s)+'</loc></url>').join('\n')+'\n</urlset>';
 if(check){
  if(!document(data[0]).includes('name="robots" content="noindex,follow"'))throw Error('Preview robots mismatch');
  console.log(JSON.stringify({mode:'check',total:data.length,groups:Object.fromEntries(groups.map(g=>[g,250])),regions:regions.length,uniqueSlugs:names.size,canPublish:publish},null,2));
  return;
 }
 const write=(f,v)=>{const dest=path.join(out,f);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,v,'utf8')};
 for(const r of data)write(r.slug+'/index.html',document(r));
 for(const p of regions)write('bulk-lab-hub/'+p+'/index.html',regionHub(p));
 write('bulk-lab-hub/index.html',homeHub());
 if(publish){
  for(const g of groups)write('bulk-lab-sitemap-'+g.toLowerCase()+'.xml',xml(data.filter(r=>r.cohort===g).map(r=>site+r.slug+'/')));
  write('bulk-lab-sitemap-hubs.xml',xml([site+'bulk-lab-hub/',...regions.map(p=>site+'bulk-lab-hub/'+p+'/')]));
  const files=[...groups.map(g=>'bulk-lab-sitemap-'+g.toLowerCase()+'.xml'),'bulk-lab-sitemap-hubs.xml','sitemap.xml'];
  write('sitemap_index.xml','<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+files.map(p=>'<sitemap><loc>'+site+p+'</loc></sitemap>').join('\n')+'\n</sitemapindex>');
 }
 write('audit.json',JSON.stringify({mode:publish?'publish':'preview',count:data.length,groups:Object.fromEntries(groups.map(g=>[g,250])),hubs:regions.length+1,generated:new Date().toISOString()},null,2));
 console.log('Generated '+data.length+' '+(publish?'publish':'preview')+' pages at '+out);
})();
