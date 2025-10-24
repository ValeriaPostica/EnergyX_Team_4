import asyncio
import signal
import os 
# commands to start each part
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 

FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend", "api")

# We want to run both the frontend dev server (vite) and the frontend Node server
# `npm run server`. Represent them as a list of commands so we can start both.
FRONTEND_CMDS = [["npm", "run", "dev"], ["npm", "run", "server"]]  # adjust if needed
BACKEND_CMD = ["flask", "run"]  

if os.name == "nt":
    import shutil

    npm_path = shutil.which("npm")
    if npm_path:
        # replace npm executable in all frontend commands
        for cmd in FRONTEND_CMDS:
            cmd[0] = npm_path
    else:
        print("Warning: 'npm' not found in PATH. Make sure it's installed and available.")
    venv_path = os.environ.get("VIRTUAL_ENV")

    if not venv_path:
        print("Warning: VIRTUAL_ENV not set. Make sure the virtual environment is activated!!")
    flask_path = os.path.join(venv_path, "Scripts", "flask")

    if flask_path and os.path.isfile(flask_path):
        BACKEND_CMD[0] = flask_path
    else:
        print("Warning: 'flask' not found in virtual environment. Make sure the virtual environment is activated.")

    print("VIRTUAL_ENV:", venv_path)
    print("FLASK_PATH:", flask_path)


env = os.environ.copy()

async def stream_output(prefix, process):
    """Stream subprocess stdout in real time with prefix."""
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        print(f"[{prefix}] {line.decode().rstrip()}")
    await process.wait()

async def main():
    # start both processes
    frontend_procs = []
    for i, cmd in enumerate(FRONTEND_CMDS, start=1):
        p = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=FRONTEND_DIR,
            env=env,
        )
        frontend_procs.append((f"FRONTEND-{i}", p))

    backend = await asyncio.create_subprocess_exec(
        *BACKEND_CMD,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=BACKEND_DIR,
        env=env,
    )

    print("✅ Frontend (dev + server) and backend started. Press Ctrl+C to stop.\n")

    # stream outputs concurrently
    tasks = [asyncio.create_task(stream_output(name, proc)) for name, proc in frontend_procs]
    tasks.append(asyncio.create_task(stream_output("BACKEND", backend)))

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    finally:
        # terminate processes cleanly on exit
        # frontend_procs is a list of (name, proc)
        for _, p in frontend_procs:
            if p.returncode is None:
                p.terminate()
                try:
                    await asyncio.wait_for(p.wait(), timeout=5)
                except asyncio.TimeoutError:
                    p.kill()
        if backend and backend.returncode is None:
            backend.terminate()
            try:
                await asyncio.wait_for(backend.wait(), timeout=5)
            except asyncio.TimeoutError:
                backend.kill()

def handle_sigint(sig, frame):
    print("\n🛑 Received Ctrl+C, shutting down...")
    for task in asyncio.all_tasks():
        task.cancel()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
