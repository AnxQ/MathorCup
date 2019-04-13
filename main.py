from xls_tool import *
from itertools import chain
import numpy as np
from queue import Queue
from random import randint
from

work_in_mat = np.delete(np.array(read_xls('B题附件1.xlsx', has_head=True)), 0, axis=1).astype(np.int)
work_out_mat = np.delete(np.array(read_xls('B题附件2.xlsx', has_head=True)), 0, axis=1).astype(np.int)

A_queue: List[List] = work_in_mat.tolist()
B_queue: List[List] = work_out_mat.T.tolist()

for q in B_queue:
    if 0 in q:
        q.remove(0)

port_loc = [i * 47 / 6 for i in range(1, 6)] + [50 + i * 47 / 9 for i in range(1, 9)]
Port_queue =


def init_plan():
    # Example plan
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


def generation():
    pass


def simulate():
    pass


if __name__ == "__main__":
    init_plan()
    pass
