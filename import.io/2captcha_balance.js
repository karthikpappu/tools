const https = require('https')

function getBalance(key) {
  var options = {
    hostname: '2captcha.com',
    port: 443,
    path: '/res.php?key='+key+'&action=getbalance',
    method: 'GET'
  }

  var req = https.request(options, function(res) {
    console.log("\nstatus code: ", res.statusCode);
    res.on('data', (d) => {
      console.log(d);
      process.stdout.write(d);
    })
  });

  req.on('error', (e) => {
    console.error(e);
  });
  req.end();

};

getBalance('eeb1ed6ba9bffdf874ccf3e9373e26b3');
