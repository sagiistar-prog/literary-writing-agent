const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname,'..');
const output = path.join(root,'output','browser-check');
fs.mkdirSync(output,{recursive:true});
const fixture = name => JSON.parse(fs.readFileSync(path.join(root,'examples',name),'utf8'));
const example = fixture('revision-input.json');

(async()=>{
 const server = spawn(process.env.PYTHON || 'python',['-u','scripts/serve_app.py','--port','8887'],{cwd:root,stdio:['ignore','pipe','pipe'],windowsHide:true});
 let browser;
 try {
  const url = await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(new Error('Server did not start')),15000);
   server.once('error',reject); server.once('exit',()=>reject(new Error('Server exited before readiness')));
   server.stdout.on('data',data=>{const match=String(data).match(/http:\/\/[^\s]+/);if(match){clearTimeout(timer);resolve(match[0]);}});
  });
  browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL ? {channel:process.env.BROWSER_CHANNEL}: {})});
  const reports=[];
  for (const width of [1440,390]) {
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce',acceptDownloads:true});
   await context.addInitScript({path:require.resolve('axe-core/axe.min.js')});
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   page.on('dialog',dialog=>dialog.accept());
   await page.goto(url);
   await page.getByRole('button',{name:'试读修订',exact:true}).click();
   await page.locator('#review-count').waitFor();
   assert.equal(await page.locator('#scene-input').inputValue(),example.scene);
   assert.equal(await page.locator('.review-preview .manuscript-text').textContent(),example.scene);
   async function choose(id,choice) {
    const response=page.waitForResponse(r=>r.url().endsWith('/api/session')&&r.request().method()==='POST');
    await page.locator(`#edit-${id} [data-choice="${choice}"]`).click();await response;
    await page.waitForFunction(()=>document.querySelector('#generate').disabled===false);
   }
   await choose('E1','accepted');await choose('E2','rejected');
   const selected=await page.locator('.review-preview .manuscript-text').textContent();
   assert(selected.includes('折痕已经发白。'));assert(selected.includes('阿禾低下头'));assert(selected.includes('她很紧张，她不知道要不要走。'));
   await page.getByRole('button',{name:'撤销上一步',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('#generate').disabled===false);
   assert((await page.locator('#edit-E2 h4').textContent()).includes('待审阅'));
   const downloadEvent=page.waitForEvent('download');await page.locator('#download-manuscript').click();
   const download=await downloadEvent;assert.equal(fs.readFileSync(await download.path(),'utf8'),selected);
   if (!await page.locator('#save-project').isVisible()) await page.locator('.project-panel summary').click();
   await page.locator('#save-project').click();await page.reload();
   if (!await page.locator('#project-list').isVisible()) await page.locator('.project-panel summary').click();
   const saved=await page.locator('#project-list option').nth(1).getAttribute('value');await page.locator('#project-list').selectOption(saved);
   assert.equal(await page.locator('.review-preview .manuscript-text').textContent(),selected);
   await page.locator('#scene-input').fill(example.scene+'\n新的结尾。');
   assert(await page.locator('#download-manuscript').isDisabled());
   assert(await page.locator('#export-request').isDisabled());
   const badResponse=page.waitForResponse(r=>r.url().endsWith('/api/session'));
   await page.locator('#import-proposal').setInputFiles(path.join(root,'examples/revision-proposal.json'));
   assert.equal((await badResponse).status(),400);await page.waitForFunction(()=>!document.querySelector('#generate').disabled);
   assert((await page.locator('#scene-input').inputValue()).endsWith('新的结尾。'));
   await page.locator('#scene-input').fill(example.scene);
   assert.equal(await page.locator('.review-preview .manuscript-text').textContent(),selected);
   await page.locator('#import-proposal').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{broken')});
   await page.waitForFunction(()=>document.querySelector('#status-line').textContent.includes('有效 JSON'));
   assert.equal(await page.locator('.review-preview .manuscript-text').textContent(),selected);
   await choose('E2','rejected');
   const axe=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
   const violations=axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}));
   await page.evaluate(()=>{document.querySelector('#output').scrollTop=0;window.scrollTo(0,0);});await page.screenshot({path:path.join(output,`desktop-${width}.png`),fullPage:true});
   await page.locator('#output').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,`review-${width}.png`)});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false);
   // A hostile model output remains text; import and output do not execute markup.
   const hostile=fixture('revision-proposal.json');hostile.edits[0].after='<img src=x onerror="window.pwned=true">';
   await page.locator('#import-proposal').setInputFiles({name:'hostile.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(hostile))});
   await page.waitForFunction(()=>document.querySelector('#edit-E1 .edit-comparison')?.textContent.includes('onerror'));
   await choose('E1','accepted');assert.equal(await page.evaluate(()=>window.pwned),undefined);
   assert.equal(await page.locator('#output img').count(),0);
   // Authored outline import and request export for a different task.
   await page.locator('[data-task="outline"]').click();
   const outline=fixture('outline-input.json');await page.locator('#brief-input').fill(outline.brief);await page.locator('#notes-input').fill(outline.instructions);
   await page.locator('#import-proposal').setInputFiles(path.join(root,'examples/outline-proposal.json'));
   await page.waitForFunction(()=>document.querySelector('#output').textContent.includes('最后一栏'));
   assert(await page.locator('#download-manuscript').isDisabled());
   const exported=page.waitForEvent('download');await page.locator('#export-request').click();
   const request=JSON.parse(fs.readFileSync(await (await exported).path(),'utf8'));
   assert.equal(request.input.brief,outline.brief);assert.equal(request.input.instructions,outline.instructions);
   reports.push({width,errors,violations,selectionAndUndo:true,downloadMatches:true,saveReload:true,staleImportRejected:true,failedImportPreservesDraft:true,hostileTextSafe:true,outlineImport:true,requestMatches:true});
   await context.close();
  }
  fs.writeFileSync(path.join(output,'acceptance.json'),JSON.stringify(reports,null,2));
  console.log(JSON.stringify(reports,null,2));
  assert(reports.every(r=>r.errors.length===0&&r.violations.length===0));
 } finally {if(browser)await browser.close();server.kill();}
})().catch(error=>{console.error(error);process.exitCode=1;});
