
-- Top 10 best trading days by daily percentage return
SELECT
    trade_date,
    ticker,
    close_price,
    daily_return_pct
FROM read_csv_auto('data/gold/stock_analytics.csv')
WHERE daily_return_pct IS NOT NULL
ORDER BY daily_return_pct DESC
LIMIT 10;

-- Top 10 worst trading days by daily percentage return
SELECT
    trade_date,
    ticker,
    close_price,
    daily_return_pct
FROM read_csv_auto('data/gold/stock_analytics.csv')
WHERE daily_return_pct IS NOT NULL
ORDER BY daily_return_pct ASC
LIMIT 10;
