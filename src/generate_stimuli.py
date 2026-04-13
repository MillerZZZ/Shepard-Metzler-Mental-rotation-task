import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from logic_engine import StimulusGenerator

def render_and_save_structure(coords, filename, elevation=25, azimuth=35, angle=0):
    """
    使用相机视角旋转，保持整数坐标，解决断裂问题。
    """
    fig = plt.figure(figsize=(5, 5), facecolor='none')
    ax = fig.add_subplot(111, projection='3d', proj_type='ortho')
    ax.set_facecolor('none')

    min_vals = np.min(coords, axis=0).astype(int)
    max_vals = np.max(coords, axis=0).astype(int)
    grid_shape = (max_vals - min_vals + 1)
    voxels = np.zeros(grid_shape, dtype=bool)

    for x, y, z in coords:
        voxels[int(x - min_vals[0]), int(y - min_vals[1]), int(z - min_vals[2])] = True

    # 光照增强立体感
    ls = LightSource(azdeg=315, altdeg=45)
    ax.voxels(voxels,
              facecolors='#B0C4DE', # 冷灰色材质
              edgecolors='black',
              linewidth=0.8,
              shade=True,
              lightsource=ls)

    ax.view_init(elev=elevation, azim=azimuth + angle)
    ax.axis('off')
    plt.savefig(filename, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

def main():
    stimuli_dir = "./stimuli"
    os.makedirs(stimuli_dir, exist_ok=True)
    generator = StimulusGenerator()

    # 参数配置
    complexities = [3, 4, 5]
    angles = [0, 45, 90, 135, 180]
    trials_per_condition = 100 # 每个复杂度生成10组骨架

    print(f"🚀 开始生成刺激物。命名模式：[骨架ID]_[复杂度]_[角度]_[类型].png")

    for trial in range(trials_per_condition):
        for complexity in complexities:
            try:
                # 生成基础拓扑
                base_coords = generator.generate_topology(total_cubes=10, num_bends=complexity)

                # 再次校验：强制 3D 检查，防止生成看起来像平面的图
                if np.any(np.ptp(base_coords, axis=0) == 0):
                    continue

                for angle in angles:
                    # 按照用户要求的新命名规则：骨架编号_复杂度_角度_类型
                    base_name = f"{trial:02d}_{complexity}_{angle:03d}"

                    same_fn = os.path.join(stimuli_dir, f"{base_name}_same.png")
                    mirror_fn = os.path.join(stimuli_dir, f"{base_name}_mirror.png")

                    # 生成相同图 (Same)
                    render_and_save_structure(base_coords, same_fn, angle=angle)

                    # 生成镜像图 (Mirror)
                    mirror_coords = generator.generate_mirror(base_coords)
                    render_and_save_structure(mirror_coords, mirror_fn, angle=angle)

            except Exception as e:
                print(f"生成骨架 {trial:02d} (复杂度 {complexity}) 失败: {e}")

    print(f"✅ 素材生成完毕，请检查 {stimuli_dir} 文件夹。")

if __name__ == "__main__":
    main()