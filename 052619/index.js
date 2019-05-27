// https://medium.com/@e_mad_ehsan/getting-started-with-puppeteer-and-chrome-headless-for-web-scrapping-6bf5979dee3e

const mongoose = require('mongoose');
const User = require('./models/user');
const puppeteer = require('puppeteer');
const CREDS = require('./creds');

async function run() {
    const browser = await puppeteer.launch({ 
        headless: false,
        slowMo: 25,
        // executablePath: 'C:/Users/kenners/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    // await page.setViewport({ width: 1080, height: 1080 })

    await page.goto('https://github.com/login');
    
    // // dom element selectors
    // const USERNAME_SELECTOR = '#login_field'
    // const PASSWORD_SELECTOR = '#password'
    // const BUTTON_SELECTOR = '#login > form > div.auth-form-body.mt-3 > input.btn.btn-primary.btn-block'

    // await page.click(USERNAME_SELECTOR);
    // await page.keyboard.type(CREDS.username);

    // await page.click(PASSWORD_SELECTOR);
    // await page.keyboard.type(CREDS.password);

    // await page.click(BUTTON_SELECTOR);
    // await page.waitForNavigation();

    // const searchUrl = 'https://github.com/search?q=john&type=Users&utf8=%E2%9C%93';
    const userToSearch = 'john';
    const searchUrl = `https://github.com/search?q=${userToSearch}&type=Users&utf8=%E2%9C%93`;

    await page.goto(searchUrl, {waitUntil: 'load'});
    // await page.goto('https://github.com/search?q=john&type=Users&utf8=%E2%9C%93');
    
    await page.waitFor(2 * 1000);

    const LIST_USERNAME_SELECTOR = '#user_search_results > div.user-list > div:nth-child(INDEX) > div.d-flex.flex-auto > div > a'
    const LIST_NAME_SELECTOR = '#user_search_results > div.user-list > div:nth-child(INDEX) > div.d-flex.flex-auto > div > div'
    
    const LENGTH_SELECTOR_CLASS = 'user-list-item';

    const numPages = await getNumPages(page);
    
    console.log('Numpages: ', numPages);

    for (let h = 1; h <= numPages; h++) {

        let pageUrl = searchUrl + '&p=' + h;

        await page.goto(pageUrl);

        let listLength = await page.evaluate((sel) => {
            return document.getElementsByClassName(sel).length;
        }, LENGTH_SELECTOR_CLASS);
    
        for (let i =1; i <= listLength; i++) {
            // change index to the next child
            let usernameSelector = LIST_USERNAME_SELECTOR.replace("INDEX", i);
            let nameSelector = LIST_NAME_SELECTOR.replace("INDEX", i);
    
            let username = await page.evaluate((sel) => {
                return document.querySelector(sel).getAttribute('href').replace('/', '');
            }, usernameSelector);
    
            let name = await page.evaluate((sel) => {
                let element = document.querySelector(sel);
                return element? element.innerHTML: null;
            }, nameSelector);
    
            // if any users do not have name visible
            if (!name)
                continue;
            // console.log(i);
            console.log(username, ' ->', name);
    
            //x.TODO: save this user
            upsertUser({
                username: username,
                name: name,
                dateCrawled: new Date()
            });

        }
    }
    // await page.screenshot({ path: 'screenshots/github.png' });
  
    // browser.close();
}

async function getNumPages(page) {
    const NUM_USER_SELECTOR = '#js-pjax-container > div > div.col-12.col-md-9.float-left.px-2.pt-3.pt-md-0.codesearch-results > div > div.d-flex.flex-column.flex-md-row.flex-justify-between.border-bottom.pb-3.position-relative > h3'
    let inner = await page.evaluate((sel) => {
        let html = document.querySelector(sel).innerHTML;

        // format is : "##,### users"
        return html.replace(',','').replace('users', '').trim();
    }, NUM_USER_SELECTOR);

    let numUsers = parseInt(inner);

    console.log('numUsers: ', numUsers);

    // bc GH shows 10 results per page
    let numPages = Math.ceil(numUsers / 10);
    return numPages
}

function upsertUser(userObj) {
    // const DB_URL = 'mongodb://localhost:27017/thal';
    const DB_URL = 'mongodb://localhost/thal';

    if(mongoose.connection.readyState == 0) { mongoose.connect(DB_URL); }

    // if this name exists, update entry, do not insert
    let conditions = { name: userObj.name };
    let options = { upsert: true, new: true, setDefaultsOnInsert: true };

    User.findOneAndUpdate(conditions, userObj, options, (err, result) => {
        if (err) throw err;
    });

}

run();

