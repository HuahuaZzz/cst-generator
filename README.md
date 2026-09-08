# CST Generator

`cst-generator` 是一個 Codex skill，用來建立與自動化 CST Studio Suite 模型。它涵蓋 Microwave Studio 幾何、參數、材料、ports、boundary、monitor、solver，以及原生 Array Task / Full Array 工作流程。

## 功能

- 將自然語言需求整理成 CST 模型參數與模擬設定。
- 使用 Python 搭配 `cst.interface` 或 `win32com.client` 控制 CST。
- 產生可保留於 CST History 的 VBA 建模指令。
- 從已最佳化的單一天線建立原生 Array Task 與 Full Array 子專案。
- 設定陣列間距、激發、共用反射板與遠場 monitors。
- 驗證 shapes、materials、ports、參數、反射板體積及專案關係。

## 安裝

將整個 `cst-generator` 資料夾放入 Codex skills 目錄：

```text
%CODEX_HOME%/skills/cst-generator
```

如果沒有設定 `CODEX_HOME`，Windows 預設位置通常是：

```text
C:\Users\<使用者名稱>\.codex\skills\cst-generator
```

重新開啟 Codex 後，即可在 CST 建模或自動化需求中使用此 skill。

## 使用範例

```text
使用 cst-generator，根據最佳化的單一天線 CST 專案建立 4×4 原生 Array Task。
中心間距為 30 mm，設定等幅同相激發，在 5.6–5.9 GHz 建立遠場 monitors，先不要啟動 solver。
```

建立一般 CST 模型時，也可以描述幾何尺寸、材料、頻段、port 與輸出路徑。若關鍵電磁條件未提供，skill 會先釐清會改變設計意圖的參數。

## 檔案結構

```text
cst-generator/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── cst-array-task-workflow.md
│   └── cst-python-vba-generation.md
└── scripts/
    └── create_cst_model_template.py
```

- `SKILL.md`：Codex skill 入口與工作路由。
- `references/cst-array-task-workflow.md`：原生 Array Task、Full Array、共用反射板、激發與驗證流程。
- `references/cst-python-vba-generation.md`：Python、COM 與 CST VBA 建模範例。
- `scripts/create_cst_model_template.py`：可重用的 CST Python 起始範本。

## Array Task 流程

```text
保存最佳化單元與設定
          ↓
估算並選擇陣列間距
          ↓
建立原生 PhasedArrayTask
          ↓
建立並連結 Full Array 子專案
          ↓
生成原生陣列幾何與 ports
          ↓
整合共用反射板（若需要）
          ↓
設定激發、solver 與 monitors
          ↓
驗證、儲存並重新開啟檢查
```

陣列因子估算只用於選擇起始間距，不能視為全波模擬的 realized gain。只有 CST solver 完成並檢查結果後，才能判定性能是否達標。

## 環境需求

- Windows
- CST Studio Suite（實際 API 與 History 語法可能因版本不同）
- Python 3
- CST 隨附的 Python libraries，或安裝 `pywin32` 以使用 `win32com.client`

執行自動化前，請確認來源與輸出路徑、CST 版本、solver 狀態及專案是否已開啟。預設不覆寫既有 `.cst` 專案，也不自行啟動長時間模擬。

