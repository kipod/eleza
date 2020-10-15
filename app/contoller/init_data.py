import os
import subprocess


PATH_TO_RESULT = os.path.abspath(os.environ.get("PATH_TO_RESULT", "results"))
MODULE_GENERATOR = os.path.abspath("init_file_generator.py")


class ParsingError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def generate_bkg_exp(file_pkl, file_data):
    # LOAD PKL FILE
    cmd = [MODULE_GENERATOR, f"--file-pkl={file_pkl}", f"--file-data={file_data}"]
    try:
        test_process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = test_process.communicate(timeout=10)
        if errs:
            raise ParsingError(errs.decode())
    except subprocess.TimeoutExpired:
        raise ParsingError("TIMEOUT!!!")

    background_file, explainer_file, plot_file = None, None, None
    for line in outs.decode().split('\n'):
        line = line.strip()
        if PATH_TO_RESULT not in line:
            continue
        if not background_file:
            background_file = line
            continue
        if not explainer_file:
            explainer_file = line
            continue
        if not plot_file:
            plot_file = line
            continue

    return background_file, explainer_file, plot_file
