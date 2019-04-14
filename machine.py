from enum import Enum
import queue
from typing import List, Callable


# TODO: Record the A-out as output B-out as input

class Status(Enum):
    Move = 1
    Wait = 2
    Work = 3
    Idle = 0


class RGV_queue(list):
    def __init__(self, *iter):
        super().__init__(*iter)

    def front(self, cur):
        i = self.index(cur)
        return None if i < 0 else self[-1] if i == 0 else self[i - 1]


def time_arrived(p, r):
    return (p.location - r.location) / r.speed


def distance(p, r):
    return p.location - r.location if p.location - r.location > 0 else p.location - r.location + 100


# TODO: Get next RGV destination for the RGV id

class Port:
    identity: str
    location: float
    _I_O: bool

    def __repr__(self):
        return f"<ID:{self.identity}, Location:{self.location:.2f}>"

    def __init__(self, identity, location):
        self.identity = identity
        self.location = location
        self._I_O = True if 'I' in self.identity else False

    def transport(self, r, tick, display):
        if display:
            if self._I_O:
                print(f"{tick:.2f}: Port:{self.identity} Import into RGV:{r.identity}")
            else:
                print(f"{tick:.2f}: Port:{self.identity} Export from RGV:{r.identity}")


class RGV:
    identity: int
    velocity = 1.5
    length = 1.3
    period_work = 10
    tick_fin: float = 0
    tick_rec: float = 0
    stat: Status = Status.Idle
    location: float
    target: Port

    def __repr__(self):
        return f"<ID:{self.identity}, Location:{self.location:.2f}, Status:{self.stat.name}, Target:{self.target}>"

    def __init__(self, identity, location):
        self.identity = identity
        self.location = location

    def start(self, target):
        self.target = target
        self.tick_fin = distance(target, self) / self.velocity
        self.stat = Status.Move


    def update(self, tick_cur, queue: RGV_queue, get_target: Callable, display=False):
        """
        将RGV状态刷新到当前时刻，由前向后
        :param tick_cur:
        :param queue:
        :param get_target:
        :return:
        """
        rgv_front: RGV = queue.front(self)
        if tick_cur == self.tick_fin:
            if self.stat == Status.Work:
                # 由于本车最先执行完动作导致的时刻刷新
                self.target = get_target(self.identity)
                if not self.target:
                    self.stat = Status.Idle
                    self.tick_fin = rgv_front.tick_fin
                    return
                self.stat = Status.Move
                self.tick_fin = tick_cur + distance(self.target, self) / self.velocity
            elif self.stat == Status.Move:
                # 由于移动到位导致的刷新
                self.stat = Status.Work
                self.target.transport(self, tick_cur, display)
                self.tick_fin = tick_cur + self.period_work
            elif self.stat == Status.Wait:
                # 等待完成导致刷新
                self.stat = Status.Move
                self.tick_fin = tick_cur + distance(self.target, self) / self.velocity
            else:
                self.location = (rgv_front.location - self.length) % 100
                self.tick_fin = rgv_front.tick_fin
            self.tick_rec = tick_cur
            return self.tick_fin
        elif self.stat == Status.Move:
            # 由于前车已完成update，且自己的移动动作此时也未完成，要考虑前方是否进入等待状态
            approach_dis = (tick_cur - self.tick_rec) * self.velocity
            impact_dis = distance(rgv_front, self) - self.length
            if impact_dis < approach_dis:
                # 获取前方预计等待时间 决定自己的tick_fin(此时为等待完成时间) 置入等待状态
                # 这会导致完成时间提前/延后 因此需要之后以等待完成位置再次计算移动完成时间
                self.stat = Status.Wait
                self.location = (self.location + impact_dis) % 100
                self.tick_fin = rgv_front.tick_fin - impact_dis / self.velocity
            else:
                # 不遇前车的情况 直接选择前进 不修改完成时刻
                self.location = (self.location + approach_dis) % 100
        elif self.stat == Status.Work:
            # 尚在工作,且未完成
            pass
        elif self.stat == Status.Wait:
            # 等待状态
            pass
        else:
            self.location = (rgv_front.location - self.length) % 100
            self.tick_fin = rgv_front.tick_fin
        self.tick_rec = tick_cur
        return self.tick_fin
