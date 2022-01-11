from os import path
from time import sleep

import yaml

from kubernetes import client, config

DEFAULT_JOB_PREFIX='redun-job'

def get_k8s_batch_client():
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    return batch_v1

def get_k8s_core_client():
    config.load_kube_config()
    core_v1 = client.CoreV1Api()
    return core_v1

def create_job_object(name=DEFAULT_JOB_PREFIX, image="bash", command="false", labels={}, uid=None):
    container = client.V1Container(
        name=name,
        image=image,
        command=command)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0)
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=name, labels=labels, uid=uid),
        spec=spec)
    return job

def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default")
    return api_response

def get_job_status(api_instance, job):
    job_completed = False
    while not job_completed:
        api_response = api_instance.read_namespaced_job_status(
            name=job.metadata.name,
            namespace="default")
        if api_response.status.succeeded is not None or \
                api_response.status.failed is not None:
            job_completed = True
        sleep(1)
        print("Job status='%s'" % str(api_response.status))
    
if __name__ == '__main__':
    main()