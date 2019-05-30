require('dotenv').config();
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page_home = await browser.newPage();
  await page_home.authenticate({username: process.env.USR, password: process.env.PSS});
  // await page.authenticate({username: "kenners", password: "$%RTfgvb0318"});
  await page_home.goto('https://nychhcuat.service-now.com/');
  const page_call = await browser.newPage();
  await page_call.goto('https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do');

// //   await page.screenshot({path: 'example.png'});

// //   await browser.close();
})();

// new call - https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do
// caller field - #sys_display\.new_call\.caller
