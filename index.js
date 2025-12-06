// --- 1. BENÖTIGTE MODULE IMPORTIEREN ---
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;
const { Client, GatewayIntentBits } = require('discord.js');
const dotenv = require('dotenv');
const ejs = require('ejs');
const path = require('path');

// --- 2. INITIALISIERUNG & KONFIGURATION ---
dotenv.config();

const PORT = process.env.PORT || 3000;

// Express App initialisieren (Muss vor allen app.get/app.use stehen)
const app = express(); 

// Discord Client initialisieren
const client = new Client({ 
    // Fügen Sie hier die benötigten Intents hinzu
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] 
});

// EJS als View Engine setzen
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware für Datenverarbeitung
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// --- 3. PASSPORT UND SESSION SETUP ---

// Session Middleware
app.use(session({
    secret: process.env.SESSION_SECRET || 'EinSehrSicheresGeheimnis', 
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

// Logik zur Auswahl der richtigen Callback URL (Dev oder Prod)
const callbackURL = process.env.NODE_ENV === 'production' 
    ? process.env.CALLBACK_URL 
    : process.env.CALLBACK_DEV_URL;

// Passport Strategie Konfiguration
passport.use(new DiscordStrategy({
    clientID: process.env.DISCORD_CLIENT_ID,
    clientSecret: process.env.DISCORD_CLIENT_SECRET,
    callbackURL: callbackURL, 
    scope: ['identify', 'guilds']
}, 
function(accessToken, refreshToken, profile, done) {
    // Hier wird der Benutzer in der Datenbank gesucht/erstellt
    return done(null, profile);
}));

// Benutzer serialisieren/deserialisieren
passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));

// Funktion zur Überprüfung, ob der Benutzer eingeloggt ist
function ensureAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
        return next();
    }
    res.redirect('/auth/discord'); 
}

// --- 4. ROUTEN DEFINITIONEN ---

// Homepage
app.get('/', (req, res) => {
    res.render('index_home', { 
        user: req.user,
        isAuthenticated: req.isAuthenticated()
    });
});

// Start-Route für Discord-Login (BEHEBT: Cannot GET /auth/discord)
app.get('/auth/discord', passport.authenticate('discord'));

// Callback-Route nach erfolgreichem Login
app.get('/auth/discord/callback', passport.authenticate('discord', {
    failureRedirect: '/' // Fehlerfall
}), (req, res) => {
    // Erfolgreicher Login. Weiterleitung zu den Einstellungen
    res.redirect('/team/settings'); 
});

// Die korrigierte und stabilisierte Einstellungsseite (BEHEBT alle Syntaxfehler)
app.get('/team/settings', ensureAuthenticated, (req, res) => {
    
    // ZUSÄTZLICHER SCHRITT: Prüfen, ob der Benutzer Administrator ist
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).render('error', { 
            message: 'Zugriff verweigert. Du bist kein Administrator.'
        });
    }

    res.render('team_settings', { 
        user: req.user
    });
});


// --- 5. DISCORD BOT START LOGIK ---

client.once('ready', () => {
    console.log(`🤖 Discord Bot ist als ${client.user.tag} online und bereit!`);
});

//client.on('messageCreate', (message) => { /* ... Bot-Commands hier ... */ });

// --- 6. SERVER START ---

// Startet den Discord Bot
client.login(process.env.DISCORD_TOKEN);

// Startet den Express Server
app.listen(PORT, () => {
    console.log(`🌐 Express Server läuft auf Port ${PORT}`);
    console.log(`Zugriff über: http://localhost:${PORT}`);
});