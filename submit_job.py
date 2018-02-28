#!/projects/tir1/users/pengchey/anaconda2/bin/python
from __future__ import print_function
from sh import sbatch
import sh
import sys

if len(sys.argv) <= 2:
	print('USAGE: python submit_job.py JOB_NAME job_script1.sh job_script2.sh')
	exit(1)

job_name = sys.argv[1]
job_scripts = sys.argv[2:]
job_num = len(job_scripts)

jobs = []
print('submitting batched job: %s' % job_name)
for job_script in job_scripts:
	print('\tsubmitting: %s' % job_script)

slurm_script = """#!{path_to_python}

import sh, sys
jobs = []
for job_script in {job_scripts}:
	job = sh.bash(job_script, _bg=True, _out=sys.stdout)
	jobs.append(job)

for job in jobs: job.wait()
""".format(path_to_python=sh.which('python'), 
		   job_scripts='[%s]' % ', '.join(['"%s"' % job_script for job_script in job_scripts]))

job = sbatch('--gres', 'gpu:1',
             '--job-name', job_name,
             '--mem', 10000 * job_num,  # memory
             '--cpus-per-task', job_num,  # number of cpus
             '--time', 0,  # wait time: unlimited
             '--output', 'output.out',  # assume you don't need stdout
             _in=slurm_script)

print(job.stdout)
