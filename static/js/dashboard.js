// Dashboard JavaScript

// Global variables
let stockChart;
let indicatorsChart;
let currentSymbol = '';
let currentTimeframe = '1y';

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    document.getElementById('loadChartBtn').addEventListener('click', loadStockChart);
    document.getElementById('timeframeSelector').addEventListener('change', function() {
        currentTimeframe = this.value;
        if (currentSymbol) {
            loadStockChart();
        }
    });
    
    // Load market data (NIFTY and SENSEX)
    loadMarketData();
    
    // Load watchlist
    loadWatchlist();
    
    // Initialize empty charts
    initializeCharts();
    
    // Set up auto-refresh for real-time updates
    setupAutoRefresh();
});

// Set up auto-refresh for real-time data updates
function setupAutoRefresh() {
    // Add refresh button to the UI
    const refreshButton = document.createElement('button');
    refreshButton.className = 'btn btn-sm btn-outline-primary position-fixed';
    refreshButton.style.bottom = '20px';
    refreshButton.style.right = '20px';
    refreshButton.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh Data';
    refreshButton.addEventListener('click', refreshAllData);
    document.body.appendChild(refreshButton);
    
    // Set up auto-refresh timer (every 5 minutes)
    setInterval(refreshAllData, 5 * 60 * 1000);
    
    // Add refresh indicator
    const refreshIndicator = document.createElement('div');
    refreshIndicator.id = 'refreshIndicator';
    refreshIndicator.className = 'position-fixed d-none';
    refreshIndicator.style.top = '70px';
    refreshIndicator.style.right = '20px';
    refreshIndicator.style.padding = '5px 10px';
    refreshIndicator.style.backgroundColor = 'rgba(40, 167, 69, 0.9)';
    refreshIndicator.style.color = 'white';
    refreshIndicator.style.borderRadius = '4px';
    refreshIndicator.style.zIndex = '1050';
    refreshIndicator.innerHTML = '<i class="bi bi-arrow-repeat"></i> Refreshing data...';
    document.body.appendChild(refreshIndicator);
    
    // Add last refresh time display
    const timeDisplay = document.createElement('div');
    timeDisplay.className = 'position-fixed small text-muted';
    timeDisplay.style.bottom = '50px';
    timeDisplay.style.right = '20px';
    timeDisplay.innerHTML = 'Last refresh: <span id="lastRefreshTime">' + new Date().toLocaleTimeString() + '</span>';
    document.body.appendChild(timeDisplay);
}

// Load market data (NIFTY and SENSEX)
function loadMarketData() {
    // Load NIFTY data
    fetchStockData('^NSEI', '1mo').then(data => {
        if (data && !data.error) {
            updateMarketCard('nifty', data);
            calculateMarketTrend(data);
        }
    });
    
    // Load SENSEX data
    fetchStockData('^BSESN', '1mo').then(data => {
        if (data && !data.error) {
            updateMarketCard('sensex', data);
        }
    });
}

// Update market overview cards
function updateMarketCard(index, data) {
    const latestPrice = data.prices.close[data.prices.close.length - 1];
    const previousPrice = data.prices.close[data.prices.close.length - 2];
    const change = latestPrice - previousPrice;
    const changePercent = (change / previousPrice) * 100;
    
    const valueElement = document.getElementById(`${index}Value`);
    const changeElement = document.getElementById(`${index}Change`);
    
    valueElement.textContent = latestPrice.toFixed(2);
    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
    changeElement.className = change >= 0 ? 'price-up' : 'price-down';
    changeElement.innerHTML += change >= 0 ? ' <i class="bi bi-arrow-up"></i>' : ' <i class="bi bi-arrow-down"></i>';
}

