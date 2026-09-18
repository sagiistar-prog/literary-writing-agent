const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'output', 'browser-check');
const png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a6ioAAAAASUVORK5CYII=';
const original = JSON.parse(fs.readFileSync(path.join(root, 'examples/revision-input.json'), 'utf8'));
fs.mkdirSync(output, {recursive:true});

(async () => {
  const server = spawn(process.env.PYTHON || 'python', ['-u', 'scripts/serve_app.py', '--port', '8887'],
    {cwd:root, stdio:['ignore','pipe','pipe'], windowsHide:true});
  let browser;
  try {
    const url = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Server did not start')), 15000);
      server.once('error', reject); server.once('exit', () => reject(new Error('Server exited')));
      server.stdout.on('data', data => { const match = String(data).match(/http:\/\/[^\s]+/); if(match) {clearTimeout(timer);resolve(match[0]);} });
    });
    browser = await chromium.launch({headless:true, ...(process.env.BROWSER_CHANNEL ? {channel:process.env.BROWSER_CHANNEL} : {})});
    const reports = [];
    for (const width of [1440, 390]) {
      const context = await browser.newContext({viewport:{width,height:1000}, reducedMotion:'reduce', acceptDownloads:true});
      await context.addInitScript({path:require.resolve('axe-core/axe.min.js')});
      const page = await context.newPage(), errors = [];
      page.on('pageerror', e => errors.push(e.message));
      let acceptReplacement = true;
      page.on('dialog', dialog => acceptReplacement ? dialog.accept() : dialog.dismiss());
      const ready = () => page.waitForFunction(() => !document.querySelector('#generate').disabled);
      const library = async () => {if(!await page.locator('#save-project').isVisible()) await page.locator('.project-panel summary').click();};
      const choose = async (id, choice) => {
        const response = page.waitForResponse(r => r.url().endsWith('/api/session'));
        await page.locator(`#edit-${id} [data-choice="${choice}"]`).click(); await response; await ready();
      };
      await page.goto(url);
      await page.locator('#try-review').click(); await page.locator('#review-count').waitFor(); await ready();
      await choose('E1','accepted'); await choose('E2','rejected');
      const selected = await page.locator('.review-preview .manuscript-text').textContent();
      await library();
      await page.locator('#image-input').setInputFiles({name:'原创色块.png',mimeType:'image/png',buffer:Buffer.from(png,'base64')});
      await page.locator('#image-gallery img').waitFor({state:'attached'});
      const downloaded = page.waitForEvent('download'); await page.locator('#export-project').click();
      const bundle = JSON.parse(fs.readFileSync(await (await downloaded).path(), 'utf8'));
      assert.equal(bundle.schema_version,'1.0');
      await context.close();

      // Restore in an empty browser profile, not the exporter's localStorage.
      const fresh = await browser.newContext({viewport:{width,height:1000}, reducedMotion:'reduce',acceptDownloads:true});
      await fresh.addInitScript({path:require.resolve('axe-core/axe.min.js')});
      const recovered = await fresh.newPage();
      recovered.on('pageerror',e=>errors.push(e.message));
      recovered.on('dialog',d=>acceptReplacement ? d.accept() : d.dismiss());
      await recovered.goto(url);
      const waitReady = () => recovered.waitForFunction(() => !document.querySelector('#generate').disabled);
      const load = async data => {
        const response = recovered.waitForResponse(r=>r.url().endsWith('/api/project/validate'));
        await recovered.locator('#import-project').setInputFiles({name:'project.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(data))});
        const result=await response;await waitReady();return result.status();
      };
      const draft = () => recovered.locator('#scene-input').inputValue();
      const preview = () => recovered.locator('.review-preview .manuscript-text').textContent();
      assert.equal(await load(bundle),200);
      assert.equal(await draft(),original.scene);assert.equal(await preview(),selected);
      assert((await recovered.locator('#edit-E2 h4').textContent()).includes('已保留原文'));
      assert.equal(await recovered.locator('#image-gallery img').getAttribute('src'),`data:image/png;base64,${png}`);
      await recovered.locator('.illustration-board summary').click();
      assert(await recovered.locator('#image-gallery img').isVisible());
      assert(await recovered.locator('#image-gallery img').evaluate(img=>img.complete && img.naturalWidth===1));
      await recovered.locator('.illustration-board summary').click();
      assert((await recovered.locator('.illustration-board').boundingBox()).height < 100);
      await recovered.getByRole('button',{name:'撤销上一步',exact:true}).click();await waitReady();
      assert((await recovered.locator('#edit-E2 h4').textContent()).includes('待审阅'));
      await recovered.getByRole('button',{name:'撤销上一步',exact:true}).click();await waitReady();
      assert.equal(await preview(),original.scene);
      assert.equal(await load(bundle),200);
      const savedDownload=recovered.waitForEvent('download');await recovered.locator('#download-manuscript').click();
      assert.equal(fs.readFileSync(await(await savedDownload).path(),'utf8'),selected);
      if(!await recovered.locator('#save-project').isVisible()) await recovered.locator('.project-panel summary').click();
      await recovered.locator('#save-project').click();
      const firstId=await recovered.locator('#project-list').inputValue();
      await load({...bundle,id:firstId});await recovered.locator('#save-project').click();
      assert.notEqual(await recovered.locator('#project-list').inputValue(),firstId);
      assert.equal(await recovered.locator('#project-list option').count(),3);

      // Cached outputs cannot replace the author's selected manuscript.
      const forged=structuredClone(bundle);
      forged.reviews.revision.session.revised_scene='伪造整稿';forged.reviews.revision.session.markdown='伪造整稿';
      assert.equal(await load(forged),200);assert.equal(await preview(),selected);
      const invalid=structuredClone(bundle);invalid.reviews.revision.history.push({E999:'accepted'});
      assert.equal(await load(invalid),400);assert.equal(await preview(),selected);
      await recovered.locator('#import-project').setInputFiles({name:'broken.json',mimeType:'application/json',buffer:Buffer.from('{broken')});
      await recovered.waitForFunction(()=>document.querySelector('#status-line').textContent.includes('有效 JSON'));
      assert.equal(await preview(),selected);
      await recovered.locator('#scene-input').fill(original.scene+'\n自己的新结尾。');
      const newDraft=await draft();
      acceptReplacement=false;assert.equal(await load(bundle),200);assert.equal(await draft(),newDraft);acceptReplacement=true;
      await recovered.route('**/api/project/validate',route=>route.abort());
      await recovered.locator('#import-project').setInputFiles({name:'project.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(bundle))});
      await recovered.waitForFunction(()=>document.querySelector('#status-line').classList.contains('is-error'));
      await waitReady();assert.equal(await draft(),newDraft);await recovered.unroute('**/api/project/validate');
      assert.equal(await load({...bundle,scene:newDraft}),200);assert.equal(await draft(),newDraft);
      assert(await recovered.locator('#download-manuscript').isDisabled());
      assert(await recovered.locator('#export-request').isDisabled());
      await recovered.locator('#scene-input').fill(original.scene);assert.equal(await preview(),selected);

      // Inputs remain locked while the validated replacement is in flight.
      let release;
      const gate=new Promise(resolve=>release=resolve);
      await recovered.route('**/api/project/validate',async route=>{await gate;await route.continue();});
      await recovered.locator('#import-project').setInputFiles({name:'project.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(bundle))});
      await recovered.waitForFunction(()=>document.querySelector('#generate').disabled);
      assert(await recovered.locator('#scene-input').isDisabled());assert(await recovered.locator('#import-project-button').isDisabled());
      release();await waitReady();await recovered.unroute('**/api/project/validate');
      const axe=await recovered.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
      const violations=axe.violations.map(v=>({id:v.id,impact:v.impact}));
      assert.equal(await recovered.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false);
      assert.equal(await recovered.locator('body').textContent().then(text=>text.includes('·')),false);
      await recovered.evaluate(()=>window.scrollTo(0,0));
      await recovered.screenshot({path:path.join(output,`project-${width}.png`),fullPage:true});
      reports.push({width,errors,violations,crossBrowserRecovery:true,selectionAndUndo:true,downloadMatches:true,
        imageRestored:true,saveAsCopy:true,cacheRecomputed:true,invalidImportPreservesDraft:true,
        cancelPreservesDraft:true,networkFailurePreservesDraft:true,staleRecordProtected:true,busyLocked:true});
      await fresh.close();
    }
    fs.writeFileSync(path.join(output,'project-acceptance.json'),JSON.stringify(reports,null,2));
    console.log(JSON.stringify(reports,null,2));
    assert(reports.every(r=>r.errors.length===0&&r.violations.length===0));
  } finally {if(browser)await browser.close();server.kill();}
})().catch(error=>{console.error(error);process.exitCode=1;});
