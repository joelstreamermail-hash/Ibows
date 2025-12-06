
// Definiert die GET-Route für die Team-Einstellungen
app.get('/team/settings', ensureAuthenticated, (req, res) => {
    
    // ZUSÄTZLICHER SCHRITT: Prüfen, ob der Benutzer Administrator oder Teammitglied ist
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).render(error, { 
            message: 'Zugriff verweigert. Du bist kein Administrator.' 
        });
    }

    // Rendert das View-Template team_settings.ejs
    res.render(team_settings, { 
        user: req.user,
        // Hier können Sie Gilden-Daten oder andere Informationen hinzufügen
    });
});

// Definiert die GET-Route für die Team-Einstellungen
app.get('/team/settings', ensureAuthenticated, (req, res) => {
    
    // ZUSÄTZLICHER SCHRITT: Prüfen, ob der Benutzer Administrator ist
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).render('error', { 
            // Deutsche Fehlermeldung in Anführungszeichen, um Syntaxfehler zu vermeiden
            message: 'Zugriff verweigert. Du bist kein Administrator.' 
        });
    }

    // Rendert das View-Template 'team_settings.ejs'
    res.render('team_settings', { 
        user: req.user,
    });
});

// Definiert die GET-Route für die Team-Einstellungen
app.get('/team/settings', ensureAuthenticated, (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).render('error', { 
            message: 'Zugriff verweigert. Du bist kein Administrator.' 
        });
    }
    res.render('team_settings', { user: req.user });
});
