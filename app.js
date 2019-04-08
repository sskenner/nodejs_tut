const http = require('http');
const server = http.createServer((req,res)=>{
    if(req.url === '/'){
        res.write('sup');
        res.end();
    }
    else {
        res.write('some other');
        res.end();
    }
});

server.listen('3000');