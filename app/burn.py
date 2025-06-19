import subprocess
import logging

def burn_subtitle_to_video(input_path, ass_path, output_path, font_dir):
    """
    字幕烧录逻辑

    :param input_path: 源文件路径
    :param ass_path: ass 字幕路径
    :param output_path: 生成后的字幕视频路径
    :param font_dir: 字体目录
    :return: 无
    """
    filter_args = (
        f"subtitles='{ass_path}':"
        f"fontsdir='{font_dir}':"
    )

    logging.info("字幕过滤参数: %s", filter_args)

    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", filter_args,
        "-c:v", "libx264",
        "-crf", "20",
        "-preset", "veryfast",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]

    logging.info(f"运行ffmpeg命令: {' '.join(command)}")
    subprocess.run(command, check=True)
    logging.info("FFmpeg 成品加工.")