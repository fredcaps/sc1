import subprocess

def print_message(message, symbol="*"):
    print(f"\n{symbol * 10} {message} {symbol * 10}\n")

def is_tool_installed(tool_name):
    try:
        result = subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def prompt_install_tool(tool_name):
    if not is_tool_installed(tool_name):
        answer = input(f"{tool_name} n'est pas installé. Souhaitez-vous l'installer ? (yes/no): ").lower()
        if answer in ['yes', 'y']:
            pass  # Logique pour installer l'outil
