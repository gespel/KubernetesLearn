import json
import logging
import argparse
import uuid
import yaml
import os

from kubernetes import client
from kubernetes import config
from kubernetes.client import V1Container, V1PodSpec, V1Pod

import tools

logging.basicConfig(level=logging.INFO)
config.load_kube_config()


class StensKubernetesHandler:
    def __init__(self):

        # Init Kubernetes
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    def create_namespace(self, namespace):

        namespaces = self.core_api.list_namespace()
        all_namespaces = []
        for ns in namespaces.items:
            all_namespaces.append(ns.metadata.name)

        if namespace in all_namespaces:
            logging.info(f"Namespace {namespace} already exists. Reusing.")
        else:
            namespace_metadata = client.V1ObjectMeta(name=namespace)
            self.core_api.create_namespace(
                client.V1Namespace(metadata=namespace_metadata)
            )
            logging.info(f"Created namespace {namespace}.")

        return namespace

    def create_container(self, image, name, pull_policy, command: list):

        # env = client.V1EnvVar(name="API_KEY", value="RGAPI-a16c5a5d-3a81-4a3a-a4ca-e00b66007d36")

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            command=command,
            args=[],
            env=[],
        )

        logging.info(
            f"Created container with name: {container.name}, "
            f"image: {container.image} and command: {container.command}"
        )

        return container

    def create_pod_spec(self, container: V1Container):
        pod_spec = client.V1PodSpec(

            containers=[container]
        )
        return pod_spec

    def create_pod(self, pod_spec: V1PodSpec):
        return V1Pod(
            spec=pod_spec
        )

    def get_pod_yml(self, pod: V1Pod):
        return yaml.dump(pod.to_dict())

    def create_pod_template(self, pod_name, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                restart_policy="Never",
                containers=[container]
            ),
            metadata=client.V1ObjectMeta(
                name=pod_name,
                labels={"pod_name": pod_name}
            ),
        )

        logging.info(
            f"Created pod-template with name: {pod_name}"
        )

        return pod_template

    def create_job(self, job_name, namespace, pod_template):
        metadata = client.V1ObjectMeta(
            name=job_name,
            labels={"job_name": job_name},
            namespace=namespace
        )

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(
                backoff_limit=0, template=pod_template
            ),
        )

        logging.info(
            f"Created job with name: {job_name}"
        )

        return job

    def execute_job(self, job_name: str, uid: str, image_name: str, cmd: list):
        logging.info(
            f"Sending job to kubernetes cluster now!"
        )
        self.batch_api.create_namespaced_job(
            namespace="default",
            body=self.create_job(
                job_name=f"{job_name}-{uid}",
                namespace="default",
                pod_template=self.create_pod_template(
                    f"{job_name}-pod-{uid}",
                    self.create_container(
                        image=image_name,
                        name=f"{job_name}-image-{uid}",
                        pull_policy="Always",
                        command=cmd
                    )
                )
            )
        )
        logging.info(f"Job sent to kubernetes!")


class StensKubernetes:
    def __init__(self):
        self.sk8s = StensKubernetesHandler()

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

    def delete_all_local_jobs(self):
        os.system("kubectl delete jobs `kubectl get jobs -o custom-columns=:.metadata.name`")
