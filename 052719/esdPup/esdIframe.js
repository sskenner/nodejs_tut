require('dotenv').config();
const puppeteer = require('puppeteer');
const caller = 'kenners';
const URL_HOME = 'https://nychhcuat.service-now.com/';
const URL_CALL = 'https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do';

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    // executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
    // args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page_home = await browser.newPage();
  await page_home.authenticate({username: process.env.USR, password: process.env.PSS});
  await page.authenticate({username: "kenners", password: "$%RTfgvb0318"});
  await page_home.goto(URL_HOME);
  // const page = await browser.newPage();
  
  // const frameName = 'gsft_main'

  // await page.goto(URL_CALL, { 
  //   timeout: 25000,
  //   waitUntil: 'networkidle2' 
  // });
  // await page.waitForSelector(`iframe[name=${frameName}]`);
  
  // console.info(`found frame iframe[name=${frameName}]`);

  // const frames = page.frames();

  // console.info('available frames', frames.map(frame => frame.name()));

  // if (frames.find(frame => frame.name().includes(frameName))) {
  //   console.info(`frame ${frameName} in DOM and frames list`)
  // } else {
  //   console.error(`frame ${frameName} in DOM but not frames list`)
  // }
  
  // const SELECTOR_CALLER = '#sys_display\.new_call\.caller';
  // const SELECTOR_CALLER = '//*[@id="element.new_call.caller"]/div[2]/div[2]';
  

  // await page_call.waitForSelector(SELECTOR_CALLER);
  // await page_call.waitForXPath(SELECTOR_CALLER);
  // await page_call.click(SELECTOR_CALLER);
  // await page_call.keyboard.type(caller);

  // const SELECTOR_PW_RESET = '#templates-list-container > a:nth-child(4)'
  // await page.waitForSelector(SELECTOR_PW_RESET);
  // await page.click(SELECTOR_PW_RESET);

  // await page_call.click(SELECTOR_PW_RESET);

  // const SELECTOR_SUBMIT_BUTTON = '#sysverb_insert_bottom'

  // await page_call.click(SELECTOR_SUBMIT_BUTTON);

// //   await page.screenshot({path: 'example.png'});

// //   await browser.close();
})();

// new call - https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do
// caller field - #sys_display\.new_call\.caller
