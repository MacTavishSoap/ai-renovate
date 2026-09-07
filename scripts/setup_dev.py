# ============================================================================
# 一键搭建开发环境 — Windows / macOS / Linux 通用
# 用法：python scripts\setup_dev.py     (Windows)
#       python scripts/setup_dev.py     (macOS/Linux)
# ============================================================================
"""
AI 家装项目 — 开发环境一键搭建脚本

功能：
  1. 创建虚拟环境 (venv)
  2. 安装锁定依赖 (requirements.lock)
  3. 复制 .env.example → .env（如不存在）
  4. 运行测试验证

用法：
  python scripts/setup_dev.py
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# 颜色输出
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def info(msg):  print(f"{GREEN}✓{RESET} {msg}")
def warn(msg):  print(f"{YELLOW}⚠{RESET} {msg}")
def fail(msg):  print(f"{RED}✗{RESET} {msg}")

def main():
    # 确定项目根目录（backend/ 的上级）
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    backend_dir = project_root / "backend"

    if not backend_dir.exists():
        fail(f"找不到 backend 目录：{backend_dir}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  AI 家装项目 — 开发环境搭建")
    print(f"  Python {sys.version.split()[0]} @ {platform.system()}")
    print(f"{'='*60}\n")

    # 1. 检查 Python 版本
    if sys.version_info < (3, 11):
        fail("需要 Python 3.11+，当前版本过低")
        sys.exit(1)
    if sys.version_info < (3, 12):
        warn("推荐 Python 3.12.7，当前版本可用但可能不一致")
    else:
        info(f"Python 版本检查通过: {sys.version.split()[0]}")

    os.chdir(backend_dir)

    # 2. 创建虚拟环境
    venv_dir = backend_dir / "venv"
    if venv_dir.exists():
        warn(f"虚拟环境已存在: {venv_dir}")
        answer = input("  重新创建？(y/N): ").strip().lower()
        if answer == "y":
            shutil.rmtree(venv_dir)
            create_venv(venv_dir)
        else:
            info("复用现有虚拟环境")
    else:
        create_venv(venv_dir)

    # 3. 获取 pip 路径
    if platform.system() == "Windows":
        pip_path = str(venv_dir / "Scripts" / "pip.exe")
        python_path = str(venv_dir / "Scripts" / "python.exe")
    else:
        pip_path = str(venv_dir / "bin" / "pip")
        python_path = str(venv_dir / "bin" / "python")

    # 4. 升级 pip
    print("\n--- 升级 pip ---")
    run_cmd([python_path, "-m", "pip", "install", "--upgrade", "pip"])

    # 5. 安装锁定依赖
    lock_file = backend_dir / "requirements.lock"
    if lock_file.exists():
        print("\n--- 安装锁定依赖 (requirements.lock) ---")
        info("使用锁定版本，确保环境完全一致")
        run_cmd([pip_path, "install", "-r", str(lock_file)])
    else:
        print("\n--- 安装依赖 (pyproject.toml) ---")
        warn("未找到 requirements.lock，使用 pyproject.toml（版本可能不完全一致）")
        run_cmd([pip_path, "install", "-e", ".[dev]"])

    # 6. 以可编辑模式安装项目本身
    print("\n--- 安装项目本身 (可编辑模式) ---")
    run_cmd([pip_path, "install", "-e", ".", "--no-deps"])

    # 7. 复制 .env.example → .env
    env_example = backend_dir.parent / ".env.example"
    env_file = backend_dir.parent / ".env"
    if env_example.exists():
        if not env_file.exists():
            shutil.copy2(env_example, env_file)
            info(f"已创建 .env 文件: {env_file}")
            warn("请编辑 .env 填入实际的 API Key 等配置")
        else:
            info(".env 已存在，跳过")
    else:
        warn("未找到 .env.example")

    # 8. 运行测试验证
    print("\n--- 运行测试验证 ---")
    ret = subprocess.call([python_path, "-m", "pytest", "tests/", "-v", "--tb=short"])
    if ret == 0:
        info("测试全部通过！环境搭建成功 ✅")
    else:
        warn("测试未通过，请检查上方输出")

    # 9. 提示下一步
    print(f"\n{'='*60}")
    print("  🎉 环境搭建完成！")
    print(f"{'='*60}")
    print("\n下一步：")
    if platform.system() == "Windows":
        print(f"  cd backend")
        print(f"  venv\\Scripts\\activate")
    else:
        print(f"  cd backend")
        print(f"  source venv/bin/activate")
    print(f"  uvicorn app.main:app --reload --port 8000")
    print(f"\n  📖 API 文档: http://127.0.0.1:8000/docs")
    print()

def create_venv(venv_dir):
    print(f"\n--- 创建虚拟环境: {venv_dir} ---")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    info("虚拟环境创建成功")

def run_cmd(cmd):
    """运行命令，失败时继续而非退出"""
    ret = subprocess.call(cmd)
    if ret != 0:
        warn(f"命令返回非零退出码: {ret}")
    return ret

if __name__ == "__main__":
    main()
