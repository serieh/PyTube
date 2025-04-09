# https://www.youtube.com/watch?v=dQw4w9WgXcQ
import os, sys, time, traceback, ctypes, yt_dlp, shutil
from prettytable import PrettyTable


def is_admin():
    try:
        try:return ctypes.windll.shell32.IsUserAnAdmin()
        except:return False
    except Exception as e:
        log_error(e, "Unexpected error while checking admin")


def run_as_admin():
    try:
        if is_admin():return
        else:   # Re-run the program with admin rights
            params = ' '.join([f'"{arg}"' for arg in sys.argv])
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            if result <= 32:    # The user refused the elevation
                cprint("Administrator privileges are required to run this program.", 'e')
                time.sleep(2)
            sys.exit(0)
    except Exception as e:
        log_error(e, "Unexpected error while getting admin")


def log_error(e, message='An Exception Happened :('):
    error_message = f"{message}\n{'#'*100}\n{str(e)}\n{'#'*100}\n{traceback.format_exc()}"
    try:
        import keyboard
        with open('ytdownload_error_log.txt', 'a', encoding='utf-8') as file:file.write(error_message)
        print('\033[91m' + '\n' + message + '\033[0m')
        print(f"\nError Log was saved to 'ytdownload_error_log.txt'")
    except Exception as log_error:print(f"Failed to write error log: {log_error}")
    print("Press any key to continue...")
    keyboard.read_event()
    sys.exit(1)


def cprint(string, type = 'm2'):
    try:
        colors = {'e': '\033[91m',  # Error [Red]
                  'w': '\033[38;5;208m',  # Warring or Notes [Orange]
                  'w2':'\033[38;5;214m', # Warring or Notes v2 [Light Orange]
                  'c': '\033[92m',  # Confirmation massage [Light Green]
                  'o': '\033[97m',  # Regular output [White]
                  'm': '\033[33m',  # Massage output [Yellow]
                  'm2': '\033[93m' # Massage output v2 [Light Yellow]
                  }
        print(colors.get(type,colors['o']) + string + '\033[0m')
    except Exception as e:
        log_error(e,"Unexpected error in the Printing possess")


def cinput(string, type = 1):
    try:
        color = '\033[33m' if type == 1 else '\033[93m' # if: Yellow ,else: Light Yellow
        inputted_string = input(color + string + '\033[94m').strip()
        print('\033[0m',end='')
        return inputted_string
    except Exception as e:
        log_error(e, "Unexpected error in the Input possess")


def check_ffmpeg():
    try:
        if not shutil.which("ffmpeg"):
            cprint("\n*** Missing dependencies: ffmpeg\n*** Please install it or add to PATH and try again.",
                   'e')
            time.sleep(3)
            sys.exit(0)
    except Exception as e:
        log_error(e, "Failed to detect FFmpeg. Please install it and add it to your system PATH.")


def exit_program():
    clear_terminal()
    cprint('Good-by :)', 'w')
    cprint(f'\nExiting in 3 Seconds ...')
    for i in range(3,0, -1):
        cprint(f'{i}...')
        time.sleep(1)
    sys.exit(0)


def clear_terminal():
    os.system('cls')


def change_codec(filename, encode):
    import tempfile, subprocess
    try:
        temp_output_file = os.path.join(tempfile.gettempdir(), os.path.basename(filename))
        query =  ['ffmpeg', '-i', filename, '-y', temp_output_file]
        query[3:3] = ['-c:v',encode['desired_codec'],'-c:a','copy'] if encode['encode_type'] == 1 else ['-c:a',encode['desired_codec']]
        subprocess.run(query, check=True)
        if os.path.exists(temp_output_file):
            shutil.move(temp_output_file, filename)
            cprint(f"*** Video Converted successfully", 'c')
        else:
            cprint("Conversion failed. Original file was not replaced.", 'e')

    except PermissionError as e:
        log_error(e,"Permission denied. Try running as administrator.")
    except FileNotFoundError as e:
        log_error(e, "Error: FFmpeg is not installed or not found in PATH.")
    except subprocess.TimeoutExpired as e:
        log_error(e, "FFmpeg conversion timed out.")
    except subprocess.CalledProcessError as e:
        log_error(e, f"FFmpeg conversion failed: {e.stderr}")
    except OSError as e:
        log_error(e, "File system error (permission denied, file in use, etc.)")
    except Exception as e:
        log_error(e, "Unexpected error in while encoding")


