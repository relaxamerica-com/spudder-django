
// These two lines are required to initialize Express in Cloud Code.
var express = require('express');
var parseExpressHttpsRedirect = require('parse-express-https-redirect');
var parseExpressCookieSession = require('parse-express-cookie-session');
var app = express();

// Global app configuration section
 
app.set('views', 'cloud/views');  // Specify the folder to find templates
app.set('view engine', 'ejs');    // Set the template engine
app.use(parseExpressHttpsRedirect());
app.use(express.bodyParser());    // Middleware for reading request body
app.use(express.cookieParser('SpudderLoginCookie'));
app.use(parseExpressCookieSession({ cookie: { maxAge: 3600000 } }));

var keys = require('cloud/keys.js')('karol');

// middleware allowing to use user in template

app.use(function(req, res, next){
	Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());
	var currentUser = Parse.User.current();
	if (currentUser) {
		currentUser.fetch().then(function(user) {
			res.locals.user = currentUser;
			next();
		});
	} else {
		res.locals.user = null;
		next();
	}
	
});

// modules 

var home = require('cloud/home/actions');
app.get('/', home.home);

var accounts = require('cloud/accounts/actions')(keys);
app.post('/accounts/login', accounts.login);
app.post('/accounts/register', accounts.register);
app.get('/accounts/logout', accounts.logout);

var tournament = require('cloud/tournament/actions');
app.get('/tournament', tournament.view);

var dashboard = require('cloud/dashboard/actions');
app.get('/dashboard', dashboard.spuds);
app.get('/dashboard/general', dashboard.general);

app.listen();
