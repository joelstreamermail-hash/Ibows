const express = require('express');
const app = express();

const session = require('express-session'); // Benötigt für Sessions/Passport
const passport = require('passport');       // Benötigt für Authentifizierung
const DiscordStrategy = require('passport-discord').Strategy; // Oder der spezifische Name Ihrer Strategie
const dotenv = require('dotenv');
const ejs = require('ejs');
const path = require('path');
const fs = require('fs');

dotenv.config();

// --- Globale Variablen und Konfiguration ---
const PORT = process.env.PORT || 3000;

// EJS als View Engine setzen
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware für JSON, URL-Encoded-Daten und Statische Dateien
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public'))); // Stellen Sie sicher, dass ein 'public' Ordner existiert

// --- Passport/Session Konfiguration ---
app.use(session({
    secret: process.env.SESSION_SECRET || 'EinSehrSicheresGeheimnis', // MUSS gesetzt sein
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

// Funktion zur Überprüfung, ob der Benutzer eingeloggt ist
function ensureAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
        return next();
    }
    // Leitet zur Discord-Login-Seite um
    res.redirect('/auth/discord'); 
}

// --- Hauptrouten ---

// Beispiel-Homepage
app.get('/', (req, res) => {
    res.render('index_home', { 
        user: req.user,
        isAuthenticated: req.isAuthenticated()
    });
});

// Die korrigierte und stabilisierte Route
// BEHEBT: ReferenceError, SyntaxError(Anführungszeichen), SyntaxError(Klammern)
app.get('/team/settings', ensureAuthenticated, (req, res) => {
    
    // ZUSÄTZLICHER SCHRITT: Prüfen, ob der Benutzer Administrator ist
    // *Ihre Admin-Logik muss hier implementiert sein*
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).render('error', { 
            message: 'Zugriff verweigert. Du bist kein Administrator.'
        });
    }

    // Rendert das View-Template 'team_settings.ejs'
    res.render('team_settings', { 
        user: req.user
    });
});

// Fügen Sie hier weitere Routen ein (z.B. /dashboard, /auth/discord/callback)

// --- Server starten ---

app.listen(PORT, () => {
    console.log(`Server läuft auf Port ${PORT}`);
    console.log(`Zugriff über: http://localhost:${PORT}`);
});