# Bot de Descarga de Pólizas - Seguros Bolívar

Bot automatizado para descargar archivos Excel de la plataforma interna de Seguros Bolívar.

## 🚀 Características

- Login automático
- Navegación por menús
- Configuración de filtros
- Descarga automática de Excel
- Logs detallados
- Ejecución programada

## 📦 Requisitos

- Python 3.8+
- Google Chrome
- ChromeDriver

## 🔧 Instalación Local

```bash
# Instalar dependencias
pip3 install -r requirements.txt

# Instalar ChromeDriver (Mac)
brew install chromedriver
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

## ▶️ Ejecución

```bash
python3 bot_polizas.py
```

## 📅 Ejecución Automática (Cron)

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecución diaria a las 8 AM
0 8 * * * cd ~/bot_polizas_bolivar && python3 bot_polizas.py
```

## 📁 Estructura

```
bot_polizas_bolivar/
├── bot_polizas.py      # Script principal
├── requirements.txt    # Dependencias
├── README.md          # Documentación
└── setup_gcp.sh       # Script de instalación para GCP
```

## 📊 Logs

Los logs se guardan en: `~/polizas_bolivar_logs/bot_polizas_YYYYMMDD.log`

## 🔒 Seguridad

⚠️ **IMPORTANTE**: No subir credenciales al repositorio. Usar variables de entorno.