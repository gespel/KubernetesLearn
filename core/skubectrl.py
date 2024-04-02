import logging
import os
import time
import uuid

import yaml

import tools
from core.core import StensKubernetesCore


class StensKubernetes:
    def __init__(self):
        self.sk8s = StensKubernetesCore()

    def create_job_and_execute_command(self, job_name: str, image_name: str, cmd: list):
        uid = uuid.uuid4()
        cmd_out = []
        cmd_out.extend(["sh", "-c"])
        i = 0
        temp_cmd = ""

        for c in cmd:

            command = c[0]
            for a in range(1, len(c)):
                command += f" '{c[a]}'"

            if i == (len(cmd) - 1):
                temp_cmd += command
            else:
                temp_cmd += command + " && "
            i += 1
        cmd_out.append(temp_cmd)

        logging.info(f"commands are {cmd_out}")

        self.sk8s.execute_job(
            job_name=job_name,
            uid=str(uid),
            image_name=image_name,
            cmd=cmd_out
        )

    def create_easy_yml(self, job_name: str):
        return tools.convert_to_camel_case(
            yaml.dump(
                self.sk8s.create_job(
                    job_name=f"{job_name}",
                    namespace="default",
                    pod_template=self.sk8s.create_pod_template(
                        pod_name=f"{job_name}-pod",
                        container=self.sk8s.create_container(
                            image="debian:latest",
                            name=f"{job_name}-container",
                            pull_policy="Always",
                            command=["echo"]
                        ),
                    )
                ).to_dict()
            )
        )

    def delete_all_jobs(self, namespace: str):
        for job in self.sk8s.list_all_jobs(namespace).items:
            logging.info(f"{job.metadata.name} is getting deleted...")
            self.sk8s.delete_job(job.metadata.name, namespace)
        logging.info(f"all jobs deleted!")

    def delete_all_local_jobs(self):
        os.system("kubectl delete jobs `kubectl get jobs -o custom-columns=:.metadata.name`")

    def execute_all_yaml_files(self, path):
        for file in os.listdir(path):
            if file.endswith(".yml") or file.endswith(".yaml"):
                try:
                    self.sk8s.execute_yaml_file(os.path.join(path, file))
                except Exception as e:
                    logging.error(f"{file} could not be executed! Exception: {e}")

    def execute_yaml_file(self, path):
        try:
            self.sk8s.execute_yaml_file(path)
            time.sleep(1)
        except Exception as e:
            print(f"{path} ERROR. {e}")