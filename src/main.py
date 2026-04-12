import os
import glob
import random
import configparser
import pandas as pd
from psychopy import visual, core, event

def load_config():
    """读取 config.ini 配置文件"""
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.ini')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"找不到配置文件: {config_path}")
    config.read(config_path, encoding='utf-8')
    return config

def main():
    # --- 1. 加载配置 ---
    cfg = load_config()
    SUBJECT_ID = cfg.get('Subject', 'id')
    EXP_NAME = cfg.get('Experiment', 'name')
    NUM_TRIALS_REQ = cfg.getint('Experiment', 'num_trials') # 读取轮数
    MAX_WAIT = cfg.getfloat('Experiment', 'max_wait_sec')
    FIX_DUR = cfg.getfloat('Experiment', 'fixation_duration')

    KEY_SAME = cfg.get('Keys', 'same')
    KEY_DIFF = cfg.get('Keys', 'different')
    KEY_ESC = cfg.get('Keys', 'escape')
    KEY_STRAT1 = cfg.get('Keys', 'strategy_intuition')
    KEY_STRAT2 = cfg.get('Keys', 'strategy_logic')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STIM_DIR = os.path.join(BASE_DIR, cfg.get('Paths', 'stimuli_dir'))
    DATA_DIR = os.path.join(BASE_DIR, cfg.get('Paths', 'data_dir'))
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- 2. 解析并筛选实验试次 ---
    all_images = glob.glob(os.path.join(STIM_DIR, "*.png"))
    all_possible_trials = []
    for img_path in all_images:
        filename = os.path.basename(img_path).replace('.png', '')
        parts = filename.split('_')
        if len(parts) != 4: continue
        angle, complexity, type_str, trial_id = parts[0], parts[1], parts[2], parts[3]
        baseline_path = os.path.join(STIM_DIR, f"000_{complexity}_same_{trial_id}.png")
        if os.path.exists(baseline_path):
            all_possible_trials.append({
                'baseline_img': baseline_path, 'target_img': img_path,
                'angle': int(angle), 'complexity': int(complexity),
                'is_mirror': (type_str == 'mirror'), 'topology_id': trial_id
            })

    random.shuffle(all_possible_trials)

    # --- 核心逻辑：根据配置截取轮数 ---
    if NUM_TRIALS_REQ > 0:
        trials = all_possible_trials[:NUM_TRIALS_REQ]
    else:
        trials = all_possible_trials

    trial_data = []

    # --- 3. 初始化窗口 ---
    win = visual.Window(size=(1280, 800), fullscr=False, color='white', useRetina=True, units='pix')
    stim_left = visual.ImageStim(win, pos=(-350, 0), size=(500, 500))
    stim_right = visual.ImageStim(win, pos=(350, 0), size=(500, 500))
    fixation = visual.TextStim(win, text='+', color='black', height=50)

    instr_msg = f"判断是否相同：\n\n[ {KEY_SAME.upper()} ] 相同\n[ {KEY_DIFF.upper()} ] 不同\n\n(共 {len(trials)} 轮)"
    probe_msg = f"报告策略:\n\n[ {KEY_STRAT1} ] 视觉直觉\n[ {KEY_STRAT2} ] 逻辑推演"
    probe_text = visual.TextStim(win, text=probe_msg, color='black', height=40)

    print(f"实验启动 | 受试者: {SUBJECT_ID} | 本次运行轮数: {len(trials)}")

    # --- 4. 实验主循环 ---
    for trial_idx, t in enumerate(trials):
        fixation.draw()
        win.flip()
        core.wait(FIX_DUR)

        stim_left.image = t['baseline_img']
        stim_right.image = t['target_img']
        stim_left.draw()
        stim_right.draw()
        win.flip()

        trial_clock = core.Clock()
        keys = event.waitKeys(maxWait=MAX_WAIT, keyList=[KEY_SAME, KEY_DIFF, KEY_ESC])
        rt = trial_clock.getTime()

        if not keys:
            res, strat, acc, crash = 'TIMEOUT', 'TIMEOUT', 0, True
        else:
            res = keys[0]
            if res == KEY_ESC: break
            acc = 1 if ((not t['is_mirror'] and res == KEY_SAME) or (t['is_mirror'] and res == KEY_DIFF)) else 0

            probe_text.draw()
            win.flip()
            strat_keys = event.waitKeys(keyList=[KEY_STRAT1, KEY_STRAT2, KEY_ESC])
            if strat_keys[0] == KEY_ESC: break
            strat = 'Intuition' if strat_keys[0] == KEY_STRAT1 else 'Logic'
            crash = False

        trial_data.append({
            'subject_id': SUBJECT_ID,
            'trial_idx': trial_idx + 1,
            'complexity_bends': t['complexity'],
            'angle': t['angle'],
            'is_mirror': t['is_mirror'],
            'rt_sec': rt,
            'accuracy': acc,
            'strategy': strat,
            'wm_crash': crash
        })

    win.close()
    if trial_data:
        df = pd.DataFrame(trial_data)
        csv_fn = os.path.join(DATA_DIR, f"{EXP_NAME}_{SUBJECT_ID}_Data.csv")
        df.to_csv(csv_fn, index=False)
        print(f"✅ 实验结束，数据已保存。")
    core.quit()

if __name__ == "__main__":
    main()