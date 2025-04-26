# FA-PyScrapper
Este mini-projeto consiste na criação de um scrapper feito especificamente para [esta](https://www.fundoambiental.pt/veiculos-de-emissoes-nulas-ven-2024/total-candidaturas.aspx) página do site do Fundo Ambiental.   
Resumidamente, este scrapper pega nos dados relativos a uma categoria específica e guarda-os.   
Posteriormente, estes dados são escritos numa [folha de cálculo](https://docs.google.com/spreadsheets/d/1KgPB1uCa2ZbapGPTD3um3V6HCYnAsnKZ0fUV3O3-9dI/edit?usp=sharing) e, desta forma, consigo, mais eficaz e facilmente, monitorizar estes dados diariamente.

---
Tecnologias utilizadas:
* Python
* Selenium - Foi utilizada esta biblioteca em vez de BeautifulSoup, por exemplo, porque o webiste está a fazer XHR (XMLHttpRequest). Devido a estes *requests*, preferi usar Selenium, pois acredito ser mais fácil de usar, neste caso específico, do que BeautifulSoup.
* Google Cloud
* Google Sheets API & Google Drive API
