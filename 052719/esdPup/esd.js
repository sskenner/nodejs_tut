require('dotenv').config();
const puppeteer = require('puppeteer');
const caller = 'kenners';
const URL_HOME = 'https://nychhcuat.service-now.com/';
const URL_CALL = 'https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do';

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  // const page_home = await browser.newPage();
  // await page_home.authenticate({username: process.env.USR, password: process.env.PSS});
  // await page.authenticate({username: "kenners", password: "$%RTfgvb0318"});
  // await page_home.goto(URL_HOME);
  const page_call = await browser.newPage();
  await page_call.goto(URL_CALL, { waitUntil: 'load' });

  const 

// //   await page.screenshot({path: 'example.png'});

// //   await browser.close();
})();

// new call - https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do
// caller field - #sys_display\.new_call\.caller
