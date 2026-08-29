"""같은 와이파이에서 발견한 상대들을 담아두는 곳."""

import threading
import time
from dataclasses import dataclass

from . import config


@dataclass
class Peer:
    """상대 한 명."""

    uid: str            # 고유번호. IP가 바뀌어도 이건 안 바뀐다
    alias: str          # 화면에 보일 이름
    ip: str
    port: int           # 이 사람의 TCP 포트
    last_seen: float    # 마지막으로 신호를 받은 시각


class PeerRegistry:
    """상대 목록. 여러 스레드가 같이 쓴다."""

    def __init__(self):
        self._peers: dict[str, Peer] = {}
        self._lock = threading.Lock()

    def touch(self, peer: Peer) -> bool:
        """신호를 받았을 때 부른다. 처음 보는 사람이면 True."""
        with self._lock:
            known = self._peers.get(peer.uid)
            if known is None:
                self._peers[peer.uid] = peer
                return True

            # 이미 아는 사람이면 시각만 갱신한다.
            # IP나 별명은 바뀔 수 있으니 최신 값으로 덮어쓴다.
            known.ip = peer.ip
            known.port = peer.port
            known.alias = peer.alias
            known.last_seen = peer.last_seen
            return False

    def reap(self) -> list[Peer]:
        """오래 조용한 사람을 목록에서 뺀다. 뺀 사람들을 돌려준다."""
        now = time.time()
        with self._lock:
            gone_uids = [
                uid
                for uid, peer in self._peers.items()
                if now - peer.last_seen > config.PEER_TIMEOUT
            ]
            return [self._peers.pop(uid) for uid in gone_uids]

    def all(self) -> list[Peer]:
        """지금 목록. 복사본이라 밖에서 만져도 안전하다."""
        with self._lock:
            return list(self._peers.values())


if __name__ == "__main__":
    reg = PeerRegistry()
    someone = Peer("u1", "테스트", "192.168.0.8", 50001, time.time())

    print("처음 등록:", reg.touch(someone))   # True
    print("또 등록:", reg.touch(someone))     # False
    print("목록 수:", len(reg.all()))         # 1

    someone.last_seen = time.time() - 100     # 오래전에 본 걸로 조작
    print("정리된 사람:", reg.reap())
    print("목록 수:", len(reg.all()))         # 0
