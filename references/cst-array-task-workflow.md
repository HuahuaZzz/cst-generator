# CST 原生 Array Task 自動化工作流程

適用於將已最佳化的單一天線擴充為 CST 原生 Array Task 與 Full Array 子專案。流程整理自 2026-09-07 工作延續至 2026-09-08 凌晨的 biquad 2×2 程式與 CST history；現存檔案時間為 2026-09-08。本文件保存可重用的操作順序與限制，不代表已完成全波模擬。

## 1. 保存單元與辨識實際設定

- 先讀取來源 `.cst` 的參數 expression/value、實際 shape/material、port 座標及方向、頻段、boundary、monitor、solver 與有效 history。另存快照，保留最佳化原件。
- 建立新的 master/output，遇到同名輸出或 task 時停止或改用新名稱；只在使用者已授權的範圍內修改既有模型。修改前確認相關專案的 solver 閒置。
- 以 shape 實際指定的材質為準。此案例的金屬為 PEC，基板為 `FR-4 (lossy)`，epsilon=4.3、tanD=0.025；舊參數 `sub_tand=0.02` 對應未使用材質，不能當成現行基板損耗。
- 使用與安裝版本相符的 `cst.interface`。本次程式使用 CST Studio Suite 2025 的 `AMD64/python_cst_libraries`；將安裝路徑、來源、輸出改為設定或命令列參數，不依賴作者的 NAS 路徑或匯入時即存在的 snapshot。
- 透過 `DesignEnvironment.connect_to_any()` 取得環境後，以完整路徑辨識專案；多個候選時不要任取第一個。

## 2. 陣列間距的前置估算

先確認 nx/ny、dx/dy、排列平面與 grid angle、單元朝向、掃描方向、激發、共用反射板及頻段。若需求含間距選擇，可用單元遠場乘上 array factor 估算，再以全陣列模擬確認。

本案例 2×2、XY、等幅同相 broadside 使用：

```text
AF = 4 cos(pi dx/lambda sin(theta)cos(phi))
       cos(pi dy/lambda sin(theta)sin(phi))
P_array_est = P_element × |AF/4|²
D_broadside_est = 4 pi P_array_est(theta=0) / integral(P_array_est dOmega)
```

積分包含 sin(theta) 權重；資料若是 dB power，先轉為線性 power。若主瓣偏離 broadside，不能把 broadside 值當作 peak directivity。依實際掃描範圍檢查 grating lobes；broadside 條件不能直接套到掃描陣列。

保存掃描 CSV、選擇原因、不可行條件與單位。此案例的 `spacing_choice.json` 顯示：

| 項目 | 歷史案例值，不是通用預設 |
| --- | --- |
| 陣列 / 頻段 | 2×2 / 5.6–5.9 GHz |
| 選用中心間距 | dx=dy=49 mm |
| 掃描點數 / 滿足 -15 dB 前半球旁瓣的點數 | 468 / 0 |
| 最差頻點預估方向性 | 約 18.10 dBi |
| 最差前半球旁瓣估計 | 約 -13.55 dB |
| 選擇原因 | 在取樣最大方向性 0.1 dB 內，取最小整數毫米正方間距 |

這些估算忽略互耦及共用反射板變化，且單元方向圖來自原本獨立反射板。不能寫成 full-array realized gain、全波驗證結果或宣稱已達 -15 dB 目標。

## 3. 建立原生 Array Task

在新 Design Studio master 建立 `CSTMWSFile` block，指向保存的最佳化單元；使用實際 block 名稱。設定 schematic 的 Length=mm、Frequency=GHz。

以下為從本地程式整理的 API 順序片段，變數需由目前專案提供：

