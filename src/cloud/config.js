module.exports = function (app, express) {
    var parseExpressHttpsRedirect = require('parse-express-https-redirect');
    var parseExpressCookieSession = require('parse-express-cookie-session');

    app.set('views', 'cloud/views');  // Specify the folder to find templates
    app.set('view engine', 'ejs');    // Set the template engine
    app.use(parseExpressHttpsRedirect());
    app.use(express.bodyParser());    // Middleware for reading request body
    app.use(express.cookieParser('SpudderCookie'));
    app.use(express.cookieSession({ secret: 'SpudderCookie' }));
    app.use(parseExpressCookieSession({ cookie: { maxAge: 3600000 } }));
};