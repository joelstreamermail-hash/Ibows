const express = require('express');
const app = express();

const session = require('express-session');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy; 

// --- Bot spezifische Requires ---
const { Client, GatewayIntentBits } = require('discord.js');
// Erfordert dotenv, da der Token verwendet wird
const dotenv = require('dotenv');
const ejs = require('ejs');
const path = require('path');

dotenv.config();

// --- Globale Variablen und Konfiguration ---
const PORT = process.env.PORT || 3000;

// EJS als View Engine setzen und statische Dateien bereitstellen
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
// Standardmäßig gibt es keinen 'public' Ordner in Ihrem Projekt, 
// daher wurde die Zeile für statische Dateien entfernt, um Fehler zu vermeiden.
// app.use(express.static(path.join(__dirname, 'public'))); 

// --- Passport/Session Konfiguration ---
// Passport muss Sessions verwenden
app.use(session({
    secret: process.env.SESSION_SECRET || 'EinSehrSicheresGeheimnis', 
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

// Ihre Passport Strategie Konfiguration MUSS hier stehen
/* passport.use(new DiscordStrategy({
    clientID: process.env.DISCORD_CLIENT_ID,
    clientSecret: process.env.DISCORD_CLIENT_SECRET,
    callbackURL: process.env.DISCORD_CALLBACK_URL || 'http://localhost:3000/auth/discord/callback',
    scope: ['identify', 'guilds'] // Gewünschte Scopes
}, 
function(accessToken, refreshToken, profile, done) {
    // Hier wird der Benutzer in der Datenbank gesucht/erstellt
    return done(null, profile);
}));

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));
*/

// Funktion zur Überprüfung, ob der Benutzer eingeloggt ist
function ensureAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
        return next();
    }
    res.redirect('/auth/discord'); 
}

// --- Discord Bot Logik ---
const client = new Client({ 
    // Fügen Sie hier die notwendigen Intents hinzu
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] 
});

client.once('ready', () => {
    console.log(`🤖 Discord Bot ist als ${client.user.tag} online und bereit!`);
});

// client.on('messageCreate', (message) => { /* ... Bot-Commands hier ... */ });

// --- Hauptrouten ---

// 1. Start-Route für Discord-Login (BEHEBT: Cannot GET /auth/discord)
app.get('/auth/discord', passport.authenticate('discord'));

// 2. Callback-Route nach erfolgreichem Login
app.get('/auth/discord/callback', passport.authenticate('discord', {
    failureRedirect: '/' // Fehlerfall
}), (req, res) => {
    // Erfolgreicher Login. Weiterleitung zum Dashboard/den Einstellungen
    res.redirect('/team/settings'); 
});


// Beispiel-Homepage
app.get('/', (req, res) => {
    res.render('index_home', { 
        user: req.user,
        isAuthenticated: req.isAuthenticated()
    });
});

// Die korrigierte und stabilisierte Route
app.get('/team/settings', ensureAuthenticated, (req, res) => {
    
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).render('error', { 
            message: 'Zugriff verweigert. Du bist kein Administrator.'
        });
    }

    res.render('team_settings', { 
        user: req.user
    });
});

// --- Server starten ---

// Startet den Discord Bot (MUSS vor dem Express Server LogIn stehen, aber nach der Definition)
client.login(process.env.DISCORD_TOKEN); 


app.listen(PORT, () => {
    console.log(`🌐 Express Server läuft auf Port ${PORT}`);
    console.log(`Zugriff über: http://localhost:${PORT}`);
});