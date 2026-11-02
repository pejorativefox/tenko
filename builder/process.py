import logging
import subprocess


def run_process(command, log=None, env=None, expected_return=[0, ], cwd=None):
    """Run a process using popen with optional logging and squelch.

    arguments
    ---------
    command:            a command to execute. Can be a string or list
                        (as per the submodule documentation)
    log:                instance of logging.log.
    env:                environment variables to include when running.
    expected_return:    A list of valid return values from the process.
    """
    if isinstance(command, str):
        command = command.split(" ")
    if not log:
        log = logging.getLogger(command[0])

    log.info('Running: "%s"', " ".join(command))
    with subprocess.Popen(command, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, env=env, cwd=cwd) as proc:
        for line in proc.stdout:
            text = line.decode("utf-8", errors="replace").strip()
            if text:
                log.info(text)
        proc.wait()

    log.info("Finished. returncode: %s", proc.returncode)
    return proc.returncode
