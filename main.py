from xls_tool import *
import numpy as np

work_in_mat = np.array(read_xls('B题附件1.xls', has_head=True)).T
work_out_mat = np.array(read_xls('B题附件2.xls', has_head=True)).T

A1_queue = work_in_mat.T[1].tolist()
A2_queue = work_in_mat.T[2].tolist()

B1_queue = work_out_mat.T[1].tolist()
B2_queue = work_out_mat.T[2].tolist()
B3_queue = work_out_mat.T[3].tolist()
B4_queue = work_out_mat.T[4].tolist()


def simulate():
    pass


if __name__ == "__main__":
    pass
