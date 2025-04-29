# HR-AI-Agent

一个用于 HR 平台（BossZH、51Job、Liepin）的自动化、人性化浏览器爬取框架，支持缓存和可配置设置。

## 前置条件

- Python 3.8 及以上  
- （可选）Google Chrome 或其他支持的 Selenium 浏览器  
- 安装依赖：  
  ```bat
  pip install -r requirements.txt
  ```

## 快速开始

1. 克隆仓库并创建虚拟环境  
   ```bat
   git clone https://github.com/raselmahmud-coder/HR-AI-Agent.git
   cd HR-AI-Agent
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
2. 安装依赖  
   ```bat
   pip install -r requirements.txt
   ```
3. 在 `config/settings.py` 中配置项目所需的 URL、超时、查询参数等  
4. 运行主程序  
   ```bat
   python main.py
   ```

## 目录结构

- `.vscode/`  
  - `settings.json` — VSCode 工作区设置（格式化、Lint 规则）  
- `config/`  
  - `settings.py` — 存放 URL、超时、查询参数和技能映射等配置  
  - `__init__.py` — 导出全局常量  
- `helpers/`  
  - `lookup_caching.py` — 缓存 API 或界面元素查找结果  
  - `mouse_movements.py` — 实现 `human_like_mouse_move` 和 `human_click`，模拟真实鼠标动作  
  - `sleeping_time.py` — 随机化延迟函数  
- `browsers/`  
  - `pyautogui_browser.py` — 基于 PyAutoGUI 的自动化实现  
  - `selenium_browser.py` — 基于 Selenium WebDriver 的自动化实现  
  - `stealth.min.js` — 注入以规避无头检测的 JS 脚本  
- `scraper_agents/`  
  - `boss_hr/`  
    - `candidate_db.py` — `CandidateDatabase`，用于跟踪已抓取的候选人及统计信息  
    - `__init__.py` — 模块入口  
  - `jobs51_hr/`  
    - `__init__.py` — Jobs51 爬取逻辑入口  
  - `liepin_hr/`  
    - `__init__.py` — Liepin 爬取逻辑入口  
- `cache_database/`  
  - `jobs51_cache_database.json` — Jobs51 结果的持久化 JSON 缓存  
- `data_extract/`  
  - （HTML 解析和数据提取工具）  
- `utils/`  
  - `logger.py` — 统一配置的日志工具  
- `tests/`  
  - 单元测试（使用 `pytest` 运行）  
- `resources/`  
  - 静态资源、模板和数据文件  
- `logs/`  
  - 运行时日志文件（格式：`YYYYMMDD_HHMMSS.log`）

## 文件概览

- `main.py` — 项目入口：初始化代理、加载配置并启动爬取流程  
- `requirements.txt` — 第三方依赖（PyAutoGUI、Selenium、requests 等）  
- `.gitignore` — 忽略虚拟环境、日志、缓存及 Python 生成文件  

## 使用提示

- 在 `config/settings.py` 中自定义 `JOB_QUERY`、`IT_SKILLS`、`EXPERIENCE_LEVELS` 等常量  
- 在 `main.py` 中切换 PyAutoGUI 与 Selenium 驱动  
- 查看 `logs/` 下的日志文件以调试运行时问题  
- 按照现有结构，在 `scraper_agents/` 下添加新爬虫代理模块  

---

祝开发顺利！  
欢迎通过 Fork、分支和 Pull Request 共同协作。  



# HR-AI-Agent

An automated, human-like browser scraping framework for HR platforms (BossZH, 51Job, Liepin), with caching and configurable settings.

## Prerequisites

- Python 3.8+
- (Optional) Google Chrome or a supported browser for Selenium
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

## Quick Start

1. Clone the repo and create a virtual environment  
   ```sh
   git clone https://github.com/raselmahmud-coder/HR-AI-Agent.git
   cd HR-AI-Agent
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install requirements  
   ```sh
   pip install -r requirements.txt
   ```
3. Configure settings in [config/settings.py](config/settings.py)  
4. Run the main script  
   ```sh
   python main.py
   ```

## Directory Structure

- `.vscode/`  
  - [settings.json](.vscode/settings.json) – VSCode workspace settings (formatting, linting).
- `config/`  
  - [settings.py](config/settings.py) – URLs, timeouts, query parameters, skill maps.  
  - [__init__.py](config/__init__.py) – Exposes constants for easy import.
- `helpers/`  
  - [lookup_caching.py](helpers/lookup_caching.py) – Caches API or page lookup results.  
  - [mouse_movements.py](helpers/mouse_movements.py) – Implements [`human_like_mouse_move`](helpers/mouse_movements.py) and [`human_click`](helpers/mouse_movements.py) for realistic mouse actions.  
  - [sleeping_time.py](helpers/sleeping_time.py) – Generates randomized delays to mimic human pauses.
- `browsers/`  
  - [pyautogui_browser.py](browsers/pyautogui_browser.py) – Automation using PyAutoGUI.  
  - [selenium_browser.py](browsers/selenium_browser.py) – Automation using Selenium WebDriver.  
  - [stealth.min.js](browsers/stealth.min.js) – Injected JS to evade headless detection.
- `scraper_agents/`  
  - `boss_hr/`  
    - [candidate_db.py](scraper_agents/boss_hr/candidate_db.py) – [`CandidateDatabase`](scraper_agents/boss_hr/candidate_db.py) tracks scraped candidates & stats.  
    - [__init__.py](scraper_agents/boss_hr/__init__.py) – Module entrypoint.
  - `jobs51_hr/`  
    - [__init__.py](scraper_agents/jobs51_hr/__init__.py) – Imports Jobs51 scraping logic.
  - `liepin_hr/`  
    - [__init__.py](scraper_agents/liepin_hr/__init__.py) – Imports Liepin scraping logic.
