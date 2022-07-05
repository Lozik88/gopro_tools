import os
import glob
import subprocess
import logging
import datetime
import sys

from pathlib import Path
is_main = __name__ == '__main__'
log_file = f'gopro_logs_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
if is_main:
    if sys.platform == 'win32':
        output = os.environ['USERPROFILE']
    if sys.platform == 'linux':
        output = os.environ['HOME']
    output = os.path.join(output,'Videos','gopro')
    if not os.path.exists(output):
        os.mkdir(output)
    logs = os.path.join(
        output
        ,log_file
        )
else:
    logs = os.path.join(os.path.dirname(__name__),log_file)
    output = 'somePath'

file_handler = logging.FileHandler(filename=logs)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    # filename=logs
    handlers=handlers
    # ,format='%(asctime)s %(levelname)-8s %(message)s'
    ,format = '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    ,datefmt='%Y-%m-%d %H:%M:%S'
    ,level=logging.DEBUG
    )

def get_chaptered(path:str) -> list:
    """
    Used to group and order gopro .mp4 files. Returns dict of files grouped by fileid.
    
    {
        gopro_fileid1:
        {
            0:file_path
            ,1:file_path
            ,2:file_path
        },
        gopro_fileid2:
        {
            0:file_path
            ,1:file_path
        }
    }
    
    https://community.gopro.com/s/article/GoPro-Camera-File-Naming-Convention?language=en_US
    """
    files={}
    logging.info(f"Processing files in directory: {path}")
    for file in glob.glob(os.path.join(path,"*.mp4")):
        file = Path(file)
        fileid = file.stem[4:]
        chapter = file.stem[2:4]
        if not fileid in files.keys():
            files[fileid] = {}
        if chapter == 'PR':
            chapter = 0
        else:
            chapter = int(chapter)
        files[fileid][chapter] = str(file)
    return files        

def join_chaptered(d:dict,dest:str) -> None:
    """
    joins files grouped by `get_chaptered()`
    """
    for fileid,files in d.items():
        output = os.path.join(dest,fileid+'.mp4')
        fileorder=[]
        for i in range(len(files)):
            fileorder.append(
                "file '"+
                'file:'+files[i].replace(
                '\\','/').replace(
                    "'","'\\''") + "'"
            )
        file_cmd = os.path.join(dest,fileid+'.txt')
        with open(file_cmd,'w') as f:
            f.write('\n'.join(fileorder))
        logging.info('merging files:\n\t{0}'.format('\n\t'.join(files.values())))
        process_output = subprocess.Popen(
            ['ffmpeg'
            ,'-safe','0'
            ,'-f','concat'
            ,'-i',file_cmd
            ,'-c','copy',output]
            # ,capture_output=True
            # ,text=True
            ,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE
        )
        std = process_output.communicate(b'\n')
        logging.info('ffmpeg output: \n{0}'.format(std[1].decode('ascii')))

if is_main:
    path = r"C:\Users\jarre\Desktop\Videos\Meme & Dede's 60th Anniversary"
    files = get_chaptered(path)
    join_chaptered(files,output)