// Calculate market trend
function calculateMarketTrend(data) {
    // Simple trend calculation based on SMA crossovers
    const prices = data.prices.close;
    const dates = data.dates;
    
    // Calculate 20-day and 50-day SMAs
    const sma20 = calculateSMA(prices, 20);
    const sma50 = calculateSMA(prices, 50);
    
    // Determine trend
    let trend = 'Neutral';
    let confidence = 50;
    
    if (sma20[sma20.length - 1] > sma50[sma50.length - 1]) {
        // Bullish if short-term SMA is above long-term SMA
        trend = 'Bullish';
        // Calculate confidence based on the distance between SMAs
        confidence = Math.min(80, 50 + (sma20[sma20.length - 1] - sma50[sma50.length - 1]) / sma50[sma50.length - 1] * 100);
    } else if (sma20[sma20.length - 1] < sma50[sma50.length - 1]) {
        // Bearish if short-term SMA is below long-term SMA
        trend = 'Bearish';
        confidence = Math.min(80, 50 + (sma50[sma50.length - 1] - sma20[sma20.length - 1]) / sma50[sma50.length - 1] * 100);
    }
    
    // Update UI
    document.getElementById('marketTrend').textContent = trend;
    const trendBar = document.getElementById('marketTrendBar');
    trendBar.style.width = `${confidence}%`;
    
    if (trend === 'Bullish') {
        trendBar.className = 'progress-bar progress-bar-bullish';
    } else if (trend === 'Bearish') {
        trendBar.className = 'progress-bar progress-bar-bearish';
    } else {
        trendBar.className = 'progress-bar progress-bar-neutral';
    }
    
    // Set AI Sentiment based on trend and recent price action
    const recentPrices = prices.slice(-10);
    const priceChange = (recentPrices[recentPrices.length - 1] - recentPrices[0]) / recentPrices[0] * 100;
    
    let sentiment = 'Neutral';
    let sentimentConfidence = 50;
    
    if (trend === 'Bullish' && priceChange > 2) {
        sentiment = 'Strongly Bullish';
        sentimentConfidence = 75;
    } else if (trend === 'Bullish') {
        sentiment = 'Bullish';
        sentimentConfidence = 65;
    } else if (trend === 'Bearish' && priceChange < -2) {
        sentiment = 'Strongly Bearish';
        sentimentConfidence = 75;
    } else if (trend === 'Bearish') {
        sentiment = 'Bearish';
        sentimentConfidence = 65;
    }
    
    document.getElementById('aiSentiment').textContent = sentiment;
    const sentimentBar = document.getElementById('aiSentimentBar');
    sentimentBar.style.width = `${sentimentConfidence}%`;
    
    if (sentiment.includes('Bullish')) {
        sentimentBar.className = 'progress-bar progress-bar-bullish';
    } else if (sentiment.includes('Bearish')) {
        sentimentBar.className = 'progress-bar progress-bar-bearish';
    } else {
        sentimentBar.className = 'progress-bar progress-bar-neutral';
    }
}

// Calculate Simple Moving Average
function calculateSMA(data, period) {
    const sma = [];
    
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            sma.push(null);
        } else {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            sma.push(sum / period);
        }
    }
    
    return sma;
}

