// Measure all caption lines in Chromium with the actual Hindi/Bengali fonts.
const fs=require('fs'),path=require('path');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..');
(async()=>{
 const cache=path.join(require('os').homedir(),'.npm/_npx');
 const cached=fs.existsSync(cache)?fs.readdirSync(cache).map(d=>path.join(cache,d,'node_modules/puppeteer-core')).find(p=>fs.existsSync(p)):null;
 const puppeteer=require(process.env.CAPTION_PUPPETEER_PATH||cached||'puppeteer-core');
 const browser=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{
  const page=await browser.newPage();
  await page.goto(pathToFileURL(path.join(root,'hindi/caption-project/index.html')).href);
  const lessons=JSON.parse(fs.readFileSync(path.join(root,'hindi/videos.json'),'utf8'));
  const rows=await page.evaluate(async lessons=>{
   await document.fonts.ready;await Promise.all([document.fonts.load('700 39px Hindi'),document.fonts.load('600 34px Bangla')]);
   const context=document.createElement('canvas').getContext('2d');const rows=[];
   for(const l of lessons)for(const [sentence,s] of l.sentences.entries())for(const [key,font,size,weight] of [['hindi','Hindi',39,700],['bangla_pronunciation','Bangla',34,600],['bangla_meaning','Bangla',34,600]]){
    context.font=`${weight} ${size}px ${font}`;const width=context.measureText(s[key]).width;
    const fitted=Math.min(size,Math.floor(size*566/(width+4)*10)/10);
    rows.push({number:l.video_number,sentence:sentence+1,key,text:s[key],width,font_size:fitted});
   }return rows;
  },lessons);
  fs.writeFileSync(path.join(root,'hindi/.local/caption-text-fit.json'),JSON.stringify(rows,null,2));
  console.log('Measured',rows.length,'lines; smallest sizes:');console.log(rows.sort((a,b)=>a.font_size-b.font_size).slice(0,12));
 }finally{await browser.close()}
})();
