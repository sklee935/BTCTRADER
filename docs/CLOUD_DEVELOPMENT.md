# Cloud development guide

이 프로젝트는 로컬 PC에 VS Code를 설치하지 않아도 GitHub Codespaces의 브라우저 IDE에서 개발할 수 있게 구성되어 있습니다.

## 추천 방식

GitHub Codespaces를 1순위로 사용합니다.

- 브라우저에서 VS Code와 비슷한 환경으로 개발합니다.
- `.devcontainer/devcontainer.json`이 Python 개발 환경과 VS Code 확장을 자동 설정합니다.
- OpenAI API Key, 업비트 API Key, 실제 주문 기능은 사용하지 않습니다.
- 업비트 Public API만 사용하므로 지금 단계에서는 별도 비밀값이 필요 없습니다.

## GitHub에 올리는 방법

로컬에 Git이나 VS Code가 없어도 가능합니다.

1. GitHub에서 새 repository를 만듭니다.
2. 공개가 부담되면 `Private`로 만듭니다.
3. 이 프로젝트 압축을 풀고 GitHub 웹 화면의 `Add file` -> `Upload files`로 전체 파일을 업로드합니다.
4. 커밋합니다.
5. repository 화면에서 `Code` -> `Codespaces` -> `Create codespace on main`을 누릅니다.

## Codespaces가 열리면

자동으로 아래 작업이 실행됩니다.

- `config.example.json`을 `config.json`으로 복사
- `data/`, `exports/` 폴더 생성
- 단위 테스트 실행

터미널에서 바로 실행할 수 있는 명령입니다.

```bash
make run-once
make backtest
make test
make summary
make export
```

직접 Python 명령으로 실행해도 됩니다.

```bash
python run_bot.py --config config.json --once
python run_backtest.py --config config.json --pages 5
python -m unittest discover -s tests -v
```

## 비용 0원으로 쓰는 규칙

Codespaces는 무료 한도가 있지만, 켜져 있는 시간 동안 사용량이 쌓입니다.

- 개발할 때만 켭니다.
- 작업이 끝나면 Codespace를 Stop 합니다.
- 사용하지 않는 Codespace는 Delete 합니다.
- 24시간 봇 실행용으로 쓰지 않습니다.
- 가장 작은 기본 머신을 사용합니다.
- `make run`처럼 계속 실행되는 명령은 개발 테스트용으로만 짧게 사용합니다.

## 데이터 보관

SQLite DB는 기본적으로 `data/paper_trading.sqlite3`에 저장됩니다. 이 파일은 `.gitignore`에 포함되어 GitHub에 올라가지 않습니다.

CSV로 추출하려면 다음을 실행합니다.

```bash
make export
```

추출 결과는 `exports/` 폴더에 생성됩니다.

- `candles.csv`
- `events.csv`
- `portfolio_state.csv`

이 CSV를 ChatGPT에 업로드하면 거래 로그 사후 분석에 사용할 수 있습니다.

## 주의할 점

Codespaces는 개발 환경입니다. 실제 자동매매 운영 서버로 쓰기에는 적합하지 않습니다.

- 장시간 실행하면 무료 한도를 소진합니다.
- Codespace를 삭제하면 커밋하지 않은 코드와 `data/`의 SQLite DB가 사라질 수 있습니다.
- 현재 프로젝트는 실제 주문 기능이 없습니다.
- 나중에 실거래로 전환한다면 API Key, IP 제한, Secrets, 권한 분리, 주문 차단 장치를 별도 설계해야 합니다.
