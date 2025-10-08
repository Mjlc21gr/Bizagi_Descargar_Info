#!/bin/bash

# Script de instalación para Google Cloud Platform (Compute Engine)
# Este script instala todas las dependencias necesarias en una VM de Ubuntu

set -e

echo "=================================================="
echo "Instalando dependencias del Bot de Pólizas"
echo "=================================================="

# Actualizar sistema
echo "Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Python 3 y pip
echo "Instalando Python 3..."
sudo apt-get install -y python3 python3-pip python3-venv

# Instalar dependencias del sistema para Chrome
echo "Instalando dependencias para Chrome..."
sudo apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libxtst6 \
    xdg-utils

# Instalar Google Chrome
echo "Instalando Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y
rm google-chrome-stable_current_amd64.deb

# Verificar versión de Chrome
CHROME_VERSION=$(google-chrome --version)
echo "Chrome instalado: $CHROME_VERSION"

# Instalar ChromeDriver compatible
echo "Instalando ChromeDriver..."
# Obtener la versión de Chrome instalada
CHROME_MAJOR_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+' | cut -d'.' -f1)
echo "Versión major de Chrome: $CHROME_MAJOR_VERSION"

# Descargar ChromeDriver compatible
wget -q "https://storage.googleapis.com/chrome-for-testing-public/$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_MAJOR_VERSION)/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64 chromedriver-linux64.zip

# Verificar ChromeDriver
echo "ChromeDriver instalado: $(chromedriver --version)"

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Crear directorio de logs
mkdir -p ~/polizas_bolivar_logs

# Configurar permisos
chmod +x bot_polizas.py

echo "=================================================="
echo "✓ Instalación completada exitosamente"
echo "=================================================="
echo ""
echo "Para ejecutar el bot:"
echo "  python3 bot_polizas.py"
echo ""
echo "Para configurar ejecución automática:"
echo "  crontab -e"
echo "  Agregar: 0 8 * * * cd ~/bot-polizas-bolivar && python3 bot_polizas.py"
echo ""

