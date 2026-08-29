"""같은 와이파이에 누가 있는지 찾고, 나도 알린다.

UDP 브로드캐스트를 2초마다 뿌리고, 남이 뿌린 것도 받는다.
"""

import json
import socket
import threading
import time
from typing import Callable

from . import config
from .peer import Peer, PeerRegistry


class Discovery:
    def __init__(
        self,
        uid: str,
        alias: str,
        registry: PeerRegistry,
        on_join: Callable[[Peer], None] | None = None,
        on_leave: Callable[[Peer], None] | None = None,
    ):
        self.uid = uid
        self.alias = alias
        self.registry = registry
        self.on_join = on_join
        self.on_leave = on_leave

        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    # --- 켜고 끄기 -------------------------------------------------

    def start(self):
        for target in (self._beacon_loop, self._listen_loop, self._reap_loop):
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            self._threads.append(thread)

    def stop(self):
        self._stop.set()

    # --- 내가 여기 있다고 알리기 -------------------------------------

    def _beacon_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        payload = json.dumps({
            "uid": self.uid,
            "alias": self.alias,
            "port": config.TRANSFER_PORT,
        }).encode("utf-8")

        with sock:
            while not self._stop.is_set():
                try:
                    sock.sendto(payload, (config.BROADCAST_ADDR, config.DISCOVERY_PORT))
                except OSError as e:
                    print(f"[신호 실패] {e}")
                self._stop.wait(config.BEACON_INTERVAL)

    # --- 남의 신호 받기 ---------------------------------------------

    def _listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", config.DISCOVERY_PORT))
        sock.settimeout(1.0)

        with sock:
            while not self._stop.is_set():
                try:
                    data, addr = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break

                peer = self._parse(data, addr[0])
                if peer is None:
                    continue

                if self.registry.touch(peer) and self.on_join:
                    self.on_join(peer)

    def _parse(self, data: bytes, ip: str) -> Peer | None:
        """받은 패킷을 Peer 로 바꾼다. 이상하면 None."""
        try:
            msg = json.loads(data.decode("utf-8"))
            uid = msg["uid"]
            alias = msg["alias"]
            port = int(msg["port"])
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return None

        if uid == self.uid:
            return None      # 내가 뿌린 게 나한테도 온다

        return Peer(uid=uid, alias=alias, ip=ip, port=port, last_seen=time.time())

    # --- 조용해진 사람 정리 -----------------------------------------

    def _reap_loop(self):
        while not self._stop.is_set():
            for peer in self.registry.reap():
                if self.on_leave:
                    self.on_leave(peer)
            self._stop.wait(config.REAPER_INTERVAL)


if __name__ == "__main__":
    import sys
    import uuid

    from .identity import load_identity

    # 인자로 별명을 주면 임시 신분으로 돈다. 한 PC에서 두 개 띄워 시험할 때 쓴다.
    if len(sys.argv) > 1:
        me = {"uid": str(uuid.uuid4()), "alias": sys.argv[1]}
    else:
        me = load_identity()

    print(f"나: {me['alias']} ({me['uid'][:8]})  - Ctrl+C 로 종료")

    discovery = Discovery(
        uid=me["uid"],
        alias=me["alias"],
        registry=PeerRegistry(),
        on_join=lambda p: print(f"[발견] {p.alias}  {p.ip}:{p.port}"),
        on_leave=lambda p: print(f"[퇴장] {p.alias}"),
    )
    discovery.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        discovery.stop()
        print("종료")
