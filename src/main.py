import os
import glob
import random
import configparser
import pandas as pd
from psychopy import visual, core, event

def load_config():
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.ini')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"找不到配置文件: {config_path}")
    config.read(config_path, encoding='utf-8')
    return config

def main():
    # --- 1. 初始化配置 ---
    cfg = load_config()
    SUBJECT_ID = cfg.get('Subject', 'id')
    EXP_NAME = cfg.get('Experiment', 'name')
    NUM_TRIALS_REQ = cfg.getint('Experiment', 'num_trials')
    MAX_WAIT = cfg.getfloat('Experiment', 'max_wait_sec')
    FIX_DUR = cfg.getfloat('Experiment', 'fixation_duration')

    KEYS = {
        'same': cfg.get('Keys', 'same'),
        'diff': cfg.get('Keys', 'different'),
        'esc': cfg.get('Keys', 'escape'),
        's1': cfg.get('Keys', 'strategy_intuition'),
        's2': cfg.get('Keys', 'strategy_logic')
    }

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STIM_DIR = os.path.join(BASE_DIR, cfg.get('Paths', 'stimuli_dir'))
    DATA_DIR = os.path.join(BASE_DIR, cfg.get('Paths', 'data_dir'))
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- 2. 解析新规则 [ID]_[Comp]_[Angle]_[Type] ---
    all_images = glob.glob(os.path.join(STIM_DIR, "*.png"))
    all_possible_trials = []

    for img_path in all_images:
        filename = os.path.basename(img_path).replace('.png', '')
        parts = filename.split('_')
        if len(parts) != 4: continue

        # 对应新格式: {trial_id}_{complexity}_{angle}_{type}
        trial_id, comp, angle_str, type_str = parts

        # 过滤掉 0度-Same (左右完全一致的试次)
        if angle_str == '000' and type_str == 'same':
            continue

        # 根据新命名规则寻找 Baseline: {ID}_{Comp}_000_same.png
        baseline_path = os.path.join(STIM_DIR, f"{trial_id}_{comp}_000_same.png")

        if os.path.exists(baseline_path):
            all_possible_trials.append({
                'baseline_img': baseline_path,
                'target_img': img_path,
                'angle': int(angle_str),
                'complexity': int(comp),
                'is_mirror': (type_str == 'mirror'),
                'skeleton_id': trial_id
            })

    random.shuffle(all_possible_trials)
    trials = all_possible_trials[:NUM_TRIALS_REQ] if NUM_TRIALS_REQ > 0 else all_possible_trials

    # --- 3. 实验运行 ---
    win = visual.Window(size=(1280, 800), fullscr=False, color='white', useRetina=True, units='pix')
    stim_left = visual.ImageStim(win, pos=(-350, 0), size=(500, 500))
    stim_right = visual.ImageStim(win, pos=(350, 0), size=(500, 500))
    fixation = visual.TextStim(win, text='+', color='black', height=50)
    probe_text = visual.TextStim(win, text=f"Report the strategies you have used:\n\n[ {KEYS['s1']} ] Visual intuition or rotation\n[ {KEYS['s2']} ] Logical analysis", color='black', height=40)

    print(f"实验启动 | 当前筛选出的有效试次总数: {len(all_possible_trials)}")

    trial_data = []
    for idx, t in enumerate(trials):
        fixation.draw(); win.flip(); core.wait(FIX_DUR)

        stim_left.image = t['baseline_img']
        stim_right.image = t['target_img']
        stim_left.draw(); stim_right.draw(); win.flip()

        trial_clock = core.Clock()
        keys = event.waitKeys(maxWait=MAX_WAIT, keyList=[KEYS['same'], KEYS['diff'], KEYS['esc']])
        rt = trial_clock.getTime()

        if not keys or keys[0] == KEYS['esc']: break

        res = keys[0]
        acc = 1 if ((not t['is_mirror'] and res == KEYS['same']) or (t['is_mirror'] and res == KEYS['diff'])) else 0

        probe_text.draw(); win.flip()
        strat_keys = event.waitKeys(keyList=[KEYS['s1'], KEYS['s2'], KEYS['esc']])
        if not strat_keys or strat_keys[0] == KEYS['esc']: break
        strat = 'Intuition' if strat_keys[0] == KEYS['s1'] else 'Logic'

        trial_data.append({
            'trial_idx': idx + 1,
            'skel_id': t['skeleton_id'],
            'complexity': t['complexity'],
            'angle': t['angle'],
            'is_mirror': t['is_mirror'],
            'rt_sec': rt,
            'accuracy': acc,
            'strategy': strat
        })

    win.close()
    if trial_data:
        pd.DataFrame(trial_data).to_csv(os.path.join(DATA_DIR, f"{SUBJECT_ID}_Results.csv"), index=False)
        print(f"✅ 结果已保存至 {DATA_DIR}")
    core.quit()

if __name__ == "__main__":
    main()