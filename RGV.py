from enum import Enum
import queue
from typing import List, Callable


# TODO: Record the A-out as output B-out as input

class Status(Enum):
    Move = 1
    Wait = 2
    Work = 3


class RGV_queue(list):
    def front(self, cur):
        i = self.index(cur)
        return None if i < 0 else self[-1] if i == 0 else self[i - 1]


def time_arrived(p, r):
    return (p.location - r.location) / r.speed


def distance(p, r):
    return p.location - r.location if p.location - r.location > 0 else p.location - r.location + 100


# TODO: Get next RGV destination for the RGV id

class Port:
    identity: int
    location: float
    record_item: queue

    def __init__(self, identity, location, ):
        pass

    def transport(self, r, tick):
        self.record_item.append([r.identity, tick])


def get_target_by_id(id) -> Port:
    # 任务分配
    return 0


class RGV:
    identity: int
    velocity = 1.5
    length = 1.3
    period_work = 10
    tick_fin: float
    tick_rec: float
    stat: Status
    location: float
    target: Port

    def update(self, tick_cur, queue: RGV_queue):
        """
        将RGV状态刷新到当前时刻，由前向后
        :param tick_cur:
        :param queue:
        :return:
        """
        rgv_front: RGV = queue.front(self)
        if tick_cur == self.tick_fin:
            if self.stat == Status.Work:
                # 由于本车最先执行完动作导致的时刻刷新
                self.target = get_target_by_id(self.identity)
                self.stat = Status.Move
                self.tick_fin = distance(self.target, self) / self.velocity
            elif self.stat == Status.Move:
                # 由于移动到位导致的刷新
                self.stat = Status.Work
                self.target.transport(self, tick_cur)
                self.tick_fin += self.period_work
            elif self.stat == Status.Wait:
                # 等待完成导致刷新
                self.stat = Status.Move
                self.tick_fin = distance(self.target, self) / self.velocity
            self.tick_rec = tick_cur
            return self.tick_fin
        elif self.stat == Status.Move:
            # 由于前车已完成update，且自己的移动动作此时也未完成，要考虑前方是否进入等待状态
            approach_dis = (tick_cur - self.tick_rec) * self.velocity
            impact_dis = distance(queue.front(self), self) - self.length
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
        else:
            # 等待状态
            pass
        self.tick_rec = tick_cur
        return self.tick_fin
