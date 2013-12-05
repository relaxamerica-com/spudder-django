var express = require('express');
var app = express();
var keys = require('cloud/keys.js')('spudmart');

require('cloud/config.js')(app, express);
require('cloud/middleware.js')(app, keys);
require('cloud/modules.js')(app, keys);

app.listen();
