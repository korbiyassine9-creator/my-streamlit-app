FACTORY_PROFILES = {
    "Zone industrielle Moknine": {
        "sector":          "Textile & Agroalimentaire",
        "employees":        1200,
        "daily_emissions":  "~85 tonnes CO2/jour",
        "main_pollutants":  "PM2.5, NOx, SO2",
        "operating_hours":  "06:00 — 22:00",
        "certification":    "ISO 14001",
        "contact":          "direction@zi-moknine.tn",
        "risk_level":       "Élevé",
        "description": (
            "Zone industrielle majeure spécialisée dans le textile "
            "et l'agroalimentaire. Forte densité d'unités de production "
            "avec impact significatif sur la qualité de l'air local."
        )
    },
    "Zone industrielle Teboulba": {
        "sector":          "Industrie manufacturière",
        "employees":        800,
        "daily_emissions":  "~60 tonnes CO2/jour",
        "main_pollutants":  "PM10, CO, NOx",
        "operating_hours":  "07:00 — 21:00",
        "certification":    "En cours",
        "contact":          "direction@zi-teboulba.tn",
        "risk_level":       "Modéré",
        "description": (
            "Zone spécialisée dans les industries manufacturières légères. "
            "Proximité avec la zone résidentielle nécessite une surveillance accrue."
        )
    },
    "Zone industrielle Ksibet": {
        "sector":          "Artisanat & Textile",
        "employees":        400,
        "daily_emissions":  "~30 tonnes CO2/jour",
        "main_pollutants":  "PM2.5, COV",
        "operating_hours":  "08:00 — 20:00",
        "certification":    "Non certifié",
        "contact":          "direction@zi-ksibet.tn",
        "risk_level":       "Faible",
        "description": (
            "Petite zone industrielle orientée artisanat et textile. "
            "Émissions relativement faibles mais surveillance nécessaire "
            "en raison de la proximité côtière."
        )
    },
    "Zone industrielle Monastir": {
        "sector":          "Textile, Électronique, Agroalimentaire",
        "employees":        3500,
        "daily_emissions":  "~150 tonnes CO2/jour",
        "main_pollutants":  "PM2.5, PM10, NOx, SO2, COV",
        "operating_hours":  "00:00 — 24:00",
        "certification":    "ISO 14001, ISO 9001",
        "contact":          "direction@zi-monastir.tn",
        "risk_level":       "Critique",
        "description": (
            "Plus grande zone industrielle de la région. "
            "Activité 24h/24 avec émissions importantes. "
            "Zone prioritaire pour la surveillance et les alertes."
        )
    },
    "Zone industrielle Mahdia": {
        "sector":          "Agroalimentaire & Pêche",
        "employees":        950,
        "daily_emissions":  "~70 tonnes CO2/jour",
        "main_pollutants":  "PM10, NH3, H2S",
        "operating_hours":  "05:00 — 23:00",
        "certification":    "ISO 14001",
        "contact":          "direction@zi-mahdia.tn",
        "risk_level":       "Modéré",
        "description": (
            "Zone orientée agroalimentaire et transformation des produits "
            "de la pêche. Émissions caractéristiques de composés azotés "
            "et soufrés nécessitant une surveillance spécifique."
        )
    },
    "Zone industrielle Sahline": {
        "sector":          "Industrie légère",
        "employees":        300,
        "daily_emissions":  "~25 tonnes CO2/jour",
        "main_pollutants":  "PM2.5, CO",
        "operating_hours":  "08:00 — 19:00",
        "certification":    "Non certifié",
        "contact":          "direction@zi-sahline.tn",
        "risk_level":       "Faible",
        "description": (
            "Petite zone d'industrie légère en expansion. "
            "Émissions limitées mais croissance rapide "
            "nécessite une mise à niveau environnementale."
        )
    },
}

def get_profile(factory_name):
    return FACTORY_PROFILES.get(factory_name, {
        "sector":          "Inconnu",
        "employees":        0,
        "daily_emissions":  "N/A",
        "main_pollutants":  "N/A",
        "operating_hours":  "N/A",
        "certification":    "N/A",
        "contact":          "N/A",
        "risk_level":       "N/A",
        "description":      "Aucune information disponible."
    })