# Added functions to provide questions for each service for interactive_installer.py

def get_authelia_questions(current_config: dict) -> list:
    return [
        {
            "key": "authelia_domain",
            "message": "Enter Authelia domain:",
            "default": current_config.get("config/authelia/configuration.yml", {}).get("domain", "auth.example.com"),
        },
        {
            "key": "authelia_port",
            "message": "Enter Authelia port:",
            "default": str(current_config.get("config/authelia/configuration.yml", {}).get("port", "9091")),
        },
        {
            "key": "authelia_enable_2fa",
            "message": "Enable 2FA for Authelia? (yes/no):",
            "default": "yes" if current_config.get("config/authelia/configuration.yml", {}).get("two_factor_enabled", True) else "no",
        },
    ]

def get_searxng_questions(current_config: dict) -> list:
    return [
        {
            "key": "searxng_instance_name",
            "message": "Enter Searxng instance name:",
            "default": current_config.get("config/searxng/settings.yml", {}).get("instance_name", "My Searxng"),
        },
        {
            "key": "searxng_theme",
            "message": "Enter Searxng theme (e.g., 'light', 'dark'):",
            "default": current_config.get("config/searxng/settings.yml", {}).get("theme", "light"),
        },
    ]

def get_swag_questions(current_config: dict) -> list:
    return [
        {
            "key": "swag_subdomain",
            "message": "Enter SWAG proxy subdomain:",
            "default": "swag",
        },
        {
            "key": "swag_ssl_enabled",
            "message": "Enable SSL for SWAG? (yes/no):",
            "default": "yes",
        },
    ]

def get_synapse_questions(current_config: dict) -> list:
    return [
        {
            "key": "synapse_server_name",
            "message": "Enter Synapse server name:",
            "default": current_config.get("config/synapse/homeserver.yaml", {}).get("server_name", "matrix.example.com"),
        },
        {
            "key": "synapse_enable_registration",
            "message": "Enable user registration on Synapse? (yes/no):",
            "default": "no",
        },
    ]
