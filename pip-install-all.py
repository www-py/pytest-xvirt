import subprocess

def install_requirements():
    try:
        subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
        subprocess.check_call(['pip', 'install', '-r', 'requirements-pypi.txt'])
        subprocess.check_call(['pip', 'install', '-e', '.'])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    install_requirements()