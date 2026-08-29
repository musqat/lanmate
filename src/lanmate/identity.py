"""고유번호와 별명 설정"""

import json
import socket
import uuid

from . import config


def load_identity() -> dict:
    # 1. 파일이 이미 있으면 읽어서 돌려준다
    if config.IDENTITY_FILE.exists():
        return json.loads(config.IDENTITY_FILE.read_text(encoding="utf-8"))

    # 2. 없으면 새로 만든다
    identity = {
        'uid': str(uuid.uuid4()),
        'alias': socket.gethostname(),
    }

    # 3. 저장한다 (폴더가 없을 수 있다)
    config.APP_DIR.mkdir(parents=True, exist_ok=True)
    config.IDENTITY_FILE.write_text(json.dumps(identity), encoding="utf-8")

    return identity


if __name__ == "__main__":
    me = load_identity()
    print(type(me), me)