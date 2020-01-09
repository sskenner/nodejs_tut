require('dotenv').config();
const puppeteer = require('puppeteer');
const caller = 'kenners';
const URL_HOME = 'https://nychhcuat.service-now.com/';
const URL_CALL = 'https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do';

(async () => {
<<<<<<< HEAD
  const browser = await puppeteer.launch({ headless: false });
  const page_home = await browser.newPage();
  await page_home.setViewport({ width: 1280, height: 800 });
  await page_home.authenticate({username: process.env.USR, password: process.env.PSS});
  // await page.authenticate({username: "kenners", password: "$%RTfgvb0318"});
  await page_home.goto('https://nychhcuat.service-now.com/');
  const page_call = await browser.newPage();
  await page_call.setViewport({ width: 1280, height: 800 });
  await page_call.goto('https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do', { waitUntil: 'networkidle2' });
=======
  const browser = await puppeteer.launch({
    headless: false,
    // executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
    // args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  // const page_home = await browser.newPage();
  const page = await browser.newPage();
  // await page_home.authenticate({username: process.env.USR, password: process.env.PSS});
  await page.authenticate({username: process.env.USR, password: process.env.PSS});
  // await page.authenticate({username: "kenners", password: "$%RTfgvb0318"});
  // await page_home.goto(URL_HOME);
  
  const frameName = 'gsft_main'

  await page.goto(URL_CALL, { 
    timeout: 25000,
    waitUntil: 'networkidle2' 
  });
  await page.waitForSelector(`iframe[name=${frameName}]`);

  // /new_call.do?sys_id=-1&sysparm_stack=new_call_list.do
  
  console.info(`found frame iframe[name=${frameName}]`);

  const frames = page.frames();

  console.info('available frames', frames.map(frame => frame.name()));

  if (frames.find(frame => frame.name().includes(frameName))) {
    console.info(`frame ${frameName} in DOM and frames list`)
  } else {
    console.error(`frame ${frameName} in DOM but not frames list`)
  }

  const frame = await page.frames().find(f => f.name() === frameName);
  const button = await frame.$('#sys_display.new_call.caller');
  button.click();
  
  // #sys_display\.new_call\.caller
  //*[@id="sys_display.new_call.caller"]


  // <input id="sys_display.new_call.caller" name="sys_display.new_call.caller" aria-labelledby="label.new_call.caller" type="search" autocomplete="off" autocorrect="off" value="" ac_columns="user_name;email" ac_order_by="name" data-type="ac_reference_input" data-completer="AJAXTableCompleter" data-dependent="company" data-dependent-value="" data-ref-qual="" data-ref="new_call.caller" data-ref-key="null" data-ref-dynamic="false" data-name="caller" data-table="sys_user" class="form-control element_reference_input" style="; " spellcheck="false" onfocus="if (!this.ac) addLoadEvent(function() {var e = gel('sys_display.new_call.caller'); if (!e.ac) new AJAXTableCompleter(gel('sys_display.new_call.caller'), 'new_call.caller', 'company', ''); e.ac.onFocus();})" aria-required="false" role="combobox" aria-autocomplete="list" aria-owns="AC.new_call.caller" aria-expanded="false" title="" aria-invalid="false" data-original-title=""></input>

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
>>>>>>> cf80ed22050b6cb74d365df680c0924f9e0dfe6a

// //   await page.screenshot({path: 'example.png'});

// //   await browser.close();
})();

// new call - https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do
// caller field - #sys_display\.new_call\.caller
