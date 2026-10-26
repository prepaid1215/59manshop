
(function(){
  var article=document.getElementById('article'),slot=document.getElementById('slot'),file=document.getElementById('photo');
  var preview=document.getElementById('photo-preview'),status=document.getElementById('status'),save=document.getElementById('save');
  var open=document.getElementById('open-article'),chosen=null,objectURL=null;
  var args=new URLSearchParams(location.search);
  function update(){
    var opt=article.selectedOptions[0],target=opt&&opt.dataset.path;
    open.href=target?target+'?image-slots=1':'/guide/';
    save.disabled=!(chosen&&article.value);
    if(chosen&&article.value)status.textContent='파일명: '+article.value+'--'+slot.value+'.webp';
  }
  fetch('/data/photo-pages.json').then(function(r){if(!r.ok)throw Error('글 목록을 불러올 수 없습니다.');return r.json();}).then(function(rows){
    rows.forEach(function(row){
      var option=document.createElement('option');option.value=row.slug;option.dataset.path=row.path;
      option.textContent=row.label;article.appendChild(option);
    });
    var wanted=args.get('page');if(wanted&&rows.some(function(r){return r.slug===wanted;}))article.value=wanted;
    if(args.get('slot')==='02')slot.value='02';update();
  }).catch(function(e){status.textContent=e.message;});
  article.addEventListener('change',update);slot.addEventListener('change',update);
  file.addEventListener('change',function(){
    chosen=file.files&&file.files[0];if(objectURL){URL.revokeObjectURL(objectURL);objectURL=null;}
    if(!chosen){preview.style.display='none';save.disabled=true;return;}
    if(!chosen.type.startsWith('image/')){status.textContent='이미지 파일을 선택하세요.';chosen=null;return;}
    if(chosen.size>25*1024*1024){status.textContent='25MB 이하 이미지를 선택하세요.';chosen=null;return;}
    objectURL=URL.createObjectURL(chosen);preview.src=objectURL;preview.style.display='block';update();
  });
  save.addEventListener('click',function(){
    if(!chosen||!article.value)return;
    save.disabled=true;status.textContent='이미지 파일을 WebP로 변환합니다.';
    var input=new Image(),temporary=URL.createObjectURL(chosen);
    input.onload=function(){
      var scale=Math.min(1,1400/Math.max(input.naturalWidth,input.naturalHeight));
      var canvas=document.createElement('canvas');
      canvas.width=Math.max(1,Math.round(input.naturalWidth*scale));canvas.height=Math.max(1,Math.round(input.naturalHeight*scale));
      canvas.getContext('2d').drawImage(input,0,0,canvas.width,canvas.height);
      canvas.toBlob(function(blob){
        URL.revokeObjectURL(temporary);save.disabled=false;
        if(!blob){status.textContent='이미지 변환에 실패했습니다. 다른 사진을 선택하세요.';return;}
        var a=document.createElement('a'),url=URL.createObjectURL(blob);
        a.href=url;a.download=article.value+'--'+slot.value+'.webp';document.body.appendChild(a);a.click();a.remove();
        setTimeout(function(){URL.revokeObjectURL(url);},2000);
        status.textContent='저장한 파일 '+a.download+'을 GitHub에 올려주세요.';
      },'image/webp',0.85);
    };
    input.onerror=function(){URL.revokeObjectURL(temporary);save.disabled=false;status.textContent='이미지를 열 수 없습니다.';};
    input.src=temporary;
  });
})();