def download(url, extension, ydl_options, encode):
    try:
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            filename = os.path.splitext(ydl.prepare_filename(ydl.extract_info(url, download=True)))[0] + '.' + extension
        if encode['encode_type'] != 0:change_codec(filename, encode)
        clear_terminal()
        cprint(f"*** Download saved to: '{filename}' successfully!", 'c')
        choice = cinput("\n# Download another video/audio? (Enter:no /y:yes): ").lower()
        clear_terminal()
        main() if choice.lower() == 'y' else exit_program()

    except yt_dlp.utils.DownloadError as e:cprint(f"Download error: {e}", 'e')
    except yt_dlp.utils.ExtractorError as e:cprint(f"Extractor error: {e}", 'e')
    except yt_dlp.utils.PostProcessingError as e:cprint(f"Post-processing error: {e}", 'e')
    except OSError as e:log_error(e, "File system error (permission denied, file in use, etc.)")
    except Exception as e:log_error(e, "Failed to download the video. Ensure yt-dlp is installed and the URL is correct.")


def save_directory(ydl_options):
    try:
        clear_terminal()
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        choice = cinput(f"# Change download location? (Default:'{default_path}') (y/n): ").lower()
        if choice == 'y':
            while True:
                new_directory = cinput('# Enter the path (Default:d): ',2)
                if not new_directory:continue
                elif new_directory.lower() == 'd':break
                elif os.path.exists(new_directory):
                    ydl_options['outtmpl'] = os.path.join(new_directory, '%(title)s.%(ext)s')
                    return
                else:cprint("\nDirectory does not exist. Please try again.", 'e')

        ydl_options['outtmpl'] = os.path.join(default_path, "%(title)s.%(ext)s")
    except PermissionError as e:
        log_error(e,"Permission denied. Try running as administrator.")
    except Exception as e:log_error(e,"Unexpected error in setting the save directory")


def video_defaults(chosen_format, ydl_options):
    try:
        clear_terminal()
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        cprint('# Do Defaults ? (Enter:Accept /n:No)', 'w2')
        cprint(f'- Video ID: {chosen_format.get('format_id')}'
              f'\n- RESOLUTION: {chosen_format.get('resolution')}'
              f'\n- FPS: {str(chosen_format.get('fps')).replace('.0', '')}'
              f'\n- Extension: MP4'
              f'\n- VCodec: H.264/AVC1'
              f'\n- Size: {format_size(chosen_format.get('filesize'))}'
              f'\n- With Audio: YES'
              f'\n- Save Directory: {default_path}'
               , 'w2')

        while True:
            choice = cinput('\n>> ')
            if not choice:
                extension = 'mp4'
                ydl_options['merge_output_format'] = extension
                ydl_options['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': extension}]
                encode = {
                    'encode_type': 1,
                    'desired_codec': 'libx264',
                    'codec_name': 'H.264/AVC1'
                }
                ydl_options['format'] = chosen_format.get('format_id') + '+ba/best'
                ydl_options['outtmpl'] = os.path.join(default_path, "%(title)s.%(ext)s")
                cprint('*** Using Defaults.....','w')
                return extension, encode, True
            elif choice.lower() == 'n':return None, None, False
            cprint("Invalid Choice. Please try again.", 'e')
    except Exception as e:
        log_error(e,"Unexpected error while setting video defaults")


