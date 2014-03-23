var express = require('express');
var app = express();
var keys = require('cloud/keys.js')();

require('cloud/config.js')(app, express);
require('cloud/middleware.js')(app, keys);
require('cloud/routing/main.js')(app, keys);

app.listen();