```python
s = master.schematic
b = s.Block
b.Reset()
b.Name(element_block)
b.Type('CSTMWSFile')
b.SetRelativePath(False)
b.SetFile(str(source.resolve()))
b.Create()

pa = s.PhasedArrayTask
pa.Reset()
pa.Name(task_name)
pa.SetShapeCustom(nx, ny, dx, dy, 90)
pa.SetExcitationPattern('Uniform')
pa.SetElementModel('Block: ' + element_block)
pa.Create()
master.save()
```

`Uniform`、XY 與 90° 是本案例條件，其他需求需調整。僅建立 task 不會自動證明 Full Array 幾何及 port 已建立。

## 4. 產生 Full Array 子專案

優先用原生 Array 功能，保留 task、單元來源、port 編號及 simulation-project 關係。若目前版本沒有可直接呼叫的 wizard API，先用 GUI 產生代表性案例、讀取其 history，再依該版本重放；不要猜測 COM 方法。

本案例可用的 Python 路徑是 `SimulationProject` 匯入單元，再用 GUI history 中的 `PhasedAntennaArray` 生成：

```python
sp = s.SimulationProject
sp.Reset()
sp.ResetComponents()
sp.SetBlock(element_block, '3D')
sp.SetUseReferenceData(True)
sp.LoadReferenceDataFromBlock('Block: ' + element_block)
sp.SetUseReferenceBlockCoordinateSystem(True)
sp.SetLinkGeometry(True)
sp.Create('MWS', full_name)
sp.SetSolverType('HF_TRANSIENT')  # 此案例 solver；其他模型依需求設定
```

- 本次 `Get3D` 回傳的 COM dispatch 無法經 Python Bus 傳遞；改用 `DesignEnvironment.list_open_projects()`，比對新 master 的子目錄與完整子專案檔名，再 `get_open_project()`。匹配數必須是 1。
- 在子專案寫入 `array_dx/dy/nx/ny` 參數，以 `model3d.add_to_history()` 加入原生生成段。
- 錄製段包含 `PhasedAntennaArray.Reset`、`Orientation "XY"`、`NumberOfElements`、`Spacing`、`GridAngle "90"`、`FillSpace "True"`、`ForceParallelogram "False"`、`ElementTypes`、`ElementLabel`、`IdenticalPorts "True"`、`InsertElements "True"`、`ExcludeComponents ""`、`Create`。單一 element type 的列表長度及 `(ix.iy);` labels 數量均需等於 nx×ny，依實際 history 的順序建立。
- 完成子專案設定後呼叫 `sp.EndCreation()`，以 `SimulationTask.Name(full_name)` / `MoveInTree(task_name, '')` 放回 Array Task 節點下，儲存 master 與子專案並重開驗證。
- `Transform` 手動複製 + 重建 ports 的舊方案只可明確標示為幾何 fallback；它不是原生 Create Full Array wizard，也不保證修改 nx/ny 後原生重建。不要用它冒充已完成原生 Array Task 流程。

## 5. 共用反射板與座標

僅在需求包含共用反射板時處理。`FillSpace=True` 在此案例會將原單元反射板裁為各 cell 的 tiles；先列舉 shapes，確認預期 tile 數量、名稱與材質，再刪除這些生成的 tiles，加入單一連續板。不刪除原始單元專案的反射板。

原生生成案例的單元中心位於 0、dx、… 與 0、dy、…，不是 ±dx/2。先查驗實際座標，再使用：

```text
cx = (nx-1)*dx/2
cy = (ny-1)*dy/2
shared_l = (nx-1)*dx + original_reflector_l
shared_w = (ny-1)*dy + original_reflector_w
Xrange = cx ± shared_l/2
Yrange = cy ± shared_w/2
Zrange = -refl_t .. 0    # 僅適用於本案例原始 z 基準
```

2×2、49 mm 間距、原板 70×70 mm 時，共用板為 119×119 mm，中心 (24.5,24.5) mm。本案例原生參數名亦出現 `PAA_UC_DS1/DS2`；API 腳本則用 `array_dx/dy`。依目前 child 的參數命名引用，勿混用兩套座標。

