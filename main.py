import gui
from core import StensKubernetes

if __name__ == "__main__":
    sk = StensKubernetes()
    g = gui.start_gui(sk)

    #sk.create_job_and_execute_command(job_name="hallo", cmd=[["apt-get", "update"], ["echo", "I love you"], ["apt-get", "-y", "upgrade"], ["apt-get", "-y", "install", "neofetch"], ["neofetch"]])
    #print(sk.create_easy_yml("asd"))