def get_audio():
    try:
        clear_terminal()
        choice = cinput("# Download with audio? (Enter:yes /n: no): ").lower()
        return '' if choice.lower() == 'n' else '+ba/best'
    except Exception as e:
        log_error(e,"Unexpected error in get_audio")


def get_vcodec(codec):
    try:
        clear_terminal()
        encode = {'encode_type':0}   # 0: No, 1: Video, 2: Audio
        vcodec_list = {
            '1': ['H.264/AVC1', 'libx264'],
            '2': ['H.265/HEVC', 'libx265'],
            '3': ['VP9', 'libvpx-vp9'],
            '4': ['VP8', 'libvpx'],
            '5': ['AV1', 'libaom-av1'],
            '6': ['MPEG-2', 'mpeg2video'],
            '7': ['ProRes', 'prores'],
            '8': ['Theora', 'libtheora'],
            '9': ['DivX', 'mpeg4'],
            '10': ['Xvid', 'libxvid']
        }
        codec = codec.split('.')[0].replace('0', '').upper()
        cprint('# Change the vcodec (Enter:Stays the same): ','m')
        for k, v in vcodec_list.items(): cprint(f"[{k}] {v[0].upper()}")
        choice = cinput('\n>> ')
        choice = vcodec_list.get(choice, [False])
        if not choice[0] or codec in choice[0]:
            encode = {'encode_type':0}   # 0: No, 1: Video, 2: Audio
        else:
            encode = {
                'encode_type':1,
                'desired_codec':choice[1],
                'codec_name':choice[0]
            }
        return encode
    except Exception as e:
        log_error(e,"Unexpected error in get_vcodec")


def get_extension(original_extension, extension_list):
    try:
        clear_terminal()
        cprint('# Change the format (Enter:Stays the same): ','m')
        for k, v in extension_list.items(): cprint(f"[{k}] {v.upper()}")
        choice = cinput('\n>> ')
        return extension_list.get(choice, original_extension)
    except Exception as e:
        log_error(e,"Unexpected error in get_extension")


def format_size(size):
    try:
        if size is None:
            return "Unknown"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except Exception as e:
        log_error(e,"Unexpected error in format_size")


def video_format(formats):
    try:
        clear_terminal()
        past_height = None
        available_formats = {}
        count = 1
        table = PrettyTable()
        table.field_names = ["Index", "Ext", "Resolution", "FPS", "Filesize", "VCodec"]

        for f in formats:
            if f.get('vcodec') not in ['audio only', None, 'none'] and f.get('height') and f.get('height') >= 144:
                available_formats[count] = f
                if past_height and past_height != f.get('height'):
                    table.add_row(
                        ["---", "-" * 5, "-" * 10, "-" * 10, "-" * 7, "-" * 14])  # Simulate horizontal line

                table.add_row([
                    str(count), f.get('ext'), str(f.get('resolution')), (str(f.get('fps')) + 'fps').replace('.0', ''),
                    format_size(f.get('filesize')), f.get('vcodec')
                ])

                past_height = f.get('height')
                count += 1
        cprint(str(table))

        while True:
            chosen_format = cinput("\n# Choose format by number (Enter:The Best Video): ")
            if not chosen_format:return available_formats[count - 1]
            elif chosen_format.isdigit() and available_formats.get(int(chosen_format) , False):return available_formats.get(int(chosen_format))
            cprint("Invalid Choice. Please try again.", 'e')
    except Exception as e:
        log_error(e,"Unexpected error in video_format")


