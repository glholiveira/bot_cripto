import pandas as pd
import time
import pandas_ta as ta
import binance as bn
import json
import os
import math
from decimal import Decimal, ROUND_DOWN
from datetime import datetime
# from dotenv import load_dotenv
from key import cliente
# load_dotenv()

# api_key = os.environ['API_KEY_BINANCE']
# api_secret = os.environ['SECRET_KEY_BINANCE']

# cliente = bn.Client(api_key, api_secret)

def round_down(quantity, step_size):
    # Converta para Decimal para evitar erros de ponto flutuante
    quantity = Decimal(str(quantity))
    step_size = Decimal(str(step_size))
    
    # Arredonde para baixo de acordo com o step_size
    rounded_quantity = (quantity // step_size) * step_size
    
    # Retorne como float, formatando com a precisão do step_size
    precision = step_size.as_tuple().exponent * -1
    return float(round(rounded_quantity, precision))

# Função para carregar o estado do bot
def carregar_estado():
    estado_inicial = {
        'compras': {
            'BTCUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},
            'ETHUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},
            'BNBUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},
            'SOLUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando SOL
            'LTCUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando LTCUSDT
            'DOGEUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando DOGEUSDT
            'TRXUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando TRON
            'ADAUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando ADAUSDT
            'AVAXUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando AVAXUSDT
            'XRPUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando AVAXUSDT
            'APTUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando APTUSDT
            'ARBUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando ARBUSDT
            'MOVEUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando MOVE
            'USUALUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando USUAL
            'HIVEUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},  # Adicionando HIVE
            'MATICUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},
            'ATOMUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},
            'FTMUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},
            'SANDUSDT': {'compra': False, 'quantidade': 0, 'preco_compra': 0, 'comprou_extra': False, 'quantidade_extra': 0, 'preco_compra_extra': 0},

        },
        'lucro_acumulado': 0.0
    }

    if os.path.exists('estado_bot.json'):
        with open('estado_bot.json', 'r') as f:
            estado_salvo = json.load(f)
        
        # Verificar e adicionar as chaves necessárias
        for symbol in estado_inicial['compras']:
            if symbol not in estado_salvo['compras']:
                estado_salvo['compras'][symbol] = estado_inicial['compras'][symbol]
            for key in estado_inicial['compras'][symbol]:
                if key not in estado_salvo['compras'][symbol]:
                    estado_salvo['compras'][symbol][key] = estado_inicial['compras'][symbol][key]
                    
        return estado_salvo
    
    return estado_inicial

# Função para salvar o estado do bot
def salvar_estado(estado):
    with open('estado_bot.json', 'w') as f:
        json.dump(estado, f)

# Função para atualizar dados de um símbolo
def atualizar_dados(symbol):
    try:
        df = pd.DataFrame(cliente.get_historical_klines(symbol, '1m', "60m"))  # 60 minutos de dados
        df = df.iloc[:, :6]
        df.columns = ['date_open', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('date_open')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)

        df['rsi'] = ta.rsi(df['Close'], length=14)
        df['sma_20'] = ta.sma(df['Close'], length=20)
        df['sma_50'] = ta.sma(df['Close'], length=50)

        if df.shape[0] < 50:
            print(f"Erro: Dados insuficientes para {symbol}: {df.shape[0]} velas.")
            return None

        df = df.dropna()
        
        if df.empty:
            print(f"Todos os dados de {symbol} foram descartados devido a NaN.")
            return None
        
        return df
    except Exception as e:
        print(f"Erro ao atualizar dados para {symbol}: {e}")
        return None

# Função para obter o tamanho mínimo do lote e valor mínimo de notional
def get_lot_size_and_notional(symbol):
    try:
        info = cliente.get_symbol_info(symbol)
        min_qty = None
        step_size = None
        min_notional = None
        for filt in info['filters']:
            if filt['filterType'] == 'LOT_SIZE':
                min_qty = float(filt['minQty'])
                step_size = float(filt['stepSize'])
            if filt['filterType'] == 'MIN_NOTIONAL':
                min_notional = float(filt['minNotional'])
            if filt['filterType'] == 'NOTIONAL':
                min_notional = float(filt['minNotional'])
        return min_qty, step_size, min_notional
    except Exception as e:
        print(f"Erro ao buscar informações de LOT_SIZE e MIN_NOTIONAL para {symbol}: {e}")
    return None, None, None

# Função para obter o tempo do servidor
def get_server_time():
    try:
        server_time = cliente.get_server_time()
        return server_time['serverTime']
    except Exception as e:
        print(f"Erro ao obter o tempo do servidor: {e}")
        return None

# Função para executar ordem de compra ou venda
def executar_ordem(symbol, side, quantidade, server_time):
    try:
        ordem = cliente.create_order(
            symbol=symbol, 
            side=side, 
            type='MARKET', 
            quantity=f"{quantidade:.8f}", 
            recvWindow=6000, 
            timestamp=server_time
        )
        print(f"Ordem {side} realizada para {symbol}: {quantidade:.8f}")
        return True
    except Exception as e:
        print(f"Erro ao executar ordem {side} para {symbol}: {e}")
        return False

# Obter diferença de tempo entre servidor e sistema local
local_time = int(time.time() * 1000)
server_time = get_server_time()
time_diff = server_time - local_time if server_time else 0

# Carrega o estado do bot
estado_bot = carregar_estado()
compras = estado_bot['compras']
lucro_acumulado = estado_bot['lucro_acumulado']
# Verifica o LOT_SIZE e MIN_NOTIONAL para cada símbolo
lot_sizes = {}
for symbol in compras.keys():
    min_qty, step_size, min_notional = get_lot_size_and_notional(symbol)
    if min_notional is None:
        min_notional = 10.0
    lot_sizes[symbol] = (min_qty, step_size, min_notional)
    print(f"{symbol} - Min Qty: {min_qty:.8f}, Step Size: {step_size:.8f}, Min Notional: {min_notional:.2f}")
    
# Taxa de transação
taxa_transacao = 0.001

def ajustar_quantidade(valor, step_size):
    # Converte para Decimal para maior precisão
    valor = Decimal(str(valor))
    step_size = Decimal(str(step_size))
    return float(valor.quantize(step_size, rounding=ROUND_DOWN))



# Loop principal
while True:
    print(str(datetime.now()))
    for symbol in compras.keys():
        df = atualizar_dados(symbol)
        if df is None:
            print("aqui")
            time.sleep(5)
            continue

        preco_atual = df['Close'].iloc[-1]
        min_qty, step_size, min_notional = lot_sizes[symbol]
        min_notional = min_notional + 1
        casas = len(str(step_size).replace('.','').split('1')[0])
        if casas > 0:
            preco_compra = round((min_notional / preco_atual) + step_size,casas)       
        else:
            preco_compra = math.ceil(min_notional / preco_atual)
        print(f"Preço atual para {symbol}: {preco_atual} USDT -- Valor minimo para comprar {preco_compra}")

        if not compras[symbol]['compra']:
            # Primeira compra
            if df['rsi'].iloc[-1] < 30 and preco_atual < df['sma_20'].iloc[-1]:
                if preco_compra >= min_qty:
                    adjusted_time = int(time.time() * 1000) + time_diff
                    if executar_ordem(symbol, 'BUY', preco_compra, adjusted_time):
                        compras[symbol]['compra'] = True
                        compras[symbol]['quantidade'] = preco_compra
                        compras[symbol]['preco_compra'] = preco_atual
                        compras[symbol]['comprou_extra'] = False
                        compras[symbol]['quantidade_extra'] = 0  # Zera quantidade extra caso tenha sido vendido
                        
                        # Salva o estado imediatamente após a compra extra
                        estado_bot['compras'] = compras
                        salvar_estado(estado_bot)
        else:
            # Compra extra
            if not compras[symbol]['comprou_extra'] and df['rsi'].iloc[-1] < 30 and preco_atual < df['sma_20'].iloc[-1]:
                if preco_compra >= min_qty:
                    adjusted_time = int(time.time() * 1000) + time_diff
                    if executar_ordem(symbol, 'BUY', preco_compra, adjusted_time):
                        compras[symbol]['quantidade_extra'] = preco_compra
                        compras[symbol]['preco_compra_extra'] = preco_atual
                        compras[symbol]['comprou_extra'] = True
                        
                        # Salva o estado imediatamente após a compra extra
                        estado_bot['compras'] = compras
                        salvar_estado(estado_bot)

            # Venda da compra principal
            preco_venda = (1 - taxa_transacao) * preco_atual
            preco_min_venda = compras[symbol]['preco_compra'] * (1 + taxa_transacao + 0.007)
            print(f"Preço mínimo para venda da compra principal para {symbol}: {preco_min_venda:.2f} USDT")
            if compras[symbol]['quantidade'] > 0 and preco_venda > preco_min_venda:
                adjusted_time = int(time.time() * 1000) + time_diff
                if executar_ordem(symbol, 'SELL', compras[symbol]['quantidade'], adjusted_time):
                    lucro_transacao = (preco_venda - compras[symbol]['preco_compra']) * compras[symbol]['quantidade']
                    lucro_acumulado += lucro_transacao
                    compras[symbol]['compra'] = False
                    print(f"Lucro da venda principal para {symbol}: {lucro_transacao:.2f} USDT")

            # Venda da compra extra
            if compras[symbol]['quantidade_extra'] > 0:
                preco_min_venda_extra = compras[symbol]['preco_compra_extra'] * (1 + taxa_transacao + 0.007)
                print(f"Preço mínimo para venda da compra extra para {symbol}: {preco_min_venda_extra:.2f} USDT")
                if preco_venda > preco_min_venda_extra:
                    adjusted_time = int(time.time() * 1000) + time_diff
                    if executar_ordem(symbol, 'SELL', compras[symbol]['quantidade_extra'], adjusted_time):
                        lucro_transacao = (preco_venda - compras[symbol]['preco_compra_extra']) * compras[symbol]['quantidade_extra']
                        lucro_acumulado += lucro_transacao
                        compras[symbol]['quantidade_extra'] = 0
                        compras[symbol]['comprou_extra'] = False
                        print(f"Lucro da venda extra para {symbol}: {lucro_transacao:.2f} USDT")

        estado_bot['compras'] = compras
        estado_bot['lucro_acumulado'] = lucro_acumulado
        salvar_estado(estado_bot)

    time.sleep(60)