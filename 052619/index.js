
const puppeteer = require('puppeteer');
const CREDS = require('./creds');

async function run() {
    const browser = await puppeteer.launch({ 
        headless: false,
        slowMo: 25,
        executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    // await page.setViewport({ width: 1080, height: 1080 })

    await page.goto('https://github.com/login');
    
    // dom element selectors
    const USERNAME_SELECTOR = '#login_field'
    const PASSWORD_SELECTOR = '#password'
    const BUTTON_SELECTOR = '#login > form > div.auth-form-body.mt-3 > input.btn.btn-primary.btn-block'

    await page.click(USERNAME_SELECTOR);
    await page.keyboard.type(CREDS.username);

    await page.click(PASSWORD_SELECTOR);
    await page.keyboard.type(CREDS.password);

    await page.click(BUTTON_SELECTOR);

    await page.waitForNavigation();

    const searchUrl = 'https://github.com/search?q=john&type=Users&utf8=%E2%9C%93';
    // const userToSearch = 'john';
    // const searchUrl = 'https://github.com/search?q=${userToSearch}&type=User&utf8=%E2%9C%93';

    await page.goto(searchUrl);
    await page.waitFor(2*1000);



    // await page.screenshot({ path: 'screenshots/github.png' });
  
    // browser.close();
}

run();