def video_options(formats, ydl_options):
    try:
        chosen_format = video_format(formats)
        extension, encode, indicator =  video_defaults(chosen_format, ydl_options)
        if indicator:return extension, encode

        extension_list = {'1': 'mp4', '2': 'mkv', '3': 'webm', '4': 'avi', '5': 'mov', '6': 'flv'}
        extension = get_extension(chosen_format.get('ext'), extension_list)
        ydl_options['merge_output_format'] = extension
        ydl_options['postprocessors'] = [{'key': 'FFmpegVideoConvertor','preferedformat': extension}]
        encode = get_vcodec(chosen_format.get('vcodec'))
        ydl_options['format'] = chosen_format.get('format_id') + get_audio()
        save_directory(ydl_options)

        clear_terminal()
        cprint("# Download Configuration:", 'w2')
        cprint(f'- Video ID: {chosen_format.get('format_id')}'
              f'\n- RESOLUTION: {chosen_format.get('resolution')}'
              f'\n- FPS: {str(chosen_format.get('fps')).replace('.0', '')}'
              f'\n- Extension: {extension.upper()}'
              f'\n- VCodec: {encode.get('codec_name' , 'Missing').upper() if encode.get('encode_type', 0) != 0 else chosen_format.get('vcodec' , 'Missing')}'
              f'\n- Size: {format_size(chosen_format.get('filesize'))}'
              f'\n- With Audio: {'YES' if '+ba/best' in ydl_options['format']  else 'NO'}'
              f'\n- Save Directory: {ydl_options['outtmpl'].replace("\\%(title)s.%(ext)s",'')}'
               , 'w2')
        return extension, encode
    except Exception as e:
        log_error(e,"Unexpected error in video_options")


def audio_defaults(chosen_format, ydl_options):
    try:
        clear_terminal()
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        cprint('# Do Defaults ? ( Enter:Accept , n:No )', 'w')
        cprint(f'- Audio ID: {chosen_format.get('format_id')}'
              f'\n- Extension: MP3'
              f'\n- ACodec: MP3'
              f'\n- ABR: {chosen_format.get('abr')}'
              f'\n- ASR: {chosen_format.get('asr')}'
              f'\n- Size: {format_size(chosen_format.get('filesize'))}'
              f'\n- Save Directory: {default_path}'
               , 'w2')
        while True:
            choice = cinput('\n>> ')
            if not choice:
                extension = 'mp3'
                ydl_options['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': extension}]
                encode = {'encode_type': 0}
                ydl_options['outtmpl'] = os.path.join(default_path, "%(title)s.%(ext)s")
                cprint('*** Using Defaults.....','w')
                return extension, encode, True
            elif choice.lower() == 'n':return None, None, False
            cprint("Invalid Choice. Please try again.", 'e')
    except Exception as e:
        log_error(e,"Unexpected error while setting audio defaults")


def get_acodec(codec ,extension ):
    try:
        clear_terminal()
        if extension in ['mp3', 'opus', 'flac', 'dsf', 'aac']:return {'encode_type': 0}
        codec = codec.split('.')[0].replace('0', '').upper()
        acodec_list = {
            'm4a': {'1': 'aac', '2': 'alac'},
            'wav': {'1': 'pcm_s16le', '2': 'adpcm', '3': 'pcm_f32le'},
            'ogg': {'1': 'vorbis', '2': 'opus', '3': 'flac', '4': 'Speex'},
            'wma': {'1': 'wmav2', '2': 'wmapro', '3': 'wmalossless'},
            'mka': {'1': 'aac', '2': 'vorbis', '3': 'opus', '4': 'flac', '5': 'mp3'},
            'amr': {'1': 'amr_nb', '2': 'amr_wb'},
            'aiff': {'1': 'pcm_s16be', '2': 'pcm_s24be'}
        }
        cprint('# Change the vcodec (Enter:The first choice): ', 'm')
        available_acodecs = acodec_list[extension]
        for k, v in available_acodecs.items(): cprint(f"[{k}] {v.upper()}")
        choice = cinput('\n>> ')
        choice = available_acodecs.get(choice, False)
        if not choice or codec in choice:encode = {'encode_type': 0}  # 0: No, 1: Video, 2: Audio
        else:
            encode = {
                'encode_type':2,
                'desired_codec':choice,
                'codec_name':choice
            }
        return encode
    except Exception as e:
        log_error(e,"Unexpected error while setting the audio options")


