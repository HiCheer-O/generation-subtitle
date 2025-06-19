import os
import shutil
import logging
from snownlp import SnowNLP

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ]
    )

def clean_temp_files(directory: str):
    """
    清理临时文件夹
    :param directory: 文件夹地址
    :return:
    """
    try:
        shutil.rmtree(directory)
        logging.info(f"Cleaned up temporary directory: {directory}")
    except Exception as e:
        logging.warning(f"Failed to clean up {directory}: {e}")

def preprocess_subtitle_text(text: str, need_segmentation: bool = False) -> str:
    """
    对字幕文本进行预处理：如果需要，使用 SnowNLP 进行中文分词并自动换行。
    """
    if not need_segmentation:
        return text.strip()

    s = SnowNLP(text)
    sentences = s.sentences
    # 去除空句并确保每句在一行
    return '\n'.join([sent.strip() for sent in sentences if sent.strip()])

import pysubs2

def set_wrapstyle_and_margin(
    ass_path: str,
    font_name: str,
    font_size: int,
    primary_color: str,   # 白色（BGR顺序，&HAABBGGRR）
    outline_color: str,   # 黑色描边
    outline: float = 0.5,
    shadow: float = 0.5,
    marginl: int = 10,
    marginr: int = 10,
    marginv: int = 30,     # 新增上下边距参数，默认10
    wrap_style: int = 1
):
    """
    设置 ASS 字幕样式

    :param ass_path: ass 文件路径
    :param font_name: 字体名称
    :param font_size: 字体大小
    :param primary_color: 主字体颜色（ASS格式，如 &H00FFFFFF 表示白色）
    :param outline_color: 描边颜色（ASS格式）
    :param outline: 描边宽度
    :param shadow: 阴影大小
    :param marginl: 左边距
    :param marginr: 右边距
    :param marginv: 下边距（控制字幕纵向位置，数值越小字幕越往上）
    :param wrap_style: 自动换行样式（0=不换行，1=换行）
    """
    subs = pysubs2.load(ass_path)
    for style in subs.styles.values():
        style.fontname = font_name
        style.fontsize = font_size
        style.primarycolor = primary_color
        style.outlinecolor = outline_color
        style.outline = outline
        style.shadow = shadow
        style.marginl = marginl
        style.marginr = marginr
        style.marginv = marginv   # 设置上下边距
        style.wrap_style = wrap_style
    subs.save(ass_path)