保留來源板厚與材質。用後加 history block 讓處理可重放；完整 array 更新是否保留此 block 仍須實際測試。再次執行前檢查 tile 數與共用板是否已存在，避免重複刪改。

## 6. 激發、monitor 與 solver

- 本案例每單元一個 port，2×2 共四個，等幅 1、相位 0°。多 port 單元需建立實際 element-port 對照，不能假設總 port 數永遠等於 nx×ny。
- 使用 `CombineResults`：Reset、SetOffsetType("Phase")、SetReferenceFrequency、SetLabel、SetNone，再逐 port 呼叫 `SetExcitationValues("port", port_id, mode, amplitude, phase)`，最後 `AddToExcitationList`。
- 本地腳本使用 `StimulationPort("Selected")`、`ResetExcitationModes()`、`ActivateExcitation("Simultaneous", label, "1", "True")`。不同 history 還可能出現 `SParameterPortExcitation` / `SimultaneousExcitation` 設定；須讀回目前 solver 的有效激發列表，不能只因 history 名稱是「simultaneous」就認定成功。
- 確認 port impedance、方向、mode 與位置未因生成改變。全 S-matrix 的逐 port 求解與特定同時激發的方向圖是不同輸出需求，依使用者需求配置。
- 遠場 monitor 由目標頻段參數化；本例 5.6–5.9 GHz、0.05 GHz 一點共七點。設定完成不等於執行模擬；只有已授權求解才啟動 solver。

## 7. 完成判定與交付

| 檢查 | 應保存的證據 |
| --- | --- |
| 原始單元保持最佳化設定 | source snapshot、有效 history、shape/material 對照 |
| 原生 task 與 child 關係 | task tree、來源 block、master/child 路徑 |
| 佈局与幾何 | nx/ny/dx/dy、各單元中心、形狀清單、模型截圖 |
| 共用反射板 | 只有一塊目標板，位置及體積 L×W×t 正確 |
| Ports 與激發 | port 座標、方向、impedance、element-port 映射、有效激發列表 |
| 物理設定 | 實際材質、boundary、solver、monitor 與頻段 |
| 儲存可重現性 | 重開 master/child；需要參數化更新時，在副本測試 rebuild |
| 模擬結果（若有求解） | solver 完成狀態、結果時間、S parameters、效率與相應 gain 指標 |

此 biquad 特例預期 4 PCB + 4 radiator + 1 reflector = 9 shapes；其他單元不可硬套 9。若檢查失敗，保留診斷資料並停止該階段，不宣稱成功、不繼續自動啟動 solver。

交付時分開報告「腳本已產生」「CST 接受 history」「模型檢查通過」「重開/rebuild 通過」「solver 完成」與「性能達標」。尚未驗證的項目明確列為待驗證。

## 來源與重用邊界

此次參考的原工作目錄為 `CST/CST_Python/biquad_array_2x2/`。這些專案檔不是本 skill 的執行相依：

- `source_snapshot.json`、`optimized_element_history.json`：來源參數與有效材質。
- `estimate_spacing.py`、`spacing_choice.json`：間距估算與未達旁瓣目標的紀錄。
- `build_array_task.py`：建立原生 Array Task。
- `native_full_array_history.json`、`native_full_array2_history.json`：GUI 生成的 history，記錄版本為 2025.1。
- `native_array_api.py`：由錄製 history 整理的原生 API 流程，含上述 Python Bus 限制。
- `finalize_full_array.py`：共用板、monitor、ports、shape/volume 檢查。
- `create_full_array.py`：較早的手動幾何 fallback，不能與原生路徑混淆。

原腳本包含固定來源 snapshot、元件名稱、49 mm、5.75 GHz、70 mm 邊界與特定材料等案例設定。重用時從新來源推導並驗證，不能原封不動當作一般 NxM 生成器。此 skill 更新只整理文件；沒有重新執行 CST 或宣稱新一次模擬驗證。

