import os
import sys
from python_utils.hpc import get_loc
from snakemake.utils import read_job_properties


# Read arguments
args = sys.argv[1:]
timestamp = args[0]
logs_dir = args[1]
application_name = args[2] if len(args) >= 4 else 'snakemake'
job_cmd = sys.argv[-1]

# Get submit command from python_utils/hpc.py
loc = get_loc()
submit_cmd = loc.cluster['submit_cmd']

# Replace submit command wildcards with current job properties
job_properties = read_job_properties(job_cmd)

submit_cmd = submit_cmd\
    .replace('{threads}', str(job_properties.get('threads', 1)))\
    .replace('{resources.mem_mb}', str(job_properties.get('resources', {}).get('mem_mb', 2000)))

job_name = job_properties.get('rule') or job_properties.get('groupid') or application_name
if 'wildcards' in job_properties:
    wcs = job_properties['wildcards']
    if isinstance(wcs, list):
        values = wcs
    else:
        values = wcs.values()
    if values:
        job_name += '.' + '__'.join(values)

submit_cmd = submit_cmd\
    .replace('{job_name}', job_name)\
    .replace('{log_file}', os.path.join(logs_dir, f'{timestamp}_{job_name}.cluster.log'))

# Run submittion command
cmd = f'{submit_cmd} {job_cmd}'
sys.stderr.write(cmd + '\n')
os.system(cmd)