// Load watchlist data
function loadWatchlist() {
    fetch('/watchlist')
        .then(response => response.json())
        .then(data => {
            const watchlistTable = document.getElementById('watchlistTable');
            watchlistTable.innerHTML = '';
            
            data.forEach(stock => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><a href="#" class="stock-link" data-symbol="${stock.symbol}">${stock.symbol}</a></td>
                    <td>${stock.name}</td>
                    <td>${stock.current_price ? stock.current_price.toFixed(2) : '--'}</td>
                    <td class="${stock.price_change > 0 ? 'price-up' : 'price-down'}">
                        ${stock.price_change ? (stock.price_change > 0 ? '+' : '') + stock.price_change.toFixed(2) + ' (' + stock.price_change_pct.toFixed(2) + '%)' : '--'}
                    </td>
                    <td>
                        ${getRecommendationBadge(stock.recommendation)}
                    </td>
                `;
                
                watchlistTable.appendChild(row);
            });
            
            // Add event listeners to stock links
            document.querySelectorAll('.stock-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const symbol = this.getAttribute('data-symbol');
                    document.getElementById('stockSymbol').value = symbol;
                    loadStockChart();
                });
            });
        })
        .catch(error => console.error('Error loading watchlist:', error));
}

// Get recommendation badge HTML
function getRecommendationBadge(recommendation) {
    if (!recommendation) return '<span class="badge bg-secondary">--</span>';
    
    let badgeClass = 'bg-secondary';
    
    switch (recommendation.toLowerCase()) {
        case 'strong buy':
            badgeClass = 'badge-strong-buy';
            break;
        case 'buy':
            badgeClass = 'badge-buy';
            break;
        case 'strong sell':
            badgeClass = 'badge-strong-sell';
            break;
        case 'sell':
            badgeClass = 'badge-sell';
            break;
        case 'hold':
            badgeClass = 'badge-hold';
            break;
    }
    
    return `<span class="badge ${badgeClass}">${recommendation}</span>`;
}

// Initialize charts
function initializeCharts() {
    // Stock price chart options
    const stockChartOptions = {
        chart: {
            type: 'candlestick',
            height: 400,
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    selection: true,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: true
                }
            }
        },
        title: {
            text: 'Stock Price',
            align: 'left'
        },
        xaxis: {
            type: 'datetime'
        },
        yaxis: {
            tooltip: {
                enabled: true
            }
        },
        tooltip: {
            enabled: true
        },
        series: [{
            name: 'Price',
            data: []
        }]
    };
    
    // Technical indicators chart options
    const indicatorsChartOptions = {
        chart: {
            type: 'line',
            height: 400,
            toolbar: {
                show: true
            }
        },
        title: {
            text: 'Technical Indicators',
            align: 'left'
        },
        stroke: {
            width: 2,
            curve: 'smooth'
        },
        xaxis: {
            type: 'datetime'
        },
        tooltip: {
            shared: true
        },
        series: []
    };
    
    // Initialize charts
    stockChart = new ApexCharts(document.getElementById('stockChart'), stockChartOptions);
    indicatorsChart = new ApexCharts(document.getElementById('indicatorsChart'), indicatorsChartOptions);
    
    stockChart.render();
    indicatorsChart.render();
}

// Load stock chart
function loadStockChart(showLoading = true) {
    const symbolInput = document.getElementById('stockSymbol');
    const symbol = symbolInput ? symbolInput.value.trim().toUpperCase() : currentSymbol;
    
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }
    
    currentSymbol = symbol;
    
    // Show loading state if requested
    if (showLoading) {
        document.getElementById('stockChart').innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading chart data...</p></div>';
        document.getElementById('indicatorsChart').innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading indicators...</p></div>';
    }
    
    // Fetch chart data
    fetchStockData(symbol, currentTimeframe)
        .then(data => {
            if (data.error) {
                if (showLoading) alert(data.error);
                return;
            }
            
            // Re-initialize charts
            document.getElementById('stockChart').innerHTML = '';
            document.getElementById('indicatorsChart').innerHTML = '';
            initializeCharts();
            
            // Update stock price chart
            updateStockChart(data);
            
            // Update indicators chart
            updateIndicatorsChart(data);
            
            // Load AI analysis
            loadAnalysis(symbol, !showLoading);
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            if (showLoading) alert('Failed to load chart data. Please try again.');
        });
}

// Fetch stock data from the server
function fetchStockData(symbol, timeframe) {
    return fetch('/chart-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symbol, timeframe })
    })
    .then(response => response.json());
}

// Update stock price chart
function updateStockChart(data) {
    const candlestickData = data.dates.map((date, i) => ({
        x: new Date(date),
        y: [
            data.prices.open[i],
            data.prices.high[i],
            data.prices.low[i],
            data.prices.close[i]
        ]
    }));
    
    stockChart.updateOptions({
        title: {
            text: `${currentSymbol} Stock Price`
        }
    });
    
    stockChart.updateSeries([{
        name: 'Price',
        data: candlestickData
    }]);
}

// Update technical indicators chart
function updateIndicatorsChart(data) {
    const series = [];
    
    // Add RSI if available
    if (data.technical.rsi && data.technical.rsi.length > 0) {
        series.push({
            name: 'RSI',
            type: 'line',
            data: data.technical.rsi.map((value, i) => ({
                x: new Date(data.dates[i]),
                y: value ? value.toFixed(2) : null
            }))
        });
    }
    
    // Add moving averages if available
    if (data.technical.sma_20 && data.technical.sma_20.length > 0) {
        series.push({
            name: 'SMA 20',
            type: 'line',
            data: data.technical.sma_20.map((value, i) => ({
                x: new Date(data.dates[i]),
                y: value ? value.toFixed(2) : null
            }))
        });
    }
    
    if (data.technical.sma_50 && data.technical.sma_50.length > 0) {
        series.push({
            name: 'SMA 50',
            type: 'line',
            data: data.technical.sma_50.map((value, i) => ({
                x: new Date(data.dates[i]),
                y: value ? value.toFixed(2) : null
            }))
        });
    }
    
    indicatorsChart.updateOptions({
        title: {
            text: `${currentSymbol} Technical Indicators`
        }
    });
    
    indicatorsChart.updateSeries(series);
}

// Load AI analysis for a stock
function loadAnalysis(symbol, silent = false) {
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symbol, timeframe: currentTimeframe })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (!silent) {
                document.getElementById('analysisContainer').innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            }
            return;
        }
        
        // Update analysis container
        updateAnalysisContainer(data);
        
        // Update last updated timestamp
        const now = new Date();
        const timestamp = document.getElementById('lastUpdated');
        if (timestamp) {
            timestamp.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        } else {
            const timestampDiv = document.createElement('div');
            timestampDiv.id = 'lastUpdated';
            timestampDiv.className = 'text-muted small text-end mt-2';
            timestampDiv.textContent = `Last updated: ${now.toLocaleTimeString()}`;
            document.getElementById('analysisContainer').appendChild(timestampDiv);
        }
    })
    .catch(error => {
        console.error('Error loading analysis:', error);
        if (!silent) {
            document.getElementById('analysisContainer').innerHTML = `<div class="alert alert-danger">Failed to load analysis. Please try again.</div>`;
        }
    });
}

// Refresh all data on the dashboard
function refreshAllData() {
    // Show refresh indicator
    const indicator = document.getElementById('refreshIndicator');
    indicator.classList.remove('d-none');
    
    // Refresh market data
    loadMarketData();
    
    // Refresh watchlist
    loadWatchlist();
    
    // Refresh current stock chart if one is loaded
    if (currentSymbol) {
        loadStockChart(false); // false means don't show loading spinner during refresh
    }
    
    // Hide refresh indicator after a delay
    setTimeout(() => {
        indicator.classList.add('d-none');
        
        // Show success toast
        const toast = document.createElement('div');
        toast.className = 'position-fixed bg-success text-white p-2 rounded';
        toast.style.bottom = '70px';
        toast.style.right = '20px';
        toast.style.zIndex = '1050';
        toast.innerHTML = '<i class="bi bi-check-circle"></i> Data refreshed successfully';
        document.body.appendChild(toast);
        
        // Update last refresh time
        const now = new Date();
        const lastRefreshEl = document.getElementById('lastRefreshTime');
        if (lastRefreshEl) {
            lastRefreshEl.textContent = now.toLocaleTimeString();
        }
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }, 1500);
}

// Update analysis container
function updateAnalysisContainer(data) {
    const container = document.getElementById('analysisContainer');
    const recommendation = data.recommendation;
    const prediction = data.prediction;
    const analysis = data.analysis;
    
    let sentimentClass = 'neutral';
    if (recommendation.verdict.toLowerCase().includes('buy')) {
        sentimentClass = 'bullish';
    } else if (recommendation.verdict.toLowerCase().includes('sell')) {
        sentimentClass = 'bearish';
    }
    
    let html = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h4>${data.symbol}</h4>
                <h6>₹${data.current_price.toFixed(2)}</h6>
            </div>
            <div>
                ${getRecommendationBadge(recommendation.verdict)}
            </div>
        </div>
        
        <div class="analysis-card ${sentimentClass}">
            <div class="analysis-title">AI Verdict: ${recommendation.verdict}</div>
            <p>${recommendation.summary}</p>
            <div class="analysis-confidence">
                <strong>Confidence:</strong> ${prediction.confidence * 100}%
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <h6>Bullish Factors</h6>
                <ul class="list-group">
    `;
    
    if (recommendation.reasons.bullish && recommendation.reasons.bullish.length > 0) {
        recommendation.reasons.bullish.forEach(reason => {
            html += `<li class="list-group-item">${reason}</li>`;
        });
    } else {
        html += `<li class="list-group-item text-muted">No bullish factors identified</li>`;
    }
    
    html += `
                </ul>
            </div>
            <div class="col-md-6">
                <h6>Bearish Factors</h6>
                <ul class="list-group">
    `;
    
    if (recommendation.reasons.bearish && recommendation.reasons.bearish.length > 0) {
        recommendation.reasons.bearish.forEach(reason => {
            html += `<li class="list-group-item">${reason}</li>`;
        });
    } else {
        html += `<li class="list-group-item text-muted">No bearish factors identified</li>`;
    }
    
    html += `
                </ul>
            </div>
        </div>
        
        <div class="mt-4">
            <h6>Technical Indicators</h6>
            <div class="row">
    `;
    
    // Add technical indicators
    const indicators = [
        { name: 'RSI', value: analysis.rsi ? analysis.rsi.value : null },
        { name: 'MACD', value: analysis.macd ? (analysis.macd.macd_above_signal ? 'Bullish' : 'Bearish') : null },
        { name: 'Stochastic', value: analysis.stochastic ? analysis.stochastic.value : null },
        { name: 'Bollinger Bands', value: analysis.bollinger_bands ? (analysis.bollinger_bands.position === 'above' ? 'Overbought' : analysis.bollinger_bands.position === 'below' ? 'Oversold' : 'Middle') : null }
    ];
    
    indicators.forEach(indicator => {
        html += `
            <div class="col-md-6 col-lg-3 mb-3">
                <div class="card">
                    <div class="card-body p-3">
                        <h6 class="card-title">${indicator.name}</h6>
                        <p class="card-text">${indicator.value !== null ? indicator.value : '--'}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
        
        <div class="mt-4">
            <h6>AI Prediction</h6>
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Direction:</strong> <span class="${prediction.direction === 'up' ? 'price-up' : 'price-down'}"> 
                                ${prediction.direction === 'up' ? 'Upward' : 'Downward'} 
                                <i class="bi bi-arrow-${prediction.direction === 'up' ? 'up' : 'down'}"></i>
                            </span></p>
                            <p><strong>Expected Return:</strong> <span class="${prediction.predicted_return >= 0 ? 'price-up' : 'price-down'}"> 
                                ${prediction.predicted_return >= 0 ? '+' : ''}${prediction.predicted_return}% 
                            </span></p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Confidence:</strong> ${(prediction.confidence * 100).toFixed(0)}%</p>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar ${prediction.direction === 'up' ? 'progress-bar-bullish' : 'progress-bar-bearish'}" 
                                    role="progressbar" style="width: ${prediction.confidence * 100}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}