- `cache_database/`  
  - [jobs51_cache_database.json](cache_database/jobs51_cache_database.json) – Persistent JSON cache of Jobs51 results.
- `data_extract/`  
  - (parsers and extraction utilities for scraped HTML/data)
- `utils/`  
  - (shared utilities, e.g., logging)  
  - [`logger`](utils/logger.py) – Configured logger for consistent output.
- `tests/`  
  - Unit tests for critical functions; run with:
    ```sh
    pytest
    ```
- `resources/`  
  - Static assets, templates, or data files.
- `logs/`  
  - Runtime logs (`YYYYMMDD_HHMMSS.log`) for debugging.

## File Overview

- [main.py](main.py)  
  Entry point: initializes agents, loads settings, and starts scraping workflows.
- [requirements.txt](requirements.txt)  
  Third‑party dependencies (PyAutoGUI, Selenium, requests, etc.).
- [.gitignore](.gitignore)  
  Excludes virtual environments, logs, cache, and Python artifacts.

## Usage Tips

- Customize `JOB_QUERY`, `IT_SKILLS`, `EXPERIENCE_LEVELS` in [config/settings.py](config/settings.py).
- Switch between PyAutoGUI and Selenium in `main.py`.
- Monitor `logs/` for detailed run information.
- Extend or add new agents under `scraper_agents/` by following the existing structure.

---

Happy scraping!  
Collaborate by forking, branching, and submitting pull requests.// filepath: README.md
# HR-AI-Agent

An automated, human-like browser scraping framework for HR platforms (BossZH, 51Job, Liepin), with caching and configurable settings.

## Prerequisites

- Python 3.8+
- (Optional) Google Chrome or a supported browser for Selenium
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

## Quick Start

1. Clone the repo and create a virtual environment  
   ```sh
   git clone https://github.com/raselmahmud-coder/HR-AI-Agent.git
   cd HR-AI-Agent
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install requirements  
   ```sh
   pip install -r requirements.txt
   ```
3. Configure settings in [config/settings.py](config/settings.py)  
4. Run the main script  
   ```sh
   python main.py
   ```

## Directory Structure

- `.vscode/`  
  - [settings.json](.vscode/settings.json) – VSCode workspace settings (formatting, linting).
- `config/`  
  - [settings.py](config/settings.py) – URLs, timeouts, query parameters, skill maps.  
  - [__init__.py](config/__init__.py) – Exposes constants for easy import.
- `helpers/`  
  - [lookup_caching.py](helpers/lookup_caching.py) – Caches API or page lookup results.  
  - [mouse_movements.py](helpers/mouse_movements.py) – Implements [`human_like_mouse_move`](helpers/mouse_movements.py) and [`human_click`](helpers/mouse_movements.py) for realistic mouse actions.  
  - [sleeping_time.py](helpers/sleeping_time.py) – Generates randomized delays to mimic human pauses.
- `browsers/`  
  - [pyautogui_browser.py](browsers/pyautogui_browser.py) – Automation using PyAutoGUI.  
  - [selenium_browser.py](browsers/selenium_browser.py) – Automation using Selenium WebDriver.  
  - [stealth.min.js](browsers/stealth.min.js) – Injected JS to evade headless detection.
- `scraper_agents/`  
  - `boss_hr/`  
    - [candidate_db.py](scraper_agents/boss_hr/candidate_db.py) – [`CandidateDatabase`](scraper_agents/boss_hr/candidate_db.py) tracks scraped candidates & stats.  
    - [__init__.py](scraper_agents/boss_hr/__init__.py) – Module entrypoint.
  - `jobs51_hr/`  
    - [__init__.py](scraper_agents/jobs51_hr/__init__.py) – Imports Jobs51 scraping logic.
  - `liepin_hr/`  
    - [__init__.py](scraper_agents/liepin_hr/__init__.py) – Imports Liepin scraping logic.
- `cache_database/`  
  - [jobs51_cache_database.json](cache_database/jobs51_cache_database.json) – Persistent JSON cache of Jobs51 results.
- `data_extract/`  
  - (parsers and extraction utilities for scraped HTML/data)
- `utils/`  
  - (shared utilities, e.g., logging)  
  - [`logger`](utils/logger.py) – Configured logger for consistent output.
- `tests/`  
  - Unit tests for critical functions; run with:
    ```sh
    pytest
    ```
- `resources/`  
  - Static assets, templates, or data files.
- `logs/`  
  - Runtime logs (`YYYYMMDD_HHMMSS.log`) for debugging.

## File Overview

- [main.py](main.py)  
  Entry point: initializes agents, loads settings, and starts scraping workflows.
- [requirements.txt](requirements.txt)  
  Third‑party dependencies (PyAutoGUI, Selenium, requests, etc.).
- [.gitignore](.gitignore)  
  Excludes virtual environments, logs, cache, and Python artifacts.

## Usage Tips

- Customize `JOB_QUERY`, `IT_SKILLS`, `EXPERIENCE_LEVELS` in [config/settings.py](config/settings.py).
- Switch between PyAutoGUI and Selenium in `main.py`.
- Monitor `logs/` for detailed run information.
- Extend or add new agents under `scraper_agents/` by following the existing structure.

---

Happy scraping!  
Collaborate by forking, branching, and submitting pull requests.