const fs=require('fs'),path=require('path');const {pathToFileURL}=require('url');
(async()=>{
 const root=path.resolve(__dirname,'..');const cache=path.join(require('os').homedir(),'.npm/_npx');
 const cached=fs.existsSync(cache)?fs.readdirSync(cache).map(d=>path.join(cache,d,'node_modules/puppeteer-core')).find(p=>fs.existsSync(p)):null;
 const puppeteer=require(process.env.CAPTION_PUPPETEER_PATH||cached||'puppeteer-core');
 const browser=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{const page=await browser.newPage();await page.evaluateOnNewDocument(()=>{window.__timelines={}});await page.goto(pathToFileURL(path.join(root,'hindi/.local/caption-layers/index.html')).href);
 const audit=await page.evaluate(async()=>{await document.fonts.ready;let errors=[],count=0;
 for(const group of document.querySelectorAll('.caption')){if(group.children.length!==3)errors.push({id:group.id,error:'line count'});
 for(const el of group.children){count++;const r=el.getBoundingClientRect();const range=document.createRange();range.selectNodeContents(el);const text=range.getBoundingClientRect();
 if(r.left<0||r.right>720||r.top<0||r.bottom>1280||text.left<r.left||text.right>r.right)errors.push({id:group.id,text:el.textContent,error:'text fit',box:{x:r.x,y:r.y,width:r.width,height:r.height},textWidth:text.width});
 }}return {count,errors};});
 fs.writeFileSync(path.join(root,'hindi/.local/caption-layout-audit.json'),JSON.stringify(audit,null,2));console.log(JSON.stringify(audit));if(audit.count!==1500||audit.errors.length)process.exitCode=1;
 }finally{await browser.close()}
})();
