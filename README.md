# lanmate

같은 와이파이에 있는 사람끼리 채팅하고 파일을 주고받는다.
서버가 없다. 각자의 프로그램이 서로를 직접 찾아 연결한다.

## 어떻게 찾는가

2초마다 UDP 브로드캐스트로 "나 여기 있다"를 뿌린다.
같은 신호를 받으면 목록에 넣고, 8초 동안 조용하면 뺀다.

대화와 파일은 TCP로 1:1 연결을 맺어 주고받는다.

| 포트 | 용도 |
|---|---|
| UDP 50000 | 서로 찾기 |
| TCP 50001 | 채팅, 파일 전송 |

## 실행
<details>

```bash
uv sync
uv run python -m lanmate.discovery
```

한 PC에서 두 개를 띄워 시험하려면 별명을 인자로 준다.

```bash
uv run python -m lanmate.discovery 개미
uv run python -m lanmate.discovery 베짱이
```
</details>

## 진행 상황

- [x] 서로 찾기
- [ ] 채팅
- [ ] 파일 전송
- [ ] 화면
- [ ] exe 만들기

## 안 될 때

- 첫 실행에서 방화벽 팝업이 뜨면 "개인 네트워크"를 체크하고 허용한다
- 한쪽만 보이면 `config.py`의 `BROADCAST_ADDR`를 `192.168.0.255`처럼 내 대역 주소로 바꾼다
- 공유기에 AP 격리가 켜져 있으면 무선끼리 통신이 막힌다
