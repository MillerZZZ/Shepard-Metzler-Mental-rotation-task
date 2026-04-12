import numpy as np
import random
from warnings import deprecated

class StimulusGenerator:
    def __init__(self):
        self.directions = [
            np.array([1, 0, 0]), np.array([-1, 0, 0]),
            np.array([0, 1, 0]), np.array([0, -1, 0]),
            np.array([0, 0, 1]), np.array([0, 0, -1])
        ]

    def _is_orthogonal(self, dir1, dir2):
        return np.dot(dir1, dir2) == 0

    def generate_topology(self, total_cubes=10, num_bends=3):
        max_retries = 3000 # 因为增加了纯 3D 约束，提高重试次数
        segments = num_bends + 1
        min_required = 1 + segments
        if total_cubes < min_required:
            raise ValueError(f"方块数不足！{num_bends} 个弯折至少需要 {min_required} 个方块。")

        for _ in range(max_retries):
            blocks_to_add = [1] * segments
            extra_cubes = total_cubes - min_required
            for _ in range(extra_cubes):
                blocks_to_add[random.randint(0, segments - 1)] += 1

            coords = [np.array([0, 0, 0])]
            current_dir = random.choice(self.directions)
            valid_structure = True

            for i, add_count in enumerate(blocks_to_add):
                if i > 0:
                    possible_dirs = [d for d in self.directions if self._is_orthogonal(d, current_dir)]
                    current_dir = random.choice(possible_dirs)

                for _ in range(add_count):
                    new_pos = coords[-1] + current_dir
                    if any(np.array_equal(new_pos, c) for c in coords):
                        valid_structure = False
                        break
                    coords.append(new_pos)
                if not valid_structure:
                    break

            if valid_structure and len(coords) == total_cubes:
                coords_matrix = np.array(coords)

                # 【核心修复】：强制 3D 约束
                # np.ptp 计算每个坐标轴上的 (最大值 - 最小值)。
                # 如果有任何一个轴的差值为 0，说明它是扁平的 2D 图形，必须抛弃重试。
                if np.any(np.ptp(coords_matrix, axis=0) == 0):
                    continue

                center_of_mass = np.mean(coords_matrix, axis=0)
                return coords_matrix - np.round(center_of_mass)

        raise Exception(f"在 {max_retries} 次尝试后仍无法生成无碰撞的 3D 结构，请降低弯折数。")

    def generate_mirror(self, coords_matrix):
        mirror_matrix = coords_matrix.copy()
        mirror_matrix[:, 0] = mirror_matrix[:, 0] * -1
        return mirror_matrix