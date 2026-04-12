import os
import numpy as np
import matplotlib.pyplot as plt
from logic_engine import StimulusGenerator

def render_and_save_structure(coords, filename, elevation=30, azimuth=45):
    """
    将 3D 坐标矩阵渲染为带有黑色描边的 2D 纯色积木，并保存为透明 PNG。
    """
    fig = plt.figure(figsize=(5, 5), facecolor='none') # 透明背景
    # 开启正交投影 (proj_type='ortho') 以消除透视变形带来的深度线索干扰
    ax = fig.add_subplot(111, projection='3d', proj_type='ortho')
    ax.set_facecolor('none')

    # 确定网格的边界，以容纳所有的坐标
    min_vals = np.min(coords, axis=0)
    max_vals = np.max(coords, axis=0)

    # 构建 voxel 布尔矩阵
    grid_shape = (max_vals - min_vals + 1).astype(int)
    voxels = np.zeros(grid_shape, dtype=bool)

    # 将坐标映射到体素网格中
    for x, y, z in coords:
        voxels[int(x - min_vals[0]), int(y - min_vals[1]), int(z - min_vals[2])] = True

    # 渲染体素：白色填充，黑色描边边界
    ax.voxels(voxels, facecolors='white', edgecolors='black', linewidth=1.5)

    # 调整视角 (仰角和方位角)
    ax.view_init(elev=elevation, azim=azimuth)

    # 隐藏坐标轴，我们只需要纯粹的图形
    ax.axis('off')

    # 保存图片
    plt.savefig(filename, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

def main():
    stimuli_dir = "./stimuli" # 确保输出到上一级的 stimuli 文件夹
    os.makedirs(stimuli_dir, exist_ok=True)

    generator = StimulusGenerator()

    # --- 生成参数配置 ---
    complexities = [3, 4, 5] # 拓扑弯折数：简单、中等、复杂
    angles = [0, 45, 90, 135, 180] # 旋转角度
    trials_per_condition = 2 # 每个条件生成几组不同的基础图形

    print("开始批量生成实验刺激物...")

    for complexity in complexities:
        for trial in range(trials_per_condition):
            try:
                # 1. 生成基础拓扑
                base_coords = generator.generate_topology(total_cubes=10, num_bends=complexity)

                # 2. 为每个角度生成相同图 (Same) 和镜像图 (Mirror)
                for angle in angles:
                    # 旋转坐标 (绕 Y 轴)
                    rotated_coords = generator.generate_rotation(base_coords, angle, axis='y')
                    mirror_coords = generator.generate_mirror(rotated_coords)

                    # 命名规范：角度_复杂度_是否镜像_trial编号.png
                    # (加入 trial 编号以防止同一条件下的不同拓扑互相覆盖)
                    same_filename = os.path.join(stimuli_dir, f"{angle:03d}_{complexity}_same_{trial}.png")
                    mirror_filename = os.path.join(stimuli_dir, f"{angle:03d}_{complexity}_mirror_{trial}.png")

                    # 渲染并保存
                    render_and_save_structure(rotated_coords, same_filename)
                    render_and_save_structure(mirror_coords, mirror_filename)

            except Exception as e:
                print(f"跳过一个无效拓扑: {e}")

    print(f"✅ 生成完毕！请检查 {stimuli_dir} 文件夹。")

if __name__ == "__main__":
    main()