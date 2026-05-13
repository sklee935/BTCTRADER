# Free BTC Paper Trading Bot

비용 0원 목표로 시작하는 **업비트 BTC/KRW 모의 자동매매 MVP**입니다.

이 프로젝트는 다음 원칙을 지킵니다.

- OpenAI API를 사용하지 않습니다.
- 업비트 Public API만 사용합니다.
- 실제 주문을 넣지 않습니다.
- API Key가 필요 없습니다.
- Python 표준 라이브러리만 사용합니다.
- 기본 실행은 모의거래입니다.

> 주의: 이 코드는 투자 조언이 아니며, 실거래용이 아닙니다. 실제 주문 기능은 일부러 포함하지 않았습니다.

## 구조

```text
free_btc_paper_bot/
  config.example.json
  run_bot.py
  run_backtest.py
  src/free_btc_bot/
    bot.py
    upbit_public.py
    strategy.py
    risk.py
    paper_broker.py
    storage.py
    indicators.py
    models.py
    config.py
  scripts/
    export_logs.py
    db_summary.py
  docs/
    CLOUD_DEVELOPMENT.md
  .devcontainer/
    devcontainer.json
  .vscode/
    tasks.json
    launch.json
  tests/
```


## 브라우저 클라우드 개발

로컬 PC에 VS Code가 없어도 GitHub Codespaces에서 개발할 수 있게 설정되어 있습니다.

```text
GitHub Repository -> Code -> Codespaces -> Create codespace on main
```

Codespaces가 열리면 자동으로 `config.json` 생성과 단위 테스트가 실행됩니다. 이후 터미널에서 아래 명령을 사용할 수 있습니다.

```bash
make run-once
make backtest
make test
make summary
make export
```

자세한 절차는 `docs/CLOUD_DEVELOPMENT.md`를 참고하세요.

> 비용 주의: Codespaces는 개발용으로만 짧게 사용하세요. 켜져 있는 동안 무료 사용량이 차감되므로 24시간 봇 운영에는 적합하지 않습니다.

## 설치

Python 3.10 이상을 권장합니다.

외부 패키지가 필요 없으므로 바로 실행할 수 있습니다.

```bash
cd free_btc_paper_bot
python run_bot.py --once
```

## 설정

기본 설정 파일을 복사합니다.

```bash
cp config.example.json config.json
```

`config.json`에서 아래 값을 조정할 수 있습니다.

```json
{
  "market": "KRW-BTC",
  "candle_unit": 5,
  "poll_seconds": 60,
  "initial_cash": 1000000,
  "fee_rate": 0.0005,
  "slippage_rate": 0.0005,
  "max_position_ratio": 0.3,
  "max_trade_ratio": 0.1,
  "max_daily_loss_ratio": 0.02,
  "min_confidence": 0.6,
  "stop_loss_pct": 0.02,
  "take_profit_pct": 0.04,
  "dry_run": true
}
```

## 1회 실행 테스트

```bash
python run_bot.py --config config.json --once
```

정상 동작하면 다음과 비슷한 로그가 나옵니다.

```text
[2026-05-12T10:00:00] KRW-BTC price=143,000,000 equity=1,000,000 cash=1,000,000 btc=0.00000000
signal=HOLD confidence=0.50 reason=...
risk=HOLD signal
```

## 계속 실행

```bash
python run_bot.py --config config.json
```

중지하려면 `Ctrl+C`를 누르세요.

## 백테스트

최근 분봉 데이터를 업비트 Public API에서 받아서 간단한 백테스트를 실행합니다.

```bash
python run_backtest.py --config config.json --pages 5
```

업비트 분봉 API는 1회 최대 200개 캔들을 반환하므로, `--pages 5`는 최대 약 1,000개 캔들을 가져오려고 시도합니다.

## 데이터 저장 위치

기본 SQLite DB:

```text
data/paper_trading.sqlite3
```

저장되는 항목:

- 캔들 데이터
- 모의 포트폴리오 상태
- 매매 판단 로그
- 모의 체결 로그

## 비용 검토

이 MVP 기준 개인 지출은 0원에 가깝습니다.

| 항목 | 비용 |
|---|---:|
| Python | 0원 |
| SQLite | 0원 |
| 업비트 Public API | 0원 |
| OpenAI API | 사용 안 함 |
| 실제 주문 | 사용 안 함 |
| 서버 | 내 PC 또는 Codespaces 무료 한도 내 사용 |

다만 PC를 계속 켜두면 전기료는 발생할 수 있고, Codespaces는 켜져 있는 동안 무료 사용량이 차감됩니다. 실거래로 전환하면 거래 수수료, 스프레드, 슬리피지, 세금 가능성이 생깁니다.

## 다음 개발 단계

1. 모의거래 로그를 며칠간 쌓기
2. `data/paper_trading.sqlite3` 또는 CSV 추출 결과를 ChatGPT에 업로드해서 사후 분석
3. 전략 개선
4. 손절/익절/쿨다운 강화
5. 충분한 검증 후에도 실거래 전환은 별도 프로젝트에서 API Key, 권한, 보안을 다시 설계

