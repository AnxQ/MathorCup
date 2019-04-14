from xls_tool import *
from itertools import chain
import numpy as np
from queue import Queue
from random import randint
from machine import Port, RGV, RGV_queue, Status

work_in_mat: np.ndarray = np.delete(np.array(read_xls('B题附件1.xlsx', has_head=True)), 0, axis=1).astype(np.int)
work_out_mat: np.ndarray = np.delete(np.array(read_xls('B题附件2.xlsx', has_head=True)), 0, axis=1).astype(np.int)
n_rgv = 9
l_rgv = 1.30

A_queue: List[List] = work_in_mat.tolist()
B_queue: List[List] = work_out_mat.T.tolist()

for q in B_queue:
    if 0 in q:
        q.remove(0)

port_loc = [i * 47 / 6 for i in range(1, 6)] + [50 + i * 47 / 9 for i in range(1, 9)]
port_id = ['AO3', 'AO2', 'AO1', 'AI2', 'AI1', 'BO1', 'BI1', 'BO2', 'BI2', 'BO3', 'BI3', 'BO4', 'BI4']
rgv_loc = [0 - i * l_rgv for i in range(n_rgv)]
rgv_id = [i for i in range(1, n_rgv + 1)]
Ports = [Port(i, l + 47 / 2) for i, l in zip(port_id, port_loc)]
RGVs = RGV_queue([RGV(i, l) for i, l in zip(rgv_id, rgv_loc)])

port_map = [
    [4, 3],
    [5, 7, 9, 11],
    [6, 8, 10, 12],
    [2, 1, 0]
]


def init_plan():
    # Initial plan
    plan_i_src = list(chain.from_iterable((1, 2) for i in range(100)))
    plan_i_des = list(chain.from_iterable(A_queue))
    plan_o_src = []

    for i_des in plan_i_des:
        if sum(len(q) for q in B_queue[i_des - 1:]):
            o_src = randint(i_des, len(B_queue))
            while not B_queue[o_src - 1]:
                o_src = randint(i_des, len(B_queue))
            B_queue[o_src - 1].pop()
            plan_o_src.append(o_src)
        else:
            # 非复合作业
            plan_o_src.append(0)

    for i in range(sum(len(q) for q in B_queue)):
        o_src = randint(1, len(B_queue))
        while not B_queue[o_src - 1]:
            o_src = randint(1, len(B_queue))
        B_queue[o_src - 1].pop()
        plan_o_src.append(o_src)

    plan_o_des = [0 if plan_o_src[i] == 0 else i % 3 + 1 for i in range(len(plan_o_src))]
    plan = []

    head_len = len(plan_i_src)
    tail_len = len(plan_o_src)

    for i in range(tail_len):
        plan.append([
            plan_i_src[i] if i < head_len else 0,
            plan_i_des[i] if i < head_len else 0,
            plan_o_src[i],
            plan_o_des[i]
        ])
    return plan


def still_running() -> bool:
    for rgv in RGVs:
        if rgv.stat is not Status.Idle:
            return True
    return False


def mutation(len):
    init_mutation = [randint(0, 1) for i in range(len)]
    yield init_mutation
    while True:
        yield


def generation():
    pass


def simulate(plan):
    plan_list = []
    for j in range(n_rgv):
        plan_list.append(list(chain.from_iterable(plan[i] for i in range(j, len(plan), n_rgv))))
    cur_step = [-1 for i in range(n_rgv)]

    print(plan_list[0])
    print(plan_list[1])
    print(plan_list[2])

    def allocate_target(id) -> Port:
        cur_step[id - 1] += 1
        if cur_step[id - 1] >= len(plan_list[id - 1]):
            return None
        while plan_list[id - 1][cur_step[id - 1]] == 0:
            cur_step[id - 1] += 1
        idx = cur_step[id - 1]
        # 由port_map计算出所到转运口index
        return Ports[port_map[idx % 4][plan_list[id - 1][idx] - 1]]

    for i in range(n_rgv):
        RGVs[i].start(allocate_target(i+1))

    tick = 0
    while still_running():
        tick = min(RGVs, key=lambda x: x.tick_fin).tick_fin
        for rgv in RGVs:
            rgv.update(tick, RGVs, allocate_target)


if __name__ == "__main__":
    plan = init_plan()
    simulate(plan)
    pass
