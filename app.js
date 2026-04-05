/* ═══════════════ HELPERS ═══════════════ */
function esc(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");}
async function loadJson(p,bust){const t=bust?`${p}${p.includes("?")?"&":"?"}ts=${Date.now()}`:p;const r=await fetch(t);if(!r.ok)throw new Error(`Failed: ${p}`);return r.json();}
async function tryJson(p,bust){try{return await loadJson(p,bust);}catch{return null;}}
function optVals(a,k){return[...new Set(a.map(i=>i[k]).filter(Boolean))].sort();}
function sRank(s){return{slurm_verified:5,sandbox_verified:4,implemented:3,draft:2,idea:1}[s]||0;}
function sLabel(v){return v.replaceAll("_"," ");}
function trunc(v,l=180){const t=String(v??"");return t.length<=l?t:t.slice(0,l-1)+"…";}
function sortSkills(sk,m){const s=[...sk];if(m==="name")return s.sort((a,b)=>a.name.localeCompare(b.name));if(m==="recent")return s.sort((a,b)=>(b.last_verified||b.last_updated||"").localeCompare(a.last_verified||a.last_updated||""));return s.sort((a,b)=>{const d=sRank(b.status)-sRank(a.status);return d?d:a.name.localeCompare(b.name);});}
function flatLeaves(tree){return(tree.children||[]).flatMap(d=>(d.children||[]).map(l=>({...l,domain_name:d.name,registry_domains:d.registry_domains||[]})));}
function sPill(s){if(s==="sandbox_verified"||s==="slurm_verified")return"v-green";if(s==="implemented")return"v-blue";if(s==="draft"||s==="idea")return"v-amber";return"v-gray";}

/* ═══════════════ PANEL LOADER ═══════════════ */
const PANEL_NAMES = ['overview', 'catalog', 'taxonomy', 'paper'];

async function loadAllPanels() {
  await Promise.all(PANEL_NAMES.map(async name => {
    try {
      const r = await fetch(`panels/${name}.html`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const html = await r.text();
      const el = document.getElementById(`panel-${name}`);
      if (el) el.innerHTML = html;
    } catch(e) {
      console.warn(`Could not load panels/${name}.html:`, e.message);
    }
  }));
}

/* ═══════════════ TAB ROUTING WITH HISTORY ═══════════════ */
const validTabs = ["overview","catalog","taxonomy","paper"];
let _currentTab="overview",_navFromPop=false;

function switchTab(id,{pushState=true}={}){
  if(!id||!validTabs.includes(id))id="overview";
  _currentTab=id;
  document.querySelectorAll(".tab-btn").forEach(t=>t.classList.toggle("active",t.dataset.tab===id));
  document.querySelectorAll(".tab-panel").forEach(p=>p.classList.toggle("active",p.id===`panel-${id}`));
  if(id==="taxonomy"&&!window._taxR){renderTaxonomy();window._taxR=true;}
  if(pushState&&!_navFromPop){
    history.pushState({tab:id},"",`#${id}`);
  }
}

// Handle browser back/forward
window.addEventListener("popstate",e=>{
  _navFromPop=true;
  const state=e.state||{};
  if(document.getElementById("sd-drawer").classList.contains("open")&&!state.drawer){
    _closeDrawerVisual();
    if(state.tab)switchTab(state.tab,{pushState:false});
    _navFromPop=false;
    return;
  }
  if(state.drawer){
    const tab=state.tab||"catalog";
    switchTab(tab,{pushState:false});
    setTimeout(()=>{openSkillDetail(state.drawer,state.drawerTab||"guide");},0);
    _navFromPop=false;
    return;
  }
  const tab=state.tab||location.hash.replace("#","").split("/")[0]||"overview";
  switchTab(tab,{pushState:false});
  _navFromPop=false;
});

// Set initial state from hash on load — deferred until panels are ready
function initRouting(){
  const raw=location.hash.replace("#","");
  const parts=raw.split("/");
  const initial=validTabs.includes(parts[0])?parts[0]:"overview";
  if(parts[1]==="skill"&&parts[2]){
    history.replaceState({tab:initial,drawer:parts[2]},"");
    switchTab(initial,{pushState:false});
    window._pendingDeepLink={skillId:parts[2],tab:"guide"};
  } else {
    history.replaceState({tab:initial},"",`#${initial}`);
    if(initial!=="overview")switchTab(initial,{pushState:false});
  }
  document.querySelectorAll(".tab-btn").forEach(t=>t.addEventListener("click",()=>switchTab(t.dataset.tab)));
}

/* ═══════════════ SKILL DETAIL DRAWER ═══════════════ */
let _sdDetails={},_sdSkills=[],_sdCurrent=null,_sdTab="guide";

function renderMd(text){
  if(!text)return'<p class="sd-empty">No content available.</p>';
  const e2=v=>String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
  const inline=s=>{
    const q=e2(s);
    return q
      .replace(/`([^`]+)`/g,(_,c)=>`<code>${c}</code>`)
      .replace(/\*\*([^*]+)\*\*/g,(_,c)=>`<strong>${c}</strong>`)
      .replace(/\*([^*]+)\*/g,(_,c)=>`<em>${c}</em>`)
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g,(_,t,u)=>{
        const safe=/^https?:\/\//.test(u)?u.replaceAll('"','%22'):'#';
        return`<a href="${safe}" target="_blank" rel="noopener">${t}</a>`;
      });
  };
  const parts=text.split(/(```[\s\S]*?```)/g);
  let html='';
  for(const part of parts){
    if(part.startsWith('```')){
      const ls=part.split('\n');
      const code=ls.slice(1,-1).join('\n');
      html+=`<pre><code>${e2(code)}</code></pre>`;
      continue;
    }
    const lines=part.split('\n');
    let inList=false,li='';
    const flush=()=>{if(inList){html+=`<ul>${li}</ul>`;inList=false;li='';}};
    for(const line of lines){
      if(!line.trim()){flush();continue;}
      const hm=line.match(/^(#{1,6})\s+(.*)/);
      if(hm){flush();const lv=hm[1].length;html+=`<h${lv}>${inline(hm[2])}</h${lv}>`;continue;}
      if(/^[-*]\s/.test(line)){inList=true;li+=`<li>${inline(line.slice(2))}</li>`;continue;}
      if(/^\d+\.\s/.test(line)){inList=true;li+=`<li>${inline(line.replace(/^\d+\.\s/,''))}</li>`;continue;}
      if(/^---+$/.test(line.trim())){flush();html+='<hr>';continue;}
      if(/^>/.test(line)){flush();html+=`<blockquote><p>${inline(line.slice(1).trim())}</p></blockquote>`;continue;}
      flush();
      html+=`<p>${inline(line)}</p>`;
    }
    flush();
  }
  return html||'<p class="sd-empty">No content available.</p>';
}

function renderMetadata(rawMeta,sk){
  if(!rawMeta&&!sk)return'<p class="sd-empty">No metadata available.</p>';
  let m=null;
  try{m=JSON.parse(rawMeta);}catch{}
  if(!m)m=sk||{};
  const fmtV=v=>{
    if(v===null||v===undefined)return'<span style="color:var(--ink-4)">—</span>';
    if(Array.isArray(v)){
      if(!v.length)return'<span style="color:var(--ink-4)">—</span>';
      return`<div class="sd-meta-pill-row">${v.map(x=>`<span class="pill v-gray">${esc(String(x))}</span>`).join('')}</div>`;
    }
    if(typeof v==='object')return`<span class="sd-meta-val-mono">${esc(JSON.stringify(v))}</span>`;
    return esc(String(v));
  };
  const fields=[
    ['Name','name'],['Domain','domain'],['Topic Path','topic_path'],
    ['Status','status'],['Authorship','authorship'],
    ['Language','language'],['Compute','compute_requirements'],
    ['Tags','tags'],['Aliases','aliases'],
    ['Source Resources','source_resources'],['Related Skills','related_skills'],
    ['Created','created_at'],['Updated','updated_at'],['Last Verified','last_verified_at'],
    ['Freshness Risk','freshness_risk'],['File Count','file_count'],
  ];
  const rows=fields
    .filter(([,k])=>m[k]!==undefined&&m[k]!==null&&!(Array.isArray(m[k])&&!m[k].length))
    .map(([l,k])=>`<tr><th>${esc(l)}</th><td>${fmtV(m[k])}</td></tr>`)
    .join('');
  return`<table class="sd-meta-table"><tbody>${rows}</tbody></table>`;
}

function sdContent(tab,skillId){
  const d=_sdDetails[skillId]||{};
  const sk=_sdSkills.find(s=>s.skill_id===skillId||s.slug===skillId)||null;
  if(tab==='guide')return`<div class="sd-md">${renderMd(d.skill_md)}</div>`;
  if(tab==='meta') return renderMetadata(d.metadata_raw,sk);
  if(tab==='refs') return`<div class="sd-md">${renderMd(d.refs_md)}</div>`;
  if(tab==='tests'){
    const cmds=sk?.test_commands||[];
    const cmdHtml=cmds.length?`<div style="margin-bottom:20px"><div class="sd-section-label">Test Commands</div>${cmds.map(c=>`<code class="sd-cmd">${esc(c)}</code>`).join('')}</div>`:'';
    const mdHtml=d.tests_md?`<div class="sd-section-label" style="margin-bottom:8px">Test Notes</div><div class="sd-md">${renderMd(d.tests_md)}</div>`:'';
    return (cmdHtml||mdHtml)?cmdHtml+mdHtml:'<p class="sd-empty">No test information available.</p>';
  }
  return '';
}

function sdSwitchTab(tab){
  _sdTab=tab;
  document.querySelectorAll('.sd-tab').forEach(b=>b.classList.toggle('active',b.dataset.sdTab===tab));
  document.getElementById('sd-body').innerHTML=sdContent(tab,_sdCurrent);
}

function openSkillDetail(skillId,tab){
  tab=tab||'guide';
  _sdCurrent=skillId;
  const sk=_sdSkills.find(s=>s.skill_id===skillId||s.slug===skillId);
  document.getElementById('sd-title').textContent=sk?.name||skillId;
  const pills=document.getElementById('sd-pills');
  pills.innerHTML=sk?`<span class="pill ${sPill(sk.status)}">${esc(sLabel(sk.status))}</span><span class="pill v-gray">${esc(sk.domain)}</span>`:'';
  document.querySelectorAll('.sd-tab').forEach(b=>b.classList.toggle('active',b.dataset.sdTab===tab));
  _sdTab=tab;
  document.getElementById('sd-body').innerHTML=sdContent(tab,skillId);
  document.getElementById('sd-overlay').classList.add('open');
  document.getElementById('sd-drawer').classList.add('open');
  document.body.style.overflow='hidden';
  if(!_navFromPop){
    history.pushState({tab:_currentTab,drawer:skillId,drawerTab:tab},"",`#${_currentTab}/skill/${skillId}`);
  }
}

function _closeDrawerVisual(){
  document.getElementById('sd-overlay').classList.remove('open');
  document.getElementById('sd-drawer').classList.remove('open');
  document.body.style.overflow='';
}

function closeSkillDetail(){
  if(!document.getElementById('sd-drawer').classList.contains('open'))return;
  _closeDrawerVisual();
  if(!_navFromPop){history.back();}
}

/* ═══════════════ OVERVIEW RENDERS ═══════════════ */
function renderStats(skills,graph,tree){
  const rc=graph.nodes.filter(n=>n.type==="resource").length;
  const s=[{l:"Skills",v:skills.length},{l:"Resources",v:rc},{l:"Covered",v:tree.covered_leaf_count||0},{l:"Frontier",v:tree.frontier_leaf_count||0},{l:"Sandbox Verified",v:skills.filter(s=>s.status==="sandbox_verified").length},{l:"Slurm Verified",v:skills.filter(s=>s.status==="slurm_verified").length},{l:"Domains",v:(tree.children||[]).length},{l:"Total Leaves",v:(tree.covered_leaf_count||0)+(tree.frontier_leaf_count||0)+(tree.todo_leaf_count||0)}];
  document.getElementById("stats-row").innerHTML=s.map(x=>`<div class="stat-tile"><div class="stat-num">${esc(x.v)}</div><div class="stat-lab">${esc(x.l)}</div></div>`).join("");
}

function renderDomainGrid(tree,sel){
  document.getElementById("domain-grid").innerHTML=(tree.children||[]).map(d=>{
    const tot=Math.max(d.children.length,1),cov=d.covered_leaf_count||0,fr=d.frontier_leaf_count||0,td=d.todo_leaf_count||0;
    const act=sel&&(d.registry_domains||[]).includes(sel);
    return`<button class="domain-card${act?" active":""}" data-domain="${esc((d.registry_domains||[])[0]||"")}"><h3>${esc(d.name)}</h3><div class="domain-meta"><span class="dm-skills"><b>${esc(d.skill_count)}</b> skills</span><span class="dm-res"><b>${esc(d.resource_count)}</b> res</span><span class="dm-leaves"><b>${esc(tot)}</b> leaves</span></div><div class="cov-bar" style="--c:${(cov/tot)*100}%;--f:${(fr/tot)*100}%;--t:${(td/tot)*100}%"><span></span><span></span><span></span></div><div class="domain-meta dm-cov"><span class="dm-cov-c"><b>${esc(cov)}</b> covered</span><span class="dm-cov-f"><b>${esc(fr)}</b> frontier</span><span class="dm-cov-t"><b>${esc(td)}</b> todo</span></div></button>`;
  }).join("");
}

function renderFrontiers(tree){
  const c=document.getElementById("frontier-list"),lv=flatLeaves(tree).filter(l=>l.coverage_status==="frontier").sort((a,b)=>a.domain_name.localeCompare(b.domain_name)||a.name.localeCompare(b.name));
  if(!lv.length){c.innerHTML=`<div class="empty">No frontier leaves — every leaf with resources has a mapped skill.</div>`;return;}
  c.innerHTML=lv.map(l=>`<div class="frontier-item"><strong>${esc(l.name)}</strong><small>${esc(l.domain_name)} · ${esc(l.resource_count)} resources · ${esc(l.skill_count)} skills</small></div>`).join("");
}

function renderTree(tree,sel){
  document.getElementById("tree").innerHTML=(tree.children||[]).filter(d=>!sel||(d.registry_domains||[]).includes(sel)).map(d=>{
    const lv=(d.children||[]).map(l=>{
      const ts=(l.skills||[])[0],tr=(l.resources||[])[0];
      const tsSlug=ts?(ts.slug||ts.path?.split('/').pop()||''):'';
      return`<div class="leaf-card" data-status="${esc(l.coverage_status)}"><div class="leaf-header"><span class="pill ${l.coverage_status==="covered"?"v-green":l.coverage_status==="frontier"?"v-amber":"v-gray"}">${esc(sLabel(l.coverage_status))}</span></div><h4>${esc(l.name)}</h4><p>${esc(l.skill_count)} skill(s) · ${esc(l.resource_count)} resource(s)</p><div class="leaf-links">${ts&&tsSlug?`<button class="sd-link" onclick="openSkillDetail('${esc(tsSlug)}','guide')">${esc(ts.name)}</button>`:`<span class="muted">No skill</span>`}${tr?` · <a href="${esc(tr.url)}" target="_blank" rel="noopener">${esc(tr.canonical_name)}</a>`:""}</div></div>`;
    }).join("");
    return`<div class="tree-domain"><h3>${esc(d.name)}</h3><p>${esc(d.skill_count)} skills · ${esc(d.resource_count)} resources · ${esc(d.covered_leaf_count||0)} covered</p><div class="leaf-list">${lv}</div></div>`;
  }).join("");
}

function renderSkills(skills){
  const c=document.getElementById("skills");
  document.getElementById("skill-count-label").textContent=`${skills.length} skill(s) match current filters.`;
  if(!skills.length){c.innerHTML=`<div class="empty">No skills match the current filters.</div>`;return;}
  const verifiedClass=v=>v&&v!=="not yet"?"meta-verified":"meta-unverified";
  c.innerHTML=skills.map(s=>`<div class="skill-card"><div class="skill-top"><span class="pill ${sPill(s.status)}">${esc(sLabel(s.status))}</span><span class="pill v-blue">${esc(s.domain)}</span><span class="pill v-gray">${esc(s.compute_requirements)}</span></div><h3 onclick="openSkillDetail('${esc(s.skill_id)}','guide')">${esc(s.name)}</h3><p>${esc(s.description)}</p><div class="skill-meta"><div class="meta-line"><span class="meta-lbl meta-lbl-topic">Topic</span><span class="meta-val">${esc(s.topic_path.join(" › "))}</span></div><div class="meta-line"><span class="meta-lbl meta-lbl-tags">Tags</span><span class="meta-val">${esc(s.tags.join(", ")||"—")}</span></div><div class="meta-line meta-line-stats"><span class="ms-res"><b>${esc(s.source_resource_count)}</b> resources</span><span class="ms-sep">·</span><span class="ms-files"><b>${esc(s.file_count)}</b> files</span><span class="ms-sep">·</span><span class="${verifiedClass(s.last_verified)}"><b>${esc(s.last_verified||"not yet")}</b> verified</span></div></div>${s.test_commands?.length?`<code class="cmd">${esc(s.test_commands[0])}</code>`:""}<div class="skill-links"><button class="sd-link" onclick="openSkillDetail('${esc(s.skill_id)}','guide')">SKILL.md</button><span class="sep">·</span><button class="sd-link" onclick="openSkillDetail('${esc(s.skill_id)}','meta')">metadata</button><span class="sep">·</span><button class="sd-link" onclick="openSkillDetail('${esc(s.skill_id)}','refs')">refs</button><span class="sep">·</span><button class="sd-link" onclick="openSkillDetail('${esc(s.skill_id)}','tests')">tests</button></div></div>`).join("");
}

/* ═══════════════ TAXONOMY RADIAL ═══════════════ */
async function renderTaxonomy(){
  let taxData;
  try{taxData=await loadJson("taxonomy-radial/taxonomy.json");}catch{return;}
  document.getElementById("tax-domains").textContent=taxData.domainCount;
  document.getElementById("tax-subdomains").textContent=taxData.subdomainCount;
  // Palette aligned with site design system
  const palette=["#3b6cef","#1a9e6f","#d97706","#7c3aed","#0891b2","#e11d48","#0d9488","#ca8a04","#9333ea","#059669","#dc2626","#2563eb"];
  const svg=document.getElementById("radial-svg"),shell=document.getElementById("viz-canvas");
  const vp=document.getElementById("viewport"),eL=document.getElementById("edge-layer"),nL=document.getElementById("node-layer"),lL=document.getElementById("label-layer");
  const sIn=document.getElementById("tax-search"),dT=document.getElementById("detail-title"),dB=document.getElementById("detail-body"),dM=document.getElementById("detail-meta");
  const st={active:null,search:"",scale:1,tx:0,ty:0,dragging:false,ds:null};
  // Pre-built element maps — O(1) hover highlight, no querySelectorAll on each event
  const domEls=new Map(),subEls=new Map(),domEdges=new Map(),subEdges=new Map(),allFadable=[];
  function regEl(el,dk,sk){allFadable.push(el);if(dk){if(!domEls.has(dk))domEls.set(dk,[]);domEls.get(dk).push(el);}if(sk){if(!subEls.has(sk))subEls.set(sk,[]);subEls.get(sk).push(el);}}
  function regEdge(el,dk,sk){allFadable.push(el);if(dk){if(!domEdges.has(dk))domEdges.set(dk,[]);domEdges.get(dk).push(el);}if(sk){if(!subEdges.has(sk))subEdges.set(sk,[]);subEdges.get(sk).push(el);}}
  function mix(a,b,t){const ah=a.replace("#",""),bh=b.replace("#","");return"#"+[0,1,2].map(i=>{const av=parseInt(ah.slice(i*2,i*2+2),16),bv=parseInt(bh.slice(i*2,i*2+2),16);return Math.round(av*(1-t)+bv*t).toString(16).padStart(2,"0")}).join("");}
  function pol(r,a){return{x:r*Math.cos(a),y:r*Math.sin(a)};}
  function alloc(tot,bands){const w=Array.from({length:bands},(_,i)=>1+i*0.18),sc=tot/w.reduce((a,b)=>a+b,0);const c=w.map(x=>Math.max(1,Math.floor(x*sc)));while(c.reduce((a,b)=>a+b,0)<tot){let idx=0;for(let i=1;i<c.length;i++)if(w[i]>w[idx])idx=i;c[idx]++;}while(c.reduce((a,b)=>a+b,0)>tot){let idx=c.indexOf(Math.max(...c));if(c[idx]>1)c[idx]--;else break;}return c;}
  function build(data){const doms=data.domains.map((d,i)=>({...d,color:palette[i%palette.length]}));const gap=0.026,wts=doms.map(d=>4+Math.pow(d.count,0.84)),us=Math.PI*2-gap*doms.length,tw=wts.reduce((a,b)=>a+b,0);let cur=-Math.PI/2;return{root:{x:0,y:0,label:data.name},domains:doms.map((d,i)=>{const span=us*wts[i]/tw,start=cur,end=start+span,angle=(start+end)/2;cur=end+gap;const dp=pol(430,angle),bc=d.count<=6?2:d.count<=11?3:4,ba=alloc(d.count,bc);let si=0;const subs=[];ba.forEach((cnt,bi)=>{const r=920+bi*130,sp=span*Math.min(1,0.74+bi*0.1),is=angle-sp/2;(cnt===1?[angle]:Array.from({length:cnt},(_,j)=>is+sp*((j+0.5)/cnt))).forEach(sa=>{const a=pol(r,sa);subs.push({id:`${d.key}::${si}`,dk:d.key,dt:d.title,label:d.subdomains[si],angle:sa,radius:r,band:bi,x:a.x,y:a.y});si++;});});return{...d,angle,span,x:dp.x,y:dp.y,subdomains:subs};})};}
  function cS(tag,a={}){const el=document.createElementNS("http://www.w3.org/2000/svg",tag);Object.entries(a).forEach(([k,v])=>el.setAttribute(k,v));return el;}
  function eP(s,t,cr,ca){return`M ${s.x} ${s.y} Q ${cr*Math.cos(ca)} ${cr*Math.sin(ca)} ${t.x} ${t.y}`;}
  function rL({x,y,angle,text,kind,fill,stroke,textColor,fontSize=16,padX=11,padY=7,meta}){const g=cS("g",{class:`label-group ${kind} searchable fadable`,transform:`translate(${x} ${y})`});if(meta.domain)g.dataset.domain=meta.domain;if(meta.sub)g.dataset.sub=meta.sub;if(meta.type)g.dataset.type=meta.type;const deg=angle*180/Math.PI,ls=deg>90||deg<-90,rot=ls?deg+180:deg;const inner=cS("g",{transform:`rotate(${rot})`});const txt=cS("text",{x:ls?-padX:padX,y:0,"text-anchor":ls?"end":"start","font-size":fontSize,fill:textColor});txt.textContent=text;inner.appendChild(txt);g.appendChild(inner);lL.appendChild(g);const bb=txt.getBBox();inner.insertBefore(cS("rect",{x:bb.x-padX*0.78,y:bb.y-padY,width:bb.width+padX*1.56,height:bb.height+padY*2,rx:kind==="domain"?16:12,ry:kind==="domain"?16:12,fill,stroke,"stroke-width":1.2}),txt);return g;}
  function setD(t,b,pills){dT.textContent=t;dB.textContent=b;dM.innerHTML="";pills.forEach(p=>{const s=document.createElement("span");s.className="pill v-gray";s.textContent=p;dM.appendChild(s);});}
  // RAF-throttled viewport update — one DOM write per animation frame
  let _vpRaf=null;
  function schedVP(){if(_vpRaf)return;_vpRaf=requestAnimationFrame(()=>{_vpRaf=null;vp.setAttribute("transform",`translate(${st.tx} ${st.ty}) scale(${st.scale})`);});}
  function aVP(){vp.setAttribute("transform",`translate(${st.tx} ${st.ty}) scale(${st.scale})`);}
  function rV(){st.scale=1;st.tx=0;st.ty=0;aVP();}
  function fV(){st.scale=0.92;st.tx=0;st.ty=40;aVP();}
  // Efficient highlight: iterate pre-built arrays, no querySelectorAll
  function aF(){for(const el of allFadable){el.classList.remove("is-active","is-match");}svg.classList.remove("has-focus","match-dim");const q=st.search.trim().toLowerCase();if(q){svg.classList.add("match-dim");for(const el of allFadable){const t=(el.dataset.label||"").toLowerCase(),d=(el.dataset.domainTitle||"").toLowerCase();if(t.includes(q)||d.includes(q))el.classList.add("is-match");}}if(!st.active)return;svg.classList.add("has-focus");const a=st.active;if(a.type==="domain"){(domEls.get(a.domain)||[]).forEach(el=>el.classList.add("is-active"));(domEdges.get(a.domain)||[]).forEach(el=>el.classList.add("is-active"));}else if(a.type==="sub"){(domEls.get(a.domain)||[]).forEach(el=>el.classList.add("is-active"));(subEls.get(a.sub)||[]).forEach(el=>el.classList.add("is-active"));(domEdges.get(a.domain)||[]).forEach(el=>el.classList.add("is-active"));(subEdges.get(a.sub)||[]).forEach(el=>el.classList.add("is-active"));}}
  const layout=build(taxData);
  layout.domains.forEach(d=>{
    // Cool blue-tinted label tones aligned with site palette
    const lc=mix(d.color,"#eef2ff",0.28),df=mix(d.color,"#f0f4ff",0.80),ds=mix(d.color,"#a0b4d8",0.34),sf=mix(d.color,"#f4f8ff",0.92),ss=mix(d.color,"#c4d0ee",0.42),stx=mix(d.color,"#0f1117",0.46);
    const edge=cS("path",{d:eP(layout.root,d,220,d.angle),class:"edge domain-edge fadable",stroke:lc,"data-domain":d.key});
    eL.appendChild(edge);regEdge(edge,d.key,null);
    const dot=cS("circle",{cx:d.x,cy:d.y,r:13,fill:d.color,class:"node-core domain-dot searchable fadable","data-domain":d.key,"data-domain-title":d.title,"data-label":d.title,"data-type":"domain"});
    nL.appendChild(dot);regEl(dot,d.key,null);
    const lp=pol(550,d.angle),lbl=rL({x:lp.x,y:lp.y,angle:d.angle,text:d.title,kind:"domain",fill:df,stroke:ds,textColor:"#0f1117",fontSize:18,padX:13,padY:8,meta:{domain:d.key,type:"domain"}});
    lbl.dataset.label=d.title;lbl.dataset.domainTitle=d.title;regEl(lbl,d.key,null);
    [dot,lbl].forEach(el=>{el.addEventListener("mouseenter",()=>{st.active={type:"domain",domain:d.key};setD(d.title,`${d.count} subdomains.`,["domain",`${d.count} subdomains`]);aF();});el.addEventListener("mouseleave",()=>{st.active=null;setD("Hover a branch","Move over any node to isolate its branch.",["interactive svg","zoom + drag","hover"]);aF();});el.addEventListener("click",e=>{e.stopPropagation();st.active={type:"domain",domain:d.key};st.scale=1.28;st.tx=-d.x*0.2;st.ty=-d.y*0.2;aVP();aF();});});
    d.subdomains.forEach(sub=>{
      const sedge=cS("path",{d:eP(d,sub,(d.radius+sub.radius)*0.56,(d.angle+sub.angle)/2),class:"edge sub-edge fadable",stroke:lc,"data-domain":d.key,"data-sub":sub.id});
      eL.appendChild(sedge);regEdge(sedge,d.key,sub.id);
      const sd=cS("circle",{cx:sub.x,cy:sub.y,r:4,fill:d.color,class:"node-core sub-dot searchable fadable","data-domain":d.key,"data-sub":sub.id,"data-domain-title":d.title,"data-label":sub.label,"data-type":"sub"});
      nL.appendChild(sd);regEl(sd,d.key,sub.id);
      const slp=pol(sub.radius+40+sub.band*6,sub.angle),slbl=rL({x:slp.x,y:slp.y,angle:sub.angle,text:sub.label,kind:"sub",fill:sf,stroke:ss,textColor:stx,fontSize:15,padX:10,padY:6,meta:{domain:d.key,sub:sub.id,type:"sub"}});
      slbl.dataset.label=sub.label;slbl.dataset.domainTitle=d.title;regEl(slbl,d.key,sub.id);
      [sd,slbl].forEach(el=>{el.addEventListener("mouseenter",()=>{st.active={type:"sub",domain:d.key,sub:sub.id};setD(sub.label,`Subdomain in ${d.title}.`,["subdomain",d.title]);aF();});el.addEventListener("mouseleave",()=>{st.active=null;setD("Hover a branch","Move over any node to isolate its branch.",["interactive svg","zoom + drag","hover"]);aF();});el.addEventListener("click",e=>{e.stopPropagation();st.active={type:"sub",domain:d.key,sub:sub.id};st.scale=1.52;st.tx=-sub.x*0.34;st.ty=-sub.y*0.34;aVP();aF();});});
    });
  });
  nL.appendChild(cS("circle",{cx:0,cy:0,r:120,class:"root-glow"}));const rn=cS("rect",{x:-140,y:-48,width:280,height:96,rx:24,ry:24,class:"root-node"});const rl2=cS("text",{x:0,y:-6,class:"root-label"});rl2.textContent=taxData.name;const rs2=cS("text",{x:0,y:22,class:"root-sub"});rs2.textContent="center node";nL.appendChild(rn);nL.appendChild(rl2);nL.appendChild(rs2);
  fV();
  document.getElementById("reset-view").addEventListener("click",rV);document.getElementById("fit-view").addEventListener("click",fV);
  sIn.addEventListener("input",e=>{st.search=e.target.value;aF();});
  svg.addEventListener("click",()=>{st.active=null;setD("Hover a branch","Move over any node to isolate its branch.",["interactive svg","zoom + drag","hover"]);aF();});
  shell.addEventListener("pointerdown",e=>{shell.classList.add("dragging");st.dragging=true;st.ds={x:e.clientX,y:e.clientY,tx:st.tx,ty:st.ty};shell.setPointerCapture(e.pointerId);});
  // RAF-throttled drag — state updated immediately, DOM write deferred to rAF
  shell.addEventListener("pointermove",e=>{if(!st.dragging||!st.ds)return;const f=3800/svg.clientWidth;st.tx=st.ds.tx+(e.clientX-st.ds.x)*f;st.ty=st.ds.ty+(e.clientY-st.ds.y)*f;schedVP();});
  function sD(e){if(st.dragging){st.dragging=false;st.ds=null;shell.classList.remove("dragging");try{shell.releasePointerCapture(e.pointerId);}catch{}}}
  shell.addEventListener("pointerup",sD);shell.addEventListener("pointercancel",sD);
  // Zoom via getBoundingClientRect — avoids expensive getScreenCTM().inverse(), RAF-throttled
  shell.addEventListener("wheel",e=>{e.preventDefault();const r=svg.getBoundingClientRect(),sc=3800/r.width;const cx=(e.clientX-r.left)*sc-1900,cy=(e.clientY-r.top)*sc-1900;const wx=(cx-st.tx)/st.scale,wy=(cy-st.ty)/st.scale;const z=e.deltaY<0?1.08:0.92,ns=Math.max(0.56,Math.min(2.8,st.scale*z));st.tx=cx-wx*ns;st.ty=cy-wy*ns;st.scale=ns;schedVP();},{passive:false});
}

/* ═══════════════ ANIMATIONS & INTERACTIONS ═══════════════ */

// Topbar scroll shadow
let _scrollTick=false;
window.addEventListener("scroll",()=>{
  if(!_scrollTick){_scrollTick=true;requestAnimationFrame(()=>{
    document.querySelector(".topbar").classList.toggle("scrolled",window.scrollY>8);
    _scrollTick=false;
  });}
},{passive:true});

// Animated number counters
function animateCounters(){
  document.querySelectorAll(".stat-num").forEach(el=>{
    const target=parseInt(el.textContent,10);
    if(isNaN(target)||target===0)return;
    const dur=600,start=performance.now();
    el.textContent="0";
    function tick(now){
      const t=Math.min((now-start)/dur,1);
      const ease=1-Math.pow(1-t,3);
      el.textContent=Math.round(target*ease);
      if(t<1)requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
}

// Drawer tab sliding indicator
function updateSdTabIndicator(){
  const strip=document.getElementById("sd-tab-strip");
  const ind=document.getElementById("sd-tab-indicator");
  if(!strip||!ind)return;
  const active=strip.querySelector(".sd-tab.active");
  if(!active){ind.style.width="0";return;}
  const sr=strip.getBoundingClientRect(),ar=active.getBoundingClientRect();
  ind.style.left=(ar.left-sr.left+strip.scrollLeft)+"px";
  ind.style.width=ar.width+"px";
}

// Enhanced drawer tab switch with cross-fade
const _origSdSwitchTab=sdSwitchTab;
sdSwitchTab=function(tab){
  const body=document.getElementById("sd-body");
  body.style.opacity="0";
  body.style.transform="translateY(6px)";
  body.style.transition="opacity 0.15s, transform 0.15s";
  setTimeout(()=>{
    _origSdSwitchTab(tab);
    updateSdTabIndicator();
    requestAnimationFrame(()=>{body.style.opacity="1";body.style.transform="translateY(0)";});
  },150);
};

// Patch openSkillDetail to update indicator
const _origOpen=openSkillDetail;
openSkillDetail=function(id,tab){
  _origOpen(id,tab);
  requestAnimationFrame(()=>requestAnimationFrame(updateSdTabIndicator));
};

/* ═══════════════ BIBTEX COPY ═══════════════ */
function copyBibTex(){
  const code = document.getElementById('bibtex-code');
  if(!code)return;
  navigator.clipboard.writeText(code.textContent).then(()=>{
    const btn = document.getElementById('bibtex-copy-btn');
    if(btn){btn.textContent='Copied!';setTimeout(()=>{btn.textContent='Copy';},2000);}
  }).catch(()=>{});
}

/* ═══════════════ MAIN ═══════════════ */
async function main(){
  const[{skills},tree,graph,detailsRaw]=await Promise.all([
    loadJson("skills.json"),
    loadJson("tree.json"),
    loadJson("graph.json"),
    tryJson("skill_details.json"),
  ]);
  _sdSkills=skills;
  _sdDetails=detailsRaw||{};

  const search=document.getElementById("search"),fS=document.getElementById("f-status"),fD=document.getElementById("f-domain"),fC=document.getElementById("f-compute"),fSo=document.getElementById("f-sort");
  const rc=graph.nodes.filter(n=>n.type==="resource").length;
  for(const v of optVals(skills,"status"))fS.insertAdjacentHTML("beforeend",`<option value="${esc(v)}">${esc(sLabel(v))}</option>`);
  for(const v of optVals(skills,"domain"))fD.insertAdjacentHTML("beforeend",`<option value="${esc(v)}">${esc(v)}</option>`);
  for(const v of optVals(skills,"compute_requirements"))fC.insertAdjacentHTML("beforeend",`<option value="${esc(v)}">${esc(v)}</option>`);

  renderStats(skills,graph,tree);
  renderDomainGrid(tree,"");
  renderFrontiers(tree);
  requestAnimationFrame(animateCounters);

  const total=(tree.covered_leaf_count||0)+(tree.frontier_leaf_count||0)+(tree.todo_leaf_count||0);
  const pct=total?Math.round((tree.covered_leaf_count||0)/total*100):0;
  document.getElementById("overview-summary").textContent=`${skills.length} skills, ${rc} resources, ${tree.covered_leaf_count||0} covered and ${tree.todo_leaf_count||0} TODO leaves across ${tree.children.length} domains.`;
  document.getElementById("hero-verify").textContent=`${skills.filter(s=>s.status==="sandbox_verified").length} sandbox + ${skills.filter(s=>s.status==="slurm_verified").length} slurm verified`;
  document.getElementById("hero-graph").textContent=`${graph.nodes.filter(n=>n.type==="skill").length} skill + ${rc} resource nodes, ${graph.edges.length} edges`;
  document.getElementById("hero-coverage").textContent=`${pct}% · ${tree.covered_leaf_count||0}/${total} leaves`;

  const update=()=>{
    const q=search.value.trim().toLowerCase(),sd=fD.value;
    const filtered=skills.filter(s=>{const h=[s.name,s.description,s.topic_path.join(" "),s.tags.join(" "),s.domain].join(" ").toLowerCase();return(!q||h.includes(q))&&(!fS.value||s.status===fS.value)&&(!sd||s.domain===sd)&&(!fC.value||s.compute_requirements===fC.value);});
    renderTree(tree,sd);
    renderSkills(sortSkills(filtered,fSo.value));
    renderDomainGrid(tree,sd);
    document.querySelectorAll("[data-domain]").forEach(btn=>{btn.addEventListener("click",()=>{const n=btn.getAttribute("data-domain")||"";fD.value=fD.value===n?"":n;switchTab("catalog");update();});});
  };
  search.addEventListener("input",update);
  fS.addEventListener("change",update);
  fD.addEventListener("change",update);
  fC.addEventListener("change",update);
  fSo.addEventListener("change",update);
  update();

  document.getElementById("sd-close").addEventListener("click",closeSkillDetail);
  document.getElementById("sd-overlay").addEventListener("click",closeSkillDetail);
  document.getElementById("sd-tab-strip").addEventListener("click",e=>{const b=e.target.closest(".sd-tab");if(b)sdSwitchTab(b.dataset.sdTab);});
  document.addEventListener("keydown",e=>{if(e.key==="Escape")closeSkillDetail();});
  window.addEventListener("resize",()=>{if(document.getElementById("sd-drawer").classList.contains("open"))updateSdTabIndicator();});

  if(window._pendingDeepLink){
    const dl=window._pendingDeepLink;
    delete window._pendingDeepLink;
    openSkillDetail(dl.skillId,dl.tab);
  }
}

/* ═══════════════ STARTUP ═══════════════ */
(async()=>{
  await loadAllPanels();
  initRouting();
  main().catch(err=>{
    const el=document.getElementById("overview-summary");
    if(el)el.textContent=err.message;
    ['hero-verify','hero-graph','hero-coverage'].forEach(id=>{const e=document.getElementById(id);if(e)e.textContent="Failed";});
  });
})();
