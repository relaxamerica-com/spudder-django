
// These two lines are required to initialize Express in Cloud Code.
var express = require('express');
<<<<<<< HEAD
=======
var parseExpressHttpsRedirect = require('parse-express-https-redirect');
var parseExpressCookieSession = require('parse-express-cookie-session');
>>>>>>> parse
var app = express();

// Global app configuration section
app.set('views', 'cloud/views');  // Specify the folder to find templates
app.set('view engine', 'ejs');    // Set the template engine
<<<<<<< HEAD
app.use(express.bodyParser());    // Middleware for reading request body
=======
app.use(parseExpressHttpsRedirect());
app.use(express.bodyParser());    // Middleware for reading request body
app.use(express.cookieParser('kgebertCookie'));
app.use(parseExpressCookieSession({ cookie: { maxAge: 3600000 } }));
>>>>>>> parse

app.use(function(req, res, next){
	Parse.initialize('RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR', 'zDk1PxddnEJwnLKxrnypGuM4pIq9Z7adAi4rprgH'); 
	var currentUser = Parse.User.current();
	if (currentUser) {
<<<<<<< HEAD
		req.user = currentUser;
	}
	next();
=======
		currentUser.fetch().then(function(user) {
			res.locals.user = currentUser;
			next();
		});
	} else {
		res.locals.user = null;
		next();
	}
>>>>>>> parse
});

// modules
var accounts = require('cloud/accounts/actions');

// This is an example of hooking up a request handler with a specific request
// path and HTTP verb using the Express routing API.
app.get('/', function(req, res) {
	res.render('home/home');
});

app.post('/accounts/login', accounts.login);
<<<<<<< HEAD
=======
app.get('/accounts/logout', accounts.logout);
>>>>>>> parse

// // Example reading from the request query string of an HTTP get request.
// app.get('/test', function(req, res) {
//   // GET http://example.parseapp.com/test?message=hello
//   res.send(req.query.message);
// });

// // Example reading from the request body of an HTTP post request.
// app.post('/test', function(req, res) {
//   // POST http://example.parseapp.com/test (with request body "message=hello")
//   res.send(req.body.message);
// });

// Attach the Express app to Cloud Code.
app.listen();
