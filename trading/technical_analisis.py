import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta

def prepare_data(ticker, days):
    """
    Prépare et nettoie les données pour l'analyse technique.
    """
    print("\n=== Début prepare_data ===")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Télécharger les données principales
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        raise ValueError(f"Pas de données trouvées pour {ticker}")

    # Supprimer le multi-index si présent
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    print(f"Colonnes après nettoyage: {df.columns.tolist()}")
    
    # Télécharger les données de référence
    vix = yf.download("^VIX", start=start_date, end=end_date)['Close']
    sp500 = yf.download("^GSPC", start=start_date, end=end_date)['Close']
    nasdaq = yf.download("^IXIC", start=start_date, end=end_date)['Close']
    dow = yf.download("^DJI", start=start_date, end=end_date)['Close']
    
    # Supprimer les multi-index des indices si présents
    for series in [vix, sp500, nasdaq, dow]:
        if isinstance(series, pd.DataFrame):
            series = series.squeeze()
    
    # Normaliser les indices
    df['VIX'] = vix
    df['SP500'] = sp500 / sp500.iloc[0]
    df['NASDAQ'] = nasdaq / nasdaq.iloc[0]
    df['DOW'] = dow / dow.iloc[0]
    
    print("Structure finale du DataFrame:")
    print(f"Shape: {df.shape}")
    print(f"Colonnes: {df.columns.tolist()}")
    print(f"Index type: {type(df.index)}")
    
    return df

