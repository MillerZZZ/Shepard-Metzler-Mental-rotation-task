import numpy as np
import random

class StimulusGenerator:
    def __init__(self):
        # 定义 3D 坐标系下的 6 个正交方向
        self.directions = [
            np.array([1, 0, 0]), np.array([-1, 0, 0]),
            np.array([0, 1, 0]), np.array([0, -1, 0]),
            np.array([0, 0, 1]), np.array([0, 0, -1])
        ]

    def _is_orthogonal(self, dir1, dir2):
        """判断两个方向是否正交（点积为0）"""
        return np.dot(dir1, dir2) == 0
    def generate_topology(self, total_cubes=10, num_bends=3):
        """
        生成一个自回避的 3D 随机游走拓扑结构。(已修复方块分配逻辑)
        """
        max_retries = 1000 # 提高重试阈值应对高复杂度碰撞
        segments = num_bends + 1

        # 极值保护：计算所需的最小方块数 (原点1个 + 每段至少延伸1个)
        min_required = 1 + segments
        if total_cubes < min_required:
            raise ValueError(f"方块数不足！{num_bends} 个弯折至少需要 {min_required} 个方块。")

        for _ in range(max_retries):
            # 1. 预先分配每段手臂要新增的方块数
            blocks_to_add = [1] * segments # 每段至少新增 1 个
            extra_cubes = total_cubes - min_required

            # 将剩余配额随机分配给各段
            for _ in range(extra_cubes):
                blocks_to_add[random.randint(0, segments - 1)] += 1

            coords = [np.array([0, 0, 0])]
            current_dir = random.choice(self.directions)
            valid_structure = True

            # 2. 按分配好的长度延伸拓扑
            for i, add_count in enumerate(blocks_to_add):
                if i > 0:
                    # 发生转折，选取正交方向
                    possible_dirs = [d for d in self.directions if self._is_orthogonal(d, current_dir)]
                    current_dir = random.choice(possible_dirs)

                # 沿当前方向添加方块
                for _ in range(add_count):
                    new_pos = coords[-1] + current_dir

                    # 自回避检测：如果撞车了，直接宣告此次游走失败
                    if any(np.array_equal(new_pos, c) for c in coords):
                        valid_structure = False
                        break
                    coords.append(new_pos)

                if not valid_structure:
                    break

            # 3. 校验并居中返回
            if valid_structure and len(coords) == total_cubes:
                coords_matrix = np.array(coords)
                center_of_mass = np.mean(coords_matrix, axis=0)
                # 返回居中对齐后的浮点矩阵
                return coords_matrix - np.round(center_of_mass)

        raise Exception(f"在 {max_retries} 次尝试后仍无法生成无碰撞结构，请降低弯折数或增加方块总数。")

    def generate_mirror(self, coords_matrix):
        """
        基于现有的坐标矩阵，生成其镜像异构体。
        :param coords_matrix: N x 3 的原图形坐标矩阵
        :return: 翻转 X 轴后的新矩阵
        """
        mirror_matrix = coords_matrix.copy()
        mirror_matrix[:, 0] = mirror_matrix[:, 0] * -1
        return mirror_matrix

    def generate_rotation(self, coords_matrix, angle_deg, axis='y'):
        """
        对 3D 坐标矩阵进行欧拉角旋转，为生成不同角度的刺激物做准备。
        """
        angle_rad = np.radians(angle_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # 围绕 Y 轴旋转的矩阵 (这是最经典的 Shepard-Metzler 深度旋转)
        if axis == 'y':
            rot_matrix = np.array([
                [cos_a, 0, sin_a],
                [0, 1, 0],
                [-sin_a, 0, cos_a]
            ])
        # 如果需要全空间旋转，可以在此补充 X 轴和 Z 轴的旋转矩阵
        else:
            raise NotImplementedError("Currently only Y-axis rotation is implemented.")

        # 将 N x 3 矩阵与 3 x 3 旋转矩阵相乘
        rotated_coords = np.dot(coords_matrix, rot_matrix)
        return rotated_coords

# 模块测试代码
if __name__ == "__main__":
    generator = StimulusGenerator()
    base_structure = generator.generate_topology(total_cubes=10, num_bends=3)
    mirror_structure = generator.generate_mirror(base_structure)

    print("Base Structure Coordinates (N x 3):")
    print(base_structure)
    print("\nMirror Structure Coordinates (X-axis inverted):")
    print(mirror_structure)