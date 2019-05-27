const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto('https://nychhcuat.service-now.com/');

//   await page.screenshot({path: 'example.png'});

//   await browser.close();
})();

// new call - https://nychhcuat.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do
// caller field - #sys_display\.new_call\.caller
