const fs = require('fs');
// // create a file
// fs.writeFile('example.txt',"this is an ex.",(err)=>{
//     if(err)
//         console.log(err);
//     else{
//         console.log('file created');
//         fs.readFile('example.txt','utf8',(err,file)=>{
//             if(err)
//                 console.log(err);
//             else
//                 console.log(file);
//         })
//     }
        
// });

// fs.rename('example.txt','example2.txt',(err)=>{
//     if(err)
//         console.log(err);
//     else
//         console.log('renamed file');
// });

// fs.appendFile('example2.txt','.. appended some data',(err)=>{
//     if(err)
//         console.log(err);
//     else
//         console.log('appended data');
// });

fs.unlink('example2.txt',(err)=>{
    if(err)
        console.log(err);
    else
        console.log('deleted file');
});