def audio_format(formats):
    try:
        clear_terminal()
        available_formats = {}
        count = 1
        table = PrettyTable()
        table.field_names = ["Index", "Ext", "ACodec", "ABR", "ASR", "Filesize"]
        for f in formats:
            if f.get('acodec') not in ['video only', None] and f.get('abr') and f.get('asr'):
                available_formats[count] = f
                table.add_row([
                    str(count), f.get('ext').upper(), str(f.get('acodec')), str(f.get('abr')), str(f.get('asr')),
                    format_size(f.get('filesize'))
                ])
                count += 1
        cprint(str(table))

        while True:
            chosen_format = cinput("\n# Choose audio format by number (Enter:The best): ")
            if not chosen_format:return available_formats[count - 1]
            elif available_formats.get(int(chosen_format), False):return available_formats.get(int(chosen_format))
            cprint("Invalid Choice. Please try again.", 'e')
    except Exception as e:
        log_error(e,"Unexpected error while Selecting audio format")


def audio_options(formats, ydl_options):
    try:
        chosen_format = audio_format(formats)
        extension_list = {'1': 'mp3',
                          '2': 'aac',
                          '3': 'm4a',
                          '4': 'opus',
                          '5': 'wav',
                          '6': 'flac',
                          '7': 'amr',
                          '8': 'aiff',
                          '9': 'dsf',
                          '10': 'ogg',
                          '11': 'wma',
                          '12': 'mka'
                          }

        extension, encode, indicator =  audio_defaults(chosen_format, ydl_options)
        if indicator:return extension, encode

        extension =  get_extension(chosen_format.get('ext'),extension_list )
        if extension == 'webm':
            extension = 'mp3'
            cprint("*** Format defaults to 'MP3'", 'w')
        ydl_options['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': extension}]
        encode = get_acodec(chosen_format.get('acodec'), extension)
        save_directory(ydl_options)

        clear_terminal()
        cprint("# Download Configuration:",'w2' )
        cprint(f"- Audio ID: {chosen_format.get('format_id')}"
              f'\n- Extension: {extension.upper()}'
              f"\n- ACodec: {encode['codec_name'].upper() if encode['encode_type'] != 0 else chosen_format.get('acodec')}"
              f'\n- ABR: {chosen_format.get('abr')}'
              f'\n- ASR: {chosen_format.get('asr')}'
              f'\n- Size: {format_size(chosen_format.get('filesize'))}'
              f'\n- Save Directory: {ydl_options['outtmpl'].replace(r"\%(title)s.%(ext)s","")}'
               , 'w2')
        return extension, encode
    except Exception as e:
        log_error(e, "Unexpected error while setting the audio options")


def get_formats():
    while True:
        try:
            ydl_options = {'quiet': True , 'noplaylist': True,'socket_timeout': 30, 'logger': None}
            url = cinput("\n# Enter YouTube video URL: ")
            if not url:continue
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                return url, (ydl.extract_info(url, download=False))['formats']
        except Exception as e:cprint("Error: Invalid YouTube URL or video unavailable.", 'e')


def main():
    try:
        cprint("\n***To Quit at any moment press [Ctrl + C]***", 'w')
        ydl_options = {'socket_timeout': 10, 'noplaylist': True, 'quiet': True, 'logger': None,}
        url, formats = get_formats()
        clear_terminal()
        choice = cinput("# Download Video or only Audio (1/Enter:Video, 2:Audio): ")
        extension, encode = audio_options(formats, ydl_options) if choice == '2' else video_options(formats, ydl_options)
        download(url, extension, ydl_options, encode)
    except KeyboardInterrupt: exit_program()
    except Exception as e:log_error(e, "Unexpected error in the main program execution.")


if __name__ == '__main__':
    clear_terminal()
    run_as_admin()
    check_ffmpeg()
    cprint('Welcome to PyTube !', 'w')
    main()