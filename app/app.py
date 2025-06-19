import os
from datetime import datetime
import logging
from flask import Flask, request, send_file
from align import align_subtitles, srt_to_ass
from burn import burn_subtitle_to_video
from utils import setup_logging, preprocess_subtitle_text, set_wrapstyle_and_margin, clean_temp_files

app = Flask(__name__)
setup_logging()

# 当前脚本所在目录（app.py 或 burn.py 所在目录）
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def index():
    return 'Hello, this is the root route!'

@app.route("/api/burn-file", methods=["POST"])
def burn_file():
    """
    字幕生成接口

    :return: 生成字幕的视频文件
    """

    tmp_dir = None # 定义临时目录参数
    base_tmp_dir = os.path.join(BASE_DIR, 'tmp') # 临时文件目录
    os.makedirs(base_tmp_dir, exist_ok=True)  # 确保基础 tmp 目录存在

    try:
        file = request.files.get("file") # 获取源文件
        subtitle_text = request.form.get("subtitle") # 获取字幕内容
        font_name = request.form.get("font_name", "SimHei")  # 实际是字体名称，默认字体 SimHei
        font_path = os.path.join(BASE_DIR, 'fonts') # 字体文件夹
        font_size = int(request.form.get("font_size") or 9) # 字体大小，默认22
        primary_color = request.form.get("font_color") or "&H00FFFFFF" # 字体颜色
        outline_color = request.form.get("outline_color") or "&H00000000" # # 描边颜色
        need_segmentation = request.form.get("need_segmentation", "false").lower() == "true" # 是否需要分词，ture：需要；默认 false

        # 必要参数校验，源文件、字幕文本内容
        if not file or not subtitle_text:
            return {"error": "file and subtitle are required"}, 400

        logging.info("收到文件和字幕。开始处理...")

        subtitle_text = preprocess_subtitle_text(subtitle_text, need_segmentation) # 预处理字幕文本

        # 在 tmp 目录中创建子目录，防止并发冲突
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        tmp_dir = os.path.join(base_tmp_dir, timestamp)
        os.makedirs(tmp_dir, exist_ok=True) # 创建临时文件

        input_path = os.path.join(tmp_dir, "input.mp4") # 临时输入文件
        srt_path = os.path.join(tmp_dir, "subtitle.srt") # 临时字幕文件 srt 格式
        ass_path = os.path.join(tmp_dir, "subtitle.ass") # 临时字幕文件 ass 格式
        output_path = os.path.join(tmp_dir, "output.mp4") # 临时最终生成的字幕视频

        file.save(input_path) # 保存临时输入文件
        logging.info(f"将 输入视频 保存到 {input_path}")

        align_subtitles(input_path, subtitle_text, srt_path) # 对齐字幕
        srt_to_ass(srt_path, ass_path) # srt 格式转 ass
        set_wrapstyle_and_margin(ass_path ,font_name, font_size, primary_color, outline_color) # 设置 ass 字幕样式

        logging.info(f"字幕对齐完成: {ass_path}")

        # 烧录字幕
        burn_subtitle_to_video(
            input_path,
            ass_path,
            output_path,
            font_path
        )

        logging.info(f"字幕烧成视频: {output_path}")

        return send_file(output_path, as_attachment=True, download_name="output.mp4")

    except Exception as e:
        logging.exception("处理视频时出错:")
        return {"error": str(e)}, 500

    finally:
        if tmp_dir:
            clean_temp_files(tmp_dir)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8091, debug=False)