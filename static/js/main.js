document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const analysisForm = document.getElementById('analysisForm');
    const stockSymbol = document.getElementById('stockSymbol');
    const timeframe = document.getElementById('timeframe');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const analysisResults = document.getElementById('analysisResults');
    const popularStocksList = document.getElementById('popularStocksList');
    const symbolLookup = document.getElementById('symbolLookup');
    const symbolModal = new bootstrap.Modal(document.getElementById('symbolModal'));
    const symbolSearch = document.getElementById('symbolSearch');
    const searchButton = document.getElementById('searchButton');
    const symbolResults = document.getElementById('symbolResults');

    // Load popular stocks
    loadPopularStocks();

    // Event listeners
    analysisForm.addEventListener('submit', function(e) {
        e.preventDefault();
        analyzeStock(stockSymbol.value, timeframe.value);
    });

    popularStocksList.addEventListener('click', function(e) {
        if (e.target.classList.contains('stock-item') || e.target.parentElement.classList.contains('stock-item')) {
            const item = e.target.classList.contains('stock-item') ? e.target : e.target.parentElement;
            const symbol = item.dataset.symbol;
            stockSymbol.value = symbol;
            analyzeStock(symbol, timeframe.value);
        }
    });

    symbolLookup.addEventListener('click', function() {
        symbolModal.show();
    });

    searchButton.addEventListener('click', function() {
        searchSymbols(symbolSearch.value);
    });

    symbolSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchSymbols(symbolSearch.value);
        }
    });

    symbolResults.addEventListener('click', function(e) {
        if (e.target.classList.contains('symbol-item') || e.target.parentElement.classList.contains('symbol-item')) {
            const item = e.target.classList.contains('symbol-item') ? e.target : e.target.parentElement;
            const symbol = item.dataset.symbol;
            stockSymbol.value = symbol;
            symbolModal.hide();
        }
    });

    // Functions
    function loadPopularStocks() {
        fetch('/symbols')
            .then(response => response.json())
            .then(data => {
                popularStocksList.innerHTML = '';
                data.forEach(stock => {
                    const item = document.createElement('a');
                    item.href = '#';
                    item.className = 'list-group-item list-group-item-action stock-item';
                    item.dataset.symbol = stock.symbol;
                    item.innerHTML = `
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${stock.name}</h6>
                            <small>${stock.symbol}</small>
                        </div>
                    `;
                    popularStocksList.appendChild(item);
                });
            })
            .catch(error => {
                console.error('Error loading popular stocks:', error);
                popularStocksList.innerHTML = '<div class="alert alert-danger">Failed to load popular stocks</div>';
            });
    }

    function searchSymbols(query) {
        if (!query || query.trim() === '') {
            symbolResults.innerHTML = '<div class="alert alert-info">Please enter a search term</div>';
            return;
        }

        symbolResults.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> Searching...</div>';

        // This is a simplified example. In a real app, you would call an API endpoint
        // For now, we'll just show some dummy results
        setTimeout(() => {
            const dummyResults = [
                { symbol: 'RELIANCE.NS', name: 'Reliance Industries Ltd.' },
                { symbol: 'TCS.NS', name: 'Tata Consultancy Services Ltd.' },
                { symbol: 'INFY.NS', name: 'Infosys Ltd.' },
                { symbol: 'HDFCBANK.NS', name: 'HDFC Bank Ltd.' },
                { symbol: 'ICICIBANK.NS', name: 'ICICI Bank Ltd.' }
            ].filter(item => 
                item.symbol.toLowerCase().includes(query.toLowerCase()) || 
                item.name.toLowerCase().includes(query.toLowerCase())
            );

            if (dummyResults.length === 0) {
                symbolResults.innerHTML = '<div class="alert alert-warning">No results found</div>';
                return;
            }

            symbolResults.innerHTML = '';
            dummyResults.forEach(stock => {
                const item = document.createElement('a');
                item.href = '#';
                item.className = 'list-group-item list-group-item-action symbol-item';
                item.dataset.symbol = stock.symbol;
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${stock.name}</h6>
                        <small>${stock.symbol}</small>
                    </div>
                `;
                symbolResults.appendChild(item);
            });
        }, 500);
    }

    function analyzeStock(symbol, period) {
        if (!symbol || symbol.trim() === '') {
            showError('Please enter a stock symbol');
            return;
        }

        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        analysisResults.classList.add('d-none');
        errorMessage.classList.add('d-none');

        // Make API request
        fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol: symbol,
                timeframe: period
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to analyze stock');
                });
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
            // Load chart data for dashboard
            loadChartData(symbol, period);
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            loadingIndicator.classList.add('d-none');
        });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        analysisResults.classList.add('d-none');
        loadingIndicator.classList.add('d-none');
    }

    function displayResults(data) {
        // Update stock title
        document.getElementById('stockTitle').textContent = data.symbol;

        // Update current price
        document.getElementById('currentPrice').textContent = `₹${data.current_price.toFixed(2)}`;

        // Update recommendation
        const recommendation = data.recommendation.verdict;
        const confidence = data.recommendation.confidence;
        const reasons = data.recommendation.reasons;

        document.getElementById('recommendationText').textContent = recommendation;
        document.getElementById('recommendationBadge').textContent = recommendation;
        document.getElementById('confidenceText').textContent = `${confidence}% confidence`;
        document.getElementById('confidenceBar').style.width = `${confidence}%`;

        // Set recommendation badge color
        const badgeElement = document.getElementById('recommendationBadge');
        badgeElement.className = 'badge';
        if (recommendation === 'BUY') {
            badgeElement.classList.add('badge-buy');
            document.getElementById('confidenceBar').className = 'progress-bar progress-bar-buy';
        } else if (recommendation === 'STRONG BUY') {
            badgeElement.classList.add('badge-strong-buy');
            document.getElementById('confidenceBar').className = 'progress-bar progress-bar-buy';
        } else if (recommendation === 'SELL') {
            badgeElement.classList.add('badge-sell');
            document.getElementById('confidenceBar').className = 'progress-bar progress-bar-sell';
        } else if (recommendation === 'STRONG SELL') {
            badgeElement.classList.add('badge-strong-sell');
            document.getElementById('confidenceBar').className = 'progress-bar progress-bar-sell';
        } else {
            badgeElement.classList.add('badge-hold');
            document.getElementById('confidenceBar').className = 'progress-bar progress-bar-hold';
        }

        // Update reasons list
        const reasonsList = document.getElementById('reasonsList');
        reasonsList.innerHTML = '';
        reasons.forEach(reason => {
            const item = document.createElement('li');
            item.className = 'list-group-item';
            
            // Determine if reason is bullish, bearish, or neutral
            if (reason.includes('bullish') || reason.includes('positive') || reason.includes('oversold')) {
                item.classList.add('reason-bullish');
            } else if (reason.includes('bearish') || reason.includes('negative') || reason.includes('overbought')) {
                item.classList.add('reason-bearish');
            } else {
                item.classList.add('reason-neutral');
            }
            
            item.textContent = reason;
            reasonsList.appendChild(item);
        });

        // Update technical indicators
        const technicalIndicators = document.getElementById('technicalIndicators');
        technicalIndicators.innerHTML = '';
        
        // Moving Averages
        const ma = data.analysis.moving_averages;
        if (ma) {
            addIndicatorRow(technicalIndicators, 'SMA (20)', `₹${ma.sma_20.toFixed(2)}`, ma.price_above_sma_20 ? 'positive' : 'negative');
            addIndicatorRow(technicalIndicators, 'SMA (50)', `₹${ma.sma_50.toFixed(2)}`, ma.price_above_sma_50 ? 'positive' : 'negative');
            if (ma.sma_200) {
                addIndicatorRow(technicalIndicators, 'SMA (200)', `₹${ma.sma_200.toFixed(2)}`, ma.price_above_sma_200 ? 'positive' : 'negative');
            }
        }
        
        // RSI
        const rsi = data.analysis.rsi;
        if (rsi) {
            let rsiStatus = 'neutral';
            if (rsi.overbought) rsiStatus = 'negative';
            if (rsi.oversold) rsiStatus = 'positive';
            addIndicatorRow(technicalIndicators, 'RSI', rsi.value.toFixed(2), rsiStatus);
        }
        
        // MACD
        const macd = data.analysis.macd;
        if (macd) {
            addIndicatorRow(technicalIndicators, 'MACD', macd.macd.toFixed(2), macd.macd_positive ? 'positive' : 'negative');
            addIndicatorRow(technicalIndicators, 'MACD Signal', macd.signal.toFixed(2), macd.macd_above_signal ? 'positive' : 'negative');
        }

        // Update AI prediction
        const aiPrediction = document.getElementById('aiPrediction');
        aiPrediction.innerHTML = '';
        
        const prediction = data.prediction;
        if (prediction) {
            addIndicatorRow(aiPrediction, 'Direction', prediction.direction.toUpperCase(), prediction.direction === 'up' ? 'positive' : 'negative');
            addIndicatorRow(aiPrediction, 'Confidence', `${(prediction.confidence * 100).toFixed(0)}%`, prediction.confidence > 0.7 ? 'positive' : (prediction.confidence < 0.5 ? 'negative' : 'neutral'));
            addIndicatorRow(aiPrediction, 'Predicted Return', `${prediction.predicted_return.toFixed(2)}%`, prediction.predicted_return > 0 ? 'positive' : 'negative');
            if (prediction.prediction_date) {
                addIndicatorRow(aiPrediction, 'Prediction Date', prediction.prediction_date, 'neutral');
            }
        }

        // Initialize price chart
        initializeChart(data.symbol, data.chart_data);

        // Show results
        analysisResults.classList.remove('d-none');
    }

    function addIndicatorRow(table, label, value, status) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${label}</td>
            <td class="text-end indicator-${status}">${value}</td>
        `;
        table.appendChild(row);
    }

    // Load chart data for a stock
    function loadChartData(symbol, timeframe) {
        fetch('/chart-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol, timeframe })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading chart data:', data.error);
                return;
            }
            
            // Initialize chart with data
            initializeChart(symbol, data);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
    }

    // Initialize price chart
    function initializeChart(symbol, chartData) {
        // Check if ApexCharts is available
        if (typeof ApexCharts === 'undefined') {
            // Load ApexCharts if not available
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/apexcharts';
            script.onload = function() {
                createChart(symbol, chartData);
            };
            document.head.appendChild(script);
        } else {
            createChart(symbol, chartData);
        }
    }

    // Create price chart
    function createChart(symbol, chartData) {
        const chartElement = document.getElementById('priceChart');
        if (!chartElement) return;
        
        // Clear previous chart if any
        chartElement.innerHTML = '';
        
        // Prepare candlestick data
        const ohlc = chartData.dates.map((date, i) => ({
            x: new Date(date),
            y: [
                chartData.prices.open[i],
                chartData.prices.high[i],
                chartData.prices.low[i],
                chartData.prices.close[i]
            ]
        }));
        
        // Prepare volume data
        const volume = chartData.dates.map((date, i) => ({
            x: new Date(date),
            y: chartData.volume[i]
        }));
        
        // Chart options
        const options = {
            series: [{
                name: 'Price',
                type: 'candlestick',
                data: ohlc
            }],
            chart: {
                height: 400,
                type: 'candlestick',
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
                text: `${symbol} Stock Price`,
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
            }
        };
        
        // Create chart
        const chart = new ApexCharts(chartElement, options);
        chart.render();
    }
});