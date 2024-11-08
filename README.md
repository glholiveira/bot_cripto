
# Trading Bot com Binance API e `pandas_ta`

Este projeto é um bot de trading automatizado que usa a API da Binance para operar em pares de criptomoedas. O bot utiliza a biblioteca `pandas_ta` para realizar análises técnicas e opera com lógica de compra e venda com base em indicadores técnicos, como o Índice de Força Relativa (RSI) e Médias Móveis Simples (SMA).

## Funcionalidades

- **Carregamento e Salvamento de Estado**: O bot armazena o estado de cada criptomoeda no arquivo `estado_bot.json`, incluindo detalhes como quantidade comprada, preço de compra e status de compra extra.
- **Análise Técnica**: Utiliza o RSI e SMA para identificar oportunidades de compra e venda com base em condições de sobrecompra ou sobrevenda.
- **Execução de Ordens**: Implementa ordens de compra e venda para cada par de criptomoeda configurado.
- **Gerenciamento de Riscos**: Calcula e compara preços mínimos de venda para cada compra realizada, considerando a taxa de transação.

## Como Adicionar Novas Moedas

Para adicionar uma nova moeda ao bot:
1. **Atualize a Função `carregar_estado`**: Adicione a nova moeda no dicionário `estado_inicial` com os mesmos campos de configuração dos pares de moedas existentes. 
   ```python
   'NOVOMOEDAUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0}
   ```
2. **Atualize a Lista de Símbolos no Loop Principal**: Certifique-se de que a nova moeda está incluída nas operações de compra e venda no loop principal.

## Cálculos Detalhados

### 1. Cálculo da Quantidade de Compra
Ao identificar uma oportunidade de compra:
- Calcula a quantidade de criptomoeda a ser comprada com base em um valor fixo de USDT (exemplo: 12.0 USDT) e divide pelo preço atual.
- Ajusta a quantidade para atender aos requisitos mínimos de quantidade (`LOT_SIZE`) da Binance.

### 2. Cálculo de Compra Extra
Se uma compra inicial já foi feita e uma segunda oportunidade de compra é identificada:
- Calcula a quantidade extra de compra (exemplo: 10.0 USDT) e segue as mesmas regras de ajuste da quantidade para o `LOT_SIZE`.

### 3. Cálculo do Preço de Venda e Lucro
Para cada venda:
- Calcula o `preco_min_venda` com base no preço de compra e na taxa de transação (0.1%).
- Executa a venda se o preço atual superar o `preco_min_venda`, e calcula o lucro da transação, adicionando-o ao `lucro_acumulado`.

## Dependências

- `pandas`
- `pandas_ta`
- `json`
- `os`
- Biblioteca da API da Binance (não incluída no código fornecido, mas necessária para `cliente`)

## Como Executar

1. Certifique-se de instalar todas as dependências.
2. Configure as credenciais da Binance e inicialize o objeto `cliente`.
3. Execute o código.

O bot manterá a execução e atualizará o estado periodicamente.