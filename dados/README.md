# Dados do projeto

Esta pasta reunirá as bases utilizadas nos experimentos e sua documentação. Nesta versão, há uma estrutura inicial; os arquivos de dados ainda precisam ser obtidos.

## Fontes

| Base | Instituição | Acesso | Situação |
| --- | --- | --- | --- |
| Oceanic Niño Index (ONI), ERSSTv6 | NOAA / Climate Prediction Center | [Série histórica](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/) | Fonte selecionada; coleta pendente |
| Dados históricos meteorológicos | INMET | [Arquivos anuais](https://portal.inmet.gov.br/dadoshistoricos) | Anos e estações a definir |

## Como preencher as pastas

### 1. ONI

Acesse a série histórica indicada acima e preserve uma cópia da tabela utilizada em `brutos/oni/`, registrando versão, URL e data de obtenção. Caso a tabela seja convertida para CSV, documente essa transformação e preserve também a cópia original.

Mantenha ano, trimestre e valor do índice. Ao associar o índice às observações meteorológicas, registre a convenção temporal adotada; por exemplo, DJF corresponde a dezembro-janeiro-fevereiro e pode ser associado ao mês central, janeiro. Essa convenção é uma decisão do projeto.

A página informa que o RONI passou a ser usado no monitoramento oficial do ENSO. Este projeto mantém o ONI previsto na proposta; qualquer troca de índice deverá ser documentada. [Fonte NOAA](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/).

### 2. INMET

1. Defina o intervalo de anos da pesquisa.
2. Acesse a página de dados históricos e baixe os arquivos anuais necessários.
3. Selecione as estações pertinentes à Região Metropolitana de São Paulo, conferindo localização, período de operação e disponibilidade de registros.
4. Guarde os arquivos originais selecionados em `brutos/inmet/`, preservando seus nomes e cabeçalhos. Uma subpasta por ano pode facilitar a organização.
5. Registre os códigos e coordenadas das estações e o critério de seleção em `metadados/`.

O portal apresenta os downloads por ano para estações automáticas. [Fonte INMET](https://portal.inmet.gov.br/dadoshistoricos).

### 3. Preparação

Salve as versões limpas em `processados/`. Documente unidades, fuso horário, tratamento de ausências e duplicatas, filtros e agregações. Não transforme registros ausentes de precipitação em chuva zero.

Antes de integrar as bases, defina a unidade de observação, como estação-dia ou estação-mês, e como ela se relacionará com o inventário de enchentes e as variáveis espaciais. Registre a regra de associação ao ONI e a regra de classificação climática.

## Registro de origem

Use o [modelo de metadados](metadados/README.md) para cada arquivo ou conjunto de arquivos. Mantenha os dados brutos separados dos processados e registre como reproduzir cada transformação.

Ao adicionar as bases ao GitHub, inclua os dados efetivamente usados no estudo. Para arquivos volumosos, mantenha nesta pasta a documentação, o endereço de obtenção e as instruções necessárias para reproduzir o recorte.

## Pendências

- [ ] Definir os anos de análise.
- [ ] Selecionar e documentar as estações do INMET.
- [ ] Obter e registrar a versão da série ONI.
- [ ] Adicionar os arquivos selecionados às pastas de dados brutos.
- [ ] Definir a integração temporal e espacial das bases.
- [ ] Obter o inventário de enchentes e as demais variáveis geoespaciais.
- [ ] Documentar o processamento e os dados resultantes.
