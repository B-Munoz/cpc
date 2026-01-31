# --- Configuration & Setup ---
DB_PATH = "expenses.db" # (Kept for reference, though we use Postgres now)

# Key = user_param (from URL), Value = Their specific settings
CONFIGS = {
    "neon": {
        # YOUR ORIGINAL SETTINGS
        "CATEGORY_CONFIG": {
            "Transporte": 150000,
            "Vivienda": 1200000,
            "Ocio" : 400000,
            "Salud" : 300000,
            "Ropa" : 300000,
            "Misceláneo": 1000000,
            "Departamento" : 700000,
            "Ahorro": 0,
            "Vacaciones": 0
        },
        "ALLOCATION_PCT": {
            "Transporte": 0.05,
            "Vivienda": 0.28,
            "Ocio": 0.09,
            "Salud": 0.02,
            "Ropa" : 0.02,
            "Misceláneo": 0.24,
            "Departamento": 0.05,
            "Ahorro": 0.20,
            "Vacaciones": 0.05
        }
    },
    "pachi": {
        # HER SETTINGS (Customize these as she needs)
        "CATEGORY_CONFIG": {
            "Comida": 200000,
            "Transporte": 100000,
            "Salidas": 150000,
            "Arriendo": 400000,
            "Varios": 200000,
            "Ahorro": 0
        },
        "ALLOCATION_PCT": {
            "Comida": 0.20,
            "Transporte": 0.10,
            "Salidas": 0.15,
            "Arriendo": 0.35,
            "Varios": 0.10,
            "Ahorro": 0.10
        }
    }
}

def get_user_config(user_key):
    """
    Returns the configuration dictionary for the specified user.
    Defaults to 'neon' if the user_key is not found.
    """
    return CONFIGS.get(user_key, CONFIGS["neon"])