"""
Helper functions for using Buis in combinaton with Django
"""
from toil.utils.toilStats import getStats, processData
from toil.common import Toil
from os import path, walk
from pathlib import Path
from toil.jobStores.abstractJobStore import NoSuchJobStoreException
from ruamel import yaml


def list_files(prefix: Path, extensions=None):
    if not extensions:
        extensions = ['cwl']
    for root, dirs, files in walk(str(prefix)):
        subfolder = root[len(str(prefix)) + 1:]
        for f in files:
            if f.split('.')[-1] in extensions:
                yield path.join(subfolder, f)



def parse_job(job: Path, repo: Path):
    with open(str(job)) as f:
        loaded = yaml.safe_load(f)

    cleaned = {}
    for key, value in loaded.items():
        if type(value) is dict:
            if value['class'] in ['File', 'Directory']:
                cleaned[key] = str((job.parent / Path(value['path'])).resolve().relative_to(repo))
            else:
                cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned


def toil_jobstore_info(jobstore: str) -> dict:
    """parses a toil jobstore folder"""
    try:
        jobStore = Toil.resumeJobStore(jobstore)
    except NoSuchJobStoreException:
        return {}
    else:
        stats = getStats(jobStore)
        return processData(jobStore.config, stats)
