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

def run_block(win, trial_list, is_practice, config_dict, stim_components, data_list):
    """
    运行一个实验块（练习或正式）
    """
    win_objs = stim_components
    KEYS = config_dict['keys']
    total = len(trial_list)
    block_type = "PRACTICE" if is_practice else "ACTUAL"

    for idx, t in enumerate(trial_list):
        # 1. 注视点
        win_objs['fixation'].draw()
        win.flip()
        core.wait(config_dict['fix_dur'])

        # 2. 更新轮数显示
        win_objs['counter'].text = f"{block_type} Trial: {idx + 1} / {total}"

        # 3. 呈现刺激物
        win_objs['left'].image = t['baseline_img']
        win_objs['right'].image = t['target_img']

        # 绘制所有组件
        win_objs['left'].draw()
        win_objs['right'].draw()
        win_objs['hint'].draw()
        win_objs['counter'].draw()
        win.flip()

        trial_clock = core.Clock()
        keys = event.waitKeys(maxWait=config_dict['max_wait'], keyList=[KEYS['same'], KEYS['diff'], KEYS['esc']])
        rt = trial_clock.getTime()

        if not keys or keys[0] == KEYS['esc']:
            if keys and keys[0] == KEYS['esc']: return False
            res, strat, acc, crash = 'TIMEOUT', 'TIMEOUT', 0, True
        else:
            res = keys[0]
            acc = 1 if ((not t['is_mirror'] and res == KEYS['same']) or (t['is_mirror'] and res == KEYS['diff'])) else 0

            # 策略询问
            win_objs['probe'].draw()
            win_objs['hint'].draw() # 策略阶段也保持按键提示
            win.flip()
            strat_keys = event.waitKeys(keyList=[KEYS['s1'], KEYS['s2'], KEYS['esc']])
            if not strat_keys or strat_keys[0] == KEYS['esc']: return False
            strat = 'Intuition' if strat_keys[0] == KEYS['s1'] else 'Logic'
            crash = False

        # 只有非练习阶段才记录到 data_list
        if not is_practice:
            data_list.append({
                'subject_id': config_dict['sub_id'],
                'trial_idx': idx + 1,
                'complexity': t['complexity'],
                'skel_id': t['topology_id'],
                'angle': t['angle'],
                'is_mirror': t['is_mirror'],
                'rt_sec': rt,
                'accuracy': acc,
                'strategy': strat,
                'wm_crash': crash
            })
        else:
            print(f"练习轮 {idx+1}: RT={rt:.3f}, Acc={acc}")

    return True

def main():
    # --- 1. 配置加载 ---
    cfg = load_config()
    SUBJECT_ID = cfg.get('Subject', 'id')
    NUM_TRIALS_ACTUAL = cfg.getint('Experiment', 'num_trials')
    PRACTICE_COUNT = 5 # 固定的练习轮数

    config_dict = {
        'sub_id': SUBJECT_ID,
        'max_wait': cfg.getfloat('Experiment', 'max_wait_sec'),
        'fix_dur': cfg.getfloat('Experiment', 'fixation_duration'),
        'keys': {
            'same': cfg.get('Keys', 'same'),
            'diff': cfg.get('Keys', 'different'),
            'esc': cfg.get('Keys', 'escape'),
            's1': cfg.get('Keys', 'strategy_intuition'),
            's2': cfg.get('Keys', 'strategy_logic')
        }
    }

    STIM_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), cfg.get('Paths', 'stimuli_dir'))
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), cfg.get('Paths', 'data_dir'))
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- 2. 试次准备 ---
    all_images = glob.glob(os.path.join(STIM_DIR, "*.png"))
    all_valid = []
    for img in all_images:
        fn = os.path.basename(img).replace('.png', '')
        parts = fn.split('_')
        if len(parts) != 4: continue
        skel, comp, ang, typ = parts
        if ang == '000' and typ == 'same': continue # 过滤完全相同

        base = os.path.join(STIM_DIR, f"{skel}_{comp}_000_same.png")
        if os.path.exists(base):
            all_valid.append({'baseline_img': base, 'target_img': img, 'angle': int(ang),
                              'complexity': int(comp), 'is_mirror': (typ == 'mirror'), 'topology_id': skel})

    random.shuffle(all_valid)

    # 切分练习与正式试次
    practice_trials = all_valid[:PRACTICE_COUNT]
    actual_trials = all_valid[PRACTICE_COUNT : PRACTICE_COUNT + NUM_TRIALS_ACTUAL]

    # --- 3. 初始化窗口与组件 ---
    win = visual.Window(size=(1280, 800), fullscr=False, color='white', useRetina=True, units='pix')

    # 持续显示的提示语 (英文)
    hint_text = f"[{config_dict['keys']['same'].upper()}] Same    [{config_dict['keys']['diff'].upper()}] Different"

    win_objs = {
        'left': visual.ImageStim(win, pos=(-350, 0), size=(500, 500)),
        'right': visual.ImageStim(win, pos=(350, 0), size=(500, 500)),
        'fixation': visual.TextStim(win, text='+', color='black', height=50),
        'hint': visual.TextStim(win, text=hint_text, pos=(0, -320), color='black', height=30),
        'counter': visual.TextStim(win, text='', pos=(0, 320), color='gray', height=25),
        'probe': visual.TextStim(win, text=f"Strategy:\n\n[{config_dict['keys']['s1']}] Intuition\n[{config_dict['keys']['s2']}] Logic", color='black', height=40)
    }

    trial_data = []

    # --- 4. 运行阶段 ---
    # A. 练习阶段
    print(f"--- 启动练习阶段 ({PRACTICE_COUNT} 轮) ---")
    if run_block(win, practice_trials, True, config_dict, win_objs, trial_data):

        # B. 过渡界面
        msg = "Practice Complete.\n\nPress any key to start the actual experiment."
        visual.TextStim(win, text=msg, color='red', height=40).draw()
        win.flip()
        event.waitKeys()

        # C. 正式阶段
        print(f"--- 启动正式阶段 ({len(actual_trials)} 轮) ---")
        run_block(win, actual_trials, False, config_dict, win_objs, trial_data)

    # --- 5. 退出 ---
    win.close()
    if trial_data:
        pd.DataFrame(trial_data).to_csv(os.path.join(DATA_DIR, f"{SUBJECT_ID}_Final_Data.csv"), index=False)
        print("✅ 正式数据保存成功。")
    core.quit()

if __name__ == "__main__":
    main()