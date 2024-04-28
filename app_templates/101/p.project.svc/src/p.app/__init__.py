from {{ p.app }}.application.{{ p.app }}_application import {{ pascal(p.app) }}Application

# Start the global singleton that represents the application

{{ pascal(p.app) }}Application()