# Barbotine Arbitrage Bot 设置指南

## 1. 安装依赖

```bash
cd barbotine-arbitrage-bot
pip3 install -r requirements.txt
```

## 2. 配置交易所（exchange_config.py）

修改 `exchange_config.py` 文件：

```python
exchanges = {
    'binance':{
        'apiKey':'你的Binance测试网API Key',
        'secret':'你的Binance测试网Secret',
        'options': {
            'defaultType': 'spot',
            'urls': {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }
        }
    },
    'bybit':{
        'apiKey':'你的Bybit测试网API Key',
        'secret':'你的Bybit测试网Secret',
        'options': {
            'testnet': True
        }
    },
}
```

## 3. 运行测试模式

使用虚拟资金模式（bot-fake-money.py）：

```bash
python3 bot-fake-money.py BTC/USDT 1000 60 "测试套利" binance,bybit
```

参数说明：
- `BTC/USDT` - 交易对
- `1000` - 虚拟投资金额（USDT）
- `60` - 运行时长（分钟）
- `"测试套利"` - Telegram消息标题（可选）
- `binance,bybit` - 使用的交易所列表

## 4. 监控和优化

1. **查看日志**：
   - 日志文件在 `logs/` 目录
   - 实时输出会显示套利机会

2. **调整参数**：
   ```python
   criteria_pct = 0.3  # 最小利润百分比
   criteria_usd = 1    # 最小利润金额(USD)
   ```

3. **添加更多交易对**：
   - 可以同时运行多个交易对
   - 建议从流动性高的开始：BTC/USDT, ETH/USDT

## 5. 从测试到实盘

当测试模式运行稳定后：
1. 获取主网API密钥
2. 移除测试网配置
3. 使用 `main.py` 运行实盘
4. 从小额开始逐步增加

## 注意事项

- 测试模式会模拟真实交易延迟
- 注意两个交易所的最小交易限额
- 建议先运行24小时观察表现