/* EST 68: exportación local de expedientes disciplinarios. Sin envío de datos a otros servicios. */
(function(){
'use strict';
const WINE=[123,44,42],SAND=[231,213,167],DARK=[37,37,37],MUTED=[100,96,91],LINE=[212,207,199],WHITE=[255,255,255];
const LEFT=17,RIGHT=17,BOTTOM=258;
const kinds={llamada:'Llamada a familia',firma:'Recepción de firma',citatorio:'Citatorio',medida:'Medida',nota:'Nota'};
const statuses={realizado:'Realizado',pendiente:'Pendiente',asignado:'Asignado'};
function plain(s,otherwise='No especificado'){
 const text=String(s===null||s===undefined?'':s).replace(/\r\n?/g,'\n').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,' ').trim();
 return text||otherwise;
}
function date(s){
 if(!s)return 'No registrada';
 const match=String(s).match(/^(\d{4})-(\d\d)-(\d\d)/);
 if(match)return match[3]+'/'+match[2]+'/'+match[1];
 return plain(s);
}
function nowDate(){
 return new Intl.DateTimeFormat('es-MX',{timeZone:'America/Mexico_City',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
}
function safeFile(s){
 return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-zA-Z0-9]+/g,'_').replace(/^_+|_+$/g,'').slice(0,80);
}
async function logoPng(url){
 if(typeof Image==='undefined'||!document.createElement)return null;
 return new Promise(resolve=>{
  const img=new Image();
  img.onload=()=>{
   try{
    const w=Math.max(300,Math.ceil(img.naturalWidth*3)),h=Math.max(160,Math.ceil(img.naturalHeight*3));
    const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
    const cx=canvas.getContext('2d');if(!cx){resolve(null);return}
    cx.clearRect(0,0,w,h);cx.drawImage(img,0,0,w,h);
    resolve(canvas.toDataURL('image/png'));
   }catch(_){resolve(null)}
  };
  img.onerror=()=>resolve(null);
  img.src=url;
 });
}
async function download({student,reports,followups}){
 if(!student||typeof student!=='object')throw Error('Selecciona un alumno válido.');
 const PDF=window.jspdf&&window.jspdf.jsPDF;
 if(!PDF)throw Error('No se cargó el generador de PDF. Actualiza la página e inténtalo de nuevo.');
 const s=student;
 const records=[...(reports||[])].filter(r=>r.student_id===s.id).sort((a,b)=>String(a.report_date||'').localeCompare(String(b.report_date||''))||String(a.created_at||'').localeCompare(String(b.created_at||'')));
 const acts=[...(followups||[])];
 const schoolLogo=await logoPng('/est68/assets/emblema-secundaria-tecnica.svg');
 const doc=new PDF({orientation:'portrait',unit:'mm',format:'letter',compress:true});
 const pageW=doc.internal.pageSize.getWidth();
 const pageH=doc.internal.pageSize.getHeight();
 const bodyX=LEFT+5,bodyW=pageW-LEFT-RIGHT-10;
 let y=0,page=0;
 function color(rgb){doc.setTextColor(...rgb)}
 function topPage(first){
  if(page)doc.addPage();
  page+=1;
  doc.setFillColor(...WINE);doc.rect(0,0,pageW,5,'F');
  if(first){
   if(schoolLogo)try{doc.addImage(schoolLogo,'PNG',LEFT,11,18,22)}catch(_){}
   color(DARK);doc.setFont('helvetica','bold');doc.setFontSize(10.2);
   doc.text('ESCUELA SECUNDARIA TÉCNICA N.º 68',pageW/2,17,{align:'center'});
   doc.setFont('helvetica','normal');doc.setFontSize(8.5);
   doc.text('JUCHITLÁN, JALISCO',pageW/2,23,{align:'center'});
   color(WINE);doc.setFont('helvetica','bold');doc.setFontSize(15);
   doc.text('EXPEDIENTE DISCIPLINARIO',pageW/2,43,{align:'center'});
   doc.setDrawColor(...WINE);doc.setLineWidth(.55);doc.line(LEFT,49,pageW-RIGHT,49);
   y=56;
  }else{
   color(WINE);doc.setFont('helvetica','bold');doc.setFontSize(10.3);
   doc.text('EST 68  /  EXPEDIENTE DISCIPLINARIO',LEFT,17);
   color(MUTED);doc.setFont('helvetica','normal');doc.setFontSize(8.2);
   doc.text(plain(s.full_name),LEFT,23);
   doc.setDrawColor(...SAND);doc.setLineWidth(.5);doc.line(LEFT,28,pageW-RIGHT,28);
   y=36;
  }
 }
 function enough(height){
  if(y+height>BOTTOM)topPage(false);
 }
 function divider(){
  enough(6);doc.setDrawColor(...LINE);doc.setLineWidth(.25);doc.line(LEFT,y,pageW-RIGHT,y);y+=5;
 }
 function smallHeading(txt){
  enough(13);color(WINE);doc.setFont('helvetica','bold');doc.setFontSize(10);
  doc.text(plain(txt),LEFT,y);y+=4;
  doc.setDrawColor(...SAND);doc.line(LEFT,y,pageW-RIGHT,y);y+=7;
 }
 function wrapped(label,value){
  const text=plain(value);
  const textLines=doc.splitTextToSize(text,bodyW);
  enough(12);
  color(WINE);doc.setFont('helvetica','bold');doc.setFontSize(7.8);
  doc.text(plain(label).toLocaleUpperCase('es-MX'),bodyX,y);
  y+=5;
  doc.setFont('helvetica','normal');doc.setFontSize(9.4);color(DARK);
  for(const line of textLines){
   enough(5.2);
   doc.text(line,bodyX,y);
   y+=4.45;
  }
  y+=3.1;
 }
 function reportHead(r,n){
  enough(19);
  const x=LEFT,boxWidth=pageW-LEFT-RIGHT;
  doc.setFillColor(...SAND);doc.roundedRect(x,y,boxWidth,14,2,2,'F');
  color(DARK);doc.setFont('helvetica','bold');doc.setFontSize(9.7);
  doc.text('REPORTE '+String(n).padStart(2,'0')+'   |   '+date(r.report_date),x+5,y+5.7);
  color(WINE);doc.setFontSize(8.8);
  doc.text(plain(r.severity,'SIN CLASIFICAR'),x+boxWidth-5,y+5.7,{align:'right'});
  doc.setFont('helvetica','normal');doc.setFontSize(7.5);color(MUTED);
  doc.text('Ciclo escolar 2026-2027',x+5,y+11.4);
  y+=20;
 }
 topPage(true);
 const nameLines=doc.splitTextToSize(plain(s.full_name),pageW-LEFT-RIGHT-12);
 const cardH=29+Math.max(0,nameLines.length-1)*5.5;
 doc.setFillColor(249,247,242);doc.setDrawColor(...LINE);
 doc.roundedRect(LEFT,y,pageW-LEFT-RIGHT,cardH,2.5,2.5,'FD');
 color(WINE);doc.setFont('helvetica','bold');doc.setFontSize(7.5);
 doc.text('DATOS DEL ALUMNO',LEFT+5,y+6);
 color(DARK);doc.setFont('helvetica','bold');doc.setFontSize(11.8);
 doc.text(nameLines,LEFT+5,y+13.5);
 const afterName=y+13.5+(nameLines.length-1)*5.5;
 color(MUTED);doc.setFont('helvetica','normal');doc.setFontSize(8.9);
 doc.text('Grupo: '+plain(s.group_code,'No especificado')+'    |    N.º de lista: '+plain(s.enrollment_no,'No especificado'),LEFT+5,afterName+7);
 doc.text('Ciclo: 2026-2027    |    Total de reportes: '+records.length,LEFT+5,afterName+12);
 y+=cardH+11;
 smallHeading('HISTORIAL DE REPORTES');
 if(!records.length){wrapped('Situación','No hay reportes disciplinarios registrados para este alumno en el ciclo escolar 2026-2027.')}
 records.forEach((r,index)=>{
  reportHead(r,index+1);
  wrapped('Materia / área',r.subject_snapshot);
  wrapped('Docente que reporta',r.teacher_snapshot);
  wrapped('Motivo del reporte',r.reason);
  wrapped('Acuerdos',r.agreements);
  const items=acts.filter(f=>f.report_id===r.id).sort((a,b)=>String(a.action_date||a.created_at||'').localeCompare(String(b.action_date||b.created_at||'')));
  if(!items.length){
   wrapped('Actuaciones de seguimiento','Sin actuaciones registradas.');
  }else{
   enough(13);color(WINE);doc.setFont('helvetica','bold');doc.setFontSize(9);
   doc.text('ACTUACIONES DE SEGUIMIENTO ('+items.length+')',bodyX,y);y+=7;
   items.forEach((f,k)=>{
    enough(13);
    doc.setFillColor(246,243,238);
    doc.rect(bodyX-1,y-3,bodyW+2,9,'F');
    color(DARK);doc.setFont('helvetica','bold');doc.setFontSize(8.4);
    const fType=kinds[f.kind]||plain(f.kind);
    const fStatus=statuses[f.status]||plain(f.status);
    const header=(k+1)+'. '+fType+'  |  '+fStatus;
    const headLines=doc.splitTextToSize(header,bodyW-3);
    if(headLines.length===1){doc.text(headLines[0],bodyX+1,y+2);y+=10}
    else{
     // Se evita desbordar el ancho si una actuación tiene nombre extenso.
     doc.text(headLines[0],bodyX+1,y+2);y+=10;
     for(const part of headLines.slice(1)){enough(5);doc.text(part,bodyX+1,y);y+=5}
    }
    wrapped('Fecha de actuación',date(f.action_date));
    wrapped('Detalle de la actuación',f.detail);
   });
  }
  if(index<records.length-1){y+=1;divider();y+=3;}
 });
 enough(17);
 y+=4;
 doc.setDrawColor(...SAND);doc.line(LEFT,y,pageW-RIGHT,y);y+=6;
 color(MUTED);doc.setFont('helvetica','normal');doc.setFontSize(8.5);
 doc.text('Fecha de generación: '+nowDate(),LEFT,y);
 y+=5;doc.setFontSize(7.6);
 doc.text('Documento de consulta generado a partir de los registros de la plataforma EST 68.',LEFT,y);
 const total=doc.internal.getNumberOfPages();
 for(let n=1;n<=total;n++){
  doc.setPage(n);doc.setDrawColor(...LINE);doc.line(LEFT,pageH-18,pageW-RIGHT,pageH-18);
  color(MUTED);doc.setFont('helvetica','normal');doc.setFontSize(7.1);
  doc.text('INFORMACIÓN ESCOLAR CONFIDENCIAL  -  USO INSTITUCIONAL',LEFT,pageH-12.6);
  doc.text('Página '+n+' de '+total,pageW-RIGHT,pageH-12.6,{align:'right'});
 }
 const filename='EST68_Expediente_Disciplinario_'+safeFile(s.full_name)+'_'+safeFile(s.group_code)+'.pdf';
 doc.save(filename);
 return filename;
}
window.EST68ExpedientePDF={download};
})();