from xls_tool import *
from itertools import chain
import numpy as np
from time import time
import random
from machine import Port, RGV, RGV_queue, Status

n_rgv = 3
l_rgv = 0
max_generation = 100
child_population = 10

work_in_mat: np.ndarray = np.delete(np.array(read_xls('B题附件1.xlsx', has_head=True)), 0, axis=1).astype(np.int)
work_out_mat: np.ndarray = np.delete(np.array(read_xls('B题附件2.xlsx', has_head=True)), 0, axis=1).astype(np.int)

port_loc = [i * 47 / 6 for i in range(1, 6)] + [50 + i * 47 / 9 for i in range(1, 9)]
port_id = ['AO3', 'AO2', 'AO1', 'AI2', 'AI1', 'BO1', 'BI1', 'BO2', 'BI2', 'BO3', 'BI3', 'BO4', 'BI4']
rgv_loc = [0 - i * l_rgv for i in range(n_rgv)]
rgv_id = [i for i in range(1, n_rgv + 1)]

Ports = [Port(i, l + 47 / 2) for i, l in zip(port_id, port_loc)]
RGVs = RGV_queue([RGV(i, l, l_rgv) for i, l in zip(rgv_id, rgv_loc)])

port_map = [[4, 3], [5, 7, 9, 11], [6, 8, 10, 12], [2, 1, 0]]


def init_plan():
    # Initial plan
    A_queue: List[List] = work_in_mat.tolist()
    B_queue: List[List] = work_out_mat.T.tolist()

    for q in B_queue:
        if 0 in q:
            q.remove(0)

    plan_i_src = list(chain.from_iterable((1, 2) for i in range(100)))
    plan_i_des = list(chain.from_iterable(A_queue))
    plan_o_src = []

    for i_des in plan_i_des:
        if sum(len(q) for q in B_queue[i_des - 1:]):
            o_src = random.randint(i_des, len(B_queue))
            while not B_queue[o_src - 1]:
                o_src = random.randint(i_des, len(B_queue))
            B_queue[o_src - 1].pop()
            plan_o_src.append(o_src)
        else:
            # 非复合作业
            plan_o_src.append(0)

    for i in range(sum(len(q) for q in B_queue)):
        o_src = random.randint(1, len(B_queue))
        while not B_queue[o_src - 1]:
            o_src = random.randint(1, len(B_queue))
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


def reset_rgvs():
    for rgv, init_loc in zip(RGVs, rgv_loc):
        rgv.location = init_loc
        rgv.time_rec = 0
        rgv.time_wait = 0
        rgv.freq_wait = 0


def swap(i, j, ls: list):
    t = ls[i][2]
    ls[i][2] = ls[j][2]
    ls[j][2] = t


def mutation_point_3_change(plan_parent):
    plan_children = []
    mutate_locations = random.sample(range(len(plan_parent)), child_population * 2)
    for i in range(child_population):
        plan_child = plan_parent.copy()
        a, b = mutate_locations[i], mutate_locations[i + child_population]
        if plan_child[b][1] > plan_child[a][2] or plan_child[a][1] > plan_child[b][2]:
            # 直接丢弃该垃圾方案
            continue
        swap(a, b, plan_child)
        plan_children.append(plan_child)
    return plan_children


def mutation_regenerate(plan_parent):
    return [init_plan() for i in range(child_population)]


def generation():
    g_count = 0
    plan = init_plan()
    while g_count < max_generation:
        mutated_plans = mutation_point_3_change(plan)
        mutated_plans.append(plan)
        plan = min(mutated_plans, key=lambda x: simulate(x))
        print(f"\rGeneration: {g_count}", end="")
        g_count += 1
    return plan, simulate(plan)


def simulate(cur_plan, display=False):
    reset_rgvs()
    plan_list: List[List[int]] = []
    for j in range(n_rgv):
        plan_list.append(list(chain.from_iterable(cur_plan[i] for i in range(j, len(cur_plan), n_rgv))))
    cur_step = [-1 for i in range(n_rgv)]

    def allocate_target(target_id) -> Port or None:
        cur_step[target_id - 1] += 1
        if cur_step[target_id - 1] >= len(plan_list[target_id - 1]):
            return None
        while plan_list[target_id - 1][cur_step[target_id - 1]] == 0:
            cur_step[target_id - 1] += 1
        idx = cur_step[target_id - 1]
        # 由port_map计算出所到转运口index
        return Ports[port_map[idx % 4][plan_list[target_id - 1][idx] - 1]]

    for rgv in RGVs:
        rgv.start(allocate_target(rgv.identity))

    tick = 0
    while still_running():
        tick = min(RGVs, key=lambda x: x.tick_fin).tick_fin
        for rgv in RGVs:
            rgv.update(tick, RGVs, allocate_target, display)
    if display:
        print(f"Simulation Finished: {tick:.2f}s")
        # sum(map(lambda x: x.freq_wait, RGVs))
    return tick


if __name__ == "__main__":
    time_start = time()
    result = generation()
    time_end = time()
    print(f"\nTime cost: {time_end - time_start:.2f}")
    print(f"Result: {result}")
    pass
