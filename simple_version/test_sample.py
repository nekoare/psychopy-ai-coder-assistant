# -*- coding: utf-8 -*-
"""
AI Coder Assistant テスト用サンプルコード

このコードには意図的に以下の問題が含まれています：
1. 性能問題: ループ内での刺激作成
2. タイミング問題: time.sleep()の使用
3. ベストプラクティス違反: マジックナンバー、クリーンアップ不足
4. Builderマッピング候補: 単純な試行ループ

AIアシスタントがこれらの問題を正しく検出し、
改善提案を提供するかテストするためのコードです。
"""

import psychopy.visual as visual
import psychopy.core as core
import psychopy.event as event
import time
import random

# ❌ 問題1: マジックナンバーの使用
win = visual.Window(size=(800, 600), fullscr=False)

# ❌ 問題2: マジックナンバーの使用  
n_trials = 50
stimulus_duration = 2.0

# ❌ 問題3: マジックナンバーの使用
response_key = 'space'

# ❌ 問題4: Builderで実装可能な単純な試行ループ
for trial in range(n_trials):
    
    # ❌ 問題5: 性能問題 - ループ内で刺激を毎回作成
    text_stim = visual.TextStim(
        win, 
        text=f"試行 {trial + 1}",
        color='white',
        height=0.1
    )
    
    # 刺激提示
    text_stim.draw()
    win.flip()
    
    # ❌ 問題6: タイミング問題 - time.sleep()の使用
    time.sleep(stimulus_duration)
    
    # 反応収集
    keys = event.getKeys([response_key])
    if keys:
        print(f"試行 {trial + 1} で反応がありました")
    
    # ❌ 問題7: 性能問題 - ループ内での計算
    delay = random.uniform(0.5, 1.5)
    time.sleep(delay)
    
    # ❌ 問題8: 非効率なキーボードバッファクリア
    event.clearEvents()

# ❌ 問題9: ベストプラクティス違反 - 適切なクリーンアップなし
print("実験終了")

# 期待されるGemini AI分析結果：
"""
【Builderマッピング提案】
- 試行ループ (range(50)) → TrialHandlerコンポーネント (nReps=50)
- テキスト刺激の表示 → TextStimコンポーネント
- キーボード反応収集 → Keyboardコンポーネント
- 実験フロー → RoutineとLoop組み合わせ

【性能最適化提案】  
- TextStimをループ外で作成、ループ内でsetText()更新 (大幅な高速化)
- time.sleep()をcore.wait()に変更 (正確なタイミング)
- ランダム遅延の事前計算 (ループ内計算を回避)
- 不要なevent.clearEvents()の削除

【ベストプラクティス提案】
- マジックナンバーを定数として定義 (N_TRIALS=50, STIMULUS_DURATION=2.0, RESPONSE_KEY='space')
- 適切なリソースクリーンアップ (win.close(), core.quit())
- try-finally文によるエラー処理
- 設定セクションと実行ロジックの分離
- より読みやすい変数名の使用

このサンプルコードをCtrl+Shift+Aで分析すると、
Geminiがこれらの改善点を自動検出し、具体的な修正コードを提案します。
"""