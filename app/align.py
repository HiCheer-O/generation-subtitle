import logging
import tempfile
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import pysubs2


def align_subtitles(audio_path: str, subtitle_text: str, srt_output_path: str, max_chars_per_line: int = 13):
    """
    调用 aeneas 对齐字幕

    :param audio_path: 原视频路径
    :param subtitle_text: 文本内容
    :param srt_output_path: srt 字幕输出路径
    :param max_chars_per_line: 每行最大文字数量，默认15
    :return: 无
    """

    config_string = "task_language=zh|is_text_type=plain|os_task_file_format=srt" # 字符串配置
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_path

    # 只在句子内部插入 \N，整体作为一条字幕对齐
    def insert_linebreaks(text: str) -> str:
        # 对每段文本处理
        result = []
        for paragraph in text.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            lines = [paragraph[i:i + max_chars_per_line] for i in range(0, len(paragraph), max_chars_per_line)]
            result.append("\\N".join(lines))  # 用 \\N 加换行
        return "\n".join(result)

    subtitle_text = insert_linebreaks(subtitle_text)

    # 创建临时文本文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as temp_txt:
        temp_txt.write(subtitle_text)
        text_file_path = temp_txt.name

    task.text_file_path_absolute = text_file_path
    task.sync_map_file_path_absolute = srt_output_path

    logging.info("Running aeneas alignment task...")
    ExecuteTask(task).execute()
    task.output_sync_map_file()
    logging.info("Aeneas alignment complete.")

def srt_to_ass(srt_path, ass_path):
    """
    srt 转 ass 格式
    :param srt_path: srt 文件路径
    :param ass_path: ass 文件路径
    :return:
    """
    subs = pysubs2.load(srt_path)
    subs.save(ass_path)