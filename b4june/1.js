// const puppeteer = require('puppeteer');
// const devices = require('puppeteer/DeviceDescriptors');
// const iPhonex = devices['iPhone X'];

// (async () => {
//   const browser = await puppeteer.launch()
//   const page = await browser.newPage()
//   await page.emulate(iPhonex);
//   //start the tracing
//   await page.tracing.start({path: 'trace.json',screenshots:true});
//   await page.goto('https://www.bmw.com')
//   //stop the tracing
//   await page.tracing.stop();
//   await browser.close()
// })()

// const puppeteer = require('puppeteer');

// puppeteer.launch().then(async browser => {

// const page = await browser.newPage();

// //start coverage trace
//   await Promise.all([
//   page.coverage.startJSCoverage(),
//   page.coverage.startCSSCoverage()
// ]);

// await page.goto('https://www.cnn.com');

// //stop coverage trace
// const [jsCoverage, cssCoverage] = await Promise.all([
//   page.coverage.stopJSCoverage(),
//   page.coverage.stopCSSCoverage(),
// ]);

// let totalBytes = 0;
// let usedBytes = 0;
// const coverage = [...jsCoverage, ...cssCoverage];
// for (const entry of coverage) {
//   totalBytes += entry.text.length;
//   for (const range of entry.ranges)
//     usedBytes += range.end - range.start - 1;
// }

// const usedCode = ((usedBytes / totalBytes)* 100).toFixed(2);
// console.log('Code used by only', usedCode, '%');
//   await browser.close();
// });

// var CronJob = require('cron').CronJob;
// var job = new CronJob({
//     // runs every monday
//     cronTime: '0 10***',
//     onTick: function() {
//         const puppeteer = require('puppeteer');

//         (async () => {  
//             const browser = await puppeteer.launch({ 
//                 headless: false,
//                 slowMo: 25,
//                 executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
//                 args: ['--no-sandbox', '--disable-setuid-sandbox']
//             });
        
//             const page = await browser.newPage();
//             await page.setViewport({ width: 1080, height: 1080 })
//             // go to page and wait until loads
//             await page.goto('https://www.aymen-loukil.com/en/contact-aymen/', {waitUntil: 'networkidle2'});
//             await page.waitForSelector('#wpcf7-f671-p311-o1 > form');
//             // type the name
//             await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(2) > label > span > input');
            
//             await page.keyboard.type('PuppeteerBot');
//             // type the email
//             await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(3) > label > span > input');
//             await page.keyboard.type('PuppeteerBot@mail.com');
//             // type the website
//             await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(4) > label > span > input');
//             await page.keyboard.type('PuppeteerBot.com');
//             // type the message
//             await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(5) > label > span > textarea');
//             await page.keyboard.type('PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot!');
//             // await page.click('#wpcf7-f671-p311-o1 > form > p:nth-child(5) > input');
        
//             // await page.screenshot({path: 'amazon-noimg.png'});
//             // await browser.close();
//         })();
//     },
//     start: false,
//     timeZone: 'Europe/London'
// });
// job.start();


// const puppeteer = require('puppeteer');

// (async () => {  
//     const browser = await puppeteer.launch({ 
//         headless: false,
//         slowMo: 25,
//         executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
//         args: ['--no-sandbox', '--disable-setuid-sandbox']
//     });

//     const page = await browser.newPage();
//     await page.setViewport({ width: 1080, height: 1080 })
//     // go to page and wait until loads
//     await page.goto('https://www.aymen-loukil.com/en/contact-aymen/', {waitUntil: 'networkidle2'});
//     await page.waitForSelector('#wpcf7-f671-p311-o1 > form');
//     // type the name
//     await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(2) > label > span > input');
    
//     await page.keyboard.type('PuppeteerBot');
//     // type the email
//     await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(3) > label > span > input');
//     await page.keyboard.type('PuppeteerBot@mail.com');
//     // type the website
//     await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(4) > label > span > input');
//     await page.keyboard.type('PuppeteerBot.com');
//     // type the message
//     await page.focus('#wpcf7-f671-p311-o1 > form > p:nth-child(5) > label > span > textarea');
//     await page.keyboard.type('PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot PuppeteerBot!');
//     // await page.click('#wpcf7-f671-p311-o1 > form > p:nth-child(5) > input');

//     // await page.screenshot({path: 'amazon-noimg.png'});
//     // await browser.close();
// })()

// const puppeteer = require('puppeteer');
// const fs = require('fs');

// (async () => {  
//     const browser = await puppeteer.launch({ 
//         headless: false,
//         executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
//         args: ['--no-sandbox', '--disable-setuid-sandbox']
//     });

//     const page = await browser.newPage();
//     await page.setViewport({ width: 1080, height: 1080 })
//     await page.goto('https://www.youtube.com', {waitUntil: 'networkidle0'});
//     const html = await page.content();

//     fs.writeFile('page.html', html, _ => console.log('HTML saved'));
    
//     // await page.screenshot({path: 'amazon-noimg.png'});
//     // await browser.close();
// })()

// const puppeteer = require('puppeteer');

// (async () => {  
//     const browser = await puppeteer.launch({ 
//         headless: false,
//         executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
//         args: ['--no-sandbox', '--disable-setuid-sandbox']
//     });

