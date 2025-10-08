"""
Bot para descargar pólizas de Seguros Bolívar
Automatiza el proceso de login, búsqueda y descarga de reportes en Excel
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configuración de logging
log_dir = Path.home() / "polizas_bolivar_logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"bot_polizas_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


class BotPolizasBolivar:
    def __init__(self):
        self.url = "https://intranet.bolnet.com.co/BIZ_BOLIVAR/#"
        self.usuario = "1007409364"
        self.password = "Bolivar2025"
        self.dominio = "Bizagi"
        self.download_dir = str(Path.home() / "Downloads")
        self.driver = None

    def configurar_navegador(self):
        """Configura el navegador Chrome con las opciones necesarias"""
        logging.info("Configurando navegador Chrome...")

        options = webdriver.ChromeOptions()

        # Configuración de descargas
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        # Opciones adicionales para Mac
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")

        # MÉTODO 1: Intentar con ChromeDriver del sistema (Homebrew)
        try:
            logging.info("Intentando usar ChromeDriver del sistema...")
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            logging.info("✓ Navegador configurado correctamente (ChromeDriver del sistema)")
            return True
        except Exception as e:
            logging.warning(f"ChromeDriver del sistema no funcionó: {str(e)}")

            # MÉTODO 2: Intentar con WebDriver Manager (limpiando caché primero)
            try:
                logging.info("Limpiando caché de WebDriver Manager...")
                import shutil
                cache_path = os.path.expanduser("~/.wdm")
                if os.path.exists(cache_path):
                    shutil.rmtree(cache_path)
                    logging.info("✓ Caché eliminado")

                logging.info("Descargando ChromeDriver con WebDriver Manager...")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.implicitly_wait(10)
                logging.info("✓ Navegador configurado correctamente (WebDriver Manager)")
                return True
            except Exception as e2:
                logging.error(f"❌ Ambos métodos fallaron")
                logging.error(f"Error método 1: {str(e)}")
                logging.error(f"Error método 2: {str(e2)}")
                logging.error("Solución: Actualiza ChromeDriver con: brew upgrade chromedriver")
                return False

    def iniciar_sesion(self):
        """Realiza el inicio de sesión en la plataforma"""
        try:
            logging.info(f"Accediendo a {self.url}")
            self.driver.get(self.url)

            # Esperar a que cargue la página de login
            wait = WebDriverWait(self.driver, 30)

            # Ingresar usuario (ID correcto: "user")
            logging.info("Ingresando credenciales...")
            campo_usuario = wait.until(
                EC.presence_of_element_located((By.ID, "user"))
            )

            # Remover atributo readonly con JavaScript
            self.driver.execute_script("arguments[0].removeAttribute('readonly')", campo_usuario)
            self.driver.execute_script("arguments[0].removeAttribute('maxlength')", campo_usuario)

            # Limpiar y escribir usando JavaScript para evitar problemas
            self.driver.execute_script("arguments[0].value = ''", campo_usuario)
            self.driver.execute_script(f"arguments[0].value = '{self.usuario}'", campo_usuario)

            # También intentar con send_keys por si acaso
            campo_usuario.click()
            campo_usuario.clear()
            campo_usuario.send_keys(self.usuario)
            logging.info("✓ Usuario ingresado")

            # Ingresar contraseña (ID correcto: "password")
            campo_password = self.driver.find_element(By.ID, "password")

            # Remover readonly de contraseña también
            self.driver.execute_script("arguments[0].removeAttribute('readonly')", campo_password)
            self.driver.execute_script("arguments[0].value = ''", campo_password)
            self.driver.execute_script(f"arguments[0].value = '{self.password}'", campo_password)

            campo_password.click()
            campo_password.clear()
            campo_password.send_keys(self.password)
            logging.info("✓ Contraseña ingresada")

            # Seleccionar dominio (ID correcto: "domain")
            select_dominio = Select(self.driver.find_element(By.ID, "domain"))
            select_dominio.select_by_visible_text(self.dominio)
            logging.info("✓ Dominio seleccionado")

            # Pequeña pausa para asegurar que todo se procesó
            time.sleep(2)

            # Click en botón Ingresar (ID correcto: "btn-login")
            boton_ingresar = self.driver.find_element(By.ID, "btn-login")
            boton_ingresar.click()
            logging.info("✓ Click en botón Ingresar")

            # Esperar a que cargue el dashboard (5-10 segundos como indicaste)
            logging.info("Esperando a que cargue el dashboard...")
            time.sleep(10)

            # Esperar a que desaparezca cualquier loader/spinner
            try:
                wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "loading")))
            except:
                pass

            logging.info("✓ Login exitoso")
            return True

        except TimeoutException:
            logging.error("✗ Timeout al intentar iniciar sesión")
            self.driver.save_screenshot(str(log_dir / "error_timeout.png"))
            return False
        except Exception as e:
            logging.error(f"✗ Error en inicio de sesión: {str(e)}")
            self.driver.save_screenshot(str(log_dir / "error_login.png"))
            return False

    def navegar_a_consultas(self):
        """Navega al menú de consultas y selecciona Consulta de Caso-Poliza"""
        try:
            wait = WebDriverWait(self.driver, 30)

            logging.info("Navegando al menú Consultas...")

            # Esperar a que el dashboard esté completamente cargado
            logging.info("Esperando a que cargue completamente la interfaz...")
            time.sleep(8)

            # Buscar el elemento que contiene "Consultas"
            menu_consultas = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='text' and contains(text(), 'Consultas')]"))
            )

            # Scroll al elemento para asegurarse de que esté visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", menu_consultas)
            time.sleep(1)

            # Hacer clic en Consultas para expandir el menú
            menu_consultas.click()
            logging.info("✓ Menú Consultas expandido")

            # Esperar a que el submenú se expanda (5-10 segundos como indicaste)
            logging.info("Esperando a que se expanda el submenú...")
            time.sleep(8)

            # Buscar y hacer clic en "Otras entidades"
            otras_entidades = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Otras entidades')]"))
            )

            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", otras_entidades)
            time.sleep(1)

            otras_entidades.click()
            logging.info("✓ Otras entidades expandido")

            # Esperar a que se expanda el submenú de Otras entidades
            logging.info("Esperando a que se expanda el submenú de Otras entidades...")
            time.sleep(8)

            # Buscar y hacer clic en "IV - Consulta de Caso-Poliza"
            consulta_poliza = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'IV') and contains(text(), 'Consulta de Caso-Poliza')]"))
            )

            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", consulta_poliza)
            time.sleep(1)

            consulta_poliza.click()
            logging.info("✓ Acceso a Consulta de Caso-Poliza exitoso")

            # Esperar a que cargue la página de consulta (5-10 segundos)
            logging.info("Esperando a que cargue el formulario de consulta...")
            time.sleep(10)

            # Esperar a que el formulario esté listo
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//input | //select | //button")))
            except:
                pass

            return True

        except TimeoutException:
            logging.error("✗ Timeout al navegar a consultas")
            self.driver.save_screenshot(str(log_dir / "error_menu.png"))
            return False
        except Exception as e:
            logging.error(f"✗ Error al navegar a consultas: {str(e)}")
            self.driver.save_screenshot(str(log_dir / "error_menu.png"))
            return False

    def configurar_filtros_busqueda(self):
        """Configura los filtros de búsqueda con las fechas requeridas"""
        try:
            wait = WebDriverWait(self.driver, 30)

            logging.info("Configurando filtros de búsqueda...")

            # Esperar a que el formulario esté listo
            time.sleep(3)

            # Buscar el campo de fecha
            campo_fecha = None
            selectores_fecha = [
                (By.XPATH, "//input[@type='text' and contains(@class, 'ui-bizagi-render-date')]"),
                (By.XPATH, "//input[contains(@id, 'date')]"),
                (By.XPATH, "//input[@placeholder='d/MM/yyyy']"),
                (By.CSS_SELECTOR, "input[type='text'].ui-bizagi-render-date-only")
            ]

            for selector_type, selector_value in selectores_fecha:
                try:
                    campo_fecha = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    logging.info(f"✓ Campo fecha encontrado")
                    break
                except:
                    continue

            if not campo_fecha:
                raise Exception("No se pudo encontrar el campo de fecha")

            # Limpiar y establecer la fecha usando JavaScript
            self.driver.execute_script("arguments[0].removeAttribute('readonly')", campo_fecha)
            self.driver.execute_script("arguments[0].value = ''", campo_fecha)
            self.driver.execute_script("arguments[0].value = '01/01/2025'", campo_fecha)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }))",
                                       campo_fecha)

            logging.info("✓ Fecha establecida: 01/01/2025")

            # Cerrar cualquier calendario que pueda estar abierto
            try:
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass

            # Buscar TODOS los campos de tipo ui-select-data y encontrar el que tiene "LUIS CARLOS GOMEZ RUIZ"
            logging.info("Buscando campo Radicador...")

            try:
                # Buscar todos los campos de tipo select con ese valor
                campos_select = self.driver.find_elements(By.XPATH, "//input[contains(@class, 'ui-select-data')]")

                logging.info(f"Se encontraron {len(campos_select)} campos de tipo select")

                campo_radicador = None
                for i, campo in enumerate(campos_select):
                    valor = campo.get_attribute('value')
                    logging.info(f"Campo {i + 1}: valor = '{valor}'")

                    if valor and 'LUIS CARLOS' in valor:
                        campo_radicador = campo
                        logging.info(f"✓ Campo Radicador encontrado en posición {i + 1}")
                        break

                if campo_radicador:
                    # Scroll al elemento
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_radicador)
                    time.sleep(1)

                    # Intentar con Actions para hacer triple click y seleccionar todo
                    from selenium.webdriver.common.action_chains import ActionChains
                    from selenium.webdriver.common.keys import Keys

                    actions = ActionChains(self.driver)

                    # Triple click para seleccionar todo el texto
                    actions.move_to_element(campo_radicador).click().click().click().perform()
                    time.sleep(0.5)

                    # Eliminar el contenido
                    campo_radicador.send_keys(Keys.DELETE)
                    campo_radicador.send_keys(Keys.BACK_SPACE)

                    # Escribir el nuevo valor
                    campo_radicador.send_keys("-------------")

                    logging.info("✓ Valor '-------------' ingresado en campo Radicador")
                    time.sleep(0.5)

                    # PRESIONAR ENTER
                    campo_radicador.send_keys(Keys.ENTER)
                    logging.info("✓ Enter presionado en campo Radicador")

                    time.sleep(2)

                    # Verificar el cambio
                    nuevo_valor = campo_radicador.get_attribute('value')
                    logging.info(f"Verificación - Nuevo valor del campo: '{nuevo_valor}'")
                else:
                    logging.warning("⚠ No se encontró el campo con 'LUIS CARLOS GOMEZ RUIZ'")

            except Exception as e:
                logging.error(f"Error al buscar/modificar campo radicador: {str(e)}")
                # Intentar método alternativo con JavaScript
                try:
                    logging.info("Intentando método alternativo con JavaScript...")
                    from selenium.webdriver.common.keys import Keys

                    # Encontrar y modificar el campo
                    self.driver.execute_script("""
                        var inputs = document.querySelectorAll('input.ui-select-data');
                        for(var i = 0; i < inputs.length; i++) {
                            if(inputs[i].value.includes('LUIS CARLOS')) {
                                inputs[i].value = '-------------';
                                inputs[i].dispatchEvent(new Event('change', { bubbles: true }));
                                inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                                console.log('Campo radicador modificado');
                                return inputs[i];
                            }
                        }
                    """)

                    # Buscar el campo nuevamente y presionar Enter
                    campos_select = self.driver.find_elements(By.XPATH, "//input[contains(@class, 'ui-select-data')]")
                    for campo in campos_select:
                        if campo.get_attribute('value') == '-------------':
                            campo.send_keys(Keys.ENTER)
                            logging.info("✓ Enter presionado (método alternativo)")
                            break

                    logging.info("✓ Campo radicador modificado con JavaScript")
                except Exception as e2:
                    logging.warning(f"⚠ Método alternativo también falló: {str(e2)}")

            logging.info("✓ Filtros configurados")
            time.sleep(2)
            return True

        except Exception as e:
            logging.error(f"✗ Error al configurar filtros: {str(e)}")
            self.driver.save_screenshot(str(log_dir / "error_filtros.png"))
            return False

    def ejecutar_busqueda(self):
        """Ejecuta la búsqueda con los filtros configurados"""
        try:
            wait = WebDriverWait(self.driver, 30)

            logging.info("Ejecutando búsqueda...")

            # Buscar el botón "Buscar" usando el ID que mostraste
            boton_buscar = wait.until(
                EC.element_to_be_clickable((By.ID, "submit-for-search"))
            )

            # Scroll al botón
            self.driver.execute_script("arguments[0].scrollIntoView(true);", boton_buscar)
            time.sleep(1)

            boton_buscar.click()
            logging.info("✓ Click en botón Buscar realizado")

            # Esperar a que se ejecute la búsqueda
            logging.info("Esperando a que se carguen los resultados...")
            time.sleep(10)

            # Verificar que hay resultados (buscar la tabla o el mensaje de resultados)
            try:
                # Intentar encontrar la tabla de resultados o el div de exportación
                wait.until(
                    EC.presence_of_element_located((By.ID, "exportExcel"))
                )
                logging.info("✓ Resultados cargados correctamente")
                return True
            except TimeoutException:
                logging.warning("⚠ No se encontró el botón de exportar, pero continuando...")
                return True

        except Exception as e:
            logging.error(f"✗ Error al ejecutar búsqueda: {str(e)}")
            self.driver.save_screenshot(str(log_dir / "error_busqueda.png"))
            return False

    def descargar_excel(self):
        """Hace clic en el botón de Excel para descargar el archivo"""
        try:
            wait = WebDriverWait(self.driver, 30)

            logging.info("Buscando botón de exportar Excel...")

            # Esperar a que los resultados estén completamente cargados
            time.sleep(5)

            # Hacer scroll hacia abajo donde está el botón de Excel
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Obtener archivos antes de descargar
            archivos_antes = set(os.listdir(self.download_dir))
            logging.info(f"Archivos actuales en Downloads: {len(archivos_antes)}")

            # El botón de Excel está en un div con id="exportExcel"
            # Dentro hay un <a> tag que es el que realmente descarga
            logging.info("Buscando el link dentro del div exportExcel...")

            try:
                # Método 1: Buscar el link directamente dentro del div
                link_excel = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='exportExcel']//a"))
                )

                # Hacer visible el elemento con scroll
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_excel)
                time.sleep(1)

                logging.info("✓ Link de Excel encontrado, haciendo clic...")

                # Obtener el href del link para verificar
                href = link_excel.get_attribute('href')
                logging.info(f"Link href: {href}")

                # Hacer clic con JavaScript directamente
                self.driver.execute_script("arguments[0].click();", link_excel)
                logging.info("✓ Click realizado en el link de Excel")

            except Exception as e:
                logging.warning(f"Método 1 falló: {e}")

                # Método 2: Ejecutar el click con JavaScript puro
                logging.info("Intentando método alternativo con JavaScript...")
                self.driver.execute_script("""
                    var exportDiv = document.getElementById('exportExcel');
                    if(exportDiv) {
                        console.log('Div exportExcel encontrado');
                        var link = exportDiv.querySelector('a');
                        if(link) {
                            console.log('Link encontrado:', link.href);
                            link.click();
                            console.log('Click ejecutado');
                        } else {
                            console.log('No se encontró el link dentro del div');
                            exportDiv.click();
                        }
                    } else {
                        console.log('No se encontró el div exportExcel');
                    }
                """)
                logging.info("✓ Click ejecutado con JavaScript alternativo")

            # Esperar a que inicie la descarga
            logging.info("⏳ Esperando a que inicie la descarga...")
            time.sleep(5)

            # Verificar si apareció algún archivo nuevo o en progreso
            archivos_actuales = set(os.listdir(self.download_dir))
            archivos_nuevos = archivos_actuales - archivos_antes

            logging.info(f"Archivos nuevos detectados: {archivos_nuevos}")

            # Esperar a que se complete la descarga (máximo 3 minutos)
            logging.info("⏳ Esperando a que se complete la descarga (puede tardar hasta 3 minutos)...")

            archivo_descargado = self.esperar_descarga(archivos_antes, timeout=180)

            if archivo_descargado:
                logging.info(f"✓ Archivo descargado exitosamente: {archivo_descargado}")
                return True
            else:
                # Verificar si hay algún archivo nuevo aunque no sea Excel
                archivos_actuales_final = set(os.listdir(self.download_dir))
                archivos_nuevos_final = archivos_actuales_final - archivos_antes

                if archivos_nuevos_final:
                    logging.warning(f"⚠ Se detectaron archivos nuevos pero no son Excel: {archivos_nuevos_final}")
                else:
                    logging.error("✗ No se detectó ningún archivo nuevo en Downloads")

                self.driver.save_screenshot(str(log_dir / "error_descarga.png"))
                return False

        except TimeoutException:
            logging.error("✗ Timeout: No se encontró el botón de exportar Excel")
            self.driver.save_screenshot(str(log_dir / "error_no_boton_excel.png"))
            return False
        except Exception as e:
            logging.error(f"✗ Error al descargar Excel: {str(e)}")
            self.driver.save_screenshot(str(log_dir / "error_excel.png"))
            return False

    def esperar_descarga(self, archivos_antes, timeout=180):
        """Espera a que se complete la descarga del archivo"""
        tiempo_inicio = time.time()

        while time.time() - tiempo_inicio < timeout:
            time.sleep(2)

            # Obtener archivos actuales
            archivos_actuales = set(os.listdir(self.download_dir))
            nuevos_archivos = archivos_actuales - archivos_antes

            # Buscar archivos Excel nuevos (no temporales)
            for archivo in nuevos_archivos:
                if archivo.endswith(('.xlsx', '.xls')) and not archivo.endswith('.crdownload'):
                    # Verificar que el archivo no está siendo escrito
                    ruta_archivo = os.path.join(self.download_dir, archivo)
                    tamano_inicial = os.path.getsize(ruta_archivo)
                    time.sleep(1)
                    tamano_final = os.path.getsize(ruta_archivo)

                    if tamano_inicial == tamano_final:
                        return archivo

            # Verificar si hay archivos .crdownload (descarga en progreso)
            archivos_temp = [f for f in archivos_actuales if f.endswith('.crdownload')]
            if archivos_temp:
                tiempo_transcurrido = int(time.time() - tiempo_inicio)
                logging.info(f"Descarga en progreso... ({tiempo_transcurrido}/{timeout}s)")

        return None

    def ejecutar(self):
        """Ejecuta el proceso completo del bot"""
        inicio = datetime.now()
        logging.info("=" * 60)
        logging.info(f"INICIANDO BOT DE DESCARGA DE PÓLIZAS - {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 60)

        try:
            # Paso 1: Configurar navegador
            if not self.configurar_navegador():
                raise Exception("Error al configurar navegador")

            # Paso 2: Iniciar sesión
            if not self.iniciar_sesion():
                raise Exception("Error al iniciar sesión")

            # Paso 3: Navegar a consultas
            if not self.navegar_a_consultas():
                raise Exception("Error al navegar a consultas")

            # Paso 4: Configurar filtros
            if not self.configurar_filtros_busqueda():
                raise Exception("Error al configurar filtros")

            # Paso 5: Ejecutar búsqueda
            if not self.ejecutar_busqueda():
                raise Exception("Error al ejecutar búsqueda o no hay resultados")

            # Paso 6: Descargar Excel
            if not self.descargar_excel():
                raise Exception("Error al descargar archivo Excel")

            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()

            logging.info("=" * 60)
            logging.info(f"✓ PROCESO COMPLETADO EXITOSAMENTE")
            logging.info(f"Duración total: {duracion:.2f} segundos")
            logging.info("=" * 60)

            return True

        except Exception as e:
            logging.error("=" * 60)
            logging.error(f"✗ ERROR EN EL PROCESO: {str(e)}")
            logging.error("=" * 60)
            return False

        finally:
            # Cerrar navegador
            if self.driver:
                logging.info("Cerrando navegador...")
                time.sleep(2)
                self.driver.quit()


def main():
    """Función principal"""
    bot = BotPolizasBolivar()
    resultado = bot.ejecutar()

    if resultado:
        print("\n✓ Proceso completado exitosamente")
        print(f"✓ Archivo descargado en: {bot.download_dir}")
        print(f"✓ Log guardado en: {log_file}")
    else:
        print("\n✗ El proceso finalizó con errores")
        print(f"✗ Revisa el log en: {log_file}")

    return 0 if resultado else 1


if __name__ == "__main__":
    exit(main())