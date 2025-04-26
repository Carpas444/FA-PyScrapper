from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

#Desabilita a suspensão do computador (apenas enquanto o script corre)
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 0")
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0")


linkFA = 'https://www.fundoambiental.pt/veiculos-de-emissoes-nulas-ven-2024/total-candidaturas.aspx'
path = '/home/afonso/Downloads/chromedriver-linux64/chromedriver'

service = Service(executable_path = path)
driver = webdriver.Chrome(service = service)
driver.get(linkFA)

#Espera até que a tabela esteja carregada no site
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "table"))
)


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
    print("Erro: Linha não encontrada")
    
driver.quit()   

#Filtrei os dados a escrever uma vez que apenas algumas colunas da linha me interessam
dataToWrite = [data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]]

#Autenticação com as credenciais
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

#Abre a folha de cálculo
sheet = client.open("Progresso Fundo Ambiental").sheet1

row_to_write = len(sheet.col_values(1)) + 1 #Encontra a última linha com dados escritas na coluna A e adiciona 1 a essa linha (i.e. linha onde pretendemos escrever, linha a baixo da linha atualmente escrita)


def formatar_para_duas_casas(numero): #Formata um número para que tenha sempre duas casas inteiras (2 => 02; 14 => 14)
    return "{:02d}".format(numero)

dataData = datetime.datetime.now() #Pega na data atual. The problem is, se fizermos data.day ou data.month, por exemplo, isso vem como int e eu pretendo uma string, daí na linha imediatamente a baixo, estar sempre a converter cada valor
dataDiaEhora = str(formatar_para_duas_casas(dataData.day)) + '/' + str(formatar_para_duas_casas(dataData.month)) + '/' + str(dataData.year) + ' - ' + str(formatar_para_duas_casas(dataData.hour)) + ':' + str(formatar_para_duas_casas(dataData.minute))
range_to_write_new_date = f'A{row_to_write}:A{row_to_write}' #Células (neste caso, apenas uma) onde se pretende escrever a data atual
sheet.update(range_name=range_to_write_new_date, values=[[dataDiaEhora]]) #Escreve na célula pretendida a data atual (tem de ser array 2D, pois é o que o values está à espera de receber!!)


# Escreve os dados na sheet, começando na coluna B e acabando na coluna I
range_to_write = f'B{row_to_write}:I{row_to_write}'
sheet.update(range_name = range_to_write, values=[dataToWrite])


valorDoDiaAnterior = int(sheet.acell(f'B{row_to_write - 1}').value) #Calula o número de candidaturas aceites no dia anterior
diferencaDiariaAceites = valorDoDiaAnterior - int(dataToWrite[0]) #Calcula a diferença do número de candidaturas aceites entre o dia atual e o anterior
diferencaDiariaAceitesSTR = str(diferencaDiariaAceites) #Apenas transforma o valor inteiro numa string para poder concatenar com texto na linha imediatamente abaixo
text_to_write_in_last_cell = "Mais " + diferencaDiariaAceitesSTR + " aceites" #Concatenação do texto com a diferença de valores


range_to_write_diff = f'J{row_to_write}:J{row_to_write}' #Células (neste caso, apenas uma) onde se pretende escrever o text_to_write_in_last_cell
sheet.update(range_name = range_to_write_diff, values = [[text_to_write_in_last_cell]]) #Escreve na célula pretendida o text_to_write_in_last_cell


#Habilita de novo a suspensão do computador
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 300")
os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 300")