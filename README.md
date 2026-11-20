# pdf2png-win

把 PDF 拖放到 exe 图标上，每一页自动转成 PNG，保存在 exe 所在目录。

Windows 单文件绿色程序，免安装、目标机器不需要装 Python。

## 用法

把 PDF 文件（支持一次拖多个）拖到 `pdf2png.exe` 图标上，松手即可。

- 输出目录：**exe 所在目录**
- 文件名：`原文件名_p001.png`、`原文件名_p002.png` ……
- 转换完窗口停住显示结果，按回车关闭

也支持命令行：

```bash
pdf2png.exe a.pdf b.pdf
```

加 `--no-pause` 跳过结尾的"按回车退出"，方便批处理调用：

```bash
pdf2png.exe a.pdf --no-pause
```

## 行为说明

| 情况 | 处理方式 |
| --- | --- |
| 输出文件重名 | 不覆盖，自动加 `_1`、`_2` 后缀 |
| 拖入非 PDF 文件 | 提示并跳过 |
| 仅权限限制、无打开密码的 PDF | 用空密码解开，正常转换 |
| 设了打开密码的 PDF | 提示并跳过 |
| 某一页渲染失败 | 打印错误，继续转后面的页 |
| 多页 PDF | 页码位数自动对齐（超过 999 页时用 4 位） |

## 参数

在 `pdf2png.py` 顶部：

```python
DPI = 150            # 输出分辨率，300 更清晰但文件更大
TRANSPARENT = False  # True = 透明背景，False = 白色背景
```

A4 页面在 150 DPI 下输出 1240×1755 像素，300 DPI 下为 2480×3508。

## 从源码运行

```bash
pip install -r requirements.txt
```

```bash
python pdf2png.py 你的文件.pdf
```

## 打包 exe

```bash
pip install pyinstaller
```

```bash
pyinstaller -F --console -n pdf2png --noconfirm pdf2png.py
```

产物在 `dist/pdf2png.exe`，约 48 MB（PyMuPDF 自带 MuPDF 渲染引擎，体积主要来自这里）。
仓库里的 `pdf2png.spec` 是本次打包生成的配置，也可以直接用：

```bash
pyinstaller --noconfirm pdf2png.spec
```

## 下载

编译好的 exe 在 [Releases](../../releases) 页面，下载 `pdf2png.exe` 即可使用。

首次运行时 Windows SmartScreen 可能提示"未知发布者"（未做代码签名），
点"更多信息 → 仍要运行"。

## 技术栈

- [PyMuPDF](https://pymupdf.readthedocs.io/) 1.28.2 — PDF 渲染
- [PyInstaller](https://pyinstaller.org/) 6.22.3 — 单文件打包
- 构建环境：Python 3.14.7 / Windows 11 x64

## 目录结构

```
pdf2png.py       主程序（全部逻辑，单文件）
pdf2png.spec     PyInstaller 打包配置
requirements.txt 运行依赖
```