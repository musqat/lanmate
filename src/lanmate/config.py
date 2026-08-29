"""프로그램 전체가 공유하는 설정값."""

from pathlib import Path

# --- 네트워크 ---
DISCOVERY_PORT = 50000          # UDP. 서로를 찾는 데 쓴다
TRANSFER_PORT = 50001           # TCP. 채팅과 파일이 오간다

# 브로드캐스트가 무선 쪽으로 안 넘어가면 '192.168.0.255'로 바꿔본다
BROADCAST_ADDR = "255.255.255.255"

BEACON_INTERVAL = 2.0           # 초. 살아있다는 신호를 보내는 주기
PEER_TIMEOUT = 8.0              # 초. 이만큼 조용하면 목록에서 뺀다
REAPER_INTERVAL = 1.0           # 초. 목록을 훑어 정리하는 주기

# --- 파일 전송 ---
CHUNK_SIZE = 64 * 1024          # 한 번에 읽고 쓰는 크기
MAX_HEADER_SIZE = 64 * 1024     # 헤더가 이보다 크면 잘못된 접속으로 본다

# --- 저장 위치 ---
APP_DIR = Path.home() / ".lanchat"
IDENTITY_FILE = APP_DIR / "identity.json"   # 내 고유번호와 별명
DOWNLOAD_DIR = APP_DIR / "downloads"        # 받은 파일은 여기에만 저장한다
