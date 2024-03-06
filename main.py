import logging
import argparse
import uuid

from kubernetes import client
from kubernetes import config

logging.basicConfig(level=logging.INFO)
config.load_kube_config()


class StensKubernetes:
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

    def create_container(self, image, name, pull_policy, args):

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            command=["sh", "-c", "apt-get update && apt-get -y upgrade && apt-get -y install python3 && python3 && while :; do echo '.'; sleep 1; done"],
            args=[],
        )

        logging.info(
            f"Created container with name: {container.name}, "
            f"image: {container.image} and args: {container.args}"
        )

        return container


    def create_pod_template(self, pod_name, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )

        return pod_template

    def create_job(self, job_name, pod_template):
        metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )

        return job


if __name__ == "__main__":
    job_id = uuid.uuid4()
    pod_id = job_id

    """ Steps 1 to 3 is the equivalent of the ./manifestfiles/shuffler_job.yaml """

    # Kubernetes instance
    k8s = StensKubernetes()

    # STEP1: CREATE A CONTAINER
    image = "debian:latest"
    name = "debiantest"
    pull_policy = "Always"

    container = k8s.create_container(image, name, pull_policy, None)
    print(container.name)

    # STEP2: CREATE A POD TEMPLATE SPEC
    pod_name = f"stens-pod-{pod_id}"
    pod_spec = k8s.create_pod_template(pod_name, container)

    # STEP3: CREATE A JOB
    job_name = f"stens-job-{job_id}"
    job = k8s.create_job(job_name, pod_spec)

    # STEP4: CREATE NAMESPACE
    namespace = "stenscustomnamespace3"
    k8s.create_namespace(namespace)

    # STEP5: EXECUTE THE JOB
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job(namespace, job)
