#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF -> PNG 拖放转换工具

用法：
    把一个或多个 PDF 文件拖放到本脚本（或打包后的 exe）图标上即可。
    也可以在命令行运行：  python pdf2png.py a.pdf b.pdf

输出：
    每页生成一张 PNG，保存在“运行目录”（exe / 脚本所在目录）下，
    文件名为  <PDF文件名>_p001.png、<PDF文件名>_p002.png ...

依赖：
    pip install pymupdf
打包：
    pip install pyinstaller
    pyinstaller -F -n pdf2png pdf2png.py
"""

import os
import sys
import traceback

# ---------------- 可调参数 ----------------
DPI = 150          # 输出分辨率：150 够清晰，300 更清楚但文件更大
TRANSPARENT = False  # True = 透明背景；False = 白色背景
# -----------------------------------------


def run_dir():
    """exe / 脚本所在目录（拖放时的工作目录不一定可靠，所以用这个）。"""
    if getattr(sys, "frozen", False):          # PyInstaller 打包后
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def unique_path(folder, filename):
    """避免覆盖已有文件：重名时自动加 _1、_2 ..."""
    base, ext = os.path.splitext(filename)
    path = os.path.join(folder, filename)
    n = 1
    while os.path.exists(path):
        path = os.path.join(folder, "%s_%d%s" % (base, n, ext))
        n += 1
    return path


def convert(pdf_path, out_dir):
    import pymupdf  # 老版本可用 import fitz as pymupdf

    pdf_path = os.path.abspath(pdf_path)
    if not os.path.isfile(pdf_path):
        print("[跳过] 文件不存在：%s" % pdf_path)
        return 0

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    print("\n>>> %s" % pdf_path)

    doc = pymupdf.open(pdf_path)
    try:
        if doc.needs_pass:
            # 只设置了权限限制、没有打开密码的 PDF，空密码即可解开
            if not doc.authenticate(""):
                print("[错误] PDF 有打开密码，无法转换。")
                return 0

        total = doc.page_count
        if total == 0:
            print("[警告] 这个 PDF 没有页面。")
            return 0

        print("    共 %d 页，%d DPI，输出到：%s" % (total, DPI, out_dir))
        zoom = DPI / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)
        width = len(str(total))
        ok = 0

        for i, page in enumerate(doc, start=1):
            name = "%s_p%s.png" % (stem, str(i).zfill(max(3, width)))
            path = unique_path(out_dir, name)
            try:
                pix = page.get_pixmap(matrix=matrix, alpha=TRANSPARENT)
                pix.save(path)
                ok += 1
                print("    [%d/%d] %s  (%dx%d)"
                      % (i, total, os.path.basename(path), pix.width, pix.height))
            except Exception as e:
                print("    [%d/%d] 失败：%s" % (i, total, e))

        print("    完成：%d/%d 页" % (ok, total))
        return ok
    finally:
        doc.close()


def main():
    args = [a for a in sys.argv[1:] if a not in ("--no-pause",)]
    no_pause = "--no-pause" in sys.argv[1:]

    print("=" * 60)
    print("PDF 转 PNG 工具   (DPI=%d)" % DPI)
    print("=" * 60)

    if not args:
        print("\n请把 PDF 文件拖放到本程序图标上。")
        print("命令行用法：pdf2png.exe 文件1.pdf 文件2.pdf")
        return 1

    try:
        import pymupdf  # noqa: F401
    except ImportError:
        print("\n[错误] 缺少依赖 PyMuPDF，请先执行：pip install pymupdf")
        return 1

    out_dir = run_dir()
    pdfs = [a for a in args if os.path.splitext(a)[1].lower() == ".pdf"]
    for a in args:
        if a not in pdfs:
            print("[跳过] 不是 PDF：%s" % a)

    total_ok = 0
    for p in pdfs:
        try:
            total_ok += convert(p, out_dir)
        except Exception:
            print("[错误] 处理 %s 时出错：" % p)
            traceback.print_exc()

    print("\n全部结束，共生成 %d 张 PNG，保存在：%s" % (total_ok, out_dir))
    return 0 if total_ok else 1


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    except Exception:
        traceback.print_exc()
    # 拖放运行时窗口会一闪而过，这里停一下让人看到结果
    if "--no-pause" not in sys.argv[1:]:
        try:
            input("\n按回车键退出...")
        except (EOFError, KeyboardInterrupt):
            pass
    sys.exit(code)