from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os
import logging

#Desabilita a suspensão do computador (apenas enquanto o script corre)
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 0")
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0")
###################################################################################################################################################################

#Criar ficheiro de logs e configurá-lo
log_dir = "/home/afonso/Desktop/scrapper/logs"
os.makedirs(log_dir, exist_ok=True)

#Gerar o nome do ficheiro baseado no dia em que o script corre
today = datetime.datetime.now().strftime("%d-%m-%Y")
log_file = os.path.join(log_dir, f"scrapper-{today}.log")

# Configurar o logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,  # podes pôr INFO para menos verboso
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)
logging.info("-------------------------------------------------------------------------")
logging.info("Novo log:")
logging.info("Scrapper começou!")
###################################################################################################################################################################

linkFA = 'https://www.fundoambiental.pt/veiculos-de-emissoes-nulas-ven-2024/total-candidaturas.aspx'
path = '/home/afonso/Downloads/chromedriver-linux64/chromedriver'

service = Service(executable_path = path)
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

#Espera até que a tabela esteja carregada no site
try:
    driver.get(linkFA)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    logging.info("Site carregou tabela!")
except Exception as e:
    logging.error(f"Ocorreu um erro: {str(e)}", exc_info=True)
###################################################################################################################################################################

table = driver.find_element(By.TAG_NAME, 'table') #Encontra no site a tabela
rows = table.find_elements(By.TAG_NAME, 'tr') #Pega em todas as colunas e guarda em rows
target_text = "T4 - Bicicleta elétrica" #Encontra a linha pretendida - neste caso, a linha correspondente à categoria das bicicletas elétricas
target_row = None

#Procura em cada linha pelo target_text e coloca a linha alvo em target_row, se encon
for row in rows:
    if target_text in row.text:
        target_row = row
        break

#Este teste não seria totalmente necessário uma vez que, à partida, esta linha existirá sempre
if target_row:
    cells = target_row.find_elements(By.TAG_NAME, 'td')
    data = [cell.text for cell in cells]
    #print(data)
else:
    logging.error("Erro: Linha da categoria Bicicleta Elétrica não encontrada")
    
driver.quit()   

#Filtrei os dados a escrever uma vez que apenas algumas colunas da linha me interessam
dataToWrite = [data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]]
logging.info(f"Dados: {dataToWrite}")
###################################################################################################################################################################

try:
    #Autenticação com as credenciais
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    #Abre a folha de cálculo
    sheet = client.open("Progresso Fundo Ambiental").sheet1
    logging.info("Credenciais aprovadas e Folha de cálculo aberta!")
except Exception as e:
        logging.error(f"Ocorreu um erro: {str(e)}", exc_info=True)

row_to_write = len(sheet.col_values(1)) + 1 #Encontra a última linha com dados escritas na coluna A e adiciona 1 a essa linha (i.e. linha onde pretendemos escrever, linha a baixo da linha atualmente escrita)


def formatar_para_duas_casas(numero): #Formata um número para que tenha sempre duas casas inteiras (2 => 02; 14 => 14)
    return "{:02d}".format(numero)

dataData = datetime.datetime.now() #Pega na data atual. The problem is, se fizermos data.day ou data.month, por exemplo, isso vem como int e eu pretendo uma string, daí na linha imediatamente a baixo, estar sempre a converter cada valor
dataDiaEhora = str(formatar_para_duas_casas(dataData.day)) + '/' + str(formatar_para_duas_casas(dataData.month)) + '/' + str(dataData.year) + ' - ' + str(formatar_para_duas_casas(dataData.hour)) + ':' + str(formatar_para_duas_casas(dataData.minute))
range_to_write_new_date = f'A{row_to_write}:A{row_to_write}' #Células (neste caso, apenas uma) onde se pretende escrever a data atual
try:
    sheet.update(range_name=range_to_write_new_date, values=[[dataDiaEhora]]) #Escreve na célula pretendida a data atual (tem de ser array 2D, pois é o que o values está à espera de receber!!)
    logging.info(f"Escreveu a data atual na coluna A da linha {row_to_write}!")
except Exception as e:
        logging.error(f"Ocorreu um erro: {str(e)}", exc_info=True)

# Escreve os dados na sheet, começando na coluna B e acabando na coluna I
range_to_write = f'B{row_to_write}:I{row_to_write}'
try:
    sheet.update(range_name = range_to_write, values=[dataToWrite])
    logging.info(f"Escreveu os valores nas colunas da linha {row_to_write}!")
except Exception as e:
        logging.error(f"Ocorreu um erro: {str(e)}", exc_info=True)

valorDoDiaAnterior = int(sheet.acell(f'B{row_to_write - 1}').value) #Calula o número de candidaturas aceites no dia anterior
diferencaDiariaAceites = valorDoDiaAnterior - int(dataToWrite[0]) #Calcula a diferença do número de candidaturas aceites entre o dia atual e o anterior
diferencaDiariaAceitesSTR = str(diferencaDiariaAceites) #Apenas transforma o valor inteiro numa string para poder concatenar com texto na linha imediatamente abaixo
text_to_write_in_last_cell = "Mais " + diferencaDiariaAceitesSTR + " aceites" #Concatenação do texto com a diferença de valores


range_to_write_diff = f'J{row_to_write}:J{row_to_write}' #Células (neste caso, apenas uma) onde se pretende escrever o text_to_write_in_last_cell
try:
    sheet.update(range_name = range_to_write_diff, values = [[text_to_write_in_last_cell]]) #Escreve na célula pretendida o text_to_write_in_last_cell
    logging.info(f"Escreveu a diferença de valores ({diferencaDiariaAceitesSTR}) na célula J da linha {row_to_write}!")
except Exception as e:
        logging.error(f"Ocorreu um erro: {str(e)}", exc_info=True)

#Habilita de novo a suspensão do computador
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 300")
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 300")
logging.info("Acabou!")