def calculate_indicators(df):
    """
    Calcule tous les indicateurs techniques.
    """
    print("\n=== Début calculate_indicators ===")
    try:
        # S'assurer que toutes les colonnes nécessaires sont des Series
        for col in ['Close', 'High', 'Low', 'Volume']:
            if isinstance(df[col], pd.DataFrame):
                df[col] = df[col].squeeze()
                
        print("Calcul des moyennes mobiles...")
        # Moyennes mobiles
        df['SMA20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        
        print("Calcul du MACD...")
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        print("Calcul du RSI...")
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'])
        
        print("Calcul des Bandes de Bollinger...")
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_Upper'] = bollinger.bollinger_hband()
        df['BB_Middle'] = bollinger.bollinger_mavg()
        df['BB_Lower'] = bollinger.bollinger_lband()
        
        print("Calcul de l'ATR...")
        # ATR
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        
        print("Calcul du Stochastique...")
        # Stochastique
        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        print("Calcul du Momentum...")
        # Momentum
        df['Momentum'] = ta.momentum.roc(df['Close'])
        
        print("Calcul du VWAP...")
        # VWAP
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        print("Calcul du CRSI...")
        # CRSI (Comparaison avec SP500)
        close_returns = df['Close'].pct_change()
        sp500_returns = df['SP500'].pct_change()
        relative_returns = close_returns - sp500_returns
        df['CRSI'] = ta.momentum.rsi(pd.Series(relative_returns))
        
        print("\nCalcul des indicateurs terminé")
        print(f"Colonnes finales: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        print(f"Erreur dans calculate_indicators: {str(e)}")
        print("Traceback complet:")
        import traceback
        print(traceback.format_exc())
        raise

def generate_signals(df):
    """
    Génère les signaux de trading basés sur les indicateurs.
    """
    def get_signal_row(row):
        try:
            close = float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close'])
            sma20 = float(row['SMA20'].iloc[0]) if isinstance(row['SMA20'], pd.Series) else float(row['SMA20'])
            sma50 = float(row['SMA50'].iloc[0]) if isinstance(row['SMA50'], pd.Series) else float(row['SMA50'])
            macd = float(row['MACD'].iloc[0]) if isinstance(row['MACD'], pd.Series) else float(row['MACD'])
            macd_signal = float(row['MACD_Signal'].iloc[0]) if isinstance(row['MACD_Signal'], pd.Series) else float(row['MACD_Signal'])
            rsi = float(row['RSI'].iloc[0]) if isinstance(row['RSI'], pd.Series) else float(row['RSI'])
            bb_upper = float(row['BB_Upper'].iloc[0]) if isinstance(row['BB_Upper'], pd.Series) else float(row['BB_Upper'])
            bb_lower = float(row['BB_Lower'].iloc[0]) if isinstance(row['BB_Lower'], pd.Series) else float(row['BB_Lower'])
            stoch_k = float(row['Stoch_K'].iloc[0]) if isinstance(row['Stoch_K'], pd.Series) else float(row['Stoch_K'])
            stoch_d = float(row['Stoch_D'].iloc[0]) if isinstance(row['Stoch_D'], pd.Series) else float(row['Stoch_D'])
            momentum = float(row['Momentum'].iloc[0]) if isinstance(row['Momentum'], pd.Series) else float(row['Momentum'])
            crsi = float(row['CRSI'].iloc[0]) if isinstance(row['CRSI'], pd.Series) else float(row['CRSI'])
            vwap = float(row['VWAP'].iloc[0]) if isinstance(row['VWAP'], pd.Series) else float(row['VWAP'])

            return {
                'SMA': 'Achat' if close > sma50 and sma20 > sma50 
                       else 'Vente' if close < sma50 and sma20 < sma50 
                       else 'Neutre',
                'MACD': 'Achat' if macd > macd_signal else 'Vente',
                'RSI': 'Achat' if rsi < 30 else 'Vente' if rsi > 70 else 'Neutre',
                'BB': 'Achat' if close < bb_lower else 'Vente' if close > bb_upper else 'Neutre',
                'Stoch': 'Achat' if stoch_k < 20 and stoch_d < 20 
                         else 'Vente' if stoch_k > 80 and stoch_d > 80 
                         else 'Neutre',
                'Momentum': 'Achat' if momentum > 0 else 'Vente',
                'CRSI': 'Achat' if crsi < 30 else 'Vente' if crsi > 70 else 'Neutre',
                'VWAP': 'Achat' if close > vwap else 'Vente'
            }

        except Exception as e:
            print(f"Erreur lors du calcul des signaux: {str(e)}")
            return None

    signals_list = [get_signal_row(df.loc[idx]) for idx in df.index]
    df['Signals'] = signals_list
    return df


def create_visualization(df, ticker):
    """
    Crée la visualisation des données et indicateurs.
    """
    # Définition des couleurs personnalisées
    colors = {
        'prix': '#2E86C1',      # Bleu foncé
        'sma20': '#F39C12',     # Orange
        'sma50': '#E74C3C',     # Rouge
        'vwap': '#8E44AD',      # Violet
        'volume': '#BDC3C7',    # Gris clair
        'macd': '#2E86C1',      # Bleu
        'signal': '#F39C12',    # Orange
        'bb_bands': '#95A5A6',  # Gris
        'stoch_k': '#2E86C1',   # Bleu
        'stoch_d': '#F39C12',   # Orange
        'sp500': '#27AE60',     # Vert
        'nasdaq': '#E74C3C',    # Rouge
        'dow': '#3498DB',       # Bleu clair
        'background': 'rgb(230, 230, 255)'  # Fond bleu clair
    }
    
    try:
        fig = make_subplots(
            rows=11, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=(
                'Prix et Moyennes Mobiles',
                'MACD',
                'RSI',
                'Bandes de Bollinger',
                'ATR et VIX',
                'Stochastique',
                'Momentum',
                'CRSI',
                'Niveaux Fibonacci',
                'Indices',
                'Signaux'
            ),
            row_heights=[0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            specs=[[{"secondary_y": True}]] + [[{"secondary_y": False}]] * 10
        )

        # Prix et Moyennes Mobiles
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color=colors['prix'], width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA20', line=dict(color=colors['sma20'])), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='SMA50', line=dict(color=colors['sma50'])), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', line=dict(color=colors['vwap'], dash='dot')), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors['volume'], opacity=0.3),
                     row=1, col=1, secondary_y=True)

        # MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color=colors['macd'])), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal MACD', line=dict(color=colors['signal'])), row=2, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color=colors['prix'])), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#E74C3C", row=3, col=1)  # Rouge
        fig.add_hline(y=30, line_dash="dash", line_color="#27AE60", row=3, col=1)  # Vert

        # Bollinger Bands
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color=colors['prix'])), row=4, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Upper'],
            name='BB Sup',
            line=dict(color=colors['bb_bands'], dash='dash'),
            fill=None
        ), row=4, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Lower'],
            name='BB Inf',
            line=dict(color=colors['bb_bands'], dash='dash'),
            fill='tonexty',
            fillcolor='rgba(149, 165, 166, 0.2)'  # Gris transparent
        ), row=4, col=1)

        # ATR et VIX
        fig.add_trace(go.Scatter(x=df.index, y=df['ATR'], name='ATR', line=dict(color=colors['prix'])), row=5, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VIX'], name='VIX', line=dict(color='#E74C3C')), row=5, col=1)

        # Stochastique
        fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_K'], name='Stoch K', line=dict(color=colors['stoch_k'])), row=6, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_D'], name='Stoch D', line=dict(color=colors['stoch_d'])), row=6, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="#E74C3C", row=6, col=1)  # Rouge
        fig.add_hline(y=20, line_dash="dash", line_color="#27AE60", row=6, col=1)  # Vert

        # Momentum
        fig.add_trace(go.Scatter(x=df.index, y=df['Momentum'], name='Momentum', line=dict(color=colors['prix'])), row=7, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#2C3E50", row=7, col=1)  # Gris foncé

        # CRSI
        fig.add_trace(go.Scatter(x=df.index, y=df['CRSI'], name='CRSI', line=dict(color=colors['prix'])), row=8, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#E74C3C", row=8, col=1)  # Rouge
        fig.add_hline(y=30, line_dash="dash", line_color="#27AE60", row=8, col=1)  # Vert

        # Niveaux Fibonacci
        high_price = df['High'].max()
        low_price = df['Low'].min()
        diff = high_price - low_price
        
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color=colors['prix'])), row=9, col=1)
        
        fib_levels = [0.236, 0.382, 0.5, 0.618]
        fib_colors = ['#E74C3C', '#F39C12', '#F1C40F', '#27AE60']  # Rouge, Orange, Jaune, Vert
        
        for level, color in zip(fib_levels, fib_colors):
            fib_value = high_price - level * diff
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[fib_value] * len(df.index),
                    name=f'Fib {level*100}%',
                    line=dict(color=color, dash='dash')
                ),
                row=9, col=1
            )

        # Indices
        fig.add_trace(go.Scatter(x=df.index, y=df['SP500'], name='S&P 500', line=dict(color=colors['sp500'])), row=10, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['NASDAQ'], name='NASDAQ', line=dict(color=colors['nasdaq'])), row=10, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['DOW'], name='Dow Jones', line=dict(color=colors['dow'])), row=10, col=1)

        # Signaux
        for i, indicator in enumerate(['SMA', 'MACD', 'RSI', 'BB', 'Stoch', 'Momentum', 'CRSI', 'VWAP']):
            y_pos = i / 8
            signals = []
            for s in df['Signals']:
                if isinstance(s, dict):
                    signal_value = s.get(indicator, 'Neutre')
                    signals.append(1 if signal_value == 'Achat' else -1 if signal_value == 'Vente' else 0)
                else:
                    signals.append(0)
                    
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[y_pos] * len(signals),
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=signals,
                        colorscale=[[0, '#E74C3C'], [0.5, '#F4D03F'], [1, '#27AE60']],  # Rouge, Jaune, Vert
                        showscale=False
                    ),
                    name=indicator
                ),
                row=11, col=1
            )


        # Mise à jour du layout avec fond bleu clair
        fig.update_layout(
            height=3000,
            title_text=f"Analyse technique pour {ticker}",
            showlegend=True,
            plot_bgcolor=colors['background'],  # Fond bleu clair pour tous les sous-graphiques
            paper_bgcolor='white',
            font=dict(
                color='#2C3E50',
                size=12
            ),
            legend=dict(
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#BDC3C7',
                borderwidth=1
            )
        )

        # Mise à jour des axes avec une grille plus visible sur fond bleu
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.5)',  # Grille blanche semi-transparente
            showline=True,
            linewidth=1,
            linecolor='#BDC3C7',
            zeroline=False  # Supprime la ligne du zéro qui peut être gênante
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.5)',  # Grille blanche semi-transparente
            showline=True,
            linewidth=1,
            linecolor='#BDC3C7',
            zeroline=False  # Supprime la ligne du zéro qui peut être gênante
        )

        # Mise à jour spécifique pour chaque sous-graphique
        for i in range(1, 12):
            fig.update_xaxes(row=i, col=1, gridcolor='rgba(255, 255, 255, 0.5)')
            fig.update_yaxes(row=i, col=1, gridcolor='rgba(255, 255, 255, 0.5)')

        fig.show()

    except Exception as e:
        print(f"Erreur lors de la création du graphique: {e}")
               