//     const page = await browser.newPage();
//     await page.setRequestInterception(true);
//     page.on('request', request => {
//         if(request.resourceType() === 'script')
//             request.abort();
//         else
//             request.continue()
//     });
//     await page.setViewport({ width: 1080, height: 1080 })
//     await page.goto('https://www.youtube.com');
//     // await page.screenshot({path: 'amazon-noimg.png'});
//     // await browser.close();
// })()

// const puppeteer = require('puppeteer');

// (async () => {  
//     const browser = await puppeteer.launch({ 
//         headless: false,
//         executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
//         args: ['--no-sandbox', '--disable-setuid-sandbox']
//     });

//     const page = await browser.newPage();
//     await page.setRequestInterception(true);
//     page.on('request', request => {
//         var match = request.url().replace('http://','').replace('https://','').split(/[/?#]/)[0];
//         console.log(match);
//         if(match === 'images-na.ssl-images-amazon.com')
//             request.abort();
//         else
//             request.continue()
//     });
//     await page.setViewport({ width: 1080, height: 1080 })
//     await page.goto('https://www.amazon.com');
//     await page.screenshot({path: 'amazon-noimg.png'});
//     // await browser.close();
// })()

// const puppeteer = require('puppeteer');

// (async () => {  
//     const browser = await puppeteer.launch({ 
//         headless: false,
//         executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
//         args: ['--no-sandbox', '--disable-setuid-sandbox']
//     });

//     const page = await browser.newPage();
//     await page.setViewport({ width: 1080, height: 1080 })
//     await page.goto('https://www.google.com');
//     // await page.focus('#tsf > div:nth-child(2) > div.A7Yvie.emca > div.zGVn2e > div > div.a4bIc > input');
//     // await page.keyboard.type('i am typing using puppeteer!');
//     // await page.screenshot({ path: 'keyboard.png' })

//     // await browser.close();
// })()
  

// const puppeteer = require('puppeteer');
// // await browser.close();
// puppeteer.launch({}).then(async browser => {
//     const page = await browser.newPage();
//     const version = await page.browser().version();
//     console.log(version);
//     await browser.close();
// });

// const puppeteer = require('puppeteer');

// (async () => {  
//     const browser = await puppeteer.launch({ args: [ '--proxy-server=127.0.0.1:3030' ], headless: false });
//     const page = await browser.newPage();
//     await page.goto('https://amazon.com/');
//     // await browser.close();
// })()

// const puppeteer = require('puppeteer');

// (async () => {  
//     // const browser = await puppeteer.launch({ headless: false });
//     const browser = await puppeteer.launch();
//     const page = await browser.newPage();
//     await page.setExtraHTTPHeaders({Referer:'https://sparktoro.com/'});
//     await page.goto('https://sparktoro.com/trending');
//     await page.waitForSelector('div.title > a');
    
//     const stories = await page.evaluate(() => {
//         const links = Array.from(document.querySelectorAll('div.title > a'))
//         return links.map(link => link.href).slice(0, 10)
//     })

//     console.log(stories);
//     await browser.close();
// })()

// const puppeteer = require('puppeteer');
// const devices = require('puppeteer/DeviceDescriptors');
// const iPhonex = devices['iPhone X'];

// (async () => {  
//     const browser = await puppeteer.launch({ headless: false });
//     const page = await browser.newPage();
//     await page.emulate(iPhonex);
//     await page.goto('https://www.google.fr');
//     await page.focus('#tsf > div:nth-child(2) > div.A7Yvie.emca > div.zGVn2e > div > div.a4bIc > input');
//     await page.keyboard.type('i am typing using puppeteer!');
//     await page.screenshot({ path: 'keyboard.png' })

//     // await browser.close();
// })()

// const puppeteer = require('puppeteer');
// puppeteer.launch({ headless: false }).then(async browser => {
//     const page = await browser.newPage();
//     await page.goto('http://www.google.com/');
//     const title = await page.title()
//     console.log(title)
//     // await browser.close();
// });

// const puppeteer = require('puppeteer');
// const devices = require('puppeteer/DeviceDescriptors');
// const iPhonex = devices['iPhone X'];
// puppeteer.launch({ headless: false }).then(async browser => {
//     const page = await browser.newPage();
//     // await page.setViewport({ width: 1280, height: 800 })
//     await page.emulate(iPhonex);
//     await page.goto('http://www.homedepot.com/');
//     await page.screenshot({ path:'homedepot-iphoneX.png' }); 

//     // await browser.close();
// });

// const puppeteer = require('puppeteer');

// const options = {
//     path: 'amazon-header.png',
//     fullPage: false,
//     clip: {
//         x: 0,
//         y: 0,
//         width: 1280,
//         height: 150
//     }
// }

// puppeteer.launch({ headless: false }).then(async browser => {
//     const page = await browser.newPage();
//     await page.setViewport({ width: 1280, height: 800 })
//     await page.goto('http://www.amazon.com');
//     await page.screenshot(options); 

//     // await browser.close();
// });

// const puppeteer = require('puppeteer');
// puppeteer.launch({ headless: false }).then(async browser => {
//     const page = await browser.newPage();
//     await page.setViewport({ width: 1280, height: 800 })
//     await page.goto('http://www.aymen-loukil.com');
//     await page.screenshot({ path:'myscreenshot.png', fullPage: true });
    
//     // await browser.close();
// });