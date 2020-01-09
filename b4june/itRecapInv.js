// Replace POST with PUT to send a PUT request instead
var request = require('request');
// var url = 'http://httpbin.org/ip';
var url = 'https://imagetyperz.xyz/automation/recaptcha-invisible.html';

// request(
//   {
//     method: 'POST',
//     url: 'http://api.scraperapi.com/?api_key=85923fa80e2d251ae805c5bd5fa8115f&url=' + url,
//     // url: 'http://api.scraperapi.com/?api_key=YOURAPIKEY&url=' + url,
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({foo: 'bar'}),
//   },
//   function(error, response, body) {
//     console.log(body);
//   }
// );

//for form data
request(
  {
    method: 'POST',
    url: 'http://api.scraperapi.com/?api_key=85923fa80e2d251ae805c5bd5fa8115f&url=' + url,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    // form: {foo: 'bar'},
    form: {
        username: 'username',
        password: 'password'
    },
  },
  function(error, response, body) {
    console.log(body);
  }
);