def print_summary(df):
    """
    Affiche le résumé des analyses et recommandations.
    """
    try:
        last_row = df.iloc[-1]
        print("\nVérification des signaux:")
        signals = last_row['Signals']
        
        # Si signals est une Series, prendre sa valeur
        if isinstance(signals, pd.Series):
            signals = signals.iloc[0]
            
        if not isinstance(signals, dict):
            print(f"Format incorrect des signaux: {type(signals)}")
            print(f"Contenu: {signals}")
            raise ValueError("Les signaux ne sont pas dans le format attendu")
            
        # Compter les signaux
        buy_signals = sum(1 for s in signals.values() if s == 'Achat')
        sell_signals = sum(1 for s in signals.values() if s == 'Vente')
        neutral_signals = sum(1 for s in signals.values() if s == 'Neutre')
        
        # Création du tableau de résultats
        indicators = ['SMA', 'MACD', 'RSI', 'BB', 'Stoch', 'Momentum', 'CRSI', 'VWAP']
        results_df = pd.DataFrame({
            'Indicateur': indicators,
            'Signal': [signals[ind] for ind in indicators]
        })
        
        print("\nRésumé des signaux:")
        print(results_df.to_string(index=False))
        print(f"\nSignaux d'achat: {buy_signals}")
        print(f"Signaux de vente: {sell_signals}")
        print(f"Signaux neutres: {neutral_signals}")
        
    except Exception as e:
        print(f"Erreur dans print_summary: {str(e)}")
        print("Traceback complet:")
        import traceback
        print(traceback.format_exc())
        raise

def run_analysis(ticker="NVDA", days=180):
    """
    Fonction principale qui orchestre l'analyse complète.
    """
    try:
        # Étape 1: Préparation des données
        df = prepare_data(ticker, days)
        
        # Étape 2: Calcul des indicateurs
        df = calculate_indicators(df)
        
        # Étape 3: Génération des signaux
        df = generate_signals(df)
        
        # Étape 4: Création de la visualisation
        create_visualization(df, ticker)
        
        # Étape 5: Affichage du résumé
        print_summary(df)
        
        return df
        
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")
        raise

if __name__ == "__main__":
    #run_analysis(ticker="NVDA", days=180)
    run_analysis(ticker="TSLA", days=180)
    input("Appuyez sur Entrée pour fermer le programme...")
