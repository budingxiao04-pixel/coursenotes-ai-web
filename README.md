# CourseNotes AI | AI 雙語課程 Wiki

**LLM Wiki × 課程講義生成器**：把上課簡報、課本、學習單、考卷依科目匯入，建立持續更新的知識頁，再生成雙語重點、模擬題與心智圖大綱。

## 核心流程

`建立科目 → 匯入教材 → Ingest → Compare/Merge → Index/Log → Query/Lint → 生成筆記、題目與心智圖 → 匯出`

- 每個科目獨立管理來源、Wiki 主題頁、日誌及檔案編號。
- **離線模式**：在瀏覽器內匯入教材、將原文摘錄合併至「課程總覽」、記錄操作、關鍵字查詢、品質檢查、匯出 Wiki ZIP、生成原文練習提示。**不提供真實 AI 翻譯或答案解析**。
- **AI 模式**：連接選用 Groq 後端，使用教材與現有 Wiki 整合來源支持的新重點、提供來源標註的中英對照、模擬題與答案解析、心智圖文字樹和 Wiki 問答。AI 生成內容需人工核對。
- 匯出名稱如 `普通生物學_001_雙語重點.md`，不同科目各自編號。
- Wiki ZIP 內含 `wiki/index.md`、`wiki/pages/*.md`、`wiki/sources.md`、`wiki/log.md`。

## 如何在 GitHub Pages 使用

1. 將本專案全部檔案上傳公開 GitHub Repository（**不要上傳私人教材或 API 金鑰**）。
2. 在 Settings → Pages → Deploy from a branch → `main` → `/docs` → Save。
3. 等 GitHub Pages 產生網址，開啟網站測試新增科目、匯入 TXT、整理 Wiki、下載 ZIP。

GitHub Pages **只託管靜態網站**，不會自動執行 Python 或 AI。

## AI 後端（選用）

```bash
cd server
pip install -r requirements.txt
export GROQ_API_KEY='YOUR_SECRET_KEY'
export ALLOWED_ORIGINS='https://YOUR_USERNAME.github.io'
uvicorn app:app --host 0.0.0.0 --port 8000
```

將後端部署到可使用 HTTPS 的伺服器後，填入網站的「AI 後端網址」，並勾選資料傳送同意。後端提供 `/api/ingest`、`/api/query`、`/api/generate` 和 `/health`。

## KaTeX / LaTeX 公式支援

- 網頁透過 KaTeX 0.16.22（CDN）顯示教材 Wiki、查詢答案與生成結果中的 LaTeX 公式。支援 `$...$`、`$$...$$`、`\(...\)`、`\[...\]`。
- 公式編輯區可以直接輸入 LaTeX 命令並即時預覽；使用 `\ce{...}` 可排版化學反應式（mhchem 擴充）；在 Wiki/筆記內請包在 `$...$` 或 `$$...$$` 中。
- 可匯入 `.tex` / `.latex` 純文字檔，並以 Markdown 保留公式原始碼；「下載公式 Markdown」會使用科目專屬流水號。
- 使用者教材與 AI 產生的文字會先經 HTML 跳脫，再進行 KaTeX 渲染；`trust:false` 禁止不受信任的 HTML 功能。
- **不等於完整 TeX 編譯器**，不會自動將掃描 PDF、圖片、PPT 公式轉為 LaTeX，也尚無公式 PDF 匯出。需要網路才能載入 KaTeX CDN。

## 已知限制

- PDF、PPTX、DOCX、TXT、MD、TEX、LATEX 需可提取文字；掃描 PDF/圖片/手寫內容尚無 OCR。
- 瀏覽器 localStorage 容量有限，請定期匯出 JSON 備份；清除網站資料會遺失未備份內容。
- 第三方解析套件透過 CDN 載入，需要網路。
- AI 模式傳送教材文字至你指定的後端與模型供應商，請確認教材使用權、隱私與資料傳送同意。
- AI Wiki 以來源檔名為依據，但不等於已驗證每項內容；需要人工檢查。
- 目前輸出 Markdown 與 ZIP，不支援直接輸出 PDF。

## 專案目錄

- `docs/`：GitHub Pages 網站、科目管理、Wiki 工作流程、教材解析及匯出
- `server/`：選用 Groq API 後端（API 金鑰保存在環境變數）
- `AGENTS.md`：Agent 行為、來源、累積知識與品質檢查規範
- `examples/`：不含真實私人教材的測試樣本與操作示例

原 LLM Wiki 專案在 Google Drive 以 `LLM-Wiki-ZH-GitHub-Pages-BACKUP` 保留。
